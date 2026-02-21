# GitHub Copilot Instructions

## JUCE

- コードは常に [JUCE 公式ドキュメント](https://docs.juce.com/) の最新仕様に準拠すること。
- 非推奨 (deprecated) の API は使用しないこと。代替 API が存在する場合は必ずそちらを使うこと。
  - 例: `juce::Font::Font(float size)` → `juce::Font(juce::FontOptions{}.withHeight(size))` を使う。
  - 例: `AudioProcessorValueTreeState` のパラメータ追加には `juce::ParameterID` を使う。
- `JuceHeader.h` の利用には `juce_generate_juce_header(<target>)` を CMakeLists.txt に記述すること。
- JUCE モジュールは `target_link_libraries` で `juce::juce_*` 形式で指定すること。
- MSVC ビルドでは `_USE_MATH_DEFINES` を定義して `M_PI` を有効にすること。
- `juce::Reverb` など JUCE 標準クラスと名前が衝突しうるサードパーティクラスは、グローバルスコープ修飾子 `::ClassName` で明示すること。

## CMake

- `cmake_minimum_required` は 3.22 以上を指定すること。
- プラグインターゲットには `juce_add_plugin()` を使い、`FORMATS` に必要なフォーマット（VST3, Standalone 等）をリストすること。
- `COPY_PLUGIN_AFTER_BUILD` は開発中 `FALSE` にし、配布時に切り替えること。

## 全般

- C++17 以上を前提としたコードを書くこと。
- 生ポインタよりスマートポインタ (`std::unique_ptr`, `std::shared_ptr`) を優先すること。
- スレッドセーフが求められる箇所（パラメータ変更など）には `std::atomic` または JUCE の `std::atomic`-compatible な仕組みを使うこと。

---

## Genspark Handoff ワークフロー
このプロジェクトは Genspark (Claude Opus) → GitHub → Copilot CLI の
自動ハンドオフワークフローを使用している。
- 仕様・設計・タスク: `.copilot/handoff/`
- スケルトン: `scaffold/`
- ビルドエラー: `.copilot/build-errors.txt`
- エスカレーション: `.copilot/escalation-report.md`

## ビルドコマンド
- `cmake -B build` — Configure
- `cmake --build build/` — Build
- `ctest --test-dir build/` — Test

## コミット前チェック
cmake --build build/ が成功すること。

## コード修正の原則
Claude Opus が書いたコードを尊重する。
修正は根拠がある場合のみ、最小限で。
詳細は juce-builder エージェントの指示に従う。

## 既存ツール
JUCE MCP サーバーが設定済み。APIの調査に活用すること。
