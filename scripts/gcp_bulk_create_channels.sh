#!/usr/bin/env bash
# 글로벌 16채널용 GCP 프로젝트를 언어별로 일괄 생성 + YouTube Data API v3 활성화.
# WHY 프로젝트를 채널당 하나씩 따로 만드는지: YouTube Data API는 프로젝트당 일일
# 쿼터가 있어서(기본 1만 유닛, 업로드 1건≈1600유닛) 16채널이 프로젝트 하나를
# 같이 쓰면 업로드 개수가 서로 발목을 잡는다 — data/global_channels.json 참고.
#
# ⚠️ OAuth 동의화면 설정 + 프로덕션 전환은 이 스크립트로 안 된다 — Google이
# 이 두 가지를 다루는 공개 API/gcloud 명령을 제공하지 않아서 각 프로젝트마다
# Cloud Console(https://console.cloud.google.com/apis/credentials/consent)에서
# 수동으로 해야 한다. 이 스크립트는 "프로젝트 생성 + API 활성화"까지만 자동화하고,
# 그 다음 수동 단계 목록을 마지막에 출력한다.
#
# 사전 준비:
#   1. Google Cloud SDK 설치: https://cloud.google.com/sdk/docs/install
#   2. gcloud auth login  (16개 채널을 관리할 그 구글 계정으로 로그인)
#   3. gcloud billing accounts list  로 결제 계정 ID 확인해서 아래 BILLING_ACCOUNT_ID에 채우기
#
# 실행:
#   ./scripts/gcp_bulk_create_channels.sh <프로젝트ID-접두사>
#   예: ./scripts/gcp_bulk_create_channels.sh healthshorts
#       → healthshorts-ko, healthshorts-en, healthshorts-ja ... 16개 생성
set -euo pipefail

PREFIX="${1:?사용법: $0 <프로젝트ID-접두사> (예: healthshorts)}"
BILLING_ACCOUNT_ID="${BILLING_ACCOUNT_ID:-}"  # 비워두면 결제 연결은 건너뛰고 수동으로 안내
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHANNELS_JSON="$ROOT_DIR/data/global_channels.json"

if ! command -v gcloud &>/dev/null; then
  echo "gcloud CLI가 설치돼 있지 않습니다 — https://cloud.google.com/sdk/docs/install" >&2
  exit 1
fi

codes=$(python3 -c "
import json
d = json.load(open('$CHANNELS_JSON'))
for name, v in d.items():
    print(v['code'])
")

echo "=== 생성 대상: $(echo "$codes" | wc -l | tr -d ' ')개 채널 ==="

for code in $codes; do
  project_id="${PREFIX}-${code}"
  echo ""
  echo "--- $project_id ---"

  if gcloud projects describe "$project_id" &>/dev/null; then
    echo "이미 존재 — 건너뜀"
  else
    gcloud projects create "$project_id" --name="$project_id" --set-as-default
  fi

  if [[ -n "$BILLING_ACCOUNT_ID" ]]; then
    gcloud billing projects link "$project_id" --billing-account="$BILLING_ACCOUNT_ID"
  fi

  gcloud services enable youtube.googleapis.com --project="$project_id"

  # WHY 여기서 바로 JSON을 갱신하는지: output/completed_topics.json과 같은 패턴 —
  # 진행 상태를 대화가 아니라 파일에 직접 반영해서 어디까지 됐는지 항상 정확히
  # 알 수 있게 한다(재실행해도 위 describe 체크로 중복 생성 안 됨).
  python3 -c "
import json
p = '$CHANNELS_JSON'
d = json.load(open(p))
for name, v in d.items():
    if v['code'] == '$code':
        v['gcp_project_id'] = '$project_id'
json.dump(d, open(p, 'w'), ensure_ascii=False, indent=2)
"
done

echo ""
echo "=== 프로젝트 생성 완료 — 이제부터는 채널마다 수동 작업 (Cloud Console) ==="
echo "각 프로젝트에서 반복:"
echo "  1. https://console.cloud.google.com/apis/credentials/consent?project=<project_id>"
echo "     → OAuth 동의화면 만들기 (User Type: External)"
echo "  2. Scopes에 https://www.googleapis.com/auth/youtube.upload 추가"
echo "  3. 게시 상태를 '프로덕션'으로 전환 (검증 없이 — 리스크는 CLAUDE.md 글로벌 확장 섹션 참고)"
echo "  4. https://console.cloud.google.com/apis/credentials?project=<project_id>"
echo "     → OAuth 클라이언트 ID 만들기 (애플리케이션 유형: 데스크톱 앱)"
echo "  5. 발급된 client_id/client_secret을 .env에 채널별 변수명으로 저장"
echo "  6. python3 lib/youtube_auth_setup.py --channel <code> 실행해서 refresh_token 발급"
