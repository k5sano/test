# スケルトンコード

## CMakeLists.txt

```cmake
Copycmake_minimum_required(VERSION 3.22)
project(SimpleGain VERSION 1.0.0)

find_package(JUCE CONFIG REQUIRED)

juce_add_plugin(SimpleGain
    PLUGIN_MANUFACTURER_CODE Test
    PLUGIN_CODE Sgai
    FORMATS VST3 Standalone
    PRODUCT_NAME "SimpleGain"
)

target_sources(SimpleGain PRIVATE
    Source/PluginProcessor.cpp
    Source/PluginEditor.cpp
)

target_compile_features(SimpleGain PRIVATE cxx_std_17)

target_link_libraries(SimpleGain
    PRIVATE
        juce::juce_audio_basics
        juce::juce_audio_processors
        juce::juce_audio_plugin_client
    PUBLIC
        juce::juce_recommended_config_flags
)
```

## Parameters.h

```cpp
Copy#pragma once
#include <juce_audio_processors/juce_audio_processors.h>

namespace SimpleGainParams {
    inline juce::AudioProcessorValueTreeState::ParameterLayout createLayout() {
        std::vector<std::unique_ptr<juce::RangedAudioParameter>> params;
        params.push_back(std::make_unique<juce::AudioParameterFloat>(
            "gain_db", "Gain",
            juce::NormalisableRange<float>(-60.0f, 24.0f, 0.1f),
            0.0f));
        params.push_back(std::make_unique<juce::AudioParameterBool>(
            "bypass", "Bypass", false));
        return { params.begin(), params.end() };
    }
}
```