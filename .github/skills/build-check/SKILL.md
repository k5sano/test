---
name: build-check
description: >
  ビルドとテストを実行し結果をファイルに書き出す。
  コードは一切変更しない。
  "build check", "/build-check" で起動。
---

# Build Check

## 実行手順

1. .copilot/fix-counter.json が残っていたら中身を表示して現状把握
2. ビルド実行:
   ```
   cmake -B build 2>&1 | tee .copilot/cmake-config.log
   cmake --build build/ 2>&1 | tee .copilot/build-output.log
   ```
3. ビルド結果の判定:
   - 成功: 「✅ ビルド成功」と報告
   - 失敗: エラー部分を抽出して .copilot/build-errors.txt に保存
4. テスト実行（build/ディレクトリにCTestが設定されている場合）:
   ```
   ctest --test-dir build/ --output-on-failure 2>&1 | tee .copilot/test-output.log
   ```
5. 結果サマリーを表示:
   ```
   Build Check Result
   Config: ✅/❌
   Build: ✅/❌ (warnings: X)
   Tests: ✅/❌ (passed: X, failed: Y) / ⏭ not configured
   Errors: (エラー数。0なら「なし」)
   ```
6. エラーがある場合、各エラーについて:
   - ファイルと行番号
   - エラーメッセージ
   - juce-builder の🟡ルールに該当しそうか（判定だけ、修正はしない）

## 重要
このスキルはソースコードを変更しない。
修正の判断と実行は juce-builder エージェントに委ねる。
