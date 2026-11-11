---
name: emu-run
description: Run the current build automatically, either the PC build or the Switch NRO in the Switch emulator, with scripted input, debug variables, self-captured screenshots and a filtered log, then report what happened. Use for smoke tests before hardware tests, for reproducing bugs, for checking a fix, and whenever the user asks to "run it", "boot it" or "check it in the emulator".
argument-hint: "[pc|switch] [route or goal] [extra env vars]"
---

# Automated run

Request: $ARGUMENTS

Drivers live in `tools/test/` (committed). If the one you need does not exist yet, write it there
once, generically (target, route file, env vars, timeout, output folder), instead of a one-off
command. Outputs go to `build/test/<date>-<name>/`.

## PC build
- Run headless or minimized with the env vars from docs/notes/debug-variables.md: scripted input route
  (`tools/test/routes/*.txt`), screenshot frames, watchdog, audio off for automated runs.
- Look at frames through the port's own self-captures, never a desktop screenshot (other windows
  end up in the image).

## Switch build in the emulator
- Emulator path and version are in CLAUDE.local.md. Record the emulator version with every result:
  on Sonic Riders only one version (Eden v0.1.1) could run deko3d homebrew at all, and newer ones
  aborted in `dkDeviceCreate`. Re-check this when the emulator changes.
- The emulator needs the user's own keys in its portable `user/keys/`. Never read, copy or list
  their contents; if they are missing, tell the user.
- Copy the NRO, a copy of the disc image and `env.txt` into the emulator's SD folder for the game.
- Launch so the render surface has a real size: on Sonic Riders a minimized emulator crashed
  (zero-size surface) and a minimized PC window stalled rendering. A hidden or visible window
  is fine. Keep the emulator muted for automated runs.
- Emulator numbers are indicative only. JIT and host shader compilation make some things look
  worse (first-time scenes) and some better than hardware. Say "emulator" next to every number.

## Report
- What was reached (last screen, frame count), fps or timing summary, any `[hitch]`, `[crash]` or
  watchdog output, and the screenshot paths. Use the log-reader subagent for long logs.
- If the run contradicts STATE.md or a previous result, say so explicitly.
