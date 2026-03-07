# Loom — Architecture & Design

## Checksum Bypass Architecture

```
┌─────────────┐     read      ┌──────────────────┐
│  CF Card     │ ───────────► │  Tauri App        │
│  (OT files)  │              │  (React UI +Rust) │
└─────────────┘              └────────┬───────────┘
                                      │ TCP/WebSocket
                                      ▼
                              ┌──────────────────┐
                              │  ot_midi_engine   │
                              │  (Python/rtmidi)  │
                              └────────┬───────────┘
                                      │ MIDI CC (ch11)
                                      ▼
                              ┌──────────────────┐
                              │  Morningstar MC8  │
                              │  (USB→DIN)        │
                              └────────┬───────────┘
                                      │ DIN MIDI
                                      ▼
                              ┌──────────────────┐
                              │  Octatrack        │
                              │  (applies & saves)│
                              └──────────────────┘
```

**Key insight:** We never write bank files. We read them for visualization, then push parameter changes via MIDI CC. OT calculates its own checksums on save.

## UX Principles

1.  State is always visible
2.  Human naming (Trigless Trig → Param Point)
3.  Simple operations take 1 step
4.  Complexity is opt-in
5.  Git-like autosave
6.  OT compatibility is output format only (convert on export)
7.  Splice integration is first-class

## Concept Remapping

| OT Term | Problem | Loom Term |
| --- | --- | --- |
| Bank/Part/Pattern (3 layers) | Non-intuitive | Scene (1 layer) |
| Sample Slot (number-based) | Tedious | Sample (path-based) |
| Trigless Trig | Contradictory name | Param Point |
| Recorder Buffer | Track ≠ Recorder | Record Mode |
| .work / .strd | Dual management | Auto versioning |

## Macro System (Loom Original Feature)

Macros reduce multi-step OT workflows to single actions, all implemented via MIDI CC sequences.

| Macro | What it does | OT Steps → Loom |
| --- | --- | --- |
| Quick Resample | One-button resampling | 10 → 1 |
| Scene Morph | Slider morphs Scene A/B | manual → continuous |
| Pattern Transition | Cut/Fade/Filter pattern switch | complex → 1 choice |
| Track Mute Group | Up to 8 mute group toggles | per-track → grouped |
| Filter Sweep | Global filter sweep | multi-CC → 1 slider |
| Quick Save Snapshot | Named snapshot save | menu dive → 1 button |

## Splice Integration

Watch `~/Splice/sounds/` recursively for new WAV files. On detection:

1.  Register in SQLite (artist, pack, BPM, key, tags from path/filename)
2.  Convert to OT-compatible format (48kHz/44.1kHz, 16/24-bit, mono/stereo WAV)
3.  Generate `.ot` sidecar file (slice markers, loop points)
4.  Queue for CF card placement

## Tauri ↔ Node for Max Communication

Tauri app is the single source of truth for CF card access. Node for Max communicates via TCP to Tauri — never accesses CF card directly. This prevents file corruption from concurrent access.

```
Ableton Live
  └─ Max for Live device
       └─ Node for Max ──TCP──► Tauri App ──filesystem──► CF Card
```