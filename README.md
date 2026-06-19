# Startup Workspace

このリポジトリは、`ranzaku` の会社づくりを進める作業場です。

## Canonical Structure

- `00_inbox/` 受信箱。未整理の情報、断片メモ、会話ログ
- `01_research/` 収集した情報。市場、顧客、競合、法規、参考事例
- `02_strategy/` 決めたこと。方針、優先順位、KPI、意思決定ログ
- `03_product/` つくるもの。PRD、バックログ、仕様、リリース
- `04_design/` 体験と表現。UX、UI、ブランド、コピー
- `05_engineering/` 実装と品質。設計、API、データ、QA、セキュリティ
- `06_growth/` 集客と拡大。GTM、コンテンツ、SEO、PR、コミュニティ
- `07_sales_cs/` 営業と顧客成功。商談、導入支援、サポート、フィードバック
- `08_operations/` 会社運営。財務、人事、法務、リスク
- `09_experiments/` 仮説検証。実験、結果、学び、失敗ログ
- `10_assets/` 共有資産。ピッチ、画像、ブランド素材、配布物
- `99_archive/` 完了・廃止・旧版の退避先
- `ops-dashboard/` 内部経営ダッシュボード

## Writing Rules

- 議事録、メモ、調査結果、決定事項、実験結果はすべて`.md`で残す
- 事実は`01_research/`、決定は`02_strategy/`、実行物は各担当フォルダに分ける
- 決定したことは必ず `02_strategy/decision-log.md` に転記する
- 役職別の視点は `docs/roles/` に残し、必要に応じて各フォルダへ反映する
- すべての主要意思決定は、論点・根拠・反証・次の検証を残す
- 施策には必ず `owner`, `metric`, `deadline`, `kill condition` を付ける

## Existing Working Area

既存の `docs/` は、役職別メモと詳細テンプレートの作業領域として引き続き使えます。
公開向けの最初の顔は `site/` に置いています。

## Company Identity

会社名: `ranzaku`
プロダクト名: `HomeFlow AI`

## Initial Venture Thesis

このリポジトリでは、まず「高複雑・高単価・高頻度の人手業務をAIで会社単位ごと再設計する」スタートアップとして進めます。

- 初期の狙いは住宅・建設・リフォーム周辺
- 価値は、暗黙知の形式知化、提案速度の向上、顧客対応の標準化
- 会社としては、SaaS単体ではなく導入支援と運用設計まで含める

## Operating Mode

会社は「顧客接点 -> 証拠 -> 意思決定 -> 実装 -> 計測 -> 継続/中止」の循環で運営する。
