#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
compose_file="$repo_dir/docker-compose.aivis.yml"
engine_url="http://127.0.0.1:10101"
nise_model_uuid="6d11c6c2-f4a4-4435-887e-23dd60f8b8dd"
nise_model_sha256="6ff7eaa61c24d37434e2c6ab672fc3ba189ecc9118c08918a486ed5316e5c9d3"
nise_url="https://api.aivis-project.com/v1/aivm-models/$nise_model_uuid/download?model_type=AIVMX"
data_volume="simple-ja-aivis-data"
engine_image="ghcr.io/aivis-project/aivisspeech-engine:cpu-latest"

if ! docker volume inspect "$data_volume" >/dev/null 2>&1; then
  docker volume create "$data_volume" >/dev/null
  docker run --rm --user root --entrypoint sh \
    -v "$data_volume:/data" "$engine_image" -c 'chown -R 1000:1000 /data'
fi

docker compose -f "$compose_file" up -d

for _attempt in $(seq 1 60); do
  if curl -fsS --max-time 3 "$engine_url/version" >/dev/null 2>&1; then
    break
  fi
  sleep 2
done
curl -fsS --max-time 3 "$engine_url/version" >/dev/null

if ! curl -fsS "$engine_url/speakers" | python3 -c '
import json
import sys

expected = "bf56410a-d8e6-430d-a477-f789e16206d3"
speakers = json.load(sys.stdin)
raise SystemExit(0 if any(
    speaker.get("name") == "にせ"
    and speaker.get("speaker_uuid") == expected
    and any(style.get("name") == "ノーマル" for style in speaker.get("styles", []))
    for speaker in speakers
) else 1)
'; then
  curl -fsS -X POST -F "url=$nise_url" "$engine_url/aivm_models/install"
fi

model_path="/home/user/.local/share/AivisSpeech-Engine-Dev/Models/$nise_model_uuid.aivmx"
actual_sha256="$(docker exec simple-ja-aivis sha256sum "$model_path" | cut -d ' ' -f 1)"
if [[ "$actual_sha256" != "$nise_model_sha256" ]]; then
  echo "Nise model hash mismatch: $actual_sha256" >&2
  exit 1
fi

curl -fsS "$engine_url/speakers" | python3 -c '
import json
import sys

expected = "bf56410a-d8e6-430d-a477-f789e16206d3"
speakers = json.load(sys.stdin)
if not any(
    speaker.get("name") == "にせ"
    and speaker.get("speaker_uuid") == expected
    and any(style.get("name") == "ノーマル" for style in speaker.get("styles", []))
    for speaker in speakers
):
    raise SystemExit("Nise normal voice is unavailable")
'

echo "AivisSpeech is ready at $engine_url with the pinned Nise model."
