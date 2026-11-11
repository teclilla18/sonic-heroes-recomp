---
name: recon
description: First-contact reconnaissance of a GameCube or Wii disc image for a static-recompilation port. Verifies the dump, inventories the disc, identifies executables, compiler, SDK, middleware, DSP microcode and leads, and estimates the job. Use at the start of a new game project, when the user adds a new disc or revision, or asks what is on the disc, what toolchain or middleware the game uses, or how big the port is.
argument-hint: "[path to the disc image in baserom/]"
---

# Disc recon

Goal: a written, evidence-tagged picture of the disc before any port code exists. Output goes to
`docs/notes/recon.md` (committed: facts and hashes only, no game data) and local working files go to
`baserom/` (gitignored). Tag every claim [confirmed]/[likely]/[uncertain] and say why.

Disc: $ARGUMENTS (if empty, list `baserom/` and ask which file).

## Ground rules
- Work on the copy in `baserom/`. If there is no copy yet, copy the original (path in
  CLAUDE.local.md) into `baserom/` and confirm both SHA-1 hashes match before using it.
  Never modify, move or rename the user's original image.
- Nothing extracted from the disc leaves `baserom/` or `build/`.
- Web searches are fine. Downloading prototypes, other versions or symbol dumps is the user's call:
  report what exists and where, then ask.

## Steps

1. **Verify the dump.** SHA-1, MD5 and CRC-32 of the image. Search Redump for the title and
   region and compare. Record serial, edition and the Redump page.
2. **Disc header.** Game ID (console, title code, region, maker), disc number, revision, region
   code, internal title, DOL offset, FST offset/size, apploader date. Wii discs: note the
   partition layout and that the data partition is encrypted; use a disc tool that decrypts
   (decomp-toolkit's disc support, nod, or dolphin-tool), never hand-rolled crypto with the
   user's keys printed anywhere.
3. **FST inventory.** File count, sizes by extension/type, notable files (RELs, `.str` name tables,
   archives, video, audio banks). Save the full listing to `baserom/fst_listing.txt`; summarise it.
4. **Executables.** Extract main.dol and every REL into `baserom/`, hash them. DOL: section table
   (offset, load address, size, probable name), entry point. Each REL: module id, version, section
   table, fixSize, prolog/epilog/unresolved, imports. Note where RELs expect to be loaded.
5. **Toolchain fingerprints.** Metrowerks strings (`__start`, MetroTRK, runtime messages); SDK
   build-date strings per library; C vs C++ evidence (.ctors/.dtors contents, extab/extabindex,
   mangled names, RTTI). The exact MWCC version only matters for a matching decomp; note a guess.
6. **Middleware.** Version strings for CRI (ADX, Sofdec, AFS), RenderWare, Havok, JSystem, etc.
   Flag middleware that will cost CPU on ARM (software video decoders, audio codecs).
7. **DSP microcode.** Find the ucode the game uploads and identify it (AX family vs Zelda-style vs
   others). This decides which audio HLE the runtime needs; the Sonic Riders runtime implements AX.
8. **Hardware features to expect.** Grep/scan for EFB peeks and copies to RAM, indirect texturing,
   ARAM streaming, multiple viewports/split-screen, progressive scan, widescreen hacks, Wii
   specifics (IOS, Wiimote, NAND saves). Each one is runtime work.
9. **Leads for naming.** Map files, debug ELFs, prototypes with symbols, other platform releases
   (PC/PS2/Xbox builds with symbols), existing decomps (github.com/doldecomp), community reverse
   engineering (file formats, structs, mods, cheat codes such as widescreen Gecko codes).
10. **Scale.** Code size per executable, rough instruction count, share that is SDK/middleware.
11. **Function discovery.** Set up decomp-toolkit's `config.yml`, run its analysis, record function
    count and anything it could not resolve. Run SDK signature matching if the tooling exists
    (the previous port had `tools/sigmatch.py` against Dolphin's signature database).

## Then
- Confirm or correct the game facts in CLAUDE.md (game ID, disc revision, executables) and
  resolve every TODO marker recon can answer; show the user the diff.
- Add the risks found in steps 6-8 to STATE.md "Open problems" and to docs/REFERENCE.md if they
  affect a specific target.
- End with a short summary: what is confirmed, what is uncertain, the three biggest risks.
