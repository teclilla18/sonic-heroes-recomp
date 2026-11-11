# On-console shader compilation (plan, Investigation; nothing implemented)

Written 2026-11-11 after studying SwitchWakerHD (`<home>/SwitchWakerHD-Build`, MPL-2.0; its docs
`background-shaders-plan.md`, `shader-variant-memory-plan.md`, `runtime/third_party/uam/PATCHES.md`). Shared-runtime
work: Sonic Riders gets it too (its CLAUDE.local.md points here).

## Today (both ports)

- Specialized fragment shaders are built **ahead of time**: `tools/gen_shaders.py` turns each key in
  `config/G9SE8P/shader_keys.txt` into the ubershader source with `SPECIALIZED` and the key's constants, compiles
  it with uam, embeds the dksh table. A miss draws with the ubershader (correct, slower) and is recorded to
  `sdmc:/switch/<game>/shader_keys.txt`.
- Heroes, 2026-11-11: 17 keys cover title, menus, story movie and Seaside Hill; hardware 30.0 -> 59.4 fps
  (handheld, GPU 384 MHz set by the app), GPU 19.9 -> 4.37 ms/frame. The key list carries the speed.

## What SwitchWakerHD does

- uam 1.1.0 built as a static library (`uamlib`, zlib/MIT) linked into the app; about ten patches: real mutexes,
  DKSH to memory (`WriteDksh`), a log callback, no `exit()`/`abort()` on errors, reentrancy.
- One worker thread (8 MB stack, priority below the game's threads, cores 0/2) compiles missing shaders
  (~50 ms each) into a cache on the SD card, loaded at boot.
- First start: a "preparing graphics" pass (title screen recorded behind a loading card, related states
  predicted) compiles ~19,000 shaders in ~19 minutes; ~74% of the whole game. A shipped, code-free "template"
  (states only) seeds it.
- Lesson (their #37): keys that hashed registers the shader does not read multiplied variants (~52,000 in 4 h)
  until the Switch ran out of memory. Exact keys + a cap fixed it.

## Plan for this runtime

1. **Keep the ahead-of-time list** as the main path (PC routes with `SR_SHADER_KEYS`, plus console misses).
2. **uam on the console** for keys the list misses:
   - bring uam in as a library (follow their patch list; record upstream commit + licence in third_party/);
   - the specialized source is the ubershader + `#define`s (port gen_shaders.py's text step to C, ~100 lines);
   - one low-priority worker on a non-game core; the draw keeps the ubershader until the shader is ready
     (never skip a draw);
   - cache file `sdmc:/switch/<game>/shadercache.bin` (key -> dksh), versioned by the ubershader source hash;
   - a cap on variants and an `[mem]`-style counter; the per_warp_scratch check at run time (reject, keep the
     ubershader).
3. No first-start "preparing graphics" pass unless the key set turns out large: Heroes collapses ~31,700 draw
   states to 17 keys in the first stage.

## Open questions

- uam's size in the NRO and its memory peak during a compile on the Switch.
- Whether Android (Vulkan, glslc at build time) wants the same: shaderc on device is heavier.
