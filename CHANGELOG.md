# Changelog

Sonic Heroes native port. (The Sonic Riders port's changelog: docs/archive/riders/CHANGELOG.md.)

## Unreleased

## 0.1.0-alpha.1 (2026-11-12): TEST BUILD, not for playing

First test build for PC (Windows) and Switch, so testers can report bugs and crashes. Only Seaside Hill and the
special stage have been played through; most of the game is untested.

- Project forked from the Sonic Riders port (2026-11-11).
- Plays Seaside Hill and the special stage on PC and on the Switch (about 60 fps in Seaside Hill on an overclocked Switch); Egg Fleet starts on PC. Later stages untested.
- Widescreen ("Fit window"): the 3D view is wider instead of stretched (Hor+). Work in progress: menus are still stretched and the HUD is not at the edges yet.
- Modern controls (Gameplay tab, on by default): L / R switch the leader, the right stick turns and tilts the camera (up looks up), A confirms in the pause menu; camera speed slider (50-200%).
- Fixed purple and dark patches on the ground in Seaside Hill at higher resolutions and in widescreen (the characters' shadow pictures picked up leftovers of the previous frame at their edges).
- Switch: fixed the Team Blast gauge, whose fill showed in pieces with stray coloured blocks.
- Changing the screen mode during a stage no longer cuts off the HUD or zooms the picture: the new mode applies from the next stage.
- Fit window: the character select models stay inside their panels after coming back from a stage.
- Fixed the crash when a special stage loads ("dispatch to 841B8F18"); the same fault would have crashed most later stages (Egg Fleet and on): calls from those stages to the main program were 64 MB off.
- Switch: fewer frame-rate dips with enemies in view (the characters' shadows no longer make the game wait for the GPU 6 times a frame).
- Special stages: no bloom (the bright tube went white), and a "Special stage steering" slider (Gameplay tab, 30-100 %, default 60 %) for gentler steering.
- Fit window: the HUD moves to the screen edges only while a stage plays (dialogs such as the saving box should keep their shape; not checked yet). Known: the pause menu is off-centre and the team icon / Team Blast gauge stay near the middle.
- Switch: "Save a bug report" in the settings menu (About), like the PC's: one zip on the SD card with this run's and the last run's log, settings and the newest Atmosphère crash report.
