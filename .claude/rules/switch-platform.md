---
paths:
  - "runtime/src/platform/switch/**"
---

# Switch platform code

- Pin every host helper thread off core 0, which belongs to the game thread. Horizon does not time-slice equal priorities, so an unpinned helper on core 0 can starve the game (this once caused 10-30 s boot stalls).
- A thread that must keep up (the audio mixer) runs one priority step above its core neighbour.
- Switch CPU gains can't be measured on PC or in Eden, only on hardware. Say so instead of claiming a speedup from a PC or Eden number.
