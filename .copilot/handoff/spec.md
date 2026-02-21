SimpleGain プラグイン仕様書
概要
モノラル/ステレオ対応のシンプルなゲインプラグイン。

パラメータ
ID	名前	範囲	デフォルト	単位
gain_db	Gain	-60.0 ~ +24.0	0.0	dB
bypass	Bypass	0 / 1	0	bool
JUCE モジュール
juce_audio_basics
juce_audio_processors
juce_audio_plugin_client
ビルド要件
C++17
CMake 3.22 以上
JUCE 7.x