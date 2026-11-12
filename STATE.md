# State (2026-11-11, end: widescreen 3D + modern controls accepted on Switch; next: fog + terrain colours)

Read this at the start of every session. Rewrite it in place at the end of each session (never append). Stories
behind each line: `grep` the date or topic in [docs/HISTORY.md](docs/HISTORY.md) (Riders' history:
docs/archive/riders/). Disc facts: [docs/notes/recon.md](docs/notes/recon.md).

## Where things stand

Phase 1 (boot and play). The game boots and plays its first stage on PC and on the Switch. **No release** (v0.5.0
comes once it is playable on Switch and Android; README Road to v1.0 card: 26%).

| Target (user's order) | Status |
|---|---|
| 1. Switch (first release target) | **tested** on the OLED (handheld, GPU 384 MHz by the app, CPU/MEM overclocked): title, menus, story movie, Seaside Hill median 59.9 fps (p10 57.1, min 38.1); HOME-screen forwarder installed |
| 2. Windows PC (test loop) | **tested** (scripted routes): logos -> stage01D at 60 fps |
| 3. Android, 4. Linux / Steam Deck, 5. iOS | not started (backends inherited) |

Repo public (teclilla18/sonic-heroes-recomp). Local `user.email` is the GitHub no-reply address.

## Done 2026-11-11 (late session; HISTORY "2026-11-11 (late)")

- **Widescreen 3D (Hor+)**: patch 8019D0F0 (RwCameraSetViewWindow) **tested** PC 16:9/21:9 + Eden, played on the
  Switch. **Not done:** menus are stretched, HUD not at the edges: Heroes draws its 2D with *perspective*
  projections, so gx_render.c `wide_anchor` (ortho only, `xf_reg[0x26] != 0`) sees ~10 draws/frame.
  `rel_stage_active()` (rel.c, stageNND linked) = "in a stage" signal, already drives the HUD-edge flags + bloom.
- **Modern controls** (setting `modern_controls`, default on; si.c `modern_controls`/`modern_tilt`) **accepted**
  by the user on the Switch ("camera working fantastic"): L -> Y, R -> X (leader); right stick X -> R/L analog
  (turn); right stick Y -> tilt (stick up = view up); game gets a centred C stick; A = START in the pause menu
  (`HEROES_PAUSED` 0x8029C334 [confirmed]); `cam_speed` slider 50-200% (Gameplay tab).
- Camera RE in docs/notes/re/camera.md: turn = mulli 5 sites (80134F34/44, 80131A30/40) scaled by
  g_cam_turn_scale; tilt = orbit in the view builder (8004EA74 before / 80050B78 after), look-at at
  `*0x8042C208 + 0x24`, elevation -5..75 deg. Possible issue not seen yet: camera clipping walls when tilted.
- PC: SR_INPUT runs never open real gamepads (SR_NOGAMEPAD too); a pad moves to port 1 when port 1's goes away.
  New test tools: SR_INPUT `CX=`/`CY=` (C stick), `SR_RAMDUMPFIELD=<field>,...` (RAM dumps by VI field;
  `SR_RAMDUMPAT` needs a frame_end hook Heroes lacks). Dump-diff script: equal within groups, differ between.
- 21 shader keys (4 from the user's play tests). Console has this session's final NRO.

## Next steps, in order (user's priorities)

1. **HD look, step 1: fix the base picture** (agreed order, memory "hd-lighting-goal"):
   - **Fog is not implemented** (`[perf] fog N (not implemented)`, ~94% of stage draws). Implement GX fog (BP
     0xEE-0xF2 fog params, range adjust 0xE8-0xED) in runtime/shaders/gx.frag + shader key bits; compare with Dolphin.
   - **Purple/dark terrain patches** on the Seaside Hill track (visible in every PC shot, e.g. build/run1/ctl/,
     4:3 too): /render-bisect or /ref-compare with Dolphin; suspects: EFB copies (6/frame), the 1 indirect draw,
     TEV/fog.
2. HD look, later: bloom/grade on the Switch (PC has them), own SSAO (GTAO; not MXAO code), sun shadows
   (research: eye/look-at known now, light from GX light regs). Then the same for Riders.
3. Widescreen menus/HUD: classify perspective 2D draws (Heroes/RW Im2D: near-plane z, identity-ish modelview)
   and give them wide_anchor's treatment; or patch the menu/HUD cameras.
4. More stages + shader keys; leftover Riders hooks (mods.c, netplay.c, perftest.c); Android.

## Hardware / console notes

- Remote: scratchpad `sw.py` (FTP + sys-botbase; copy it from an older session's scratchpad), settings read from
  the Riders switch-remote config (CLAUDE.local.md). From Git Bash set `MSYS_NO_PATHCONV=1` and pass sw.py as a
  Windows path (`cygpath -m`). After remote control: `detachController`. No env.txt on the SD.
- SD `switch/sonicheroes/`: NRO, disc image, SonicHeroes.nsp (forwarder), saves, logs. Previous NRO backup:
  build/hw4/sonicheroes.prev.nro. Logs of the play tests: build/hw4, build/hw5.
- Eden v0.1.1: start hidden (`Start-Process -WindowStyle Hidden`, never minimized); default keyboard input
  (does not take the user's gamepads), muted; env.txt in its sdmc folder holds the route.

## Testing etiquette (user, 2026-11-11)

All test runs in the background, muted (`SR_NOAUDIO=1`), minimized (`SR_MINIMIZED=1`); the user plays another
emulator with a controller meanwhile. Ask before taking over the console.

## Waiting on the user

- Riders: Heroes fixes to cherry-pick are listed at the top of Riders' CLAUDE.local.md (user's call). This
  session's shared-file changes Riders could take: input_sdl.c (pads ignored in scripted runs, port-1 move),
  vi.c SR_RAMDUMPFIELD, input_script.c CX/CY, settings.c saving update_check. si.c modern controls and
  rel_stage_active are Heroes-only behaviour (would need a guard there).
- Screenshots of the terrain errors from the console (hold - menu "Save screenshot") would help step 1.

## Risks

- 2P split screen and big stages on Switch CPU/GPU (CPU-side dips to 43-55 fps already in Seaside Hill:
  vertex decode + game code); Sofdec movie speed on Switch.
- The game icon (setup/icon.png) is fan art (CC BY-NC-ND), credited in README as Riders does.

## Shared with the Riders project (not copied)

Toolchains in `<home>/AppData/Local/SonicRidersSetup/tools`; llvm-mingw / SDL2 / imgui as junctions in
`build/ext/`; Eden v0.1.1 and Dolphin in the Riders repo's `build/ext/` (paths: CLAUDE.local.md).
build.ninja holds one target: reconfigure (configure.py) when switching PC <-> Switch.

## Next session

```
Continue Sonic Heroes, HD-look step 1: fog and the purple/dark terrain patches in Seaside Hill (STATE next step 1).
Start with fog: grep "fog" in runtime/src/gx_render.c, runtime/shaders/gx.frag and gx_shader_key.c (docs/MAP.md);
plan mode (shader + key bits + both backends). Then /ref-compare a Seaside Hill frame against Dolphin for the
terrain colours (PC route: START 1300, A every 150 fields to 3700, START 3900; stage from field ~4100).
Run every test in the background, muted and minimized (the user is using the PC).
Verify: PC shots before/after vs Dolphin, Eden, then a console build (after deko3d changes every dksh must report
per_warp_scratch 0, and [deko3d] must still specialize N of N states). Update the Road to v1.0 card if graphics move.
```
