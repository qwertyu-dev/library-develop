| No | Column名称(日本語) | column_name(python) | 属性 | 桁数/文字数 | Column説明(概略) |
|----|-------------------|---------------------|------|-------------|------------------|
| 1 | 申請情報 | application_info | str | 1 | 1:人事、2:国企、3:関連ダミー課Grあり、4:関連ダミー課Grなし |
| 2 | 種類 | application_type | str | - | 新設/変更/廃止の申請種類 |
| 3 | 対象 | target_organization_level | str | - | 部店/課/エリア/拠点内営業部の対象組織レベル |
| 4 | 部門コード | human_resource_division_code | str | 3 | 人事システムの部門コード |
| 5 | 親部店コード | parent_branch_code | str | 5 | 親部店のコード。ない場合は"*****" |
| 6 | 部店コード | branch_code | str | 5 | 対象部店のコード |
| 7 | 部店名称 | branch_name | str | 78 | 対象部店の名称 |
| 8 | 課コード | section_code | str | 5 | 対象課のコード。エリアの場合は転記後ブランク |
| 9 | 課名称 | section_name | str | 48 | 対象課の名称。エリアの場合は転記後ブランク |
| 10 | 課名称(英語) | section_name_en | str | 75 | 課の英語名称（使用されない） |
| 11 | 常駐部店コード | resident_branch_code | str | 5 | エリアの場合の常駐部店コード |
| 12 | 常駐部店名称 | resident_branch_name | str | 48 | エリアの場合の常駐部店名称 |
| 13 | 共通認証受渡し予定日 | aaa_transfer_date | str | 8 | 共通認証システムへの受渡予定日 |
| 14 | 拠点内営業部コード | internal_sales_dept_code | str | 5 | 拠点内営業部のコード（使用されない） |
| 15 | 拠点内営業部名称 | internal_sales_dept_name | str | 78 | 拠点内営業部の名称（使用されない） |
| 16 | エリアコード | area_code | str | 5 | エリアの場合のコード |
| 17 | エリア名称 | area_name | str | 48 | エリアの場合の名称 |
| 18 | 備考 | remarks | str | 100 | 自由記述の備考欄 |
| 19 | 部店名称(カナ) | branch_name_kana | str | 48 | 部店名称のカナ表記（受付処理時に補記） |
| 20 | 課名称(カナ) | section_name_kana | str | 12 | 課名称のカナ表記（関連会社用） |
| 21 | 課名称(略称) | section_name_abbr | str | 10 | 課名称の略称（関連会社用） |
| 22 | BPR対象/対象外フラグ | bpr_target_flag | str | 1 | BPRシステムの対象/対象外を示すフラグ |
| 23 | 出向リカバリフラグ | secondment_recovery_flag | str | - | 出向社員のBPRシステム利用フラグ |





