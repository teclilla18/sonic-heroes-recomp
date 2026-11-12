# History

Dated sessions and hardware tests, oldest first. The Sonic Riders port's history (2026-10-15 to the fork) is in
[archive/riders/HISTORY.md](archive/riders/HISTORY.md); grep both when a problem looks familiar.

## 2026-11-11: fork

- Forked from the Sonic Riders port's `main` (309 commits; its private DX branch left out). Remote `riders` points
  at the local Riders repo for cherry-picks both ways.
- Player-facing names changed (app/exe `sonicheroes`, `SonicHeroes-*` zips, Switch title 0x010053480D9A0000,
  Android `net.srnative.sonicheroes`, update checker → `teclilla18/sonic-heroes-recomp`). Internal `SR_*` debug
  variables kept on purpose so shared files stay identical for cherry-picks.
- Riders data removed: `config/G9SE8P/` emptied (hle, patches, hot functions, shader keys), perf results, the 2P
  race route, Riders fan art (banner, cedry2kio icon). Guard and `tools/extract_iso.py` know Heroes' hashes.
- Starter-kit skills added (`/recon`, `/emu-run`, `/render-bisect`, `/hang-hunt`, `/ref-compare`, `/analyze-log`),
  plus the re-investigator agent and the recompiler / device-model rules.
- Disc copied to `baserom/`, hash equal to the original [confirmed]; `extract_iso.py` extracted main.dol, 18 RELs
  and TSonic.str, all verified [confirmed]. Nothing built yet: the runtime still expects Riders' single REL.

- First push to `teclilla18/sonic-heroes-recomp` (private). GitHub guard failed on old versions of the credited
  fan art inherited from Riders' history (`--history` scans every version); fixed with `PAST_ART` (a09bbbb),
  green on GitHub [confirmed]. Riders' public guard fails on the same 3 pictures; the fix applies to riders/main
  cleanly and keeps its fan art (tested on a temporary copy) [confirmed]; not applied to Riders (user's call).

## 2026-11-11 (later): dtk analysis of main.dol + the RELs

- First dtk 1.8.4 split stopped on "Duplicate module ID 3": stage00D and stage01D share ID 3. Every REL imports
  only itself and main.dol, so `links: []` on each module fixes the link step [confirmed].
- Next stop: stage00D relocates against 0x8044AEA8, past main.dol's bss. stage00D is a stale build for a different
  main.dol: 3,978 relocations past the DOL, 3.8% of its calls land on function starts (others 92-97%)
  [confirmed]; the stage table maps it only to stage ID 1 (unused test level). Left out of config.yml.
- Split then ran clean: main + 17 RELs, 39,075 functions, 4,680 objects, 11 s; 14 Rel14 warnings (one shared
  object in every stage REL, branch to the previous instruction) [confirmed]; whether it matters for recompiling
  [uncertain].
- Loader found: OSLink 0x801D40EC / OSUnlink 0x801D4348, each with one caller (0x80042310 load, 0x800421C8 unload)
  on one global loader object 0x8042C1C0, so one REL resident at a time [likely]. Stage ID -> REL table at
  0x80240B10 (IDs 1..61). sigmatch named 1,369 of 6,223 main.dol functions. Multi-REL design proposed (17 fixed
  bases side by side, 15.6 MB from 0x81800000; re-copy the pristine image on every OSLink): docs/notes/rel-modules.md.
- `.gitignore`: per-module dtk outputs `config/*/*/symbols.txt`, `splits.txt` were not covered; added.
- Nothing runs yet; no hardware or emulator test this session (nothing builds for Heroes).

## 2026-11-11 (evening): hle.txt, multi-REL recompiler/runtime, first PC boot

- `config/G9SE8P/hle.txt` filled from sigmatch + dtk names: OSSaveContext 801D2618 / OSLoadContext 801D2698,
  __OSInitAudioSystem 801D1C90 / __OSStopAudioSystem 801D1E4C / __OSInitMemoryProtection 801D46F4 (nop),
  OSLink 801D40EC, OSUnlink 801D4348 (new hle_OSUnlink), memcpy 800031E8, memset 80003100, memmove 801C0290.
  Riders' frame_end / vi_wait_retrace hooks are game code: not found for Heroes yet.
- Multi-REL (implemented, generic so Riders' single `_Main` uses the same code): module list from config.yml
  (`gcbin.read_modules`), section map from dtk splits.txt (`rel_section_names`; Riders' _Main still 1..4,
  checked read-only on the Riders repo), one fixed base per REL (0x81800000-0x8279FD94), `g_rel_modules[]`
  table, `rel_link_module` (relinks from the disc on every OSLink), `GUEST_RAM_SIZE` 0x02800000. Recompile:
  39,105 functions in ~170 s [confirmed]; host build links [confirmed].
- Link errors found five Riders addresses hard-coded in the runtime (`f_<addr>_orig` in hle_misc.c and
  frame_pacing.c); now looked up by hle.txt name (`hle_orig`).
- First PC boot died at once: "dispatch to 80010650" = Riders' __OSReschedule in `game_addrs.h`. SDK addresses
  there now Heroes' (RunQueue 803F23B8, RunQueueBits/Hint/Reschedule 8042CB98/9C/A0, __OSReschedule 801D6994,
  DecrementerExceptionCallback 801D1640, OSExitThread 801D6BAC by checksum match, DVD statics 8042CC18.. and
  DummyCommandBlock 803F2EC0) [confirmed by dtk names]; Riders game-state addresses point at an always-zero
  spot (`GAME_UNKNOWN`). The fatal dispatch message now dumps the SR_WATCHDOG trace.
- Second boot: runs 40 s, 3 game threads, DSP/AX, GL renderer, 8 disc reads, all 17 RELs linked at boot
  [confirmed]; then stuck after frame 2: main thread sleeps in fn_801ACC6C (RenderWare GC video driver, queue
  8042CA20) waiting for its VISetPostRetraceCallback (fn_801ABB9C) / GXSetDrawDoneCallback (fn_801AB9E0)
  wakers; the other threads wait in VIWaitForRetrace [confirmed from the watchdog dump]. Cause not looked at
  [uncertain]: retrace interrupts stop, or draw-done never signalled.

## 2026-11-11 (night): boot blocker fixed; logos, title, menus, story movie and Seaside Hill on PC

- Stall after frame 2: the main thread slept in RenderWare's GC video driver (fn_801ACC6C, queue 8042CA20) on
  a full frame-buffer ring. Its wakers (fn_801AB9E0 via GXSetBreakPtCallback 801F24B4, fn_801ABB9C via
  VISetPostRetraceCallback 801DBFC4) advance the ring when the **CP FIFO breakpoint** fires (GXEnableBreakPt
  801F24F8 / GXDisableBreakPt 801F2584 [likely, by position in GXFifo.c]). Found by: SR_DETTRACE (VI delivered
  ~60/s, no PE interrupts), SR_WATCH on the retrace queue (retrace threads fine), `[pe]` logs (no draw done
  issued), reading the wakers. Fix: gx_fifo.c models the breakpoint (hit once the GP has drained, status bit 4,
  OS interrupt 17) [confirmed: boot continues].
- Then: advertiseD -> movieD -> title -> menus -> story movie (Sofdec renders) -> stage01D, OSLink/OSUnlink for
  each [confirmed]. Stage frames showed the title card frozen over the HUD while the game ran: the 3D scene failed
  the depth test because RenderWare's **full-screen clear quad** (first main-scene draw, z always + update) lies
  outside the depth range and was clipped, leaving last frame's colour and depth. Found with SR_SKIPSAME (no
  block of draws made the overlay), SR_GXDEBUG(_ALL) (copies: the XFB copy does not clear; the clear quad covers
  0..640 x 0..480) and an SR_DEPTHCLAMP test. Fix: depth clamping instead of near/far clipping, as GX and Dolphin
  (GL_DEPTH_CLAMP; deko3d depthClampEnable; Vulkan depthClamp feature) [confirmed on PC; Switch/Vulkan not run].
- PC result: Seaside Hill at 60 fps, 2,600-2,700 draws/frame; START skips the story movie (the user's tip).
  Not implemented yet (from `[perf]`): fog (~2,000 draws/frame use it), indirect textures, Z textures.

## 2026-11-11 (late night): Switch hardware, shader keys, forwarder, public repo

- Switch NRO built (GCC, ~5 min), Eden v0.1.1 smoke test: title -> stage01D at 60 fps, frames correct
  (`SR_SHOTS`, not SR_SCREENSHOT, on the Switch). Disc image uploaded by FTP (18 min).
- Hardware test 1 (OLED handheld, GPU 384 MHz set by the app; sys-clk overclock not checked): Seaside Hill 30.0
  fps, GPU 19.9 ms/frame, "specialized shaders for 0 of 31,743 states" [confirmed]. The console recorded 17
  distinct keys (Eden the same 17). Test 2 with them built in: **59.4 fps**, GPU 4.37 ms/frame, all states
  specialized, render thread no longer waits [confirmed].
- Forwarder NSP (tools/nsp/make_forwarder.py; had kept Riders' title id, fixed to 010053480d9a0000), icon =
  somegameicons' art on a dark blue (the user's choice), user's keys passed by path. Installed by the user;
  launching from HOME works [confirmed].
- SwitchWakerHD studied: it compiles shaders on the console (uam as a library + worker + SD cache); plan in
  docs/notes/shader-compile-on-console.md; Riders told via its CLAUDE.local.md.
- Repo made public: the 12 Heroes-only commits carried the user's Gmail (Riders' public history only has the
  no-reply address), so they were rewritten to the no-reply address and the GitHub repo was deleted (by the user)
  and recreated public; guard green. Old -> new ids: a09bbbb -> 89e93e2, aa7cb5f -> 1cb9ac8, 3dd787e -> 9cc7934,
  8d5e14d -> 64086c6, 2b63b6d -> a7573d9, fb1459a -> 3020e9d.

## 2026-11-11 (end): user's play test; widescreen patch started

- User's play test (OLED, overclocked as Riders): first level runs very well, ~60 fps at 1.5x; terrain glitches
  and discolouration here and there; overlay "Fit to screen" not like Riders [accepted: first level].
- Icon: somegameicons' fan art as setup/icon.png + icon_256.jpg for every build (guard OWN_ART, README credit);
  Road to v1.0 card from Riders' tool (24%), with the rule to update it per tested change.
- Widescreen: RenderWare's RwCameraSetViewWindow is fn_8019D0CC [likely] (copies the view window to camera+0x68,
  reciprocals at 0x70/0x74, frustum update); fn_801AC6A4 builds the projection from 0x70..0x84. Patch 8019D0F0
  widens 0x68 by g_aspect_scale for screen-sized frame buffers only. Implemented, not built or run yet
  [uncertain]. No published Heroes widescreen Gecko code was found.
- sys-botbase's virtual controller blocked the user's controller until `detachController` (now in CLAUDE.local.md).

## 2026-11-11 (late): widescreen 3D, modern controls with camera tilt, pause A; user's play tests

- Widescreen: the RwCameraSetViewWindow patch works: 16:9 and 21:9 PC route shots and Eden show a wider 3D
  view, not stretched [confirmed PC, Eden]; the user played Fit window on the OLED. Menus are still stretched and
  the HUD is not at the edges: Heroes draws 2D with perspective projections, the ortho anchoring path
  (gx_render.c wide_anchor) sees ~10 draws/frame only [confirmed: SR_ANCHORLOG]. "In a stage" signal for the
  edge flags: rel_stage_active() (stageNND linked) [confirmed log: stage 1 at stage01D].
- Modern controls (setting, default on; si.c): L -> Y, R -> X (leader), right stick X -> R/L analog (turn),
  C stick centred for the game (no first-person SURVEY). Camera RE (re-investigator, docs/notes/re/camera.md):
  turn = 5 x analog trigger per frame (mulli sites in SARATOGA/JONES) -> cam_speed setting scales it [likely:
  200% about doubled a turn]. Pitch is recomputed from eye/look-at every frame, so an offset on the camera state
  did nothing [confirmed by a debug log]; the tilt is applied in the view builder (fn_8004E7EC -> fn_80050AB8):
  the eye swings about the look-at point, view pitched to match, elevation -5..75 deg (-35 went under the
  bridge) [confirmed PC shots, Eden]. Direction inverted at the user's request (stick up = view up).
- Pause menu: A also confirms while 0x8029C334 = 1 (found by SR_RAMDUMPFIELD dumps, new: RAM by VI field since
  Heroes has no frame_end hook) [confirmed PC: pause -> A -> running, twice, no reload].
- PC: scripted runs ignore real gamepads (user plays another emulator meanwhile); a pad moves to port 1 when
  port 1's pad goes away (the user's Pro Controller was taken by another program, the Xbox pad sat on port 2).
  Switch build broke on vi.c without <stdlib.h> (fixed; the first upload was the older NRO).
- User's OLED play tests (handheld, GPU 384 MHz, CPU/MEM overclocked as usual): first 60 fps median, dips to
  43-55 fps are CPU-side (vertex decode, game code), fog "not implemented" on ~94% of stage draws; second (this
  build): Seaside Hill median 59.9, p10 57.1, min 38.1 fps. User: camera "working fantastic", controls near
  perfect [accepted]. 4 new shader keys merged (21).
- User's visual goal: Wind Waker HD-like look; agreed order fog + terrain colours -> bloom/grade on Switch ->
  own SSAO -> sun shadows (research), then the same for Riders.

## 2026-11-11 (night): fog was already there; purple/dark Seaside Hill terrain fixed

- **Fog**: implemented since Riders (gx.frag, Dolphin's WriteFog); only the `[perf]` label still said "not
  implemented". Seaside Hill's fog starts far away (SR_TEVDEBUG=10: fog 0 on near geometry; on/off differ by ~1
  level). New counter: fog draws with range adjust (BP 0xE8 bit 10): 0 in Seaside Hill [confirmed PC, Eden].
- **Purple/dark ground**: found by matched comparison: SR_DFF=5000,3 (SR_GX_SYNC=1) played in Dolphin 2609a drew
  the frame right, so the state was right and our rendering wrong. SR_SKIPSAME (blocks of 200, then 20) found
  the bridge deck: 4 TEV stages, stages 1-3 subtract three 128x128 EFB copies (RGB565, exec 0x010843) weighted by
  K0.r/g/b: projected character shadows (texgen from position, clamp). SR_GLTEXDUMP of a copy: black with the
  shadow, but a green left column and light top row. Clamp smeared those edge texels over the ground, minus green
  = purple. SR_SCALE=1 was right (mean 93/108/88 vs Dolphin 92/106/87) [confirmed].
- **Cause** [confirmed]: the game clears the shadow corner with an untextured ortho quad from 0.5 to 128.5 (z
  always + update); its shadow renders are scissored to 2..125. On the GameCube (pixel centre 7/12) the quad
  covers pixel 0; at 2x the edge falls at internal 1.0 and column/row 0 keep the old picture. In widescreen the
  quad was also anchored 4:3 by wide_anchor while the 3D shadow render and the copies are stretched.
- **Fix**: gx.vert: untextured ortho draws snap their edges to the native pixel grid (`ceil(x - 7/12)`), both
  backends. gx_render.c wide_anchor: a clear (no texture, z compare always with update) is anchored STRETCH.
  Tested: PC 2x and 4x (4:3) and 16:9 match Dolphin; Eden v0.1.1 (16:9) clean, 17078 of 17078 states
  specialized, 12 dksh with per_warp_scratch 0. **Not yet on hardware.** Not checked: menus/other stages with
  the snapped untextured 2D (expected unchanged at 1x) [likely].
- **Hardware (OLED handheld, GPU 384 MHz by the app, CPU/MEM overclocked; this NRO, logs build/hw6/)**: user:
  "looks really good" [accepted for the ground]; whole log median 59.9, p10 50.3, min 33.8 fps (includes menus,
  a quit and a reload), 18572 of 18572 states specialized, no new shader keys.
- **Crash once on Pause -> Quit** (Atmosphere report build/hw6/atmo_crash.log, log crashrun.log): Data Abort
  in ld32 <- record_backtrace (sched.c, profiler attribution) <- handoff <- hle_OSLoadContext <- the game's
  exception handler (f_801D6994 -> f_801D676C) during an interrupt delivery; read of guest 0x80E687E4, inside
  the mapped window (code memory, RW, never unmapped). Not reproduced on the next try (user) nor on PC (quit ->
  Story select -> stage again). Cause unknown [uncertain]; recognise it by that stack.
- **Team Blast gauge fill split into pieces** (cyan with gaps, dark/red chunks) on the Switch in 16:9: also in
  screenshots of earlier builds, so not from this fix; suspect wide_anchor placing the fill's pieces apart
  [likely, untested].

## 2026-11-12: Team Blast gauge fill in pieces on the Switch (deko3d small-image tiling); first-release goal

- What was wrong: on the Switch the Team Blast gauge fill showed as cyan pieces with gaps and foreign red/black
  (console) or blue/white (Eden) chunks; PC drew it solid. Not a wide_anchor problem: Heroes' HUD is drawn with
  perspective cameras (only ~5 ortho draws/frame, SR_ANCHORLOG) and depth func "always" (z 0x1F) [confirmed].
- How it was found: gauge value located by RAM dumps: the user played the PC build and pressed the new F9 capture
  twice (fills 58% / 72%), dumps matched the float at 0x80303D94 (64.0 / 79.0; 100 = TEAM BLAST) [confirmed PC by
  SR_POKE]. Eden + SR_POKE 75: fault reproduced, also in 4:3. Ruled out one by one in Eden: decode helper, GP
  thread (SR_GX_SYNC), shader specialization (SR_NOSPEC), stale uploads (re-upload every frame), double texture
  retires (new check). The fill is one quad, texture C4 64x8, UV 0..1; its decoded RGBA (SR_DUMPTEX) was right.
  256 KB padding after every image turned the bad parts transparent: they were read from outside the image;
  alternating 16-texel (64-byte = one GOB) columns -> block-height mismatch between the copy and the sampler.
- Fix: render_deko.c make_image: images 8 rows tall or less (not render targets) get DkImageFlags_CustomTileSize
  + DkTileSize_OneGob. Tested Eden 4:3 and 16:9 (solid to 75%; frame diff vs before: animation only)
  [confirmed]; console OLED handheld (GPU 384 MHz by the app, CPU/MEM overclocked): user "z bar looked fine" in
  16:9 and Fit window [accepted]; 4:3 not checked because of the crop bug below.
- New tools: F9 on PC (RAM dump + screenshot + draw log of that frame), SR_POKE multi-byte with a start frame,
  `[tex] id N retired twice` check. Test runs now pass SR_FPS=0 SR_FRAMERATE=0 (the user's settings.ini has
  pc_fps=-1, which moved the screenshot clock).
- Found on the console, open: fps 41-55 while enemies are in view in Seaside Hill (draws/frame unchanged, GPU
  12 ms, game thread ~no idle: CPU bound in game code [likely]; next: SR_PROFILE on hardware). Switching to 4:3
  after 16:9 crops the picture (wide 3D view cut) [uncertain cause: view-window patch not re-applied].
- User's decision: the first release only needs to be "decently runnable" on Switch and PC (criteria in STATE).

## 2026-11-12 (later): screen-mode changes in a stage, character select in Fit, enemy fps profile (hw8)

- 4:3 after 16:9 in a stage cut the HUD on the right; 4:3 -> 16:9 looked zoomed. Reproduced on PC with the new
  SR_SCREENAT=FRAME,MODE [confirmed]. Not the view-window patch: the game calls RwCameraSetViewWindow for the stage
  camera every frame (logged) [confirmed]. The HUD bakes the widened window into its objects as the stage loads
  (RAM diff 16:9 vs 4:3: many floats scaled by exactly 854/640, e.g. k/640 pixel factors in REL data; poking one
  copy, 803ECC20 = 2 x window, did not help) [likely]. Fix: settings.c settings_hold_view (rel.c, stage
  link/unlink): a change during a stage applies at the next stage or when leaving it; menu note. Tested PC route
  16:9->4:3 and 4:3->16:9 mid-stage (shape kept, HUD intact) and 16:9->4:3 before the stage (clean 4:3)
  [confirmed PC]; applying on leaving the stage untested; console untested.
- Character select in Fit: models outside their panels after returning from a stage (user, hw8 shot_9534). The
  menu camera (advertiseD bss, 807C6F60) gets its window once as the module loads: first visit loaded at 4:3
  (unwidened = matches the stretched 2D), the second in Fit (widened). Fix: the view-window patch widens only
  while a stage REL is in (rel_stage_active) [likely; PC not re-run after this change; console pending].
- Enemy fps (hw8 log, OLED, SR_PROFILE=1): 43 fps blocks are 1/2-vsync alternation at 59.9 retraces/s, so the
  frame is only a little over 16.7 ms [likely]. Hot: GXReadDrawSync (801F37C0) from fn_801B2894 ("GP passed token
  N?") polled in a loop at 801AE220 in fn_801ADE4C: waits until the GP is done with a resource before rewriting it
  (flags +0x22, token +0x30; Egg Pawn shared skinned buffer? [uncertain]). PE reads 20k/frame on Switch vs 1.5k
  PC; PC waits 7/frame, ~0.1 ms/frame. The 27% "801D32E4 from SelectThread" is probably the vsync wait [uncertain].
  hw9 NRO on the SD carries temporary wait counters ([pewho] lines; local diffs build/temp_pewho_*.diff, not in git).

## 2026-11-12 (evening): enemy-scene GPU waits, special stage crash (far REL calls), special stage options

- hw9 (OLED docked, CPU 1785 / GPU 1152 / MEM 2133, SR_PROFILE): character select in Fit after a stage and the
  4:3 change during a stage [accepted]. Token waits with Egg Pawns: 7/frame, 1.5-2.65 ms/frame (open areas 0.1-0.2).
- Cause: RasterLock (fn_801ADE4C, RW GCN) write locks; a temp caller tally showed 6 of 7 from the character-shadow
  pass fn_800B7C88 (two 128x128 EFB-copy textures, 3 shadows), which never touches the pixels: the lock is only a
  wait [confirmed static, notes/re/rw-gcn-raster.md]. Patch: 800B7CE4/800B7E70 drop the WRITE bit. PC: 7 -> 1
  waits/frame, 0.50 -> 0.18 ms/frame; shadows look right (PC frames) and on the console (user) [accepted].
  hw10: 1 wait/frame, <= 0.41 ms/frame; fps blocks < 50: 3 of 333 (hw9: 15 of 142) [likely; different play].
  The remaining wait is the 64x64 distortion map (fn_800BEEF0, CPU-written: the wait is real).
- hw10: entering the special stage: FATAL dispatch to 841B8F18 (lr 826D2C90, stage40D). The REL at the fixed base
  82690000 calls main.dol by b/bl relocations whose displacement exceeds 26 bits; the linked word decodes 64 MB
  off (801B8F18 + 0x4000000). Fix: gcrecomp.py keeps the real target of every out-of-range REL24 (ppc2c.FAR_TARGETS,
  used by translate, branch_target and the entry fixpoint): 71027 such calls (modules above ~0x82000000). NRO 1.5 MB
  smaller. PC: special stage 40 and Egg Fleet (stage13D) play at 60 fps [confirmed PC]; console: special stage plays
  through (hw11/hw12, user) [accepted]. Other far stages untested on hardware.
- Stage select for tests: story tables at 8028CA48 (notes/re/stage-select.md); dev_stage.c writes a chosen key into
  every stage entry and the running sequence (SR_DEVSTAGE; menu only with configure --dev-menu + SR_DEVMENU=1, user:
  never in releases). Console [accepted] (switching mid-story and Off work).
- Special stages (rel_special_stage = stage40D linked): bloom off [accepted]; stick range scaled by special_steer
  (default 60 %) [accepted, "good"].
- HUD in Fit: edges only while the manager state (8029C31C) is 5 = playing [implemented]; did NOT fix the special
  stage pause menu (user: menu still off-centre everywhere; team-switch icon not at the right edge). Found: Heroes'
  stage HUD is not per-piece 2D (SR_ANCHORLOG shows only the shadow-corner draws): it is placed from the widened stage
  camera as the stage loads, so moving the icon/gauge/pause menu needs their position code [likely]. Saving box
  after a stage (split in three) untested with the change.
- User decisions: 0.1.0-alpha.1 test build (PC + Switch) for bug reports, not for playing; dev stage select out of it.

## 2026-11-12 (late): alpha prep, Switch "Save a bug report"

- Switch settings menu, About: "Save a bug report" writes bug-report-<date>.zip in switch/sonicheroes/ (info.txt:
  version, firmware, Atmosphere, docked/handheld, title/applet mode; this and the last run's log, settings.ini,
  env.txt, newest atmosphere/crash_reports file). Zip writer shared with PC (runtime/src/bug_report.c).
- Found on the console (not in Eden): the SD card cannot open the log for reading while stderr has it open for
  writing (same as FTP "550 busy"), so the first hw13 zip lacked this run's log. Fix: log_snapshot()
  (platform_switch.c) reopens stderr for reading under flockfile, copies it, reopens for appending. Console
  handheld (CPU 1785 / GPU 614 / MEM 2133): zip complete, 6 files, logging continues after [confirmed]; the save is
  one ~150 ms frame with the menu open. PC (SR_BUGREPORT=1) and Eden pass.
- README + docs/releases/0.1.0-alpha.1.md: big TEST BUILD warning and how to report; alpha/beta zips get the banner
  in README-FIRST.txt (make_release.py). SD env.txt cleared (old SR_PROFILE/SR_DEVMENU in build/hw13/env.txt.old).
- Dev builds report "v0.8.0-..." (git describe sees the inherited Riders tags); release zips use their VERSION file.

## 2026-11-12 (night): 0.1.0-alpha.1 released

- Release page: controls section (modern vs GameCube, pictures from scripted PC runs on a fresh memory card; the PC
  card's save starts Casino Park, so tests need SR_CARD=<fresh>). Pictures pinned in the guard's OWN_ART.
- The first cold Sandbox run FAILED: setup.ps1 / setup_linux.py still checked Sonic Riders' disc SHA-1 from the fork
  (every install would have stopped) [confirmed]; fixed, rerun PASS (2 installs). Switch zip setup -NoSd PASS.
- make_release needs the tools under LOCALAPPDATA/SonicHeroesSetup/tools: on this PC a scratch LOCALAPPDATA with a
  junction to SonicRidersSetup/tools was used. Launcher art: Reckoman12 banner (1800x519 crop), Nibroc.Rock icon.
- Published v0.1.0-alpha.1 (pre-release, 2fcaac6c). The --history guard scan still lists 5 old Riders pictures
  (docs/images/compare/*, settings-display.jpg) from before the fork [pre-existing].
