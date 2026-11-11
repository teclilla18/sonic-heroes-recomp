# Reference (index)

Durable facts about the port live in topic notes; this page only points to them. Dated stories of how things were
found: [HISTORY.md](HISTORY.md); current status: [../STATE.md](../STATE.md); where code lives: [MAP.md](MAP.md).
Open only the note you need, and grep inside it (`grep -n '^## '`).

This project is a fork of the Sonic Riders port (forked 2026-11-11, remote `riders`). Notes marked
**Inherited** still hold Riders' facts and numbers; revise each one for Heroes when its topic comes up.

| Note | Kind | What is in it |
|---|---|---|
| [notes/recon.md](notes/recon.md) | Current | Sonic Heroes disc recon: hashes, executables (main.dol + 18 RELs), SDK libraries, middleware, risks |
| [notes/rel-modules.md](notes/rel-modules.md) | Current | dtk run, the 18 RELs (IDs, stale stage00D), how the game loads them (OSLink callers, stage table), multi-REL design |
| [notes/shader-compile-on-console.md](notes/shader-compile-on-console.md) | Investigation | plan: uam on the console for missed shader keys (after SwitchWakerHD), shared with Riders |
| [notes/build-and-test.md](notes/build-and-test.md) | Inherited | **Quick commands** (configure/build/run for every target), Switch / PC builds, setup, releases, Eden / Dolphin |
| [notes/android.md](notes/android.md) | Inherited | Android build, install, test, touch controls, app icon, triggers, phone facts |
| [notes/debug-variables.md](notes/debug-variables.md) | Inherited | every `SR_*` debug variable (names kept from Riders on purpose), `RECOMP_*` switches |
| [notes/architecture.md](notes/architecture.md) | Inherited | GLSL (uam) rules, device/HLE boundary, shader cache, architecture decisions, SDK map (Riders' addresses) |
| [ONLINE.md](ONLINE.md), [PERF.md](PERF.md), [MODDING.md](MODDING.md), [ANDROID_PLAN.md](ANDROID_PLAN.md) | Inherited | online play, perf test, mods, Android plan |
| [notes/picture-options-port.md](notes/picture-options-port.md) | Inherited | PC picture options on Linux / Android / Switch |
| [notes/reference-projects.md](notes/reference-projects.md) | Reference | other recompilation projects to borrow ideas from, license cautions |
| [notes/launcher.md](notes/launcher.md) | Inherited | Windows launcher: build, pages, settings, install flow |
| [notes/ios.md](notes/ios.md) | Inherited | iOS port: SDL2 host layer + Vulkan on MoltenVK, signing, Documents folder, touch + pads |
| [notes/ps4-ps5-research.md](notes/ps4-ps5-research.md), [notes/vita-research.md](notes/vita-research.md) | Investigation | PS4/PS5 and PS Vita homebrew research (2026-11-03) |
| [archive/riders/](archive/riders/) | Historical | the Sonic Riders port's HISTORY, CHANGELOG, recon, game addresses, gameplay plans (read-only) |

Kinds: **Current** / **Reference** = maintained, true for Heroes; **Inherited** = from the Riders port, mechanisms
apply, facts are Riders'; **Historical** = true when written; **Investigation** = analysis with its evidence limits.
When a note is superseded, move it to `docs/archive/` with `git mv` and fix the links here.
