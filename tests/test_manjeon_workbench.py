"""통합 작업대(deploy/작업/만사전.md) 병합·받기 동작을 임시 작업대로 확인한다.

WHY(2026-10-25 사용자 "건강·육아·댕냥 … 작업대도 따로 두고 있잖아? … 굳이 떨어질 필요가 없을 듯"): 시트를 하나로 합치면서
두 저장소 생성기가 같은 폴더를 쓴다. 한쪽이 돌 때 다른 쪽 항목·사람이 넣은 스틸이 사라지거나, 남의 클립을 받아 가면 안 된다.
병합기는 ai-video-network/tools/manjeon_sheet.py(다른 저장소) — 실제 작업대는 건드리지 않고 tmp_path에서만 돈다.
"""
from __future__ import annotations

import json
import subprocess
import sys

import pytest

from lib import tracks


def _publish(work, channel, items):
    subprocess.run([sys.executable, str(tracks.MANJEON), "--work", str(work), "publish", channel],
                   input=json.dumps({"items": items}, ensure_ascii=False), text=True, check=True, capture_output=True)


def _manifest(work):
    return json.loads((work / ".만사전" / "manifest.json").read_text(encoding="utf-8"))


@pytest.fixture
def bench(tmp_path):
    work = tmp_path / "작업"
    start = tmp_path / "start.jpg"
    start.write_bytes(b"start-frame")
    _publish(work, "health", [
        {"clip": "act_h_new", "topic": "피부_1", "mj": {"prompt": "mj h"}, "flow": {"prompt": "flow h", "sec": 6}},
        {"clip": "act_h_ready", "topic": "피부_2", "start": str(start), "flow": {"prompt": "flow h2", "sec": 6}},
    ])
    _publish(work, "baby", [{"clip": "baby_cu_eye", "topic": "_lib_parts", "mj": {"prompt": "mj baby"}}])
    _publish(work, "dang", [
        {"clip": "M64", "topic": "댕냥_간", "label": "간", "mj": {"prompt": "mj m64"}, "flow": {"prompt": "f", "sec": 4},
         "meta": {"still_name": "dog_liver"}},
        {"clip": "M65", "topic": "댕냥_간", "label": "간", "waits_for": "M64", "flow": {"prompt": "f2", "sec": 4}},
    ])
    return work, start


def test_three_channels_share_one_contiguous_sheet(bench):
    work, _ = bench
    m = _manifest(work)
    nums = [e["n"] for e in m["entries"]]
    assert nums == list(range(1, len(nums) + 1)), "번호는 세 채널 통틀어 01부터 빈칸 없이"
    assert {e["channel"] for e in m["entries"]} == {"health", "baby", "dang"}
    # 미드저니가 필요한 번호가 앞으로 몰린다(사람은 미드저니를 쫙 뽑고 Flow를 쫙 돈다)
    mj = [e["needs_mj"] for e in m["entries"]]
    assert mj == sorted(mj, reverse=True)
    sheet = (work / "만사전.md").read_text(encoding="utf-8")
    for clip in ("act_h_new", "act_h_ready", "baby_cu_eye", "M64", "M65"):
        assert f"`{clip}`" in sheet
    stills = {p.name for p in (work / "만사전_스틸").iterdir()}
    ready = next(e for e in m["entries"] if e["clip"] == "act_h_ready")
    assert ready["file"] in stills, "시작 그림이 있는 칸은 같은 번호 사본이 놓인다"
    new = next(e for e in m["entries"] if e["clip"] == "act_h_new")
    assert f"{new['no']}_act_h_new_스틸없음.txt" in stills


def test_republishing_one_channel_keeps_the_others(bench):
    work, _ = bench
    _publish(work, "health", [])        # 건강 쪽 요청을 다 받았다
    m = _manifest(work)
    assert {e["clip"] for e in m["entries"]} == {"baby_cu_eye", "M64", "M65"}
    assert [e["n"] for e in m["entries"]] == [1, 2, 3]
    assert not any(p.name.endswith("act_h_ready.jpg") for p in (work / "만사전_스틸").iterdir()), "옛 사본은 치운다"


def test_received_still_follows_the_new_number(bench):
    work, _ = bench
    m64 = next(e for e in _manifest(work)["entries"] if e["clip"] == "M64")
    stills = work / "만사전_스틸"
    (stills / m64["file"]).write_bytes(b"human-midjourney")
    (stills / "M64.mp4").write_bytes(b"video")
    _publish(work, "health", [])        # 다른 채널 생성기가 돌아 번호가 바뀐다
    m64_now = next(e for e in _manifest(work)["entries"] if e["clip"] == "M64")
    assert m64_now["no"] != m64["no"]
    assert (stills / m64_now["file"]).read_bytes() == b"human-midjourney", "사람이 넣은 스틸은 지우지 않고 새 번호로"
    assert (stills / "M64.mp4").exists(), "받은 영상은 병합기가 건드리지 않는다"
    assert "📥 들어옴" in (work / "만사전.md").read_text(encoding="utf-8")


def test_claim_returns_only_this_repo(bench):
    work, _ = bench
    stills = work / "만사전_스틸"
    (stills / "act_h_new.mp4").write_bytes(b"h")
    (stills / "M64.mp4").write_bytes(b"d")
    (stills / "act_not_on_sheet.mp4").write_bytes(b"x")
    out = subprocess.run([sys.executable, str(tracks.MANJEON), "--work", str(work), "claim", "health-shorts"],
                         capture_output=True, text=True, check=True)
    got = json.loads(out.stdout)
    assert [f["clip"] for f in got["mine"]] == ["act_h_new"]
    assert [f["clip"] for f in got["unclaimed"]] == ["act_not_on_sheet"]
    assert got["others"] == 1
    assert all("start.jpg" not in f["path"] and not f["file"].endswith("act_h_ready.jpg") for f in got["mine"]), \
        "병합기가 놓은 시작 그림 사본은 받은 파일이 아니다"


def test_prep_worksheet_publishes_only_its_section(bench, monkeypatch):
    from scripts import prep_clip_worksheet as w
    work, start = bench
    monkeypatch.setattr(tracks, "DEPLOY_WORK", work)
    req = {"name": "act_from_prep", "flow": "a person does something", "seconds": 6, "why": "테스트"}
    monkeypatch.setattr(w, "_pending", lambda track: [["소화_99", dict(req), "act"]] if track is None else [])
    monkeypatch.setattr(w, "_existing_still", lambda sub, name, track: start)
    monkeypatch.setattr(w, "_mj_refs", lambda: {})
    w.main()
    m = _manifest(work)
    clips = {e["clip"]: e for e in m["entries"]}
    assert set(clips) == {"act_from_prep", "M64", "M65"}, "건강만 다시 내도 댕냥 항목은 남고, 비운 육아 섹션은 빠진다"
    assert clips["act_from_prep"]["channel"] == "health" and not clips["act_from_prep"]["needs_mj"]


def test_collect_takes_only_this_repo_videos(bench, monkeypatch, tmp_path, capsys):
    from scripts import collect_clips as c
    work, _ = bench
    stills = work / "만사전_스틸"
    lib = tmp_path / "lib"
    lib.mkdir()
    (stills / "act_h_new.mp4").write_bytes(b"h")
    (stills / "M64.mp4").write_bytes(b"d")
    monkeypatch.setattr(tracks, "DEPLOY_WORK", work)
    monkeypatch.setattr(c, "INBOX", stills)
    monkeypatch.setattr(c, "LIB", lib)
    monkeypatch.setattr(c, "_known", lambda: {"act_h_new": {}})
    monkeypatch.setattr(c, "_refresh", lambda: None)
    monkeypatch.setattr(sys, "argv", ["collect_clips.py", "--commit"])
    c.main()
    assert (lib / "act_h_new.mp4").exists()
    assert (stills / "M64.mp4").exists(), "댕냥 클립은 그쪽 세션이 가져간다"
    assert "다른 채널 몫 1개" in capsys.readouterr().out
