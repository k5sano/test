#pragma once
#include <juce_audio_processors/juce_audio_processors.h>

namespace SimpleGainParams
{
    static const juce::ParameterID gainDbId { "gain_db", 1 };
    static const juce::ParameterID bypassId { "bypass",  1 };

    inline juce::AudioProcessorValueTreeState::ParameterLayout createLayout()
    {
        std::vector<std::unique_ptr<juce::RangedAudioParameter>> params;

        params.push_back (std::make_unique<juce::AudioParameterFloat> (
            gainDbId,
            "Gain",
            juce::NormalisableRange<float> (-60.0f, 24.0f, 0.1f),
            0.0f,
            juce::AudioParameterFloatAttributes{}.withLabel ("dB")));

        params.push_back (std::make_unique<juce::AudioParameterBool> (
            bypassId,
            "Bypass",
            false));

        return { params.begin(), params.end() };
    }
} // namespace SimpleGainParams
