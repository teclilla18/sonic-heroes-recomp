# Camera (in-stage player camera) — G9SE8P rev 0

Found 2026-11-11 by static reading of dtk's asm (tools/showfn.py). No runtime check yet.

## Pad data the game uses

- PADRead wrapper `fn_80014F60` [confirmed]: calls `fn_801DE988` (PADRead [likely]) into the raw PADStatus array
  `0x8029C1D4` (4 x 0xC), then `fn_801DDC88` (PADClamp [likely]), resets ports that report an error.
- `fn_80015170` converts one PADStatus into the game's pad record (0x4C bytes) [confirmed]:
  +0x00 held buttons, +0x04 ~held, +0x08 pressed, +0x0C released, +0x10 triggerRight, +0x12 triggerLeft (u16, from
  PADStatus +7/+6), +0x14/+0x16 main stick X/Y, +0x18/+0x1A C-stick X/Y (s16, Y negated, clamped to +-0x40,
  dead zone +-6), +0x20/+0x28 stick magnitudes (float), +0x44/+0x48 direction flags.
- Pad record arrays inside `lbl_8029BBD0` (4 records of 0x4C each, indexed through the port map `0x802408F8`):
  +0x48 = `0x8029BC18` (the one camera/game code reads), +0x210 = `0x8029BDE0` (returned by `fn_8001496C`),
  +0x3F0 = `0x8029BFC0` (live). Code addresses them as `lbl_8029BBD0 + port*0x4C + 0x48 + field`, so
  triggers show up as offsets 0x58/0x5A and C-stick X/Y as 0x228/0x22A or 0x60/0x62.

## Camera system

- Mode table `0x80239A30`: 27 entries of {name, mode function, flag}. Names [confirmed, strings]:
  0 NONE, 1 USER, 2 SAMPLE `fn_8013442C`, 3 TEST `fn_80136638`, 4 EDITOR `fn_80131168`, 5 EDITOR2 `fn_80131348`,
  6 NAPA `fn_80133220`, 7 SNAPSHOT `fn_80135C30`, 8 SARATOGA `fn_801348D0`, 9 COLL_CHECK `fn_80130E70`,
  10 KLAMATH `fn_801321B4`, 11 POINT `fn_80133BC4`, 12 ASHLAND `fn_80130DF0`, 13 SURVEY `fn_80135E68`,
  14 PATH `fn_80133948`, 15 LEAVE `fn_801323C4`, 16 COLLISION (none), 17 EASY `fn_801310C8`, 18 MOTION `fn_80132B7C`,
  19 FIX `fn_8013139C`, 20 POINT2 `fn_80133D44`, 21 TAKUTO `fn_801364C8`, 22 INCONTINENCE `fn_801313F0`,
  23 RABBIT `fn_80133FC0`, 24 JONES `fn_80131600`, 25 LINEPATH `fn_8013245C`, 26 BOSSPOINT `fn_80139FC4`.
- Per-screen camera stacks `0x802B908C` (4 x 0x2324; screen index `0x8042C1FC`), entries of 0x114, top index at
  +0x8C; entry +0x90 mode index, +0x98 frame counter, +0x9C mode function, +0xA4 work area [likely].
- Per-frame runner `fn_800519B8` [confirmed]: calls the top entry's mode function with r3 = `0x802C218C` (active
  camera state, 0x54 bytes) and r4 = entry+0x90; then `fn_80136258` and `fn_80134728`.
- Camera state `0x802C218C` [likely layout]: +0x00 state, +0x10..0x18 eye position (floats), +0x1C pitch and
  +0x20 yaw (s32 angles, 0x10000 = 360 deg), +0x34..0x3C look-at point, +0x40 float. Degree <-> angle constants
  182.04445 (`0x8042EFFC`) and 360/65536 (`0x8042F000`).

## L/R turning

- Modes SARATOGA (`80134F34`/`80134F44`) and JONES (`80131A30`/`80131A40`) [confirmed]: yaw += 5*R - 5*L each frame,
  where R = max(triggerRight, 2*C-stick X if > 0) and L = max(triggerLeft, 2*|C-stick X| if < 0). Speed follows
  the analog trigger value (0..150 after PADClamp [likely]); the 5 is a `mulli` immediate, not a float.
  TEST mode (`fn_80136638`) uses factor 3 and a fixed pitch of -0xE38 (-20 deg).
- The digital L/R bits (0x40/0x20 at record +0) are only tested to see that the player is not turning
  (SARATOGA at 80135390: no L, no R, no C-stick X -> auto camera recentres) [confirmed].
- `fn_8004D6F8` is a debug free-move (D-pad moves, L/R raise/lower), not the player camera [likely].

## Pitch

- SARATOGA only lowers pitch by 1 deg steps (down to -45 deg) when the eye collides, else keeps +0x1C [likely].
- Existing C-stick look: `fn_80136258` pushes mode 13 SURVEY (first person) when the C-stick is off-centre
  [confirmed]; SURVEY (`fn_80135E68`) turns +0x20 with C-stick X and +0x1C with C-stick Y, clamped to +-0x38E3
  (+-80 deg). Sign of "up" not checked.

## Per-frame order and the view matrix (2026-11-11, follow-up)

- `fn_8004E6F0(r3, screen)` is the per-screen camera update [confirmed, static]: `fn_80051A68` (not read),
  `fn_800519B8` (override/event layer, entry+0x90 stack: often empty, r12 == 0), `fn_800516E4` (resolve),
  then the base layer: `fn_800518AC` (SARATOGA direct, when `0x802C1D1C + screen*0x114` is non-zero) or
  `fn_80051944` (mode function of the base stack at entry+0x11D0), `fn_800516E4` again, `fn_80051614`.
- `fn_800516E4` resolves the camera state `0x802C218C` by its +0x00 state [confirmed]: state 0 and 2/4 derive
  pitch +0x1C / yaw +0x20 / distance +0x40 from the eye (+0x10) -> look-at (+0x34) vector (`fn_80051FF0`);
  states 1/3 build that vector from pitch/yaw (`fn_80051F68`) and move the look-at (1) or the eye (3).
  Modes leave state 0, so eye and look-at positions are what persists; pitch is recomputed every frame.
  This is why a value added to +0x1C does not survive [confirmed by the coordinator's PC run].
- `fn_80051614` copies the state into the per-screen copy `0x802B908C + screen*0x2324 + 0x40` (pointer in
  `0x8042C208`): +0x00 eye, +0x0C pitch, +0x10 yaw, +0x14 roll, +0x18 look-at direction, +0x24 look-at point,
  +0x3C distance [confirmed]. Many objects read this copy.
- `fn_8004E7EC` (called from 8001A234, render side) sets the view window and calls `fn_80050AB8(block+0)` at
  8004EA74 with the eye copied to block+0..8 [confirmed]. `fn_80050AB8` builds the RW camera frame
  [confirmed]: reset (`fn_8019EE04`), rotate 180 deg about Y, roll about Z (copy+0x14), pitch about X
  (copy+0x0C, as degrees in f1 at 80050B78), yaw about Y (copy+0x10, f1 at 80050BB8), then translate by the
  eye (`fn_8019EB94`), all post-concatenated (combine 2). Axis vectors 0x802429B8 X, 0x802429C4 Y, 0x802429D0 Z.
  Also called at 8004D554 / 8004D580 (other cameras, not read).

## Port features built on this (2026-11-11, PC runs in Seaside Hill)

- Turn speed (setting cam_speed): patches at the four `mulli 5` sites scale the turn [likely: a 60-field turn at
  full stick went -123 deg at 100% and about -241 deg (read +119 after the wrap) at 200%].
- Tilt (modern controls, right stick up/down): in `fn_8004E7EC` before the call at 8004EA74 the block's eye is
  swung about the look-at point (`*0x8042C208` + 0x24) and the view pitch (f1 at 80050B78) changed by the same
  angle [confirmed: with the first sign, stick up = camera high looking down; the user then asked for the inverse: stick up = camera low looking up]. Elevation is
  kept within -5..75 deg (-35 went under the bridge). Negative frame pitch = looking down.
- A value added to the state's pitch (+0x1C) around `fn_800519B8` does nothing (recomputed from eye/look-at)
  [confirmed]; the mode call in `fn_800519B8` is skipped while the camera idles.
- Pause: `0x8029C334` = 1 while the stage's pause menu is open [confirmed: 2 pause/A cycles, PC].
