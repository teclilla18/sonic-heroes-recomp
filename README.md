<p align="center">
  <img src="docs/images/banner.jpg" alt="Sonic, Tails and Knuckles leaping over the Sonic Heroes Recomp emblem in a bright blue sky" width="100%">
</p>

# Sonic Heroes native port

Play **Sonic Heroes** (GameCube, USA) natively, with no emulator, on a modded **Nintendo Switch**, and later on
**Windows**, **Android**, **Linux / Steam Deck** and **iPhone / iPad**. The game is rebuilt on your own PC from
**your own disc image**; this project contains no game files.

> [!IMPORTANT]
> **In development, not playable yet.** No downloads. Status: [STATE.md](STATE.md).

**You will need:** your own **Sonic Heroes (USA)** disc image (`G9SE8P`, revision 0, a full 1.4 GB `.iso`).

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

Sonic Heroes is © SEGA. This project is not affiliated with SEGA.
