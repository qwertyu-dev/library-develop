| No | Column名称(日本語) | column_name(python) | 属性 | 桁数/文字数 | Column説明(概略) |
|----|-------------------|---------------------|------|-------------|------------------|
| 1 | ULID | ulid | str | 5 | パターン編集後一意Key=受付後一意Key+パッチ適用一意Key=起因申請明細ID |
| 2 | 共通認証受渡予定日 | aaa_transfer_date | date | 82 | - |
| 3 | 更新の種類 | update_type | str | 6 | 行追加/変更/削除。変更情報テーブルの「種類」カラムを変換 |
| 4 | 部店コード (BPR) | branch_code_bpr | str | 56 | 更新対象レコード特定時のキー項目。BPRシステムで使う部店コード |
| 5 | 部店名 (BPR) | branch_name_bpr | str | 3 | BPRシステムで使う部店名称 |
| 6 | 課Grコード (BPR) | section_group_code_bpr | str | 5 | 更新対象レコード特定時のキー項目。BPRシステムで使う課Grコード |
| 7 | 課Gr名(BPR) | section_group_name_bpr | str | 78 | BPRシステムで使う課Gr名称 |
| 8 | 部門コード (BPR) | division_code_bpr | str | 5 | BPRシステムで使う部門コード |
| 9 | 親部店コード | parent_branch_code | str | 48 | 共通認証への受渡し対象外 |
| 10 | 拠点内営業部コード | internal_sales_dept_code | str | 78 | - |
| 11 | 拠点内営業部名称 | internal_sales_dept_name | str | 5 | - |
| 12 | 部店コード(人事) | branch_code_jinji | str | 48 | 更新対象レコード特定時のキー項目。人事システムで管理している部店コード |
| 13 | 部店名(人事) | branch_name_jinji | str | 5 | 人事システムで管理している部店名称 |
| 14 | 課Grコード (人事) | section_group_code_jinji | str | 78 | 更新対象レコード特定時のキー項目。人事システムで管理している課Grコード |
| 15 | 課Gr名(人事) | section_group_name_jinji | str | 10 | 人事システムで管理している課Gr名称 |
| 16 | 部店コード (エリア) | branch_code_area | str | 48 | 更新対象レコード特定時のキー項目。エリア情報として管理している部店コード |
| 17 | 部店名(エリア) | branch_name_area | str | 5 | エリア情報として管理している部店名称 |
| 18 | 課Grコード(エリア) | section_group_code_area | str | 48 | 更新対象レコード特定時のキー項目。エリア情報として管理している課Grコード |
| 19 | 課Gr名(エリア) | section_group_name_area | str | 5 | エリア情報として管理している課Gr名称 |
| 20 | 出張所コード | branch_office_code | str | 1 | 出張所・ローン推進室の場合に設定 |
| 21 | 出張所名称 | branch_office_name | str | 48 | 出張所・ローン推進室の場合に設定 |
| 22 | 業務コード | business_code | str | 1 | エリアの場合に設定 |
| 23 | エリアコード | area_code | str | 5 | エリアの場合に設定 |
| 24 | エリア名称 | area_name | str | 48 | エリアの場合に設定 |
| 25 | 常駐部店コード | resident_branch_code | str | 5 | エリアの場合に設定 |
| 26 | 常駐部店名称 | resident_branch_name | str | 48 | エリアの場合に設定 |
| 27 | ポータル使用 | portal_use | bool | 1 | - |
| 28 | ポータル送信 | portal_send | bool | 1 | - |
| 29 | 本部/営業店フラグ | is_headquarters | bool | 1 | - |
| 30 | 組織分類 | organization_classification | str | - | - |
| 31 | 組織分類コード | organization_classification_code | str | 2 | - |
| 32 | 部店ソート番号 | branch_sort_number | int | 2 | - |
| 33 | 部店ソート番号2 | branch_sort_number2 | int | 1 | - |
| 34 | カナ組織名(部店カナ) | organization_name_kana | str | 48 | - |
| 35 | DPコード | dp_code | str | 8 | - |
| 36 | DPコード (行員外) | dp_code_external | str | 9 | - |
| 37 | GRコード | gr_code | str | 20 | - |
| 38 | GRPSコード | grps_code | str | 21 | - |
| 39 | BPR・AD対象フラグ | bpr_ad_target_flag | int | 10 | BPR・AD対象: 1、ADのみ対象: 2、BPR・AD対象外:0 |
| 40 | 出向リカバリフラグ | secondment_recovery_flag | bool | 1 | 出向中に行員IDでBPRを使用できるようにするためのフラグ。特定の関連会社でONとなる |
| 41 | Sort | sort | int | 3 | - |
| 42 | 備考 | remarks | str | - | - |
| 43 | 組織変更情報 | organization_change_info | str | - | - |
| 44 | 支社内法人部コード | corporate_division_code | str | 2 | - |
| 45 | 課Grソート番号 | section_group_sort_number | int | - | - |
| 46 | メールサーバ | mail_server | str | - | ファイルサーバのOドライブの設定に使用 |
| 47 | 全行サーバ | bank_wide_server | str | - | ファイルサーバのOドライブの設定に使用 |
| 48 | 部店サーバ(DBサーバ) | branch_server | str | - | ファイルサーバのQドライブの設定に使用 |
| 49 | 部店のグループ名 | branch_group_name | str | - | ファイルサーバのQドライブの設定に使用 |
| 50 | GRコード(行員外) | gr_code_external | str | 100 | - |
| 51 | AD使用フラグ | ad_use_flag | bool | 1 | - |
| 52 | ADサーバ | ad_server | str | 5 | 80で固定 |
| 53 | ADドメイン | ad_domain | str | 3 | ブランクで固定 |
| 54 | ホームディレクトリドライブ | home_directory_drive | str | 25 | ブランクで固定 |
| 55 | 特別ドメインフラグ | special_domain_flag | bool | 1 | ブランクで固定 |
| 56 | 行員特別ドメイン名 | employee_special_domain_name | str | 8 | ブランクで固定 |
| 57 | 対象会社コード | target_company_code | str | 8 | ブランクで固定 |
| 58 | 対象会社ドメイン名 | target_company_domain_name | str | 15 | ブランクで固定 |
| 59 | サブドメインあり会社ドメイン名 | company_domain_with_subdomain | str | 15 | ブランクで固定 |
| 60 | サブドメインなし会社ドメイン名 | company_domain_without_subdomain | str | 15 | ブランクで固定 |
| 61 | 予備1 | spare1 | str | - | ブランクで固定 |
| 62 | 予備2 | spare2 | str | - | ブランクで固定 |
| 63 | 予備3 | spare3 | str | - | ブランクで固定 |
| 64 | 予備4 | spare4 | str | - | ブランクで固定 |
| 65 | 予備5 | spare5 | str | - | ブランクで固定 |
| 66 | 予備6 | spare6 | str | - | ブランクで固定 |
| 67 | 予備7 | spare7 | str | - | ブランクで固定 |
| 68 | 予備8 | spare8 | str | - | ブランクで固定 |
| 69 | 予備9 | spare9 | str | - | ブランクで固定 |
| 70 | 予備10 | spare10 | str | - | ブランクで固定 |
