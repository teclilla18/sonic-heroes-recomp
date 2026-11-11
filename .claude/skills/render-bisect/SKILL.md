---
name: render-bisect
description: Systematic method for rendering bugs (black screen, garbage geometry, missing or see-through surfaces, wrong colours, missing textures) on any backend. Bisects the pipeline with a present-path self-test, per-frame state overrides and tiny debug shaders. Use whenever output is wrong and the cause is not obvious from one look, especially when it works on one backend but not another.
argument-hint: "[symptom] [backend: gl|deko3d|android]"
---

# Render bisection

Symptom: $ARGUMENTS

Keep every piece of scaffolding you build here in `tools/test/render/` or behind a
`SR_*` variable and list it in docs/notes/debug-variables.md. On Sonic Riders the scaffolding was
deleted after the fix and only the method survived; keep both this time.

## 1. Prove the present path
EFB clear to a known colour → copy/blit → capture. If that colour is not what you read back, the
bug is in presentation, not in GX emulation. Stop and fix that first.

## 2. Capture one bad frame
Dump the frame's draw list (viewport, scissor, EFB copies, every draw with its state) and the
textures it binds. Pick one draw that should be visible and is not.

## 3. Bisect with overrides, re-rendering the same frame
Turn things off one at a time and watch whether the draw appears:
- force a flat-colour fragment shader → geometry and transform problem vs shading problem
- disable culling → winding (GX front is clockwise on screen)
- disable depth test / depth write → depth range or clear value
- force opaque, no blending → alpha/blend factors (destination alpha confusion)
- identity matrices / known vertex positions → XF upload or vertex decode
- replace a texture with a checkerboard → texture decode, palette or address problem

## 4. Tiny debug shaders
Output an intermediate value as colour (a matrix row, a vertex attribute, a TEV stage input) and
compare it with the same value computed on the CPU from the dumped state.

## 5. Known culprits (from Sonic Riders; check these early)
- uam miscompiling run-time vector/array indexing (garbage transforms) → `tools/lint_glsl.py`
- per-warp scratch memory exhausted by run-time indexed local arrays
- inverted face culling between backends
- destination-alpha constant replacing TEV alpha in blending (see-through walls, dark tint)
- unmasked physical addresses for textures/TLUTs (wrong palettes, rainbow UI)
- palette loads read too late by the GPU thread (capture them at issue time)
- missing indirect texturing, EFB copy formats, EFB→RAM write-back, Z peeks returning a constant

## 6. Close out
Fix, verify against Dolphin with /ref-compare, add a check to `.claude/checks.json` or a rule to
`.claude/rules/` if the bug class can be caught mechanically, and record it in docs/HISTORY.md.
