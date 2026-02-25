# CloudsCOSMOS 開発ログ

## 概要

Mutable Instruments Clouds のファームウェア DSP コードを JUCE 8 ベースの VST3/AU/Standalone プラグインとして移植するプロジェクト。Émilie Gillet によるオリジナルの C++ DSP コード（MIT License）をそのまま利用し、JUCE のオーディオプラグインフレームワーク上で動作させる。

開発は Claude Opus 4.6（分析・設計・コードレビュー）と Claude Code（実装・テスト実行）の協調により、約1日で主要機能を完成させた。

## 技術構成

-   **DSP エンジン**: Mutable Instruments Clouds (eurorack ライブラリ)
-   **フレームワーク**: JUCE 8.0.12 (FetchContent)
-   **ビルドシステム**: CMake
-   **出力形式**: VST3 / AU / Standalone
-   **内部サンプルレート**: 32kHz（オリジナルハードウェアと同一）
-   **対応ホストサンプルレート**: 44.1kHz ～ 196kHz 動作確認済み

## 動作モード（全4モード動作）

-   **Granular**: グラニュラーシンセシス。入力音声を小さなグレインに分割し重ね合わせ
-   **Stretch**: WSOLA タイムストレッチ。ピッチを保ちつつ時間伸縮
-   **Looping Delay**: ピッチシフト付きルーピングディレイ
-   **Spectral**: フェーズボコーダーによる周波数領域加工

## 開発タイムライン

### フェーズ 1: 基本動作

-   CMake + JUCE FetchContent によるビルドパイプライン構築
-   eurorack ライブラリの統合と GranularProcessor の初期化
-   Standalone ビルドで GUI 表示、Granular モードで最初の発音成功

### フェーズ 2: SRC（サンプルレート変換）問題の解決

**問題**: ホストサンプルレート（44.1kHz〜196kHz）と Clouds 内部レート（32kHz）の変換で、ブロック境界にグリッチ（ぶちぶちノイズ）が発生。

**原因**: 初期実装の LagrangeInterpolator がブロック境界で不連続な値を生成。

**解決**: リングバッファ方式の SampleRateAdapter に全面書き換え。Hermite 補間を使用し、入力・出力それぞれ独立したリングバッファ（最終的に 16384 サンプル）で非同期処理。これにより Granular / Looping Delay / Spectral の3モードがクリーンに動作。

### フェーズ 3: Stretch モードの修復（最大の技術的課題）

#### 問題 1: ハング（無限ループ）

**症状**: Stretch モードに切り替えると Process() が返ってこない。DAW がフリーズ。

**原因**: `kSmallBufferSize` の値がオリジナル（65535）と VCV Rack 実装（65536 - 128 = 65408）で異なっていた。127バイトの差により BufferAllocator のメモリ配置が崩れ、Correlator の内部状態が破損。

**解決**: `kSmallBufferSize = 65536 - 128` に修正（VCV Rack と同一値）。

#### 問題 2: ゼロ出力

**症状**: ハングは解消されたが、Stretch モードで完全に無音。

**調査プロセス**:

1.  テストプログラムで DSP レベルでのゼロ出力を確認（SRC やプラグインラッパーの問題ではないことを確定）
2.  `dry_wet=0.5` で音が出て `dry_wet=1.0` で無音 → wet 成分（WSOLA エンジン出力）がゼロであることを特定
3.  `libs/eurorack/clouds/dsp/wsola_sample_player.h` に fprintf デバッグを一時挿入し、Play() 内部の状態をトレース
4.  `Window::Start()` 呼び出し後も `done_ = true` のままであることを発見

**根本原因 A: `Window::Start()` に `done_ = false` が欠落**

`clouds/dsp/window.h` の `Window::Start()` 関数で `done_` フラグが `false` にリセットされていなかった。これにより `OverlapAdd()` が常にスキップされ、WSOLA の出力が全てゼロになっていた。

これはオリジナルファームウェアのバグである可能性が高い。ハードウェア上では割り込みタイミングや初期化順序の違いにより、`done_` が別の経路でリセットされていたと推測される。

**修正**: `Window::Start()` に `done_ = false;` を1行追加。

**根本原因 B: `search_target_` の初期値**

`WSOLASamplePlayer::Init()` で `search_target_ = 0` に初期化されるため、最初の `LoadCorrelator()` で `StartSearch()` に負のオフセット（`0 - 2048 + 1024 = -1024`）が渡され、`best_match()` が `-503` のような不正値を返していた。

**修正**: `search_target_ = 16384`（バッファ中央付近）に変更。

### フェーズ 4: 安全性と品質向上

-   調整可能な出力リミッター（GUI ノブ付き）
-   SampleRateAdapter のアンダーラン時にラストサンプルホールド
-   全パラメータにワンポールフィルタによるスムージング（ジッパーノイズ防止）
-   リングバッファサイズを 16384 に拡大（高サンプルレート対応）

### フェーズ 5: GUI とプリセット

-   カスタム背景画像対応（BG Image ボタン）
-   プリセットの Save/Load 機能
-   リサジュー図形によるステレオイメージ可視化
-   シアン/マゼンタ配色のカスタムノブデザイン
-   6チャンネルレベルメーター（Input, PostGain, SRC Down, Engine In, Engine Out, Output）

## VCV Rack との比較から得た知見

VCV Rack の Audible Instruments（Clouds 移植）のソースコード分析が Stretch モード修復の鍵となった。

| 項目 | VCV Rack | CloudsCOSMOS（修正前） |
| --- | --- | --- |
| small buffer size | 65536 - 128 = 65408 | 65535 |
| processor memset | Init() 前に実行 | なし |
| Prepare/Process 比率 | 1:1 | 最大 256:1（過剰） |
| モード切替 | メニューから（遅延あり） | 毎ブロック set\_playback\_mode |

VCV Rack では `PLAYBACK_MODE_LAST` → `GRANULAR` の遷移で最初の数ブロックがゼロ出力になるが、起動直後のため聴覚上問題にならない。その後の `GRANULAR` → `STRETCH` 切替は `benign_change = true` で正常に遷移する。この挙動を理解したことで、CloudsCOSMOS でも同様のウォームアップ処理を init() に導入した。

## libs/ への最小パッチ（2箇所）

オリジナルの eurorack ライブラリに対する変更は以下の2点のみ。いずれも VST 環境で Stretch モードを動作させるために必須。

```cpp
Copy// libs/eurorack/clouds/dsp/window.h - Window::Start()
// 追加: done_ = false;
done_ = false;  // FIX: Reset done flag when starting window

// libs/eurorack/clouds/dsp/wsola_sample_player.h - Init()
// 変更: search_target_ = 0 → search_target_ = 16384
search_target_ = 16384;  // FIX: Start from buffer center
```

## パラメータ一覧

**メインパラメータ**: Position, Size, Pitch (-24〜+24 st), Density, Texture

**ブレンドパラメータ**: Dry/Wet, Stereo Spread, Feedback, Reverb

**ゲインステージ**: Input Gain (-18〜+6 dB), Engine Input Trim (0.1〜1.0), Engine Output Gain (0.5〜3.0), Output Limiter (0.5〜8.0)

**モード**: Granular / Stretch / Looping Delay / Spectral

**品質**: 16bit Stereo / 16bit Mono / 8bit μ-law Stereo / 8bit μ-law Mono

## クレジット

-   **DSP エンジン**: Émilie Gillet / Mutable Instruments (MIT License)
-   **プラグイン開発**: Claude Opus 4.6 + Claude Code + K5SANO
-   **フレームワーク**: JUCE 8 (GPLv3 / Commercial License)

## ライセンス

DSP コード（libs/eurorack）は MIT License。プラグイン固有のコード（Source/）のライセンスは別途定める。

* * *

_Based on Mutable Instruments Clouds by Émilie Gillet (MIT License_