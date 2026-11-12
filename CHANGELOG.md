# Changelog

Sonic Heroes native port. Nothing released yet. (The Sonic Riders port's changelog: docs/archive/riders/CHANGELOG.md.)

## Unreleased

- Project forked from the Sonic Riders port (2026-11-11).
- Boots to the first stage (Seaside Hill) on PC and on the Switch (about 60 fps in the first stage). Not playable as a whole yet; no release.
- Widescreen ("Fit window"): the 3D view is wider instead of stretched (Hor+). Work in progress: menus are still stretched and the HUD is not at the edges yet.
- Modern controls (Gameplay tab, on by default): L / R switch the leader, the right stick turns and tilts the camera (up looks up), A confirms in the pause menu; camera speed slider (50-200%).
- Fixed purple and dark patches on the ground in Seaside Hill at higher resolutions and in widescreen (the characters' shadow pictures picked up leftovers of the previous frame at their edges).
- Switch: fixed the Team Blast gauge, whose fill showed in pieces with stray coloured blocks.
- Changing the screen mode during a stage no longer cuts off the HUD or zooms the picture: the new mode applies from the next stage.
- Fit window: the character select models stay inside their panels after coming back from a stage.
- Fixed the crash when a special stage loads ("dispatch to 841B8F18"); the same fault would have crashed most later stages (Egg Fleet and on): calls from those stages to the main program were 64 MB off.
- Switch: fewer frame-rate dips with enemies in view (the characters' shadows no longer make the game wait for the GPU 6 times a frame).
- Special stages: no bloom (the bright tube went white), and a "Special stage steering" slider (Gameplay tab, 30-100 %, default 60 %) for gentler steering.
- Fit window: the HUD moves to the screen edges only while a stage plays (dialogs such as the saving box should keep their shape; untested).
