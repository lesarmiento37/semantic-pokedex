#!/usr/bin/env bash
set -euo pipefail

# ─── Timestamps ───────────────────────────────────────────────────────────────
ts() { date '+%Y-%m-%dT%H:%M:%S%z'; }

echo "[$(ts)] Starting deployment..."

# ─── Validate required environment variables ──────────────────────────────────
MISSING=()
for VAR in AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN; do
    if [[ -z "${!VAR:-}" ]]; then
        MISSING+=("$VAR")
    fi
done

if [[ ${#MISSING[@]} -gt 0 ]]; then
    echo "ERROR: The following required environment variables are not set:" >&2
    for VAR in "${MISSING[@]}"; do
        echo "  - $VAR" >&2
    done
    echo "" >&2
    echo "Obtain short-term credentials from the AWS Access Portal (Identity Center):" >&2
    echo "  1. Log in to the AWS Access Portal." >&2
    echo "  2. Click the account/role you need." >&2
    echo "  3. Choose 'Command line or programmatic access' → copy Option 1 values." >&2
    echo "  4. Export them in your shell and re-run." >&2
    exit 1
fi

# ─── Defaults for optional variables ──────────────────────────────────────────
AWS_REGION="${AWS_REGION:-us-east-1}"
STAGE="${STAGE:-stage}"

# ─── Verify AWS credentials ───────────────────────────────────────────────────
echo "[$(ts)] Verifying AWS credentials..."
aws sts get-caller-identity

# ─── Deploy ───────────────────────────────────────────────────────────────────
cd /app

echo "[$(ts)] Deploying Serverless application (stage=${STAGE}, region=${AWS_REGION})..."
serverless deploy --stage "${STAGE}" --region "${AWS_REGION}" --verbose --force

echo "[$(ts)] Deployment completed successfully."
