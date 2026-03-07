# Claude Code — First Task & Rules

## Read First

Read all files in `.claude/handoff/` before starting any work:

-   `spec.md` — project overview, tech stack, MIDI connection, OT file structure
-   `design.md` — architecture, checksum bypass, macros, Splice integration
-   This file — first task and implementation rules

## First Task: `ot_midi_engine.py`

Build the MIDI CC engine that bridges the Tauri app and the Octatrack.

### Requirements

1.  **TCP server** — Listen on `localhost:9100` for JSON commands from Tauri
2.  **MIDI output** — Send CC messages via python-rtmidi to port index 1 (Morningstar MC8)
3.  **Channel** — OT AUTO-MIDI channel 11 (status byte `0xBA`)
4.  **Command format:**

```json
Copy{
  "type": "cc",
  "channel": 11,
  "cc": 46,
  "value": 80
}
```

```json
Copy{
  "type": "batch",
  "messages": [
    {"channel": 11, "cc": 46, "value": 80},
    {"channel": 11, "cc": 47, "value": 64}
  ],
  "interval_ms": 10
}
```

```json
Copy{
  "type": "list_ports"
}
```

1.  **Rate limiting** — Minimum 5ms between CC messages (OT can choke on rapid fire)
2.  **Logging** — All sent messages logged with timestamp
3.  **Graceful shutdown** — Clean up MIDI port on exit

### File Location

```
loom/
  midi/
    ot_midi_engine.py
    requirements.txt
```

### Test After Implementation

```bash
Copy# Terminal 1: start engine
cd loom/midi && python ot_midi_engine.py

# Terminal 2: send test command
echo '{"type":"cc","channel":11,"cc":46,"value":80}' | nc localhost 9100
```

Verify OT T8 Track Level moves.

## Implementation Rules

1.  **No bank file writing.** Read-only for CF card. All parameter changes go through MIDI CC.
2.  **OT terminology in comments only.** Code-facing names use Loom terms (Scene, Param Point, etc). Comments may reference OT terms for clarity.
3.  **Python for MIDI, Rust for files.** Do not mix. MIDI engine is Python. CF card parsing is Rust (via ot-tools-io in Tauri).
4.  **Fail safe.** If MIDI port is unavailable, queue messages and retry. Never crash silently.
5.  **Log everything.** Every MIDI message sent, every TCP command received. Timestamped.
6.  **Test with real hardware.** The verification command is: `python3 -c "import rtmidi; m=rtmidi.MidiOut(); m.open_port(1); m.send_message([0xBA, 46, 80]); print('OK')"`
7.  **Keep files small.** One file, one responsibility. No god modules.
8.  **Comments in English.** Commit messages in English.