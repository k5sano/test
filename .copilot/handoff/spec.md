# SimpleGain プラグイン仕様書

## 概要

モノラル/ステレオ対応のシンプルなゲインプラグイン。

## パラメータ

| ID | 名前 | 範囲 | デフォルト | 単位 |
| --- | --- | --- | --- | --- |
| gain\_db | Gain | \-60.0 ~ +24.0 | 0.0 | dB |
| bypass | Bypass | 0 / 1 | 0 | bool |

## JUCE モジュール

-   juce\_audio\_basics
-   juce\_audio\_processors
-   juce\_audio\_plugin\_client

## ビルド要件

-   C++17
-   CMake 3.22 以上
-   JUCE 7.x