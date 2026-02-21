#include "PluginProcessor.h"
#include "PluginEditor.h"

SimpleGainProcessor::SimpleGainProcessor()
    : AudioProcessor (BusesProperties()
          .withInput  ("Input",  juce::AudioChannelSet::stereo(), true)
          .withOutput ("Output", juce::AudioChannelSet::stereo(), true)),
      apvts (*this, nullptr, "Parameters", SimpleGainParams::createLayout())
{
}

void SimpleGainProcessor::prepareToPlay (double /*sampleRate*/, int /*samplesPerBlock*/)
{
    // Nothing to prepare for a simple gain plugin
}

void SimpleGainProcessor::releaseResources()
{
    // Nothing to release
}

void SimpleGainProcessor::processBlock (juce::AudioBuffer<float>& buffer,
                                        juce::MidiBuffer& /*midiMessages*/)
{
    juce::ScopedNoDenormals noDenormals;

    auto* bypassParam = apvts.getRawParameterValue (SimpleGainParams::bypassId.getParamID());
    if (bypassParam != nullptr && bypassParam->load() > 0.5f)
        return;

    auto* gainDbParam = apvts.getRawParameterValue (SimpleGainParams::gainDbId.getParamID());
    const float gainDb     = gainDbParam != nullptr ? gainDbParam->load() : 0.0f;
    const float gainLinear = std::pow (10.0f, gainDb / 20.0f);

    for (int ch = 0; ch < buffer.getNumChannels(); ++ch)
        buffer.applyGain (ch, 0, buffer.getNumSamples(), gainLinear);
}

juce::AudioProcessorEditor* SimpleGainProcessor::createEditor()
{
    return new SimpleGainEditor (*this);
}

void SimpleGainProcessor::getStateInformation (juce::MemoryBlock& destData)
{
    auto state = apvts.copyState();
    std::unique_ptr<juce::XmlElement> xml (state.createXml());
    copyXmlToBinary (*xml, destData);
}

void SimpleGainProcessor::setStateInformation (const void* data, int sizeInBytes)
{
    std::unique_ptr<juce::XmlElement> xml (getXmlFromBinary (data, sizeInBytes));
    if (xml != nullptr && xml->hasTagName (apvts.state.getType()))
        apvts.replaceState (juce::ValueTree::fromXml (*xml));
}

//==============================================================================
juce::AudioProcessor* JUCE_CALLTYPE createPluginFilter()
{
    return new SimpleGainProcessor();
}
