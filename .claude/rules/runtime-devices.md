---
paths:
  - "runtime/**/*.c"
  - "runtime/**/*.h"
---

# Runtime and device-model rules

Lessons from the Sonic Riders port. Each cost at least one session; verify they hold for this
game before relying on them, and add new ones here.

**Timing must look like hardware.** Games and the SDK time hardware and retry when it looks wrong.
- DVD: completion arrives after a realistic delay (Sonic Riders: 2 ms + len / 32 MB/s), and data
  must arrive **progressively during the transfer** (16 KB pieces, DIMAR/DILEN advancing).
  CRI's streaming loader decompressed while the read was still running; copying everything at
  completion made it read stale memory. [confirmed]
- The AI sample counter must never return the same value twice in a row: `__AI_SRC_INIT` timed
  two counter steps and retried until the gap looked right, which cost 10-38 s of boot on hardware.
- Use a monotonic high-resolution clock for the guest timebase (Switch: `armGetSystemTick`,
  Windows: QPC). `timespec_get`/`CLOCK_REALTIME` was slow on the Switch.

**Interrupts follow the hardware line, status & mask.**
- When a mask bit is enabled while its status bit is already set, raise the interrupt again.
- Before delivering a latched DSP-side interrupt, ask the device whether it is still asserted.
  Delivering after the game acknowledged it made the SDK wait for mail forever.
- Interrupt handlers run on the interrupted thread's stack. Leave a small gap only
  (Sonic Riders: SP - 0x100): CRI threads have 4 KB stacks and a 0x1000 gap overwrote REL bss.

**Addresses.**
- Mask GPU-side physical addresses (TLUT sources, texture images, EFB copy destinations) with
  `0x01FFFFFF` as Dolphin does; games set high bits (bit 27 seen) and an unmasked address was
  skipped as out of range, giving wrong palettes. [confirmed]
- Guest memory window indexed by `ea & 0x3FFFFFFF` folds the cached/uncached mirrors; MMIO range
  `0xC8000000-0xCFFFFFFF` goes to the device dispatcher so inline FIFO writes are caught.

**GX on its own thread.** The GP thread parses the FIFO and does draw processing; the game thread
only appends bytes (32-byte write-gather bursts). Sync points: draw-done, PE tokens, finish
interrupts, CP read pointer reads, EFB peeks/copies to RAM, frame submit. Flush pending bursts at
every PI/CP/PE access and when the scheduler idles, or the game waits on a command that never left.
Wake the GP thread per batch (~32 KB), not per burst. Capture palette (TLUT) loads at issue time on
the game thread; the GP thread may be most of a frame behind. Never skip GXDrawDone waits.

**Threads (host side).** Every host helper thread (disc timer, card writer, audio, GP) is pinned off
the core that runs the game thread. On the Switch, Horizon does not time-slice equal priorities and
guest idle loops spin, so an unpinned helper on core 0 starved for seconds. [confirmed]

**Memory card.** Write the card image from a background thread after writes go idle (and at
exit), never per page program: per-command rewrites outlasted the CARD library's timeouts.
