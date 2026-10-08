# 틱톡 캡션 — topic마다 따로 쓰지 않고 이미 있는 유튜브·네이버 클립 캡션에서 만든다.
#
# WHY(2026-10-09 사용자 "유튜브 틱톡 네이버클립 이렇게 세 개 운영" → "캡션 반영 좀 해야겠는데"): 틱톡은 캡션 링크가 안
# 눌려 제휴 링크 문단이 필요 없고, 내용은 클립 캡션(300자 안 요약)과 같다. 파일마다 세 번째 캡션을 써 두면 원고를 고칠
# 때마다 셋을 맞춰야 해서(나레이션 고치고 캡션 방치 사고), 동기화 때 그때그때 만든다.
# 제목은 유튜브 "제목:" 줄(끝이 ", <제품>" — 제품 이름 검색 유입), 본문은 클립 캡션 가운데, 해시태그는 클립 것 그대로.
from __future__ import annotations


def _platform(data: dict, name: str) -> str:
    return next((p.get("caption") or "" for p in data.get("platforms", []) if p.get("name") == name), "")


def build(data: dict) -> str | None:
    clip = _platform(data, "네이버 클립").strip()
    if not clip:
        return None
    lines = clip.splitlines()
    tags = next((l for l in reversed(lines) if l.strip().startswith("#")), "")
    body = [l for l in lines[1:] if l.strip() != tags.strip()]
    yt = _platform(data, "유튜브 쇼츠").strip().splitlines()
    title = yt[0].removeprefix("제목:").strip() if yt and yt[0].startswith("제목:") else lines[0].strip()
    products = [x for x in (data.get("products") or []) if x and x != "-"]
    # 영상 오른쪽 위에 [광고] 표시가 박혀 있어 캡션에서도 밝힌다. 링크는 안 눌리니 제품 이름만 적는다.
    note = f"영상 속 제품: {products[0]} (네이버 쇼핑 제휴 상품)" if products else ""
    out = [title, "", "\n".join(body).strip()]
    if note:
        out += ["", note]
    out += ["", tags.strip()]
    return "\n".join(x for x in out).strip()
