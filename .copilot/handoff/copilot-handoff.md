# Copilot 実装指示

## 優先順位

1.  CMakeLists.txt を作成（juce\_add\_plugin 使用）
2.  Parameters.h にパラメータ定義
3.  PluginProcessor の実装
4.  PluginEditor の実装（最低限の GUI）
5.  ビルド確認
6.  テストコード作成

## 注意事項

-   processBlock 内で new/delete 禁止
-   APVTS は PluginProcessor のコンストラクタで初期化
-   エディタサイズは 400x300 で固定

## 完了条件

-   cmake --build build/ が成功する
-   ctest --test-dir build/ が全 PASS
-   VST3 プラグインが生成される