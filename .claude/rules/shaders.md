---
paths:
  - "runtime/shaders/**"
  - "tools/gen_shaders.py"
  - "tools/embed_shaders.py"
---

# Shared GX shaders (deko3d's uam compiler miscompiles these patterns)

- Never index a vector or a local array with a runtime value. Use the explicit selects instead: `pick()` in `gx_common.glsl`, and `comp()`, `cinput()`, `ainput()`, `reg()` in `gx.frag`. uam silently returns wrong components, and a black screen was the result once.
- In vertex shaders: no loop-carried vec4 accumulator seeded from a parameter, and no `continue` in vector-accumulating loops.
- After any shader change, every dksh in `build/switch/shaders/` must report `per_warp_scratch 0`. Nonzero scratch means a runtime-indexed array slipped in.
- Shader keys must contain only bits the shader actually reads. Extra bits make states miss the specialized cache and fall back to the ubershader, which silently multiplies GPU time on the Switch.
