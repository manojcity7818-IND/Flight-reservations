#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python -m pip install -q -r services/flight-search-service/requirements.txt
python -m pip install -q -r services/booking-service/requirements.txt
python -m pip install -q -r services/payment-service/requirements.txt
python -m pip install -q -r services/notification-service/requirements.txt
python -m pip install -q -r services/user-service/requirements.txt
python -m pip install -q -r services/api-gateway/requirements.txt

mkdir -p test-results coverage

for service in flight-search-service booking-service payment-service notification-service user-service api-gateway; do
  echo "=== Testing $service ==="
  (cd "services/$service" && python -m pytest --junitxml="$ROOT/test-results/${service}.xml" --cov=app --cov-report=xml:"$ROOT/coverage/${service}.xml" || python -m pytest --junitxml="$ROOT/test-results/${service}.xml")
done

echo "=== Frontend contract tests ==="
(cd web && python -m pytest --junitxml="$ROOT/test-results/web.xml")

echo "=== Integration tests ==="
python -m pytest tests/integration --junitxml="$ROOT/test-results/integration.xml"

if [[ -f web/package.json ]]; then
  echo "=== Frontend unit tests ==="
  (cd web && npm install && npm test && npm run lint && npm run build)
fi
