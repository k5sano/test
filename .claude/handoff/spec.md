```

了解です。ではハンドオフ資料3ファイルから出力します。開発メモ v1.0 の内容を忠実に構造化し、Claude Code が一読で全体像を掴めるようにします。

【START:.claude/handoff/spec.md】

# Loom — Project Specification

## What is Loom?

Loom is a desktop tool for managing Elektron Octatrack samples and parameters from a PC/Mac. It uses Ableton Live as the host DAW, integrates Splice for sample intake, and reflects edits to the OT hardware via MIDI CC.

To avoid IP risk, Loom is designed as an "independent tool with OT-compatible output." No Elektron trademarks or UI imitation.

## Tech Stack

| Layer | Technology | Role |
| --- | --- | --- |
| Desktop App | Tauri + Rust + React/TS | CF card management, WAV conversion, main UI |
| MIDI Engine | Python + python-rtmidi | CC transmission to OT via `ot_midi_engine.py` |
| Realtime Audio | Max for Live (.amxd) | Gen~ codebox audio engine |
| DAW Bridge | Node for Max | CF card I/O, TCP communication with Tauri |
| Database | SQLite | Sample library cache |

## Development Environment

-   macOS (live performance environment is also Mac)
-   Ableton Live Suite (Max for Live included)
-   Claude Code (Claude Max subscription)
-   Claude Opus 4.6 on Genspark (design & code generation)
-   GitHub Copilot (editor completion)
-   GLM5 / OpenClaw / Antigravity (second opinions)
-   Base repo: `octatrack-manager` fork planned

## MIDI Connection (Verified 2026-03-07)

```
Mac --USB-- Morningstar MC8 (port index: 1) --DIN-- Octatrack MIDI IN
```

-   OT AUTO-MIDI channel: **11** (status byte `0xBA`)
-   Verified: CC46=80 → T8 Track Level responded

```bash
Copypython3 -c "import rtmidi; m=rtmidi.MidiOut(); m.open_port(1); m.send_message([0xBA, 46, 80]); print('OK')"
```

## OT File Structure

```
[CF]/SetName/Audio/.../*.wav + *.ot
[CF]/SetName/ProjectName/
  project.work / project.strd    ← project settings
  bank01.work ~ bank16.work      ← banks (checksum issue!)
  markers.work / markers.strd
```

-   `.work` = autosave, `.strd` = manual save
-   Slot IDs: project is 1-indexed, bank/markers are 0-indexed
-   `.ot` file = same name as WAV, placed in same folder (gain/trim/slice/loop info)

## Critical Issue: Bank Checksum

The `calculate_checksum()` in ot-tools-io (Rust crate) has been unresolved for over a year. Community-wide blocker for bank file writing.

**Our strategy: bypass entirely.** Read via octatrack-manager → send CC via MIDI → OT hardware receives and applies → OT hardware saves. Checksum is calculated by OT itself. Problem skipped.

## Key OSS References

1.  **octatrack-manager** — Tauri+React+ot-tools-io, CF scan/project read/pattern viz/parts editor ([https://github.com/davidferlay/octatrack-manager](https://github.com/davidferlay/octatrack-manager))
2.  **ot-tools-io** — Rust crate for binary I/O ([https://gitlab.com/ot-tools/ot-tools-io](https://gitlab.com/ot-tools/ot-tools-io))
3.  **OctaChainer** — .ot file generation reference ([https://github.com/KaiDrange/OctaChainer](https://github.com/KaiDrange/OctaChainer))
4.  **ot\_utils** — Rust .ot file generation ([https://github.com/icaroferre/ot\_utils](https://github.com/icaroferre/ot_utils))
5.  **OctaLib** — C# with format research notes ([https://github.com/snugsound/OctaLib](https://github.com/snugsound/OctaLib))
6.  **elektroid** — USB transfer tool ([https://github.com/dagargo/elektroid](https://github.com/dagargo/elektroid))

## OT MIDI CC Reference

Source: [https://midi.guide/d/elektron/octatrack/](https://midi.guide/d/elektron/octatrack/)

| Parameter | CC | Notes |
| --- | --- | --- |
| Track Level | 46 | Verified working |
| Cue Level | 47 |  |
| Track Mute | 49 | 0=unmute, 1-127=mute |
| Track Solo | 50 |  |
| Track Cue | 51 |  |
| Track Arm | 52 |  |
| Recorder Arm | 53 |  |
| Note On | 59 | Receive only |

Full SRC/AMP/FX1/FX2/LFO parameters: see OT manual Appendix C. All controllable via CC.