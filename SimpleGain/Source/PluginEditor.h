#pragma once
#include <juce_audio_processors/juce_audio_processors.h>
#include <juce_gui_basics/juce_gui_basics.h>
#include "PluginProcessor.h"

class SimpleGainEditor : public juce::AudioProcessorEditor
{
public:
    explicit SimpleGainEditor (SimpleGainProcessor&);
    ~SimpleGainEditor() override = default;

    //==============================================================================
    void paint (juce::Graphics&) override;
    void resized() override;

private:
    SimpleGainProcessor& processorRef;

    juce::Slider gainSlider;
    juce::Label  gainLabel;
    juce::ToggleButton bypassButton;

    juce::AudioProcessorValueTreeState::SliderAttachment gainAttachment;
    juce::AudioProcessorValueTreeState::ButtonAttachment bypassAttachment;

    JUCE_DECLARE_NON_COPYABLE_WITH_LEAK_DETECTOR (SimpleGainEditor)
};
