# CloudsCOSMOS Development Log

## Overview

A project to port the Mutable Instruments Clouds firmware DSP code into a VST3/AU/Standalone plugin based on JUCE 8. The original C++ DSP code by Émilie Gillet (MIT License) is used directly, running on top of the JUCE audio plugin framework.

Development was carried out through collaboration between Claude Opus 4.6 (analysis, design, code review) and Claude Code (implementation, test execution), with major functionality completed in approximately one day.

## Technical Stack

-   **DSP Engine**: Mutable Instruments Clouds (eurorack library)
-   **Framework**: JUCE 8.0.12 (FetchContent)
-   **Build System**: CMake
-   **Output Formats**: VST3 / AU / Standalone
-   **Internal Sample Rate**: 32kHz (identical to original hardware)
-   **Tested Host Sample Rates**: 44.1kHz to 196kHz confirmed working

## Operating Modes (All 4 Modes Functional)

-   **Granular**: Granular synthesis. Splits input audio into small grains and overlaps them
-   **Stretch**: WSOLA time-stretching. Time expansion/compression while preserving pitch
-   **Looping Delay**: Looping delay with pitch shifting
-   **Spectral**: Frequency-domain processing via phase vocoder

## Development Timeline

### Phase 1: Basic Operation

-   Build pipeline setup with CMake + JUCE FetchContent
-   Integration of the eurorack library and GranularProcessor initialization
-   First sound achieved in Standalone build with GUI display and Granular mode

### Phase 2: Solving the SRC (Sample Rate Conversion) Problem

**Problem**: Glitches (crackling noise) at block boundaries during conversion between the host sample rate (44.1kHz–196kHz) and Clouds' internal rate (32kHz).

**Cause**: The initial LagrangeInterpolator implementation produced discontinuous values at block boundaries.

**Solution**: Complete rewrite to a ring-buffer-based SampleRateAdapter using Hermite interpolation, with independent input and output ring buffers (ultimately 16384 samples each) for asynchronous processing. This enabled clean operation of Granular, Looping Delay, and Spectral modes.

### Phase 3: Fixing Stretch Mode (The Biggest Technical Challenge)

#### Issue 1: Hang (Infinite Loop)

**Symptom**: Switching to Stretch mode caused Process() to never return. DAW freeze.

**Cause**: The `kSmallBufferSize` value differed between the original (65535) and the VCV Rack implementation (65536 - 128 = 65408). The 127-byte difference caused BufferAllocator memory layout corruption, leading to corrupted Correlator internal state.

**Solution**: Changed `kSmallBufferSize = 65536 - 128` (matching VCV Rack).

#### Issue 2: Zero Output

**Symptom**: The hang was resolved, but Stretch mode produced complete silence.

**Investigation Process**:

1.  Confirmed zero output at the DSP level via test program (ruling out SRC and plugin wrapper issues)
2.  Found that `dry_wet=0.5` produced sound while `dry_wet=1.0` was silent → identified that the wet component (WSOLA engine output) was zero
3.  Temporarily inserted fprintf debugging into `libs/eurorack/clouds/dsp/wsola_sample_player.h` to trace Play() internal state
4.  Discovered that `done_` remained `true` even after calling `Window::Start()`

**Root Cause A: Missing `done_ = false` in `Window::Start()`**

The `Window::Start()` function in `clouds/dsp/window.h` did not reset the `done_` flag to `false`. This caused `OverlapAdd()` to be consistently skipped, resulting in all-zero WSOLA output.

This is likely a bug in the original firmware. On hardware, `done_` was presumably reset through a different pathway due to differences in interrupt timing and initialization order.

**Fix**: Added a single line `done_ = false;` to `Window::Start()`.

**Root Cause B: Initial Value of `search_target_`**

`WSOLASamplePlayer::Init()` initialized `search_target_ = 0`, causing the first `LoadCorrelator()` to pass a negative offset (`0 - 2048 + 1024 = -1024`) to `StartSearch()`, which made `best_match()` return invalid values like `-503`.

**Fix**: Changed to `search_target_ = 16384` (near buffer center).

### Phase 4: Safety and Quality Improvements

-   Adjustable output limiter (with GUI knob)
-   Last-sample hold on SampleRateAdapter underrun
-   One-pole filter smoothing on all parameters (zipper noise prevention)
-   Ring buffer size increased to 16384 (high sample rate support)

### Phase 5: GUI and Presets

-   Custom background image support (BG Image button)
-   Preset Save/Load functionality
-   Lissajous figure for stereo image visualization
-   Custom knob design in cyan/magenta color scheme
-   6-channel level meters (Input, PostGain, SRC Down, Engine In, Engine Out, Output)

## Insights from VCV Rack Comparison

Analysis of the VCV Rack Audible Instruments (Clouds port) source code was key to fixing Stretch mode.

| Item | VCV Rack | CloudsCOSMOS (before fix) |
| --- | --- | --- |
| small buffer size | 65536 - 128 = 65408 | 65535 |
| processor memset | Before Init() | None |
| Prepare/Process ratio | 1:1 | Up to 256:1 (excessive) |
| Mode switching | From menu (delayed) | set\_playback\_mode every block |

In VCV Rack, the `PLAYBACK_MODE_LAST` → `GRANULAR` transition produces zero output for the first few blocks, but this goes unnoticed since it occurs at startup. The subsequent `GRANULAR` → `STRETCH` switch transitions normally with `benign_change = true`. Understanding this behavior led us to introduce a similar warmup process in CloudsCOSMOS's init().

## Minimal Patches to libs/ (2 Locations)

Only two changes were made to the original eurorack library. Both are essential for Stretch mode operation in a VST environment.

```cpp
Copy// libs/eurorack/clouds/dsp/window.h - Window::Start()
// Added: done_ = false;
done_ = false;  // FIX: Reset done flag when starting window

// libs/eurorack/clouds/dsp/wsola_sample_player.h - Init()
// Changed: search_target_ = 0 → search_target_ = 16384
search_target_ = 16384;  // FIX: Start from buffer center
```

## Parameter List

**Main Parameters**: Position, Size, Pitch (-24 to +24 st), Density, Texture

**Blend Parameters**: Dry/Wet, Stereo Spread, Feedback, Reverb

**Gain Staging**: Input Gain (-18 to +6 dB), Engine Input Trim (0.1–1.0), Engine Output Gain (0.5–3.0), Output Limiter (0.5–8.0)

**Modes**: Granular / Stretch / Looping Delay / Spectral

**Quality**: 16bit Stereo / 16bit Mono / 8bit μ-law Stereo / 8bit μ-law Mono

## Credits

-   **DSP Engine**: Émilie Gillet / Mutable Instruments (MIT License)
-   **Plugin Development**: Claude Opus 4.6 + Claude Code + K5SANO
-   **Framework**: JUCE 8 (GPLv3 / Commercial License)

## License

DSP code (libs/eurorack) is under MIT License. Licensing for plugin-specific code (Source/) to be determined separately.

* * *

_Based on Mutable Instruments Clouds by Émilie Gillet (MIT License)_

その他のアクション