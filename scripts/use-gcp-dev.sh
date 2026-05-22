#!/usr/bin/env bash
set -euo pipefail

: "${GCP_PROJECT_ID:?Set GCP_PROJECT_ID before sourcing this file}"
export GOOGLE_CLOUD_PROJECT="$GCP_PROJECT_ID"
export CLOUDSDK_CORE_PROJECT="$GCP_PROJECT_ID"
export GCP_REGION="${GCP_REGION:-us-central1}"
export CLOUDSDK_COMPUTE_REGION="$GCP_REGION"
export USE_GCS="${USE_GCS:-false}"
export GCS_BUCKET="${GCS_BUCKET:-policygraph-dev-uploads}"
export GCS_PREFIX="${GCS_PREFIX:-policygraph/uploads}"
export OCR_ENGINE="paddleocr"
export PADDLEOCR_LANG="${PADDLEOCR_LANG:-en}"

echo "Configured PolicyGraph AI for GCP project: $GCP_PROJECT_ID in region: $GCP_REGION"
echo "For local client libraries, run: gcloud auth application-default login"
