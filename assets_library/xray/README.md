# xray 클립 — 여기부터 보면 됨 (2026-09-20)

반투명 인체 포맷 영상 한 편은 클립 3종으로 조립된다.

| 종류 | 뭔가 | 길이 | 누가 만드나 |
|---|---|---|---|
| **행위** | 몸이 아파서 움직이는 장면(웅크림·허리 짚기…) | 4~6초 | 구글 Flow — **사람** |
| **부위** | 그 부위만 호박색으로 켜지는 장면 | 4초 | 코드 — **세션** |
| **기전** | "왜 그런지"를 보여주는 미시 장면(3컷) | 4초 | 구글 Flow — **사람** |

부위는 Flow로 안 뽑는다 — 카메라가 밀고 들어가고 색이 켜지는 것뿐이라 스틸 한 장이면 코드로 만든다.
그래서 **사람이 할 일은 미드저니 25장 + Flow 19개**뿐이다.

---

## 파일 이름 규칙 (2026-09-20)

**번호 = 파일 이름.** `F01`을 돌리면 끝 프레임도 `F01_act_clutch_low_back_end.jpg`, 결과도 `F01_act_clutch_low_back.mp4`.
`output/`에 `F01`~`F19`가 다 있으면 끝난 것이다.

- 행위 끝 자세: `stills/act/F01~F07_*.jpg` (`F00`은 웅크림 — pilot_B가 대체하므로 안 써도 됨)
- 기전 시작 이미지: `stills/mech/F08~F19_*.jpg` (`done_*`는 위염 3종, 이미 클립까지 있음)
- 부위 클립: `output/part_*.mp4` — 내가 코드로 만드는 것이라 번호가 없다

## 사람이 할 일

👉 **실제 작업은 `RENDER_SHEET.md` 하나만 열면 된다** — **1부 미드저니 25장을 다 뽑고, 세션 검수를 받은 뒤,
2부 Flow 19개**를 돌린다. 아래 표는 그게 어디서 온 건지 알고 싶을 때만.

### STEP 1 — 미드저니 25장

| # | 무엇 | 몇 장 | 프롬프트 어디 | 결과 파일명 |
|---|---|---|---|---|
| 1-A | 행위 끝 포즈 | 7 | `flow_prompts.md` 각 `### act_*` 안의 **미드저니 (end 포즈 스틸)** | `stills/act/<act 이름>_end.jpg` |
| 1-B | 부위 클로즈업 | 6 | `part_prompts.md` 각 항목 안의 **미드저니 (신규 스틸)** | `stills/cu_<이름>.jpg` |
| 1-C | 기전 시작 이미지 | 12 | `mechanism_prompts.md` 각 `### m_*` 안의 **미드저니 (시작 이미지)** | `stills/mech/<m 이름>.jpg` |

- 1-A 7장: `act_clutch_low_back` `act_rub_leg` `act_rub_hands` `act_cover_face` `act_rush_to_toilet` `act_toss_turn` `act_sink_to_floor`
  (`act_curl_up`·`act_sway_offbalance`는 파일럿 B·C가 이미 그 장면이라 안 뽑아도 된다)
- 1-B 6장: `cu_heart` `cu_lungs` `cu_liver_pancreas` `cu_shoulder` `cu_scalp` `cu_nose_sinus`
- 1-C 12장: `m_inflammation` `m_nerve_compression` `m_nerve_overdrive` `m_fluid_retention` `m_dehydration`
  `m_toxin_load` `m_blood_flow_drop` `m_pressure_buildup` `m_bacteria_growth` `m_glucose_spike`
  `m_muscle_tension` `m_waste_buildup`
- ⚠️ 기전 스틸만 `canon_organs.jpg`를 **Style Reference**로 넣는다(Omni Reference 아님). 나머지는 프롬프트만.

### STEP 2 — Flow 19개

| # | 무엇 | 몇 개 | 시작 프레임 | 끝 프레임 | 프롬프트 어디 |
|---|---|---|---|---|---|
| 2-A | 행위 | 7 | `stills/canon_organs.jpg` | STEP 1-A에서 만든 `_end.jpg` | `flow_prompts.md`의 **Flow** 블록 |
| 2-B | 기전 | 12 | STEP 1-C에서 만든 `mech/*.jpg` | **비움** | `mechanism_prompts.md`의 **Flow** 블록 |

### STEP 3 — 파일 주기

다운로드 폴더에 그대로 두고 알려주면 된다. 세션이 이름 보고 `stills/`·`output/` 제자리로 옮긴다.

---

## 세션이 하는 일 (사람은 안 해도 됨)

- **부위 클립 31종 전부** — `scripts/make_part_clip.py`로 생성.
  ```
  .venv/bin/python3 scripts/make_part_clip.py assets_library/xray/stills/cu_eye.jpg output/part_eye.mp4
  ```
  전신 스틸에서 한 부위만 켤 땐 `--region`(좌표는 `part_regions.json`에 확정본).
- topic별 조립: `rebuild_video` → `scripts/xray_splice.py`.
- 새 topic에서 기존 기전 12종으로 안 되는 경우에만 그 topic 전용 기전 프롬프트를 새로 쓴다.

---

## 파일 지도

| 파일 | 뭐가 들어있나 |
|---|---|
| **README.md** | 이 문서. 뭘 해야 하는지. |
| **`RENDER_SHEET.md`** | **복붙용.** 남은 Flow 19개(F01~F19). 파일명이 번호와 같다 |
| `RENDER_QUEUE.md` | 렌더 순서·현황 체크리스트 |
| `flow_prompts.md` | 파일럿 3종 + **행위 9종**(미드저니 end 포즈 + Flow) |
| `part_prompts.md` | **부위 31종** — 신규 스틸 미드저니 프롬프트 + Flow 프롬프트(예비, 지금은 코드로 대체) |
| `mechanism_prompts.md` | **기전 15종**(위염 3 완료 + 범용 12) — 미드저니 + Flow |
| `midjourney_prompts.md` | 캐논 스틸(전신·부위) 프롬프트와 확정 결과 |
| `part_regions.json` | 전신 스틸에서 부위별 점등 좌표 |
| `stills/` `output/` | 스틸 원본 / 완성 클립 |

## 이미 있는 것

`output/pilot_A.mp4`(위 점등) · `pilot_B.mp4`(웅크림) · `pilot_C.mp4`(머리 움켜쥐고 비틀거림) ·
`m_acid_secretion` · `m_mucus_barrier` · `m_cell_damage` — 소화_9가 이걸로 만들어졌다.
