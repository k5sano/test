---
name: handoff-reader
description: >
  Gensparkが .copilot/handoff/ に置いた仕様書・設計書・タスクリストを
  読み込んで構造化サマリーを出力する。
  "read handoff", "load handoff", "/handoff-reader" で起動。
---

# Handoff Reader

## 読み込み手順
以下のファイルをこの順番で読む:

1. `.copilot/handoff/spec.md` — 要件と受け入れ基準
2. `.copilot/handoff/design.md` — アーキテクチャとモジュール設計
3. `.copilot/handoff/copilot-handoff.md` — 実装タスクリスト
4. `scaffold/` 配下の全ファイル — ヘッダ定義、テストスタブ

## 出力フォーマット
読み終わったら以下のサマリーを出力:

```
Handoff Summary
Feature: (copilot-handoff.md のタイトルから)
Tasks: (タスク数)
Key Components: (JUCEコンポーネント名: Processor, Editor, Filter等)
Acceptance Criteria: (spec.md の基準数)
New Dependencies: (あれば。なければ「なし」)
Ready to /plan: yes / no
```

## エラー処理
handoffファイルが1つでも見つからなければ:
- どのファイルが見つからないか明示
- 「Gensparkからのpushを確認してください」と表示
- 処理を停止
