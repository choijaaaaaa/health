# midjourney_prompts.md — 반투명 인체 라이브러리 (9:16, 캐논 스틸)

생성 → 다운로드 → `stills/<파일명>.jpg`로 저장. Flow 모션 프롬프트는 `flow_prompts.md`.

🚨 **모든 캐논은 중립(불 안 켠 상태)으로 뽑는다.** 호박색 점등은 Flow 클립 안에서
켠다 — 스틸에 미리 칠하면 부위마다 스틸이 필요해 같은 이미지를 돌려 쓸 수 없다.
그래서 `--no`에 amber·orange·red·glowing highlight를 넣어뒀다.

🚨 **정면 캐논 `stills/canon_organs.jpg`(확정)를 매번 미드저니 레퍼런스로 끌어다 넣을 것**
(웹 UI에서 Omni Reference 지정). 텍스트만으로 뽑으면 톤·체형이 달라져 다른 사람이 된다.
클로즈업도 같은 청록 톤·배경이어야 컷이 넘어갈 때 한 세계로 읽힌다.

🚨 **왜 여러 장인지**: 장기·근육·뼈·혈관·신경은 서로 가려서 한 몸에 다 넣을 수 없고
(의학 도감이 층을 나누는 이유), 속귀·치아·무릎 연골 같은 작은 부위는 전신 샷에선
몇 픽셀이라 짚을 수 없다. 방향별(정면·측면·후면) 캐논을 갖추면 Flow로 몸을 회전시킬
필요도 없어진다 — Veo가 옆·뒤를 지어내다 장기 배치가 바뀌는 문제를 피한다.

⚠️ 얼굴은 이목구비 없이 매끈하게. 표정이 들어가면 컷마다 인상이 달라지고 안전필터도 더 탄다.

## 목록

| 파일명 | 분류 | 내용 | 쓰는 topic |
|---|---|---|---|
| `canon_organs` ✅ | 전신 | 정면 장기 | 위·장·폐·심장·간·갑상선·방광 |
| `canon_organs_side` | 전신 | 측면 장기 | 어지럼증(속귀)·거북목·목어깨·척추 곡선 |
| `canon_organs_back` | 전신 | 후면 장기 | 신장·허리·등·척추 |
| `canon_muscle_front` | 전신 | 정면 근육층 | 근육통·어깨결림·허벅지 |
| `canon_muscle_back` | 전신 | 후면 근육층 | 허리·등·종아리 쥐·햄스트링 |
| `canon_skeleton_front` | 전신 | 정면 골격층 | 관절·골다공증·척추 |
| `canon_vascular_front` | 전신 | 정면 혈관층 | 혈압·혈액순환·하지정맥·동맥경화 |
| `canon_nervous_back` | 전신 | 후면 신경층 | 손발저림·좌골신경통·디스크 |
| `cu_head_front` | 클로즈업 | 머리 정면 | 두통·뇌·눈·코·입 전체 |
| `cu_head_side` | 클로즈업 | 머리 측면 | 어지럼증·이명·중이염·부비동·편도·코골이 |
| `cu_eye` | 클로즈업 | 안구 단면 | 안구건조·녹내장·백내장·황반변성·비문증 |
| `cu_mouth` | 클로즈업 | 구강 | 치아·잇몸·구취·구각염·편도결석·턱관절 |
| `cu_ear` | 클로즈업 | 귀 단면 | 이명·난청·중이염·이석증 |
| `cu_neck_thyroid` | 클로즈업 | 목·갑상선 | 갑상선·목통증·거북목 |
| `cu_torso_organs` | 클로즈업 | 몸통 장기 | 위·간·췌장·장·담낭·역류 |
| `cu_pelvis` | 클로즈업 | 골반 장기 | 방광·빈뇨·요로·여성(자궁·난소)·전립선 |
| `cu_spine_lumbar` | 클로즈업 | 허리 척추 | 허리디스크·요통·협착증 |
| `cu_knee` | 클로즈업 | 무릎 관절 | 무릎통증·관절염·연골·십자인대 |
| `cu_hand` | 클로즈업 | 손 | 손저림·손목터널·방아쇠수지·관절염 |
| `cu_foot` | 클로즈업 | 발 | 발냄새·족저근막염·무좀·통풍·발저림 |
| `cu_legs_veins` | 클로즈업 | 다리 혈관 | 하지정맥·부종·다리저림·쥐 |
| `cu_skin_section` | 클로즈업 | 피부 단면 | 피부·여드름·건조·가려움·탈모·땀 |

✅ `canon_organs` 확정(2026-09-18, test_2 — 장기 윤곽이 가장 뚜렷. 1은 골반에 검은 덩어리,
3은 사타구니 옆 해부학적으로 틀린 구체 두 개, 4는 장기가 흐려 위가 안 읽힘.
후보 전부 `stills/_candidates/canon_organs/`).

### 1차 일괄 생성 결과 (2026-09-18) — 21종 채택, 재생성 필요 2종

| 파일명 | 채택 | 메모 |
|---|---|---|
| canon_organs_side | v2 | 정확한 옆모습, 뇌·척추 곡선 보임 |
| canon_organs_back | v0 | 발뒤꿈치가 보여 뒷모습으로 읽힘, 신장 뚜렷 |
| canon_muscle_front | v2 | |
| canon_muscle_back | v2 | 승모근·척추기립근·둔근 뚜렷 |
| canon_skeleton_front | round2 v1 | 1차는 4장 모두 척추만 보여 재생성. 2차에서 갈비뼈·골반·넙다리뼈·무릎까지 보임 |
| canon_vascular_front | v2 | 심장·혈관 가장 선명 |
| canon_nervous_back | v3 | 척수·좌골신경 뚜렷 |
| cu_head_front | v1 | 안구에 홍채가 그려짐 — 눈 topic엔 오히려 적합 |
| cu_head_side | v0 | 달팽이관·부비동·기도 다 보임 |
| cu_eye | v0 | |
| cu_mouth | v2 | 나머지 3장은 치아가 상아색으로 튀어 팔레트를 깸, v2만 청록 |
| cu_ear | v2 | 달팽이관·반고리관 가장 명료 |
| cu_neck_thyroid | v3 | 4장 중 유일하게 갑상선이 보임(다른 건 가슴까지 넓게 나옴) |
| cu_torso_organs | v0 | 클로즈업이 아니라 머리~허벅지로 나옴. 정면 장기 캐논과 겹치지만 Flow 줌인으로 대체 가능해 그대로 둠 |
| cu_pelvis | v0 | 방광·요관·신장 선명 |
| cu_bladder | round2 v3 | 방광이 가장 또렷 — 빈뇨·요로 topic용 |
| cu_pelvis_female | **Gemini 편집** e0 | ⚠️ 미드저니는 8장 연속 자궁·난소를 못 그림. Gemini로 새로 그리면 장기는 정확하나 몸 실루엣·크롭이 달라져 세트에서 튐 → **`cu_pelvis.jpg`를 넣고 "그대로 두고 자궁·나팔관·난소만 추가"로 편집**시켜 구도·크롭을 원본과 픽셀 단위로 동일하게 유지 |
| cu_spine_lumbar | v0 | 허리 클로즈업이 아니라 몸통 3/4 뒷모습. 나머지는 척추만 하얗게 튀어 제외 |
| cu_knee | v1 | 슬개골·반월판 선 보임 |
| cu_hand | v1 | 손목 신경이 보여 손목터널증후군에 적합 |
| cu_foot | v0 | |
| cu_legs_veins | v2 | 정맥이 가장 잘 보임(프롬프트는 뒷모습이었으나 정면으로 나옴) |
| cu_skin_section | v3 | 표피·진피·지방층 3단이 구분됨 |

🚨 **이미지는 미드저니만 쓴다(2026-09-18 사용자 확정).** Gemini 이미지 생성·편집은 쓰지 않는다 — 선불 크레딧 소진으로 막힌 뒤 확정. `gemini_edit_still.py`·`gen_pilot_ends.py`는 기록용으로만 남긴다. end 프레임·자세 변형·부위 추가도 미드저니(레퍼런스 이미지 + 에디터/Vary Region)로 한다. `cu_pelvis_female`는 이 결정 이전에 Gemini 편집으로 만든 것이라 그대로 둔다.

미드저니는 한 번에 4장이 나오니 **파일명당 마음에 드는 1장을 고르고 나머지는
`stills/_candidates/<파일명>/`에 보관**한다(폐기 이미지도 지우지 않는다).

## canon_organs_side — 측면 장기

쓰는 topic: 어지럼증(속귀)·거북목·목어깨·척추 곡선

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, standing in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, centered with clear margins on all sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The figure is seen in exact side profile facing left, standing upright with arms at the sides. Visible inside: the brain, the inner ear behind the jaw, the curved spine from neck to pelvis, the lungs and heart, the stomach and coiled intestines, with the full skeleton faintly visible. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, front view, three-quarter view, facial features
```

## canon_organs_back — 후면 장기

쓰는 topic: 신장·허리·등·척추

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, standing in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, centered with clear margins on all sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The figure is seen from directly behind, standing upright and symmetrical, arms slightly away from the torso. Visible inside: the brain, the full spine down the centre of the back, both kidneys on either side of the lower spine, the back of the lungs, the shoulder blades and the pelvis, with the full skeleton faintly visible. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, face, front view, side view
```

## canon_muscle_front — 정면 근육층

쓰는 topic: 근육통·어깨결림·허벅지

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, standing in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, centered with clear margins on all sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The figure faces the camera, standing upright and symmetrical. Instead of organs, the full muscular system is visible under the glass skin: neck and shoulder muscles, chest, abdominal wall, arm muscles, thigh and calf muscles, each muscle's fibre direction visible. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, organs, intestines
```

## canon_muscle_back — 후면 근육층

쓰는 topic: 허리·등·종아리 쥐·햄스트링

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, standing in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, centered with clear margins on all sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The figure is seen from directly behind, standing upright and symmetrical. The full muscular system is visible under the glass skin: trapezius, back muscles along the spine, lower back muscles, glutes, hamstrings and calf muscles, each muscle's fibre direction visible. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, face, organs, intestines, front view
```

## canon_skeleton_front — 정면 골격층

쓰는 topic: 관절·골다공증·척추

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, standing in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, centered with clear margins on all sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The figure faces the camera, standing upright and symmetrical. Only the full skeleton is visible under the glass skin: skull, spine, rib cage, pelvis, arm and leg bones, knee joints, ankle joints, hand and foot bones, clearly defined. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, organs, muscles
```

## canon_vascular_front — 정면 혈관층

쓰는 topic: 혈압·혈액순환·하지정맥·동맥경화

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, standing in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, centered with clear margins on all sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The figure faces the camera, standing upright and symmetrical. Only the heart and the full network of arteries and veins are visible under the glass skin, branching from the chest down both arms and both legs, the leg veins clearly traceable to the feet. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, organs, muscles, intestines
```

## canon_nervous_back — 후면 신경층

쓰는 topic: 손발저림·좌골신경통·디스크

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, standing in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, centered with clear margins on all sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The figure is seen from directly behind, standing upright and symmetrical. Only the brain, the spinal cord and the peripheral nerves are visible under the glass skin, the nerves branching from the spine down both arms to the fingers and down both legs to the toes, the sciatic nerve clearly traceable through the back of each leg. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, face, organs, muscles, front view
```

## cu_head_front — 머리 정면

쓰는 topic: 두통·뇌·눈·코·입 전체

```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A close-up of a translucent head and neck facing the camera, shoulders at the bottom edge. Visible inside: the brain, both eyeballs in their sockets with the optic nerves, the nasal cavity, the teeth and tongue, the throat and the thyroid at the base of the neck. Smooth featureless face surface. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, full body
```

## cu_head_side — 머리 측면

쓰는 topic: 어지럼증·이명·중이염·부비동·편도·코골이

```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A close-up of a translucent head and neck in exact side profile facing left. Visible inside: the brain, the inner ear with the cochlea and semicircular canals behind the jaw, the ear canal, the sinuses, the nasal cavity, the tonsils and the airway down the throat. Smooth featureless face surface. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, front view, full body
```

## cu_eye — 안구 단면

쓰는 topic: 안구건조·녹내장·백내장·황반변성·비문증

```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. An extreme close-up cross-section of a single translucent eyeball seen from the side, showing the cornea, the lens, the iris, the vitreous body, the retina lining the back and the optic nerve leaving the rear of the eye. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, face, full head, eyelashes
```

## cu_mouth — 구강

쓰는 topic: 치아·잇몸·구취·구각염·편도결석·턱관절

```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A close-up of a translucent lower face and jaw seen at a slight three-quarter angle, showing the upper and lower rows of teeth with their roots in the jawbone, the gums, the tongue, the tonsils at the back of the mouth and the jaw joint in front of the ear. Smooth featureless surface. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, lips, facial features, full body
```

## cu_ear — 귀 단면

쓰는 topic: 이명·난청·중이염·이석증

```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A close-up cross-section of a translucent ear seen from the front, showing the outer ear, the ear canal, the eardrum, the tiny middle ear bones, the spiral cochlea and the three semicircular canals of the inner ear. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, face, full head
```

## cu_neck_thyroid — 목·갑상선

쓰는 topic: 갑상선·목통증·거북목

```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A close-up of a translucent neck seen from the front, from the jaw down to the collarbones, showing the butterfly-shaped thyroid gland wrapped around the windpipe, the cervical spine behind it and the major neck blood vessels. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, face, facial features, full body
```

## cu_torso_organs — 몸통 장기

쓰는 topic: 위·간·췌장·장·담낭·역류

```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A close-up of a translucent torso seen from the front, from the collarbones down to the hips, showing the lungs, the heart, the liver, the gallbladder, the stomach, the pancreas behind the stomach, the small intestine coils and the large intestine framing them. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, head, face, full body
```

## cu_pelvis — 골반 장기

쓰는 topic: 방광·빈뇨·요로·여성(자궁·난소)·전립선

```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A close-up of a translucent lower abdomen and pelvis seen from the front, showing the pelvic bones, the bladder, the uterus with both ovaries and fallopian tubes, the lower intestine and the ureters coming down from above. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, face, full body, genitals
```

## cu_spine_lumbar — 허리 척추

쓰는 topic: 허리디스크·요통·협착증

```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A close-up of a translucent lower back seen from behind at a slight angle, showing the lumbar vertebrae stacked with the intervertebral discs between them, the spinal cord and the nerve roots exiting each level, the pelvis at the bottom. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, face, full body
```

## cu_knee — 무릎 관절

쓰는 topic: 무릎통증·관절염·연골·십자인대

```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A close-up of a translucent knee joint seen from the front at a slight angle, showing the thigh bone, the shin bone, the kneecap, the cartilage and meniscus between the bones and the ligaments crossing the joint. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, full body
```

## cu_hand — 손

쓰는 topic: 손저림·손목터널·방아쇠수지·관절염

```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A close-up of a translucent hand and wrist, palm facing the camera with fingers slightly spread, showing all the finger bones and joints, the wrist bones, the tendons running into the fingers and the nerves passing through the wrist. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, full body, face
```

## cu_foot — 발

쓰는 topic: 발냄새·족저근막염·무좀·통풍·발저림

```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A close-up of a translucent foot and ankle seen from the side at a slight top-down angle, showing all the foot bones, the ankle joint, the arch, the plantar fascia along the sole and the toe joints. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, full body, face
```

## cu_legs_veins — 다리 혈관

쓰는 topic: 하지정맥·부종·다리저림·쥐

```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A close-up of a pair of translucent lower legs from the knees down to the feet, seen from behind, showing the calf muscles and the branching network of veins and arteries running down to the feet. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, full body, face
```

## cu_skin_section — 피부 단면

쓰는 topic: 피부·여드름·건조·가려움·탈모·땀

```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A close-up cross-section block of translucent human skin, showing the thin top layer, the thicker middle layer, the fatty layer beneath, hair follicles with hairs growing out of the surface, sweat glands, oil glands and tiny blood vessels. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, full body, face
```
