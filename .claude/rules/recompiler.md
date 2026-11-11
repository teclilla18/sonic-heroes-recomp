---
paths:
  - "tools/recomp/**"
  - "runtime/include/ppc*.h"
  - "config/*/hle.txt"
  - "config/*/patches.txt"
---

# Recompiler rules

- Files forked from ZeldaWWHDRecomp's translator stay MPL-2.0 with their headers intact; record the
  upstream commit in third_party/ when syncing. New front-end code may use the project licence.
- Function discovery comes from decomp-toolkit analysis, not hand lists. If dtk's string detection
  misbehaves on a REL section (it did on Sonic Riders REL sec 2), disable it in config.yml rather
  than patching around the output.
- Jump tables are found structurally (a data object whose words all point inside one function).
  The recompiler must *report* every `lwzx/mtctr/bctr` sequence it could not resolve; never
  silently emit a fallback.
- Dispatch to an address that is not a known function entry must abort loudly with the address.
- Callee-saved registers may live in C locals across calls (EABI), except for functions that
  save/restore context by hand (OSSaveContext/OSLoadContext, `_restfpr_N`/`_savegpr_N` style
  helpers): keep those in an explicit exception list with a comment saying why.
- Guest memory helpers must be force-inlined (`PPC_ALWAYS_INLINE`). GCC on the Switch left ~130K
  `ld32/st32` call sites as real calls while clang inlined them on PC, so the PC profile hid it.
  Check the Switch binary size and a profile after changing them. [confirmed on Sonic Riders]
- Loops that can spin waiting on interrupts must reach an interrupt check; functions that keep r1
  in a C local must hand it back at those checks (Sonic Riders: `PPC_LOOP_R1`).
- Code patches (patches.txt) and HLE replacements (hle.txt) are documented one per line with the
  reason and how it was verified. Prefer register-level device models over function-level HLE:
  the game's own SDK code then keeps running unchanged.
- After any change: regenerate, build PC and Switch, boot to the first known screen with scripted
  input, and compare the frame against the previous build.
