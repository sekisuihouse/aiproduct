# Scripts

- `send_sales_email.py` 単発送信
- `send_sales_batch.py` CSV一括送信

## send_sales_batch.py

- 既定のリードファイルは `07_sales_cs/outreach/leads.private.csv`
- `--campaign` で訴求軸を切り替え
- `--limit` で送信件数を制限
- `--dry-run` で本文確認

必要な環境変数:

- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASS`
- `FROM_ADDR`
- `FROM_NAME`
