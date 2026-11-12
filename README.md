<p align="center">
  <img src="docs/images/banner.jpg" alt="Sonic, Tails and Knuckles leaping over the Sonic Heroes Recomp emblem in a bright blue sky" width="100%">
</p>

# Sonic Heroes native port

Play **Sonic Heroes** (GameCube, USA) natively, with no emulator, on a modded **Nintendo Switch**, and later on
**Windows**, **Android**, **Linux / Steam Deck** and **iPhone / iPad**. The game is rebuilt on your own PC from
**your own disc image**; this project contains no game files.

> [!IMPORTANT]
> **Work in progress. There is no release yet and nothing to download.** The first release, **v0.5.0**, comes
> once the game is playable on the **PC & Switch (Android, Linux, and iOS come later)**. Day-to-day status: [STATE.md](STATE.md).

## Road to v1.0

<p align="center"><img src="docs/images/progress.svg" width="720" alt="Road to v1.0: 27% done"></p>

<details>
<summary><b>What v1.0 means, and what each bar still needs</b></summary>

v1.0 = the whole game (story, Challenge and extra missions, bosses, special stages, 2-player modes) plays like
the GameCube original on every supported platform, and the Switch holds its frame rate. The first release,
v0.5.0, comes once the game is playable on the Switch and Android. The overall number is a weighted average
(game 25 %, the rest 15 % each), judged by hand after each step; `tools/make_progress.py` draws the card.

| Area | Done | Left for v1.0 |
|---|---|---|
| Whole game playable | 10 % | Done: boot, menus, Team Sonic's story movie, Seaside Hill. Left: every other stage, the four teams, bosses, special stages, saving, endings |
| Graphics match the GameCube | 60 % | Seaside Hill matches Dolphin (terrain shadows fixed at every resolution and in widescreen); left: the other stages' effects, indirect-texture effects, a 1-pixel line at the left edge, an HD look (bloom, shadows) |
| Switch performance | 45 % | Seaside Hill at 60 fps (handheld; ~60 at 1.5x with an overclock, user-tested); left: shaders for the rest of the game, big stages, movies, docked checks |
| Platforms | 25 % | PC and Switch boot and play; left: Android, Linux / Steam Deck, iPhone / iPad, the setup tool |
| 2-player modes | 0 % | Split-screen versus and battle modes not tried yet |
| Features and polish | 35 % | HOME-screen forwarder and game icon done; widescreen 3D (Hor+) tested on PC, Eden and the Switch; modern controls (leader on L/R, right-stick camera turn + tilt, speed slider, A in pause) accepted on the Switch; left: menus and HUD in widescreen, launcher, installers |

</details>

## How it works

The game's PowerPC code (`main.dol` and its 18 `.rel` modules) is translated to C ahead of time on your PC
(**static recompilation**), and the GameCube hardware (graphics, disc, audio, memory card, controllers) is
reimplemented natively: deko3d on the Switch, OpenGL / Vulkan elsewhere. This project is a fork of the
[Sonic Riders native port](https://github.com/teclilla18/sonic-riders-recomp), which follows
[SwitchWakerHD](https://github.com/centollOS/SwitchWakerHD) and
[ZeldaWWHDRecomp](https://github.com/ZeldaWWHDRecomp/ZeldaWWHDRecomp), whose PowerPC→C translator it forks.

## Legal

- A fan project, **not affiliated with, endorsed or sponsored by SEGA or Nintendo**. "Sonic Heroes" and "Nintendo
  Switch" are trademarks of their owners, used only to describe what this works with.
- **This repository contains no game code, assets, data or console keys.** You need your own disc image of Sonic
  Heroes (USA), made from a disc you own. Everything derived from the game is generated locally on your PC.
- **Never share** your built `.nro`, `.exe` or `.nsp`, or your disc image.

Licensed under the [Mozilla Public License 2.0](LICENSE), like the translator it forks
(`third_party/LICENSE-MPL-2.0`).

## Credits

- The [Sonic Riders native port](https://github.com/teclilla18/sonic-riders-recomp): everything this starts from.
- [SwitchWakerHD](https://github.com/centollOS/SwitchWakerHD) and
  [ZeldaWWHDRecomp](https://github.com/ZeldaWWHDRecomp/ZeldaWWHDRecomp): the approach and the PowerPC→C translator (MPL-2.0).
- [Dolphin](https://dolphin-emu.org/): hardware documentation and behaviour reference (no Dolphin code is included).
- [decomp-toolkit](https://github.com/encounter/decomp-toolkit), [devkitPro](https://devkitpro.org/),
  [libnx](https://github.com/switchbrew/libnx), [deko3d](https://github.com/devkitPro/deko3d),
  [SDL2](https://www.libsdl.org/), [llvm-mingw](https://github.com/mstorsjo/llvm-mingw),
  [Dear ImGui](https://github.com/ocornut/imgui) (MIT),
  [AMD FidelityFX Super Resolution 1](https://github.com/GPUOpen-Effects/FidelityFX-FSR) (MIT).
- Game icon (`setup/icon.png`, used for every console's build): fan-made
  [Sonic Heroes icon](https://www.deviantart.com/somegameicons/art/Sonic-Heroes-icon-422952372) by
  [somegameicons](https://www.deviantart.com/somegameicons) on DeviantArt, used with credit, shown on a plain dark
  blue background. somegameicons, if you'd like it changed or removed, open an issue and we'll do it right away.

Sonic Heroes is © SEGA. This project is not affiliated with SEGA.
