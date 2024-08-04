| No | Column名称(日本語) | column_name (python) | 属性 | 桁数/文字数 | 備考 |
|----|-------------------|---------------------|------|------------|------|
| 1 | 報告日 | report_date | str | - | 申請フォームのA2セルに報告日 |
| 2 | no | application_number | int | - | 半角数字 |
| 3 | 有効日付 | effective_date | date | - | 日付形式 |
| 4 | 種類 | application_type | str | - | 申請の種類(新設/変更/廃止のいずれか) |
| 5 | 対象 | target_organization_level | str | - | 申請対象の組織の階層 (部店/拠点等) |
| 6 | 部門コード | human_resource_division_code | str | 1 | 人事部門コード。半角アルファベット1文字 |
| 7 | 親部店コード | parent_branch_code | str | 4 | 半角数字4桁または"****" |
| 8 | 部店コード | branch_code | str | 4-5 | 半角数字4桁または5桁、または半角数字 |
| 9 | 部店名称 | branch_name | str | - | 部店名称・出張所名称 |
| 10 | 部店名称 (英語) | branch_name_en | str | - | 統合レイアウトへの転記対象外 |
| 11 | 課/エリアコード | section_area_code | str | - | 対象エリアの場合はエリアコード、それ以外は課コード |
| 12 | 課/エリア名称 | section_area_name | str | - | 対象エリアの場合はエリア名称、それ以外の場合は課名称 |
| 13 | 課/エリア名称(英語) | section_area_name_en | str | - | 統合レイアウトへの転記対象外 |
| 14 | 常駐部店コード | resident_branch_code | str | - | 対象=エリアの場合のみ |
| 15 | 常駐部店名称 | resident_branch_name | str | - | - |
| 16 | 純新規店の組織情報受渡し予定日 (開店日基準) | new_store_info_transfer_date | date | - | 対象エリアの場合のみ |
| 17 | 共通認証受渡し予定日 (人事データ反映基準) | aaa_transfer_date | date | - | 統合レイアウトへの転記対象外 |
| 18 | 備考 | remarks | str | - | 共通認証への送信日、拠点内営業部情報、エリア課Gr情報が入っている |
