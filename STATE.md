# State (2026-11-11, end: Seaside Hill terrain colours fixed on PC + Eden; next: hardware check, then HD look)

Read this at the start of every session. Rewrite it in place at the end of each session (never append). Stories
behind each line: `grep` the date or topic in [docs/HISTORY.md](docs/HISTORY.md) (Riders' history:
docs/archive/riders/). Disc facts: [docs/notes/recon.md](docs/notes/recon.md).

## Where things stand

Phase 1 (boot and play). The game boots and plays its first stage on PC and on the Switch. **No release** (v0.5.0
comes once it is playable on Switch and Android; README Road to v1.0 card: 27%).

| Target (user's order) | Status |
|---|---|
| 1. Switch (first release target) | **tested** on the OLED (handheld, GPU 384 MHz by the app, CPU/MEM overclocked): title, menus, story movie, Seaside Hill median 59.9 fps (p10 57.1, min 38.1); HOME-screen forwarder installed |
| 2. Windows PC (test loop) | **tested** (scripted routes): logos -> stage01D at 60 fps; Seaside Hill matches Dolphin |
| 3. Android, 4. Linux / Steam Deck, 5. iOS | not started (backends inherited) |

Repo public (teclilla18/sonic-heroes-recomp). Local `user.email` is the GitHub no-reply address.

## Done 2026-11-11 (night; HISTORY "2026-11-11 (night)")

- **Fog was already implemented** (gx.frag, from Riders); only the `[perf]` label was stale. Seaside Hill's fog
  starts far away (mild effect). New `[perf]` count of fog draws with range adjust: 0 here.
- **Purple/dark ground in Seaside Hill fixed** (implemented + tested PC 2x/4x 4:3, PC 16:9, Eden v0.1.1 16:9;
  **not yet on hardware**). Cause [confirmed]: character shadows are 128x128 EFB copies subtracted by the
  terrain's TEV (stages 1-3, K0.r/g/b); the corner is cleared by an untextured ortho quad 0.5..128.5 which at 2x
  missed column/row 0 (GameCube pixel centre 7/12) and in widescreen was anchored 4:3. Fixes: gx.vert snaps
  untextured ortho draws to the native pixel grid; wide_anchor stretches clears (no texture, z always+update).
  PC means 93/108/88 vs Dolphin 92/106/87 on the matched frame.
- Method that worked: SR_DFF frame -> Dolphin playback (notes/build-and-test.md), SR_SKIPSAME bisect,
  SR_GLTEXDUMP of the copy, SR_SCALE=1 control run.
- Switch NRO built (12 dksh, per_warp_scratch 0; Eden: 17078 of 17078 states specialized). Not on the SD yet.

## Next steps, in order (user's priorities)

1. **Hardware check of the terrain fix** (ask before taking over the console): put build/switch/sonicheroes.nro
   on the SD (keep the old one as sonicheroes.prev.nro), play Seaside Hill handheld; look for purple/dark ground,
   watch fps (must stay ~60) and `[deko3d] specialized N of N`.
2. **HD look** (memory "hd-lighting-goal"): bloom/grade on the Switch (PC has them), own SSAO (GTAO), sun
   shadows (research: eye/look-at known, light from GX light regs). Then the same for Riders.
3. Widescreen menus/HUD: Heroes draws 2D with perspective projections, so wide_anchor (ortho only) sees few
   draws; classify perspective 2D (Im2D: near-plane z, identity-ish modelview) or patch the menu/HUD cameras.
4. More stages + shader keys; leftover Riders hooks (mods.c, netplay.c, perftest.c); Android.

## Hardware / console notes

- Remote: scratchpad `sw.py` (FTP + sys-botbase; copy it from an older session's scratchpad), settings read from
  the Riders switch-remote config (CLAUDE.local.md). From Git Bash set `MSYS_NO_PATHCONV=1` and pass sw.py as a
  Windows path (`cygpath -m`). After remote control: `detachController`. No env.txt on the SD.
- SD `switch/sonicheroes/`: NRO, disc image, SonicHeroes.nsp (forwarder), saves, logs. Previous NRO backup:
  build/hw4/sonicheroes.prev.nro. Logs of the play tests: build/hw4, build/hw5.
- Eden v0.1.1: start hidden (`Start-Process -WindowStyle Hidden`, never minimized); default keyboard input,
  muted; env.txt in its sdmc folder holds the route (now SR_SHOTS=5000,5600, SR_SCREEN=3). The new NRO is there.

## Testing etiquette (user, 2026-11-11)

All test runs in the background, muted (`SR_NOAUDIO=1`), minimized (`SR_MINIMIZED=1`); the user plays another
emulator with a controller meanwhile. Ask before taking over the console. PC test script: scratchpad
`fogab.sh <tag> [ENV=..]` (route START 1300, A every 150 to 3700, START 3900; shots via SHOTS=) -> build/run1/fog_<tag>/.
PC widescreen test: `SR_SCREEN=1 SR_WINDOW=1280x720` (SR_SCREEN=3 = fit window, a 4:3 window squeezes it).

## Waiting on the user

- Go-ahead for the hardware check (step 1).
- Riders: Heroes fixes to cherry-pick are listed at the top of Riders' CLAUDE.local.md (user's call). New shared
  candidates: gx.vert native-grid snap of untextured 2D, wide_anchor clear -> stretch, the [perf] fog label;
  earlier: input_sdl.c, vi.c SR_RAMDUMPFIELD, input_script.c CX/CY, settings.c update_check.

## Risks

- The 2D snap touches every untextured ortho draw (fades, bars) at scales above 1x: expected to look like the
  GameCube, but menus and other stages were not looked at yet [likely fine].
- 2P split screen and big stages on Switch CPU/GPU (CPU-side dips to 43-55 fps already in Seaside Hill);
  Sofdec movie speed on Switch. The game icon (setup/icon.png) is fan art (CC BY-NC-ND), credited in README.

## Shared with the Riders project (not copied)

Toolchains in `<home>/AppData/Local/SonicRidersSetup/tools`; llvm-mingw / SDL2 / imgui as junctions in
`build/ext/`; Eden v0.1.1 and Dolphin in the Riders repo's `build/ext/` (paths: CLAUDE.local.md).
build.ninja holds one target: reconfigure (configure.py) when switching PC <-> Switch (now: switch).

## Next session

```
Continue Sonic Heroes: hardware check of the Seaside Hill terrain fix, then HD look step 2 (STATE next steps).
Hardware result: <paste what you saw on the console, or say "go ahead" to let Claude copy the NRO by FTP>.
Use /hw-test: build/switch/sonicheroes.nro is built; keep the old NRO as sonicheroes.prev.nro on the SD.
Check the log with log-reader: fps vs build/hw5, [deko3d] specialized N of N, new shader keys.
Then plan bloom/grade on the Switch (plan mode; render_deko.c vs render_gl.c post passes, docs/MAP.md).
All PC/Eden runs in the background, muted and minimized; ask before taking over the console.
```
