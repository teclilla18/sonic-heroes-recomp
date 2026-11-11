---
name: ref-compare
description: Compare the port's rendering (or timing/RNG behaviour) against Dolphin as the reference, using matched frames from attract-mode demos or identical scenes, and list the visual differences by cause. Use when something "looks wrong", "too dark", "missing", "discoloured", for any renderer accuracy work, and before claiming a rendering bug is fixed.
argument-hint: "[scene or effect to compare]"
---

# Reference comparison against Dolphin

Target: $ARGUMENTS

Dolphin (portable, path in CLAUDE.local.md) is ground truth for what the game should look like.
All captured frames are game imagery: they stay in `build/`.

1. **Find a matched moment.** Attract-mode demos run without input in both, so they are the
   easiest match; align them by an on-screen timer or event, not by frame number (the two diverge:
   on Sonic Riders the demos differed in racers and ring placement). For menus, use the same
   save and the same route. Dolphin input movies did not take effect in the build used last
   time; a fake DSU (cemuhook) controller with background input is the next thing to try.
2. **Capture.** Dolphin: frame dump (extract stills with ffmpeg). Port: its self-capture at the
   matching frame. Same internal resolution where possible.
3. **Compose** a side-by-side or difference image with Python/PIL into `build/test/refcmp/` and
   look at it.
4. **Classify each difference** by likely stage: geometry/culling, depth, blending/alpha,
   texture decode or palette, lighting (channel colours, specular, attenuation), fog,
   EFB copies/post-effects, indirect texturing, timing/RNG divergence (not a renderer bug).
5. **Narrow it** with the port's per-frame draw dump and texture dump, and the state-override
   tricks in /render-bisect.
6. **Report** a table: difference · where on screen · suspected stage · evidence · next check.
   A difference stays [uncertain] until a matched comparison shows it fixed.
