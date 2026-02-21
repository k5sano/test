#include "PluginEditor.h"
#include "Parameters.h"

SimpleGainEditor::SimpleGainEditor (SimpleGainProcessor& p)
    : AudioProcessorEditor (&p),
      processorRef (p),
      gainAttachment   (p.apvts, SimpleGainParams::gainDbId.getParamID(), gainSlider),
      bypassAttachment (p.apvts, SimpleGainParams::bypassId.getParamID(), bypassButton)
{
    setSize (400, 300);

    gainSlider.setSliderStyle (juce::Slider::LinearVertical);
    gainSlider.setTextBoxStyle (juce::Slider::TextBoxBelow, false, 80, 20);
    addAndMakeVisible (gainSlider);

    gainLabel.setText ("Gain (dB)", juce::dontSendNotification);
    gainLabel.setJustificationType (juce::Justification::centred);
    addAndMakeVisible (gainLabel);

    bypassButton.setButtonText ("Bypass");
    addAndMakeVisible (bypassButton);
}

void SimpleGainEditor::paint (juce::Graphics& g)
{
    g.fillAll (getLookAndFeel().findColour (juce::ResizableWindow::backgroundColourId));
}

void SimpleGainEditor::resized()
{
    auto area = getLocalBounds().reduced (20);

    gainLabel.setBounds (area.removeFromTop (24));
    bypassButton.setBounds (area.removeFromBottom (36));
    gainSlider.setBounds (area);
}
