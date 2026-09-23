# flow_prompts.md — 반투명 인체 행위 클립 (9:16, 구글 플로우 모션 프롬프트 전용)

구글 플로우에 그대로 붙여넣을 모션 프롬프트만 담는다. 정지컷/키프레임 프롬프트는
`midjourney_prompts.md`에 따로 있음 — 구도·조명·부위 강조는 거기서 이미 확정된다.

각 클립: `midjourney_prompts.md`로 만든 스틸을 **start 프레임 단독**으로 넣고
(end 슬롯은 비움), 아래 모션 프롬프트를 붙여넣는다.

🚨 **플로우 클립 길이는 4·6·8·10초 네 가지뿐이다.** 비트는 하나당 최소 2초.

🚨 **end 프레임을 주지 말 것** — 두 프레임을 주면 Veo가 그 사이를 맞추려고
피사체를 변형시킨다(1biteinfo 실측). 인체 룩을 고정하는 게 목적이므로 start
단독으로 간다.

🚨 **오디오 배제** — Flow는 지시가 없으면 나레이션·BGM을 자체 생성한다. 아래
모든 클립에 배제 문구가 들어있다.

🚨 **안전필터 회피 어휘** — "collapse", "faint", "fall down", "pass out",
"seizure" 같은 단어는 의료·부상 판정으로 자주 막힌다. 같은 그림을 "sways",
"stumbling half-step", "weight shifts", "sinks down" 처럼 **동작 자체를 묘사하는
말**로 쓴다. 반투명 해부 도해라 실사 인물보다는 덜 막히지만 어휘는 계속 조심한다.

---

## 파일럿 (2026-09-18 v2 — SHOT_DESIGN_SYSTEM 적용)

v1은 start 한 장에 "전신→위 클로즈업", "정면→3/4 회전"을 텍스트로만 시켰다 —
**카메라 무빙은 텍스트가 아니라 start/end 두 프레임의 차이가 만든다**
(`ai-video-network/SHOT_DESIGN_SYSTEM.md` §1). 그래서 end 프레임을 캐논의
**재진술**로 만들었다(새로 그리지 않고 크롭 + Gemini 편집 — `gen_pilot_ends.py`).

프레임: `stills/pilot/` — `A_start`+`A_end` / `B_start`+`B_end` / `C_start`+`C_end` (start 세 장은 전부 canon_organs 사본)
결과: `clips/pilot_A.mp4` · `pilot_B.mp4` · `pilot_C.mp4`

### 샷 리스트 (A→B를 이어 붙이는 순서 기준)

```
클립:   A            B              C
역할:   디테일        커버리지        리액션
크기:   WS → MS      WS(유지)       WS(유지)
앵글:   eye          eye → 3/4좌    eye
무빙:   push-in(축)  push-in + 하강  roll 시계방향 12°
점등:   위            위·장          뇌
```

- A는 WS→MS **2단계만** 건넌다. 전신→위 ECU는 4단계라 중간이 붕괴한다(§2-1) — 위 클로즈업이
  필요하면 A 다음에 `cu_torso_organs`에서 출발하는 클립을 따로 붙인다.
- v2 1차 결과(2026-09-18)가 약했던 원인: ①세 클립 모두 "가만히 서 있다"로 시작해 앞 25%를 버림
  ②end 자세가 약해 Flow가 그 이상을 못 냄(이미지가 이김) ③안전필터를 의식해 동사를 순하게 씀
  ④C는 카메라까지 고정해 팔만 허우적대는 춤처럼 됨 ⑤B·C 마지막 0.7초에 점등이 꺼짐.
  → v3: **0초부터 동작 시작**, end 자세를 미드저니로 극단적으로 다시 뽑음(`_candidates/pilot_mj/`),
  "마지막 프레임까지 켜져 있다" 명시.
- C의 어지럼은 **화면이 기울어야** 체감된다. 텍스트로 "화면이 기운다"고 쓰면 안 먹으므로 end 프레임
  자체를 12° 기울였다(`C_end.jpg`, 수평 원본은 `C_end_level.jpg`) — Flow가 그 차이를 카메라 롤로 채운다.
  반시계로 기울이면 머리가 프레임 밖으로 잘려서 시계 방향으로 했다.
- 비트: 4초=3비트, 6초=4비트(클립 길이÷1.5초 이상, SHARED_TECH_LESSONS 2026-09-15).

### 파일럿 A ⏱ 4초 [프레임: 시작 → A_end] — WS→MS, Eye-Level, Push-in, LIGHT-RIM — 디테일

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the figure stays completely still. 0-1.3s: the camera starts moving forward from the full-body framing, the figure filling about 85 percent of the frame height. 1.3-2.7s: the push-in continues until the chest-to-hips region fills the whole frame, and a faint warm amber glow flickers on inside the stomach under the left ribs. 2.7-4s: the camera eases to a stop as the stomach glow swells to full bright amber and pulses once; every other organ, every bone and the glass skin stay soft pale cyan. The face stays smooth and featureless, the dark slate blue-grey void stays empty. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

### 파일럿 B ⏱ 6초 [프레임: 시작 → B_end] — WS→MWS, Eye-Level→High, Push-in+Descend, LIGHT-RIM — 커버리지

end는 미드저니 `B_end_mj_2`(배를 끌어안고 한쪽 무릎이 바닥 가까이). 미드저니 4장 모두 위가 아니라
장(아랫배)에 불이 들어가서 프롬프트도 "위와 장"으로 맞췄다 — 이미지가 이긴다.

```
One continuous shot in a single unbroken scene with no scene cuts. 0-1.5s: from the very first frame both hands snap inward and clamp onto the belly as a hot amber glow bursts on inside the stomach and intestines, and the camera starts pushing in. 1.5-3s: the torso jerks forward and folds hard over the hands, the shoulders hunching and the head dropping toward the chest. 3-4.5s: one knee buckles and drops sharply toward the floor while the other leg braces, the body folding into a tight doubled-over crouch, and the camera pushes in and lowers with it until the figure fills about 90 percent of the frame height. 4.5-6s: the figure stays locked in the crouch, trembling, both arms wrapped around the belly, the stomach and intestines throbbing intense amber twice and staying fully lit until the very last frame, while every other organ stays soft pale cyan. The body stays translucent glass with all organs visible inside throughout; the face stays smooth and featureless. The audio is a low synth drone that tightens, a sharp glassy crack as the knee drops and two heavy heartbeat thumps with the glow, no music, no dialogue.
```

### 파일럿 C ⏱ 6초 [프레임: 시작 → C_end(12° 기울임)] — WS, Eye-Level→Dutch, Roll, LIGHT-RIM — 리액션

end는 미드저니 `C_end_mj_0`(머리를 움켜쥐고 무릎이 꺾이며 한 발이 뜸)을 시계 방향 12° 기울인 것.

```
One continuous shot in a single unbroken scene with no scene cuts. 0-1.5s: from the very first frame one hand flies up and grips the side of the head as a hot amber glow flares inside the brain, and the head jerks sideways. 1.5-3s: the knees wobble and buckle, the torso lurches hard to one side and one foot lifts off the floor, while the whole frame begins to roll clockwise as if the viewer's own balance is going. 3-4.5s: the figure staggers a full step sideways with the free arm flung out wide, and the frame keeps rolling until the horizon is tilted about twelve degrees. 4.5-6s: the figure hangs off-balance mid-stagger clutching the head, the brain throbbing intense amber twice and staying fully lit until the very last frame, the tilted frame holding still, while every other organ stays soft pale cyan. The body stays translucent glass with all organs visible inside throughout; the face stays smooth and featureless. The audio is a high-pitched ringing that swells to a piercing whine, one heavy stumbling footstep and a deep heartbeat thump, no music, no dialogue.
```

## 파일럿 결과로 갈리는 것

| 결과 | 다음 |
|---|---|
| A 통과 | 전신 동작 9종 프롬프트 일괄 작성 |
| A 막힘 | 어휘를 더 중립적으로(“shifts weight”만 남기고 stumbling 제거) 재시도 |
| B 읽힘 | 국소 6종도 Flow로 — 클립 15종 |
| B 안 읽힘 | 국소 6종은 스틸 줌인으로 — 클립 9종 유지 |

## 전신 동작 9종 (2026-09-20 작성, 파일럿 A·B·C 통과 후)

⚠️ **다리·골반이 화면 대부분을 차지하는 크롭은 미드저니 출력 심의에 막힌다**(2026-09-20 실측:
`act_rub_leg`의 "허리~발" 크롭과 "허벅지~발" 크롭 둘 다 "generated image may fall outside our community
guidelines"로 거부, 프롬프트 자체는 safe 판정). 몸이 투명해서 노출로 읽히는 것으로 보인다 — **전신 구도로
가고 카메라 움직임은 Flow의 하강으로 만든다**(전신으로 뽑은 8종은 전부 통과했다).

⚠️ **크롭 지시는 프롬프트 맨 앞에 쓰고 `--no`에 `full body, whole figure, head`를 넣을 것**
(2026-09-20 실측: `act_clutch_low_back` 1차 시안 4장 전부 머리까지 나온 전신으로 나왔다 — 크롭 문구가
문장 중간에 묻히면 미드저니가 무시한다). 또 **"weight carried on one leg"처럼 체중 이동을 적으면 다리를
든 걸음 자세로 나온다** — "both feet flat on the floor"로 못 박을 것.


⚠️ **이 중 둘은 이미 렌더돼 있다** — `act_curl_up`은 `output/pilot_B.mp4`, `act_sway_offbalance`는
`output/pilot_C.mp4`가 그대로 쓸 수 있는 결과물이다(파일럿이 각각 웅크림·머리 움켜쥐고 비틀거림이었음).
새로 뽑을 건 나머지 7종.

부위 점등 클립은 분량이 커서 따로 뒀다 → `part_prompts.md`.

`flow_prompts.md` "전신 동작 9종" 절에 그대로 들어갈 초안. 파일럿 A/B/C(2026-09-18 v2)의
문장 구조·어휘·오디오 배제 문구를 그대로 따랐다.

## 작성 규칙 (파일럿·캐논에서 그대로 가져온 것)

- **프레임**: start = `stills/canon_organs.jpg` 단독 사본, end = 아래 미드저니로 뽑은 포즈 스틸.
  카메라 무빙은 텍스트가 아니라 두 프레임의 차이가 만든다(`SHOT_DESIGN_SYSTEM.md` §1).
- **미드저니**: `stills/canon_organs.jpg`를 **Omni Reference**로 끌어다 넣는다(캐논 규칙 —
  텍스트만으로 뽑으면 톤·체형이 달라져 다른 사람이 된다). 저장은 `stills/act/<이름>.jpg`.
- **스타일 앵커는 전문 반복하되 `standing in`의 `standing` 한 단어만 뺐다** — 웅크림·누움 포즈와
  정면충돌하는 유일한 단어라서다. 나머지 문장·`--no` 목록은 캐논과 글자 그대로 동일.
  프레임이 전신보다 좁아지는 클립(2·4·5)은 `full body visible from the top of the head to the feet`
  자리에 그 클립의 실제 프레임 범위를 적었다(파일럿 end가 캐논의 크롭이었던 것과 같은 처리).
- **점등은 스틸에 칠하지 않는다** — end 스틸도 중립(불 안 켠 상태)으로 뽑고 호박색은 Flow에서 켠다.
  그래서 `--no`에 amber·orange·red가 그대로 남아 있다.
- **0초부터 움직인다** — v2 1차가 약했던 첫 번째 원인이 "가만히 서 있다"로 시작해 앞 25%를 버린 것.
- **점등은 마지막 프레임까지 켜져 있다** — v2에서 B·C 마지막 0.7초에 점등이 꺼진 것을 명시로 막는다.
- **비트**: 4초 = 3비트(0-1.3 / 1.3-2.7 / 2.7-4), 6초 = 4비트(0-1.5 / 1.5-3 / 3-4.5 / 4.5-6).
- **안전필터**: collapse·faint·fall down·pass out·seizure 금지. `sways` `stumbling half-step`
  `weight shifts` `sinks down` `knee buckles` 처럼 동작 자체를 묘사하는 말만 쓴다.

## 샷 리스트 (9종 전체를 한 줄로 — 같은 크기 3연속 금지, 무빙 한 종류 40% 초과 금지)

```
클립:  1 웅크림      2 허리       3 다리       4 손        5 얼굴      6 휘청      7 화장실     8 뒤척임     9 주저앉음
길이:  6초          4초          6초          4초         4초         6초         6초          6초          4초
역할:  커버리지      디테일       디테일       디테일      리액션      리액션      커버리지     커버리지     리액션
크기:  WS→MWS       WS→MS        WS→MS        WS→MCU      WS→MCU      WS(유지)    WS(유지)     WS→MWS      WS→MWS
앵글:  eye→high     eye          eye→high     eye         eye→low     eye→dutch   eye          eye→부감     eye→low
무빙:  push-in+하강  tilt-down   하강          push-in(축) push-in+상승 roll 시계   track 좌→우  크레인 상승  하강
점등:  위·장        허리·신장     종아리       손목·손가락  눈뒤·부비동  속귀·뇌     방광·대장    뇌          심장
```

- 크기 4종(WS·MWS·MS·MCU), 앵글 6종, 무빙 7종 — push-in 계열이 3/9(33%)로 상한 안쪽.
- 7번 `track`은 이동 방향을 화면 **좌→우**로 고정한다(screen direction 180도 규칙).
- 9번만 scale-out(피사체가 프레임에서 작아짐) — 전환점 전용이라 주저앉기 한 곳에만 쓴다.

---

### 미드저니 — 끝 자세 스틸 9장

**act_curl_up**
```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, centered with clear margins on all sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the front from slightly above eye level, now doubled over: both forearms wrapped tightly across the belly with the hands clamped on opposite sides of the waist, elbows pressed hard against the ribs, the torso folded forward over the arms, the shoulders hunched up around the ears and the head dropped toward the chest, both knees bent deep with one knee dropped low toward the floor and the other leg bracing, the feet close together, the figure filling about ninety percent of the frame height. Visible inside: the brain, the lungs and heart, the liver, the stomach and the coiled intestines, the kidneys and the bladder, with the full skeleton faintly visible. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features
```

**act_clutch_low_back** — 쓰이는 곳: 허리 계열 10편 — 요통·허리디스크·협착증·신장·등 통증 topic.
```
A tightly cropped close view, the top edge of the frame cutting straight across the chest just below the collarbones and the bottom edge cutting across the knees, so that the head, the shoulders and the feet are completely outside the frame and not visible anywhere in the image. Medical holographic visualization of a translucent glass-like 3D human body, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, centered with clear margins on both sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same body as the reference, seen from the front at eye level, standing upright and still with both feet flat on the floor side by side and both legs straight, now with both hands pressed flat on the small of the back, the thumbs hooked forward over the hip bones and the fingers spread across the lower spine, both elbows flared wide out to the sides, the chest lifted and the lower back arched backward so the belly pushes toward the camera, the hips pushed forward. Visible inside: the lower ribs, the liver, the stomach and the coiled intestines, both kidneys on either side of the lumbar spine, the lumbar vertebrae and the pelvis, with the leg bones faintly visible. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features
```

**act_rub_leg** — 숙여서 양 무릎을 짚었다가 종아리를 주무른다(2026-09-20 채택본 자세에 맞춤)
```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, centered with clear margins on all sides, the figure filling about eighty-five percent of the frame height, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the front, now bent forward at the waist with the back rounded and the head bowed, both arms reaching straight down and both hands wrapped around one calf just below the knee, the fingers squeezing into the calf muscle from behind, that knee slightly bent with both feet flat on the floor side by side. Visible inside: the brain, the lungs and heart, the stomach and coiled intestines, the spine curving from the neck to the pelvis, the thigh bones, the knee joints, the calf muscles and the branching network of vessels running down both legs to the feet. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, walking, mid-stride, raised knee, lifted leg
```

**act_rub_hands**
```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, framed from the top of the head down to the hips, centered with clear margins on both sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the front at eye level, now with both hands raised in front of the breastbone, one hand wrapped around the other with that thumb pressing hard into the opposite palm and the fingers curled over the back of the hand, both elbows tucked in against the ribs, the shoulders drawn slightly forward and the head tilted down toward the hands. Visible inside: the finger bones and wrist bones of both hands, the tendons running into the fingers and the nerves passing through both wrists, the arm bones, the collarbones and the rib cage, with the lungs and heart faintly visible behind. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features
```

**act_cover_face**
```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, framed from just above the head down to the waist, centered with clear margins on both sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the front from slightly below eye level looking up, now with both palms pressed flat over the smooth featureless face, the heels of the hands covering the eye sockets and the fingers spread upward across the forehead, both elbows lifted forward and drawn close together in front of the chest, the head bowed into the hands and the shoulders pulled up. Visible inside: the brain, both eyeballs in their sockets behind the covering hands, the sinuses and the nasal cavity, the teeth in the jaw, the hand and wrist bones, the collarbones and the upper ribs. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features
```

**act_sway_offbalance** — 쓰이는 곳: 어지럼 계열 8편 — 어지럼증·이석증·빈혈·저혈압·기립성 topic.
```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, centered with clear margins on all sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the front at eye level, now caught mid-stagger: one hand gripping the side of the head just above the ear, the head jerked over toward that hand, the other arm flung out wide and high for balance, the torso lurched hard to one side, one knee buckled inward and the opposite foot lifted off the floor behind, the whole body leaning far off its own centre line. Visible inside: the brain, the inner ear behind the jaw on both sides, the spine, the lungs and heart, the stomach and coiled intestines, with the full skeleton faintly visible. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features
```

**act_rush_to_toilet** — 쓰이는 곳: 비뇨기·장 계열 6편 — 빈뇨·방광염·요로·설사·과민성 장 topic.
```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, the figure filling about eighty-five percent of the frame height, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference at the same size, now placed in the right third of the frame and caught in mid-stride moving toward frame right: one leg stretched far forward with the heel about to land and the other trailing behind with the toes still pushing off, the torso leaning forward over the leading leg, one hand clamped flat low across the lower belly, the free arm swung back behind the hip, the head pushed forward ahead of the shoulders. Visible inside: the lungs and heart, the stomach and the coiled intestines, the large intestine framing them, the bladder low in the pelvis, the pelvis and the leg bones. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features
```

**act_toss_turn** — 쓰이는 곳: 수면 계열 5편 — 불면·수면의 질·코골이·야간뇨·다리 불편 topic.
```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, centered with clear margins on all sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, now lying on an unseen flat surface and seen from directly overhead looking straight down, rolled onto one side with the knees drawn up toward the chest, the upper arm folded so that the hand is tucked under the head and the lower arm trapped across the ribs, the head turned down into the crook of that arm, the spine curled, one foot hooked over the other ankle. Visible inside: the brain, the spine curving through the whole body, the lungs and heart, the stomach and coiled intestines, the pelvis and the leg bones. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features
```

**act_sink_to_floor** — 쓰이는 곳: 탈진 계열 2편 — 저혈압·저혈당·기력 저하 topic.
```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, sitting low in the lower half of the frame with open dark empty space above, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the front from a camera lowered close to floor level looking slightly up, now sitting back on its own heels with both knees folded under the body, both palms flat on the floor in front with the arms locked straight and the shoulders pushed up around the ears, the back rounded and the head hanging forward between the arms. Visible inside: the brain, the lungs and the heart, the stomach and coiled intestines, the spine curving from the neck to the pelvis, the pelvis and the folded leg bones. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features
```

### Flow — 모션 프롬프트 9개

시작 프레임은 전부 `stills/canon_organs.jpg`, 끝 프레임은 위에서 만든 `<이름>_end.jpg`.

**act_curl_up ⏱ 6초 [프레임: canon_organs → act_curl_up_end] — WS→MWS, Eye-Level→High, Push-in+하강, LIGHT-RIM — 커버리지**
```
One continuous shot in a single unbroken scene with no scene cuts. 0-1.5s: from the very first frame both hands snap inward and clamp onto the belly as a hot amber glow bursts on inside the stomach and intestines, and the camera starts pushing in and lowering. 1.5-3s: the torso jerks forward and folds hard over the arms, the shoulders hunching and the head dropping toward the chest. 3-4.5s: both knees bend deep and one knee drops sharply toward the floor while the other leg braces, the body folding into a tight doubled-over crouch, and the camera keeps pushing in and descending with it until the figure fills about ninety percent of the frame height. 4.5-6s: the figure stays locked in the crouch, trembling, both arms wrapped around the belly, the stomach and intestines throbbing intense amber twice and staying fully lit until the very last frame, while every other organ stays soft pale cyan. The body stays translucent glass with all organs visible inside throughout; the face stays smooth and featureless, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a low synth drone that tightens, a sharp glassy crack as the knee drops and two heavy heartbeat thumps with the glow, no music, no dialogue.
```

**act_clutch_low_back ⏱ 4초 [프레임: canon_organs → act_clutch_low_back_end] — WS→MS, Eye-Level, Tilt-down, LIGHT-RIM — 디테일**
```
One continuous shot in a single unbroken scene with no scene cuts. 0-1.3s: from the very first frame both hands sweep backward and press flat onto the small of the back as a hot amber glow flares deep inside the lumbar spine and both kidneys, and the camera starts tilting downward without changing its distance. 1.3-2.7s: the chest lifts and the lower back arches further backward, the elbows flaring wide, and the tilt continues until the chest-to-knees region fills the whole frame. 2.7-4s: the figure holds the arch, the thumbs digging into the lower back, the lumbar spine and kidneys throbbing intense amber twice and staying fully lit until the very last frame, while every other organ, every bone and the glass skin stay soft pale cyan. The body stays translucent glass with all organs visible inside throughout; the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a low synth hum that thickens, a dull grinding creak as the back arches and two deep heartbeat thumps with the glow, no music, no dialogue.
```

**act_rub_leg ⏱ 6초 [프레임: canon_organs → act_rub_leg_end] — WS→MS, Eye-Level→High, 하강(Descend), LIGHT-RIM — 디테일**
```
One continuous shot in a single unbroken scene with no scene cuts. 0-1.5s: from the very first frame the torso hinges forward at the waist and both arms swing down toward the legs, and the camera starts descending from eye level. 1.5-3s: both hands land on the knees and press down hard, the back rounding and the head bowing between the shoulders, and a hot amber glow bursts on inside both knee joints and the calf muscles below them. 3-4.5s: the hands slide down from the knees onto the calves and knead them, the fingers squeezing into the calf muscle, while the camera keeps lowering until it sits at hip height and the bent-over figure fills about ninety percent of the frame height. 4.5-6s: the figure holds the bent-over position, still kneading, the knee joints and calf muscles throbbing intense amber twice and staying fully lit until the very last frame, while every other organ, every bone and the glass skin stay soft pale cyan. The body stays translucent glass with all structures visible inside throughout; the face stays smooth and featureless, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a low synth drone, a slow rhythmic rubbing scrape and two deep heartbeat thumps with the glow, no music, no dialogue.
```

**act_rub_hands ⏱ 4초 [프레임: canon_organs → act_rub_hands_end] — WS→MCU, Eye-Level, Push-in(축), LIGHT-RIM — 디테일**
```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis. 0-1.3s: from the very first frame both hands lift to the breastbone and one hand closes around the other, and the camera starts moving forward from the full-body framing. 1.3-2.7s: the thumb presses hard into the opposite palm and works in slow circles, the elbows tucking against the ribs, and a hot amber glow flickers on inside both wrists and the finger joints while the push-in continues until the head-to-hips region fills the whole frame. 2.7-4s: the camera eases to a stop as the hands keep kneading and the wrist and finger joints swell to full bright amber, throbbing twice and staying fully lit until the very last frame; every other structure, every bone and the glass skin stay soft pale cyan. The body stays translucent glass with all structures visible inside throughout; the face stays smooth and featureless, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum, a dry rubbing squeak of glass on glass and two deep heartbeat thumps with the glow, no music, no dialogue.
```

**act_cover_face ⏱ 4초 [프레임: canon_organs → act_cover_face_end] — WS→MCU, Eye-Level→Low, Push-in+상승, LIGHT-RIM — 리액션**
```
One continuous shot in a single unbroken scene with no scene cuts. 0-1.3s: from the very first frame both hands fly up and press flat over the face as a hot amber glow flares inside the head behind both eye sockets and across the sinuses, and the camera starts pushing in and rising. 1.3-2.7s: the heels of the hands grind into the eye sockets, the fingers spreading up across the forehead, the head bowing into the hands and the shoulders pulling up, while the camera keeps rising until it looks slightly upward and the head-to-waist region fills the whole frame. 2.7-4s: the figure holds the pose, the hands pressing harder, the area behind the eye sockets and the sinuses throbbing intense amber twice and staying fully lit until the very last frame, while every other organ, every bone and the glass skin stay soft pale cyan. The body stays translucent glass with all structures visible inside throughout; the face stays smooth and featureless, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a low synth drone that presses in, a dull throbbing pulse and two deep heartbeat thumps with the glow, no music, no dialogue.
```

**act_sway_offbalance ⏱ 6초 [프레임: canon_organs → act_sway_offbalance_end(시계 12° 기울임)] — WS(유지), Eye-Level→Dutch, Roll(시계 12°), LIGHT-RIM — 리액션**
```
One continuous shot in a single unbroken scene with no scene cuts. 0-1.5s: from the very first frame one hand flies up and grips the side of the head as a hot amber glow flares inside the inner ear behind the jaw and spreads into the brain, and the head jerks sideways. 1.5-3s: the knees wobble and one buckles inward, the torso lurches hard to that side and one foot lifts off the floor, while the whole frame begins to roll clockwise as if the viewer's own balance is going. 3-4.5s: the figure sways a full stumbling half-step sideways with the free arm flung out wide and high, and the frame keeps rolling until the horizon is tilted about twelve degrees. 4.5-6s: the figure hangs off-balance mid-stagger clutching the head, the inner ear and brain throbbing intense amber twice and staying fully lit until the very last frame, the tilted frame holding still, while every other organ stays soft pale cyan. The body stays translucent glass with all organs visible inside throughout; the face stays smooth and featureless, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a high-pitched ringing that swells to a piercing whine, one heavy stumbling footstep and a deep heartbeat thump, no music, no dialogue.
```

**act_rush_to_toilet ⏱ 6초 [프레임: canon_organs → act_rush_to_toilet_end] — WS(유지), Eye-Level, Track(좌→우 횡이동), LIGHT-RIM — 커버리지**
```
One continuous shot in a single unbroken scene with no scene cuts, the camera trucking laterally alongside the figure at a constant distance so the figure stays the same size throughout. 0-1.5s: from the very first frame one hand clamps flat across the lower belly and the figure breaks into a fast stride moving from frame left toward frame right, as a hot amber glow bursts on inside the bladder and the lower intestine. 1.5-3s: the strides lengthen and the torso leans further forward over the leading leg, the free arm swinging back behind the hip, the camera sliding along with it at the same distance. 3-4.5s: the figure keeps driving toward frame right, the head pushed forward ahead of the shoulders, until it sits in the right third of the frame still filling about eighty-five percent of the frame height. 4.5-6s: the figure holds the hurried stride, the bladder and lower intestine throbbing intense amber twice and staying fully lit until the very last frame, while every other organ stays soft pale cyan. The body stays translucent glass with all organs visible inside throughout; the face stays smooth and featureless, the dark slate blue-grey void stays empty, consistent screen direction from frame left to frame right. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a low synth drone that accelerates, quick hurried glassy footsteps and two heavy heartbeat thumps with the glow, no music, no dialogue.
```

**act_toss_turn ⏱ 6초 [프레임: canon_organs → act_toss_turn_end] — WS→MWS, Eye-Level→부감(Overhead), 크레인 상승, LIGHT-RIM — 커버리지**
```
One continuous shot in a single unbroken scene with no scene cuts. 0-1.5s: from the very first frame the knees give and the figure lowers itself backward onto an unseen flat surface, and the camera starts craning upward. 1.5-3s: the figure settles flat on its back with the arms loose at its sides, while the camera keeps climbing and swinging over until it looks straight down from directly overhead, and a hot amber glow flickers on inside the brain. 3-4.5s: the figure rolls sharply onto one side, the knees pulling up toward the chest and one hand tucking under the head, then jerks halfway back and rolls again, restless. 4.5-6s: the figure curls tight on its side and stops moving except for a shallow tremble, the brain throbbing intense amber twice and staying fully lit until the very last frame, while every other organ stays soft pale cyan. The body stays translucent glass with all organs visible inside throughout; the face stays smooth and featureless, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a low synth drone, a soft dragging rustle with each roll and two deep heartbeat thumps with the glow, no music, no dialogue.
```

**act_sink_to_floor ⏱ 4초 [프레임: canon_organs → act_sink_to_floor_end] — WS→MWS, Eye-Level→Low, 하강(Descend), LIGHT-RIM — 리액션**
```
One continuous shot in a single unbroken scene with no scene cuts. 0-1.3s: from the very first frame the weight shifts off one leg and both knees buckle as a hot amber glow bursts on inside the heart, and the camera starts descending toward floor level. 1.3-2.7s: the figure sinks down fast, the knees folding under the body and both hands shooting out to catch the floor, the arms locking straight and the shoulders pushing up, while the camera keeps lowering until it looks slightly upward from floor level. 2.7-4s: the figure settles back onto its heels with the head hanging forward between the straight arms, small empty void opening up above it, the heart throbbing intense amber twice and staying fully lit until the very last frame, while every other organ stays soft pale cyan. The body stays translucent glass with all organs visible inside throughout; the face stays smooth and featureless, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a low synth drone that drops away, a soft heavy glassy thud as the knees meet the floor and two slow heartbeat thumps with the glow, no music, no dialogue.
```


## Flow를 쓰지 않는 것 (스틸 + 전환으로 처리)

- **국소·미세 동작 6종** — 반투명 얼굴엔 이목구비가 없어 "눈 비비기"와 "코 만지기"가
  구분이 안 될 공산이 크다(파일럿 B로 확인)
- **변화·과정 5종**(체형 변화·기운 빠짐·냄새 번짐·천천히 일어섬·땀/오한) —
  4~8초 안에 형태를 바꾸면 Veo가 몸을 뭉갠다. **스틸 두 장(전/후) + 크로스디졸브**가
  훨씬 안정적이고 의도대로 나온다
