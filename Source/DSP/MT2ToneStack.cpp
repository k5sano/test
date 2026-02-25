```cpp
Copy#include "MT2ToneStack.h"
#include <cmath>

void MT2ToneStack::prepare(double sampleRate)
{
    mSampleRate = sampleRate;
    reset();
}

void MT2ToneStack::reset()
{
    mLowShelf.reset();
    mMidPeak.reset();
    mHighShelf.reset();
}

void MT2ToneStack::updateCoefficients(float eqLow, float eqMid, float eqMidFreq,
                                       float eqMidQ, float eqHigh)
{
    // Low Shelf: fixed freq 200Hz, ±15dB, fixed Q=0.707
    const double lowGainDb = (static_cast<double>(eqLow) - 0.5) * 30.0; // ±15dB
    mLowShelf.setLowShelf(200.0, lowGainDb, 0.707, mSampleRate);

    // Mid Peak: freq 200Hz..5kHz (log sweep), ±20dB, Q 0.3..10.0 (log)
    const double midFreq = 200.0 * std::pow(5000.0 / 200.0, static_cast<double>(eqMidFreq));
    const double midGainDb = (static_cast<double>(eqMid) - 0.5) * 40.0; // ±20dB
    const double midQ = 0.3 * std::pow(10.0 / 0.3, static_cast<double>(eqMidQ));
    mMidPeak.setPeak(midFreq, midGainDb, midQ, mSampleRate);

    // High Shelf: fixed freq 5kHz, ±15dB, fixed Q=0.707
    const double highGainDb = (static_cast<double>(eqHigh) - 0.5) * 30.0;
    mHighShelf.setHighShelf(5000.0, highGainDb, 0.707, mSampleRate);
}

double MT2ToneStack::processSample(double input)
{
    double x = mLowShelf.processSample(input);
    x = mMidPeak.processSample(x);
    x = mHighShelf.processSample(x);
    return x;
}
Copy
```