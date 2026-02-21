cmake_minimum_required(VERSION 3.22)
project(SimpleGain VERSION 1.0.0)

# MSVC 環境の文字コード警告を抑制
if(MSVC)
    add_compile_options(/wd4819 /utf-8)
endif()

# JUCE を追加
add_subdirectory($ENV{JUCE_PATH} ${CMAKE_BINARY_DIR}/JUCE)

# VST3 プラグインターゲット
juce_add_plugin(SimpleGain
    COMPANY_NAME            "Test"
    IS_SYNTH                FALSE
    NEEDS_MIDI_INPUT        FALSE
    NEEDS_MIDI_OUTPUT       FALSE
    PLUGIN_MANUFACTURER_CODE Test
    PLUGIN_CODE             Sgai
    FORMATS                 VST3 Standalone
    PRODUCT_NAME            "SimpleGain"
    COPY_PLUGIN_AFTER_BUILD FALSE
)

target_sources(SimpleGain
    PRIVATE
        Source/PluginProcessor.cpp
        Source/PluginEditor.cpp
)

target_compile_features(SimpleGain PRIVATE cxx_std_17)

target_compile_definitions(SimpleGain
    PUBLIC
        JUCE_WEB_BROWSER=0
        JUCE_USE_CURL=0
        JUCE_VST3_CAN_REPLACE_VST2=0
        _USE_MATH_DEFINES
)

target_link_libraries(SimpleGain
    PRIVATE
        juce::juce_audio_basics
        juce::juce_audio_processors
        juce::juce_audio_plugin_client
        juce::juce_audio_utils
    PUBLIC
        juce::juce_recommended_config_flags
        juce::juce_recommended_warning_flags
)
