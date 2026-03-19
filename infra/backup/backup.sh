#!/bin/sh
set -e

# Validate required environment variables
: "${DATABASE_URL:?DATABASE_URL is required}"
: "${R2_BUCKET_NAME:?R2_BUCKET_NAME is required}"
: "${R2_ACCESS_KEY_ID:?R2_ACCESS_KEY_ID is required}"
: "${R2_SECRET_ACCESS_KEY:?R2_SECRET_ACCESS_KEY is required}"
: "${R2_ENDPOINT_URL:?R2_ENDPOINT_URL is required}"
: "${GPG_PASSPHRASE:?GPG_PASSPHRASE is required}"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="/tmp/sphotel_${TIMESTAMP}.sql"
ENCRYPTED_FILE="${BACKUP_FILE}.gpg"

echo "[backup] Starting pg_dump at ${TIMESTAMP}"
pg_dump "${DATABASE_URL}" > "${BACKUP_FILE}"
echo "[backup] pg_dump complete ($(wc -c < "${BACKUP_FILE}") bytes)"

echo "[backup] Encrypting with GPG (AES256)"
gpg --batch --yes \
    --passphrase "${GPG_PASSPHRASE}" \
    --symmetric \
    --cipher-algo AES256 \
    --output "${ENCRYPTED_FILE}" \
    "${BACKUP_FILE}"

# Remove plaintext dump immediately after encryption
rm -f "${BACKUP_FILE}"

echo "[backup] Uploading to R2: s3://${R2_BUCKET_NAME}/backups/$(basename "${ENCRYPTED_FILE}")"
AWS_ACCESS_KEY_ID="${R2_ACCESS_KEY_ID}" \
AWS_SECRET_ACCESS_KEY="${R2_SECRET_ACCESS_KEY}" \
aws s3 cp "${ENCRYPTED_FILE}" \
    "s3://${R2_BUCKET_NAME}/backups/$(basename "${ENCRYPTED_FILE}")" \
    --endpoint-url "${R2_ENDPOINT_URL}"

rm -f "${ENCRYPTED_FILE}"
echo "[backup] Done: $(basename "${ENCRYPTED_FILE}")"
