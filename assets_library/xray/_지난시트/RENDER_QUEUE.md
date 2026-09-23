# RENDER_QUEUE.md — 렌더 순서·현황 (2026-09-20)

👉 **뭘 해야 하는지는 `README.md` 먼저.** 이 파일은 순서·현황 체크용.

**사람이 돌릴 것: 미드저니 25장 + Flow 19개.** (처음 계산은 Flow 50개였는데, 부위 점등 31개를
코드 생성으로 돌려 없앴다.) Flow가 꼭 필요한 건 몸이 움직이는 행위 7종과 3컷으로 넘어가는 기전 12종뿐이다.

프롬프트는 전부 작성돼 있다. 아래 순서대로 렌더해서 지정 폴더에 넣으면 그때부터 해당 계열 topic은
바로 조립 가능하다. 프롬프트 위치: 행위 `flow_prompts.md` · 부위 `part_prompts.md` · 기전 `mechanism_prompts.md`.

이미 있는 것: `output/pilot_A.mp4`(위 점등) · `pilot_B.mp4`(웅크림 = `act_curl_up`) ·
`pilot_C.mp4`(머리 움켜쥐고 비틀거림 = `act_sway_offbalance`) · `m_acid_secretion` · `m_mucus_barrier` · `m_cell_damage`.

## 배치 1 — 미드저니 스틸 14장 (Flow보다 먼저, 시작/끝 프레임이 없으면 Flow를 못 돌린다)
- 부위 신규 6장 → `stills/`: `cu_heart` `cu_lungs` `cu_liver_pancreas` `cu_shoulder` `cu_scalp` `cu_nose_sinus`
  (`cu_intestines`는 뺐다 — 전신 스틸에서 장만 켜는 걸로 확인됨)
- 행위 끝 포즈 7장 → `stills/act/`: `act_clutch_low_back_end` `act_rub_leg_end` `act_rub_hands_end`
  `act_cover_face_end` `act_rush_to_toilet_end` `act_toss_turn_end` `act_sink_to_floor_end`

## 배치 2 — Flow 행위 7종 → `output/act_*.mp4`
start = `stills/canon_organs.jpg`, end = 배치 1에서 만든 끝 포즈.

## 배치 3 — 부위 점등은 Flow로 뽑지 않는다 (2026-09-20)
`scripts/make_part_clip.py`가 스틸 한 장에서 4초 클립을 만든다(느린 push-in + 해당 부위만 호박색 점등·맥동).
Flow가 만들어야 할 변화가 없는 클립이라 결과가 같다 — **부위 Flow 렌더 31회가 0회가 된다.**

    .venv/bin/python3 scripts/make_part_clip.py assets_library/xray/stills/cu_eye.jpg output/part_eye.mp4
    .venv/bin/python3 scripts/make_part_clip.py assets_library/xray/stills/cu_torso_organs.jpg \
        output/part_stomach.mp4 --region 0.35,0.42,0.30,0.10

- 클로즈업 스틸(`cu_eye`·`cu_ear`·`cu_mouth`·`cu_hand`·`cu_foot`·`cu_skin_section`…)은 `--region` 없이.
- 전신 스틸에서 한 부위만 켤 땐 `assets_library/xray/part_regions.json`의 좌표를 쓴다(위·장·방광·뇌·갑상선·무릎 확정).
- 장기가 겹쳐 보이는 심장·폐·간·췌장은 좌표로 못 가른다 → 전용 클로즈업 스틸(배치 1)을 쓴다.
- `part_prompts.md`의 Flow 프롬프트는 **예비**로 남긴다(코드 결과가 부족한 부위만 Flow로).

## 배치 4 — 미드저니 기전 시작 이미지 12장 → `stills/mech/`
`canon_organs.jpg`를 **Style Reference**로(Omni Reference 금지).

## 배치 5 — Flow 기전 12종 → `output/m_*.mp4`
`m_inflammation` `m_nerve_compression` `m_nerve_overdrive` `m_fluid_retention` `m_dehydration`
`m_toxin_load` `m_blood_flow_drop` `m_pressure_buildup` `m_bacteria_growth` `m_glucose_spike`
`m_muscle_tension` `m_waste_buildup`

## 배치 6 — (Flow 불필요, 코드로 생성) 남은 부위 19종
`part_stomach`(pilot_A로 대체 가능) `part_esophagus` `part_shoulder` `part_muscle_whole` `part_skeleton`
`part_vascular_whole` `part_legs_veins` `part_nerve_limbs` `part_liver` `part_pancreas` `part_thyroid`
`part_mouth_teeth` `part_tongue_throat` `part_scalp` `part_kidney` `part_ear_inner` `part_vestibular`
`part_lungs` `part_whole_body`

## 받는 쪽
렌더한 파일은 `ai-video-network/deploy/inbox/stills`·`inbox/motion`에 넣어도 되고 다운로드 폴더에 둬도 된다 —
세션이 이름 보고 `assets_library/xray/` 아래 제자리로 옮긴다.
