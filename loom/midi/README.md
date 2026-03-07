# Loom MIDI Engine

TCP→MIDI CC bridge for Octatrack control.

## Setup

```bash
Copycd loom/midi
pip install -r requirements.txt
```

## Run

```bash
Copypython ot_midi_engine.py
```

Options:

```
--port       TCP port (default: 9100)
--midi-port  MIDI output port index (default: 1)
```

## Test

```bash
Copy# Terminal 1
python ot_midi_engine.py

# Terminal 2
python test_engine.py
```

## Quick manual test (no engine needed)

```bash
Copypython3 -c "import rtmidi; m=rtmidi.MidiOut(); m.open_port(1); m.send_message([0xBA, 46, 80]); print('OK')"
```

## Protocol

Newline-delimited JSON over TCP on `localhost:9100`.

**Single CC:**

```json
Copy{"type": "cc", "channel": 11, "cc": 46, "value": 80}
```

**Batch:**

```json
Copy{"type": "batch", "messages": [{"channel": 11, "cc": 46, "value": 80}], "interval_ms": 10}
```

**List MIDI ports:**

```json
Copy{"type": "list_ports"}
```

**Ping:**

```json
Copy{"type": "ping"}
```

All responses are JSON with an `"ok"` boolean field.