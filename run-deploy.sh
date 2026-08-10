#!/usr/bin/env bash
set -euo pipefail

# ─── Configuration (overridable via environment) ──────────────────────────────
STAGE="${STAGE:-stage}"
AWS_REGION="${AWS_REGION:-us-east-1}"
IMAGE="semantic-pokedex-deploy:local"

# ─── Validate AWS credentials are exported in the host shell ─────────────────
MISSING=()
for VAR in AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN; do
    if [[ -z "${!VAR:-}" ]]; then
        MISSING+=("$VAR")
    fi
done

if [[ ${#MISSING[@]} -gt 0 ]]; then
    echo "ERROR: The following AWS credential variables are not set in your shell:" >&2
    for VAR in "${MISSING[@]}"; do
        echo "  - $VAR" >&2
    done
    cat >&2 <<'HELP'

How to obtain short-term credentials from the AWS Access Portal (Identity Center):
  1. Log in to your AWS Access Portal URL (e.g. https://<alias>.awsapps.com/start).
  2. Click the account and role you want to use.
  3. Choose "Command line or programmatic access".
  4. Copy the three values shown under "Option 1 – Set AWS environment variables":

     export AWS_ACCESS_KEY_ID=ASIA...
     export AWS_SECRET_ACCESS_KEY=...
     export AWS_SESSION_TOKEN=...

  5. Paste them into your terminal and re-run this script.

Alternatively, if you have the AWS CLI configured with SSO:
  aws sso login --profile <your-profile>
  eval $(aws configure export-credentials --profile <your-profile> --format env)

HELP
    exit 1
fi

# ─── Build the Docker image ───────────────────────────────────────────────────
echo "Building Docker image '${IMAGE}'..."
docker build -f Dockerfile.deploy -t "${IMAGE}" .

# ─── Run the deployment container ────────────────────────────────────────────
echo "Starting deployment container (stage=${STAGE}, region=${AWS_REGION})..."
docker run --rm -it \
    -e AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY \
    -e AWS_SESSION_TOKEN \
    -e AWS_REGION="${AWS_REGION}" \
    -e STAGE="${STAGE}" \
    -v "$(pwd)":/app \
    -w /app \
    "${IMAGE}"
