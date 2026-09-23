# part_prompts (초안) — 반투명 인체 "부위 점등" 클립 4초 × 31종

`flow_prompts.md` 파일럿 A가 캐논이다(느린 축방향 push-in + 해당 부위만 호박색으로 켜져 맥동).
이 파일은 그 A를 부위별로 복제한 것 — 새 색·새 카메라 문법은 하나도 만들지 않았다.

## 공통 규칙 (전부 파일럿 A·`midjourney_prompts.md`에서 그대로 가져옴)

- **길이는 4초 고정, 비트 3개**(4÷1.5 이상). 길이는 4·6·8·10초만 허용되는데 부위 점등은 한 동작뿐이라 4초.
- **프레임은 시작 한 장만, end 슬롯은 비운다.** 고정 피사체에 두 프레임을 주면 Veo가 형태를 뭉갠다
  (`flow_prompts.md` 🚨, 1biteinfo 실측).
- **색 규칙은 청록 유리 + 문제 부위만 호박색** 하나뿐. 나머지 장기·뼈·유리 피부는 끝까지 soft pale cyan.
- **마지막 프레임까지 켜진 채 유지**를 매 프롬프트에 명시한다 — 파일럿 v2에서 마지막 0.7초에 점등이
  꺼지는 사고가 있었다.
- **시청층이 중장년이라 카메라는 느리고 또렷하게** — 축방향 push-in 하나만 쓰고 roll·tilt·흔들림은
  전 클립에서 금지 문구로 박아뒀다(어지럼증 연출이 필요하면 그건 파일럿 C 계열이지 부위 점등이 아니다).
- 화면 안 글자 금지, 오디오 자체 생성 배제 문구 필수.
- 새 스틸은 **`stills/canon_organs.jpg`를 Omni Reference로** 넣고 뽑는다(톤·체형 고정).
  4장 중 1장 채택, 나머지는 `stills/_candidates/<파일명>/`에 보관.

## 새로 뽑아야 할 미드저니 스틸 7종

| 파일명 | 왜 필요한가 | 쓰는 part |
|---|---|---|
| `cu_heart` | 순환 22편이 거의 다 심장 질환(심방세동·협심증·심근경색·심부전·판막)인데 심장 클로즈업이 없다. `canon_vascular_front`엔 전신 안에 작게만 있음 | part_heart |
| `cu_lungs` | 폐·기관지 컷이 아예 없다(미세먼지 12 + 코_3 코골이·기도) | part_lungs |
| `cu_liver_pancreas` | 간·췌장·담낭 클로즈업 없음. 대사 22 + 혈당 14 + 소화(담석)가 전부 여기 | part_liver, part_pancreas |
| `cu_shoulder` | 근골격 29편 중 오십견·회전근개·목어깨 결림이 어깨인데 어깨 관절 컷이 없다 | part_shoulder |
| `cu_nose_sinus` | 코 23편 전용 컷이 없다. `cu_head_side`엔 부비동이 머리 전체 안에 몇 픽셀로만 보임 | part_nose_sinus |
| `cu_scalp` | 머리 20편의 절반 이상이 탈모·두피(비듬·모낭염·지루성두피염). `cu_skin_section`은 일반 피부라 모낭이 주인공이 아님 | part_scalp |
| `cu_intestines` | 소화 30편(최다)의 장 계열(과민성대장·변비·SIBO·게실염·용종). `cu_torso_organs`는 머리~허벅지라 장이 화면 1/3 | part_intestines |

기존 `cu_*`로 덮이는 부위는 그대로 재사용했다(아래 각 항목의 프레임 이름 참고).

---

## 소화 (30편)

### part_stomach ⏱ 4초 [프레임: cu_torso_organs.jpg 단독]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent figure stays completely still. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the torso framing, the stomach sitting under the left ribs still the same soft pale cyan as every organ around it. 1.3-2.7s: the push-in continues until the stomach and the ribs above it fill the centre of the frame, and a faint warm amber glow flickers on inside the curved bag of the stomach. 2.7-4s: the camera eases to a stop as the stomach glow swells to full bright amber and pulses once, and the stomach stays fully lit in bright amber until the very last frame; every other organ, every bone and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `소화_*` 중 위 계열(위염·속쓰림·위경련·급체·위산부족·기능성소화불량)

### part_intestines ⏱ 4초 [프레임: cu_intestines.jpg 단독 — 신규]

**미드저니 (신규 스틸)**
```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A close-up of a translucent lower abdomen seen from the front, from just under the ribs down to the top of the hips, filling the frame, showing the coiled small intestine in the middle and the large intestine framing it up the right side, across the top and down the left side, the appendix at the lower right and the rectum at the bottom centre, the pelvic bones faint at the bottom edge. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, head, face, full body, genitals
```

**Flow**
```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent abdomen stays completely still. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the lower abdomen framing, the coiled small intestine and the large intestine around it still the same soft pale cyan. 1.3-2.7s: the push-in continues until the coiled loops fill the centre of the frame, and a faint warm amber glow flickers on and spreads along the large intestine from the lower right, up, across and down the left side. 2.7-4s: the camera eases to a stop as the whole loop of large intestine and the small intestine coils inside it swell to full bright amber and pulse once together, and they stay fully lit in bright amber until the very last frame; the pelvic bones and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `소화_*` 중 장 계열(과민성대장·변비·SIBO·게실염·대장용종·설사)

### part_esophagus ⏱ 4초 [프레임: cu_torso_organs.jpg 단독]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent figure stays completely still. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the torso framing, the long tube running from the throat down behind the breastbone into the stomach still the same soft pale cyan as everything around it. 1.3-2.7s: the push-in continues until the throat, the tube and the top of the stomach fill the centre of the frame, and a faint warm amber glow flickers on at the junction where the tube meets the stomach. 2.7-4s: the camera eases to a stop as the amber glow climbs up the tube toward the throat, swells to full bright amber and pulses once, and the whole tube from the stomach up to the throat stays fully lit in bright amber until the very last frame; the lungs, the ribs and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `소화_1`(역류성 식도염)·`소화_29`(속쓰림)·`고령_6`(연하장애)·`고령_12`(질식)

---

## 근골격 (29편) · 고령 (17편)

### part_spine_lumbar ⏱ 4초 [프레임: cu_spine_lumbar.jpg 단독]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent figure stays completely still. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the three-quarter rear view of the torso, the stacked vertebrae of the lower back still the same soft pale cyan as the rest of the spine. 1.3-2.7s: the push-in continues until the lower back from the bottom ribs down to the pelvis fills the centre of the frame, and a faint warm amber glow flickers on in the discs between the lowest vertebrae. 2.7-4s: the camera eases to a stop as the lumbar vertebrae and the discs between them swell to full bright amber and pulse once, and they stay fully lit in bright amber until the very last frame; the upper spine, the ribs, the pelvis and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `근골격_*` 허리 계열(허리디스크·요통·척추관협착증·좌골신경통)

### part_knee ⏱ 4초 [프레임: cu_knee.jpg 단독]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent leg stays completely still. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the framing of the whole leg, the knee joint in the middle of the frame still the same soft pale cyan as the bones above and below it. 1.3-2.7s: the push-in continues until the knee joint fills the centre of the frame, and a faint warm amber glow flickers on in the thin gap between the thigh bone and the shin bone. 2.7-4s: the camera eases to a stop as the cartilage gap and the kneecap over it swell to full bright amber and pulse once, and they stay fully lit in bright amber until the very last frame; the thigh bone, the shin bone and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `근골격_*` 무릎 계열(무릎통증·관절염·반월판·장경인대)

### part_shoulder ⏱ 4초 [프레임: cu_shoulder.jpg 단독 — 신규]

**미드저니 (신규 스틸)**
```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A close-up of one translucent shoulder seen from the front at a slight three-quarter angle, from the base of the neck out to the upper arm, showing the ball of the upper arm bone sitting in the shallow socket of the shoulder blade, the collarbone above it, the rotator cuff tendons wrapping over the ball, and the trapezius and deltoid muscle fibres around the joint. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, face, facial features, full body, both shoulders
```

**Flow**
```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent shoulder stays completely still. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the shoulder framing, the ball of the upper arm bone in its shallow socket still the same soft pale cyan as the collarbone and the muscle fibres around it. 1.3-2.7s: the push-in continues until the joint fills the centre of the frame, and a faint warm amber glow flickers on in the tendons wrapping over the ball of the joint. 2.7-4s: the camera eases to a stop as the tendons and the rim of the socket swell to full bright amber and pulse once, and they stay fully lit in bright amber until the very last frame; the collarbone, the shoulder blade, the muscle fibres and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `근골격_*` 어깨·목 계열(오십견·회전근개파열·목어깨 결림·담 결림·거북목)

### part_muscle_whole ⏱ 4초 [프레임: canon_muscle_front.jpg 단독]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent figure stays completely still, standing upright with arms at the sides. The camera moves forward only a little, from the full-body framing to a head-to-knees framing, and never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward, the whole muscular system under the glass skin still uniformly soft pale cyan. 1.3-2.7s: the push-in continues and a faint warm amber glow flickers on in the thigh muscles, then spreads up through the abdominal wall, the chest and the shoulders. 2.7-4s: the camera eases to a stop as every large muscle group across the body swells to full bright amber together and pulses once, and they stay fully lit in bright amber until the very last frame; the glass skin and the dark slate blue-grey void stay unchanged. The face stays smooth and featureless. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `근골격_17`(근감소증)·`고령_2`·`고령_10`(노쇠)·`피로_*`

### part_skeleton ⏱ 4초 [프레임: canon_skeleton_front.jpg 단독]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent figure stays completely still, standing upright with arms at the sides. The camera moves forward only a little, from the full-body framing to a chest-to-knees framing, and never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward, the whole skeleton under the glass skin still uniformly soft pale cyan. 1.3-2.7s: the push-in continues until the spine, the pelvis and the thigh bones sit in the centre of the frame, and a faint warm amber glow flickers on inside the vertebrae of the lower spine and the neck of each thigh bone. 2.7-4s: the camera eases to a stop as the spine, the pelvis and the tops of both thigh bones swell to full bright amber and pulse once, and they stay fully lit in bright amber until the very last frame; the ribs, the arm bones, the skull and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. The face stays smooth and featureless. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `근골격_2`(골다공증)·`고령_3`(낙상)·`근골격_6`(통풍은 발가락 점등이면 part_foot)

---

## 피부 (27편)

### part_skin ⏱ 4초 [프레임: cu_skin_section.jpg 단독]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the block of tissue stays completely still. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the framing of the whole three-layer block of translucent skin, every layer still uniformly soft pale cyan. 1.3-2.7s: the push-in continues until the top two layers fill the frame, and a faint warm amber glow flickers on in the thin outermost layer and around the hair follicles and sweat glands under it. 2.7-4s: the camera eases to a stop as the outer layer and the follicles swell to full bright amber and pulse once, and they stay fully lit in bright amber until the very last frame; the thicker middle layer, the fatty layer beneath and the hairs standing out of the surface stay soft pale cyan, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `피부_*`(가려움·건조·여드름·땀·두드러기)·`냄새_*`(땀 냄새)·`고령_9`(욕창)

---

## 눈 (26편) · 미세먼지 일부

### part_eye ⏱ 4초 [프레임: cu_eye.jpg 단독]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent eyeball stays completely still, seen from the side with the optic nerve leaving the back. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the framing of the whole eyeball, the cornea, the lens and the retina lining the back still uniformly soft pale cyan. 1.3-2.7s: the push-in continues until the front half of the eye fills the frame, and a faint warm amber glow flickers on across the curved front surface of the cornea and around the rim of the lens. 2.7-4s: the camera eases to a stop as the cornea and the lens swell to full bright amber and pulse once, and they stay fully lit in bright amber until the very last frame; the vitreous body, the retina and the optic nerve stay soft pale cyan, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `눈_*`(안구건조·백내장·녹내장·비문증·눈피로)·`미세먼지_3`

---

## 여성 (24편)

### part_uterus_ovary ⏱ 4초 [프레임: cu_pelvis_female.jpg 단독]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent torso stays completely still. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the torso framing, the uterus low in the pelvis with an ovary and a fallopian tube on each side still the same soft pale cyan as the organs above them. 1.3-2.7s: the push-in continues until the pelvis fills the centre of the frame, and a faint warm amber glow flickers on inside the uterus. 2.7-4s: the camera eases to a stop as the uterus, both fallopian tubes and both ovaries swell to full bright amber and pulse once together, and they stay fully lit in bright amber until the very last frame; the kidneys, the intestines, the pelvic bones and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `여성_*`(생리통·자궁근종·다낭성난소·갱년기·질염)

---

## 코 (23편)

### part_nose_sinus ⏱ 4초 [프레임: cu_nose_sinus.jpg 단독 — 신규]

**미드저니 (신규 스틸)**
```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A close-up of a translucent mid-face seen from the front, from the eyebrows down to the upper lip, filling the frame, showing the two hollow air chambers above the eyebrows, the two larger hollow chambers in the cheeks beside the nose, the nasal cavity down the middle with the dividing wall and the curled shelves of bone on each side, and the narrow drainage openings between the cheek chambers and the nasal cavity. Smooth featureless face surface. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, side view, full body, full head
```

**Flow**
```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent face stays completely still. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the mid-face framing, the hollow air chambers above the eyebrows and in both cheeks still the same soft pale cyan as the nasal cavity between them. 1.3-2.7s: the push-in continues until the nose and both cheek chambers fill the centre of the frame, and a faint warm amber glow flickers on inside the nasal cavity and creeps into the drainage openings. 2.7-4s: the camera eases to a stop as the nasal cavity, both cheek chambers and both chambers above the eyebrows swell to full bright amber and pulse once together, and they stay fully lit in bright amber until the very last frame; the teeth, the eye sockets and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. The face stays smooth and featureless. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `코_*`(비염·축농증·후비루·코막힘·비강건조·후각저하)

---

## 순환 (22편) · 계절질환 일부

### part_heart ⏱ 4초 [프레임: cu_heart.jpg 단독 — 신규]

**미드저니 (신규 스틸)**
```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A close-up of a translucent chest seen from the front, from the collarbones down to the bottom of the ribs, filling the frame, showing the heart sitting slightly left of centre behind the breastbone with its four chambers and the valves between them visible through the wall, the large vessels arching out of the top of the heart, and the ribs and both lungs faint behind it. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, head, face, full body
```

**Flow**
```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent chest stays completely still. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the chest framing, the heart behind the breastbone still the same soft pale cyan as the ribs and the lungs behind it. 1.3-2.7s: the push-in continues until the heart fills the centre of the frame, and a faint warm amber glow flickers on inside its chambers in the rhythm of a heartbeat. 2.7-4s: the camera eases to a stop as the whole heart and the large vessels arching out of its top swell to full bright amber and pulse once, and the heart stays fully lit in bright amber until the very last frame; the ribs, the lungs and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `순환_*` 심장 계열(심방세동·협심증·심근경색·심부전·판막질환·부정맥·심계항진)

### part_vascular_whole ⏱ 4초 [프레임: canon_vascular_front.jpg 단독]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent figure stays completely still, standing upright with arms at the sides. The camera moves forward only a little, from the full-body framing to a head-to-knees framing, and never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward, the heart and the whole branching network of arteries and veins still uniformly soft pale cyan. 1.3-2.7s: the push-in continues and a faint warm amber glow flickers on inside the heart, then runs outward along the big vessels into both arms and down both legs. 2.7-4s: the camera eases to a stop as the entire vessel network from the heart to the fingertips and the feet swells to full bright amber and pulses once, and it stays fully lit in bright amber until the very last frame; the glass skin and the dark slate blue-grey void stay unchanged. The face stays smooth and featureless. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `순환_*` 혈류 계열(혈액순환·수족냉증·레이노·저혈압)·`계절질환_*`(온도차·자율신경)

### part_legs_veins ⏱ 4초 [프레임: cu_legs_veins.jpg 단독]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent legs stay completely still. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the framing of both legs, the branching veins running down to the feet still uniformly soft pale cyan. 1.3-2.7s: the push-in continues until both calves fill the centre of the frame, and a faint warm amber glow flickers on in the veins behind the knees and creeps downward. 2.7-4s: the camera eases to a stop as the veins from the knees down to the ankles swell to full bright amber, bulge slightly and pulse once, and they stay fully lit in bright amber until the very last frame; the calf muscles, the bones and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `순환_3`(하지정맥류)·`순환_14`(모세혈관확장증)·`손발_*`(다리 부종·쥐)·`계절질환_10`(열부종)

---

## 손발 (22편)

### part_hand ⏱ 4초 [프레임: cu_hand.jpg 단독]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent hand stays completely still, palm facing the camera with fingers slightly spread. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the framing of the whole hand and forearm, the finger bones, the wrist bones and the nerves running through the wrist still uniformly soft pale cyan. 1.3-2.7s: the push-in continues until the palm and the wrist fill the centre of the frame, and a faint warm amber glow flickers on in the narrow tunnel of the wrist where the nerves pass through. 2.7-4s: the camera eases to a stop as the wrist tunnel and the nerve branches running out into the thumb and the first three fingers swell to full bright amber and pulse once, and they stay fully lit in bright amber until the very last frame; the finger bones, the tendons and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `손발_*`(손저림·손목터널)·`근골격_8`·`근골격_20`·`근골격_21`

### part_foot ⏱ 4초 [프레임: cu_foot.jpg 단독]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent foot stays completely still, seen from the side. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the framing of the whole foot and ankle, the foot bones, the arch and the thick band of tissue along the sole still uniformly soft pale cyan. 1.3-2.7s: the push-in continues until the heel and the sole fill the centre of the frame, and a faint warm amber glow flickers on where the band of tissue along the sole meets the heel bone. 2.7-4s: the camera eases to a stop as the whole band along the sole, the heel bone and the base of the big toe swell to full bright amber and pulse once, and they stay fully lit in bright amber until the very last frame; the ankle joint, the other toe bones and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `손발_*`(발저림·무좀·발뒤꿈치)·`근골격_16`(족저근막염)·`근골격_6`(통풍)·`냄새_*`(발냄새)

### part_nerve_limbs ⏱ 4초 [프레임: canon_nervous_back.jpg 단독]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent figure stays completely still, seen from directly behind and standing upright. The camera moves forward only a little, from the full-body framing to a shoulders-to-knees framing, and never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward, the spinal cord and the nerves branching out of it still uniformly soft pale cyan. 1.3-2.7s: the push-in continues and a faint warm amber glow flickers on where the nerves leave the spine, then runs outward down both arms and down the back of both legs. 2.7-4s: the camera eases to a stop as the nerve endings in both hands and both feet swell to full bright amber and pulse once, and the whole nerve path from the spine to the fingers and toes stays fully lit in bright amber until the very last frame; the glass skin and the dark slate blue-grey void stay unchanged. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `손발_*`(손발저림)·`근골격_23`(좌골신경통)·`대사_9`(당뇨병성 말초신경병증)

---

## 대사 (22편) · 혈당 (14편)

### part_liver ⏱ 4초 [프레임: cu_liver_pancreas.jpg 단독 — 신규]

**미드저니 (신규 스틸)**
```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A close-up of a translucent upper abdomen seen from the front, from the bottom of the ribs down to the navel, filling the frame, showing the large wedge-shaped liver on the right side of the body under the ribs, the small pear-shaped gallbladder tucked under its lower edge, the stomach on the left side, and the long tapering pancreas lying across the body behind the stomach with its duct running along it. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, head, face, full body
```

**Flow**
```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent abdomen stays completely still. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the upper abdomen framing, the large wedge-shaped liver under the right ribs still the same soft pale cyan as the stomach and the pancreas beside it. 1.3-2.7s: the push-in continues until the liver fills the right half of the frame, and a faint warm amber glow flickers on inside it and spreads through its whole wedge. 2.7-4s: the camera eases to a stop as the liver and the small pear-shaped gallbladder under its lower edge swell to full bright amber and pulse once, and they stay fully lit in bright amber until the very last frame; the stomach, the pancreas, the ribs and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `대사_1`(지방간)·`대사_4`(고지혈증)·`대사_12`(중성지방)·`소화_13`(담석증)·`미세먼지_9`

### part_pancreas ⏱ 4초 [프레임: cu_liver_pancreas.jpg 단독 — 신규, part_liver와 같은 스틸]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent abdomen stays completely still. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the upper abdomen framing, the long tapering pancreas lying across the body behind the stomach still the same soft pale cyan as the liver and the stomach around it. 1.3-2.7s: the push-in continues until the pancreas lies across the centre of the frame, and a faint warm amber glow flickers on at its thick head and runs along it toward the tail. 2.7-4s: the camera eases to a stop as the whole pancreas and the duct running along it swell to full bright amber and pulse once, and they stay fully lit in bright amber until the very last frame; the liver, the gallbladder, the stomach and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `혈당_*`(혈당 스파이크·당뇨)·`대사_5`(인슐린저항성)·`대사_2`(췌장염)

### part_thyroid ⏱ 4초 [프레임: cu_neck_thyroid.jpg 단독]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent figure stays completely still. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the head-and-neck framing, the butterfly-shaped gland wrapped around the windpipe at the base of the neck still the same soft pale cyan as the windpipe and the collarbones. 1.3-2.7s: the push-in continues until the base of the neck and the top of the chest fill the frame, and a faint warm amber glow flickers on inside both wings of the gland. 2.7-4s: the camera eases to a stop as the whole butterfly-shaped gland swells to full bright amber and pulses once, and it stays fully lit in bright amber until the very last frame; the windpipe, the neck vessels, the collarbones, the lungs and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. The face stays smooth and featureless. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `대사_3`(갑상선기능저하)·`대사_15`(항진증)·`대사_11`(호르몬)

---

## 입 (20편) · 냄새 일부

### part_mouth_teeth ⏱ 4초 [프레임: cu_mouth.jpg 단독]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent jaw stays completely still, seen at a slight three-quarter angle. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the framing of the whole lower face, the upper and lower rows of teeth with their roots in the jawbone still uniformly soft pale cyan. 1.3-2.7s: the push-in continues until both rows of teeth fill the centre of the frame, and a faint warm amber glow flickers on along the gum line where the teeth meet the jawbone. 2.7-4s: the camera eases to a stop as the gum line and the roots of the lower teeth swell to full bright amber and pulse once, and they stay fully lit in bright amber until the very last frame; the tongue, the jaw joint and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `입_*` 치아·잇몸 계열(치주염·충치·시린이·턱관절)

### part_tongue_throat ⏱ 4초 [프레임: cu_mouth.jpg 단독 — part_mouth_teeth와 같은 스틸]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent jaw stays completely still, seen at a slight three-quarter angle. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the framing of the whole lower face, the tongue lying between the rows of teeth and the tonsils at the back of the mouth still uniformly soft pale cyan. 1.3-2.7s: the push-in continues until the open mouth fills the centre of the frame, and a faint warm amber glow flickers on across the upper surface of the tongue toward its back. 2.7-4s: the camera eases to a stop as the back of the tongue and both tonsils behind it swell to full bright amber and pulse once, and they stay fully lit in bright amber until the very last frame; the teeth, the jawbone and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `입_*` 혀·편도 계열(설태·편도결석·구내염)·`냄새_*`(구취)

---

## 수면 (20편) · 머리 (20편)

### part_brain ⏱ 4초 [프레임: cu_head_front.jpg 단독]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent head stays completely still, facing the camera. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the head-and-shoulders framing, the brain inside the skull still the same soft pale cyan as the eye sockets and the jaw below it. 1.3-2.7s: the push-in continues until the skull and the brain inside it fill the frame, and a faint warm amber glow flickers on deep in the middle of the brain. 2.7-4s: the camera eases to a stop as the whole brain swells to full bright amber and pulses once, and it stays fully lit in bright amber until the very last frame; the eyeballs, the nasal cavity, the teeth, the neck and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. The face stays smooth and featureless. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `수면_*`(불면·수면리듬)·`머리_*` 두통·인지 계열(긴장성두통·군발두통·브레인포그·기억력)·`미세먼지_7`

### part_scalp ⏱ 4초 [프레임: cu_scalp.jpg 단독 — 신규]

**미드저니 (신규 스틸)**
```
Medical holographic visualization, translucent glass-like 3D anatomy, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. An extreme close-up cross-section block of translucent scalp seen from the side at eye level, a hard pale bone plate as the bottom layer, a soft cushioning layer and a thick outer skin layer stacked above it, and about a dozen deep hair follicles set at a slant through those layers with a single hair growing up out of each one, each follicle wrapped in a tiny oil gland and one fine feeding vessel, the hairs standing up above the top surface into empty dark space. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, face, full head, full body, white layer, cream layer
```

**Flow**
```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the block of scalp stays completely still. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the framing of the whole cross-section block, the skull bone, the fatty layer, the skin layer and the slanted hair follicles through them still uniformly soft pale cyan. 1.3-2.7s: the push-in continues until three or four follicles fill the centre of the frame, and a faint warm amber glow flickers on around the root of each follicle and in the tiny oil gland beside it. 2.7-4s: the camera eases to a stop as every follicle root and oil gland across the block swells to full bright amber and pulses once together, and they stay fully lit in bright amber until the very last frame; the hairs standing above the surface, the skin layer, the fatty layer and the skull bone stay soft pale cyan, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `머리_*` 두피·탈모 계열(비듬·지루성두피염·모낭염·원형탈모·가을탈모·견인성탈모)

---

## 비뇨기 (20편)

### part_bladder ⏱ 4초 [프레임: cu_bladder.jpg 단독]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent torso stays completely still. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the torso framing, the rounded bladder low in the pelvis still the same soft pale cyan as the kidneys and the tubes coming down to it. 1.3-2.7s: the push-in continues until the pelvis fills the centre of the frame, and a faint warm amber glow flickers on inside the bladder and rises up its wall. 2.7-4s: the camera eases to a stop as the whole bladder swells to full bright amber and pulses once, and it stays fully lit in bright amber until the very last frame; the kidneys, the tubes, the intestines, the pelvic bones and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `비뇨기_*`(빈뇨·야간뇨·방광염·요실금·전립선)

### part_kidney ⏱ 4초 [프레임: canon_organs_back.jpg 단독]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent figure stays completely still, seen from directly behind and standing upright. The camera moves forward until the mid-back to hips region fills the frame, and never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the full-body rear framing, both kidneys on either side of the lower spine still the same soft pale cyan as the spine and the ribs. 1.3-2.7s: the push-in continues until both kidneys sit in the centre of the frame, and a faint warm amber glow flickers on inside each of them. 2.7-4s: the camera eases to a stop as both kidneys and the tubes running down from them swell to full bright amber and pulse once together, and they stay fully lit in bright amber until the very last frame; the spine, the ribs, the shoulder blades, the pelvis and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `비뇨기_*` 신장 계열(요로결석·신장기능·부종)·`계절질환_11`(횡문근융해증)·`미세먼지_9`

---

## 귀 (20편) · 어지럼증 (16편)

### part_ear_inner ⏱ 4초 [프레임: cu_ear.jpg 단독]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent ear stays completely still. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the framing of the whole ear, the ear canal, the eardrum, the tiny middle ear bones and the spiral cochlea still uniformly soft pale cyan. 1.3-2.7s: the push-in continues until the middle and inner ear fill the centre of the frame, and a faint warm amber glow flickers on at the eardrum and runs along the chain of tiny bones. 2.7-4s: the camera eases to a stop as the chain of tiny bones and the spiral cochlea behind them swell to full bright amber and pulse once, and they stay fully lit in bright amber until the very last frame; the outer ear, the ear canal and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `귀_*`(이명·난청·중이염·귀먹먹함)·`고령_4`(노인성 난청)

### part_vestibular ⏱ 4초 [프레임: cu_head_side.jpg 단독]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent head stays completely still in exact side profile. The camera never rolls, never tilts and never shakes — the horizon stays perfectly level for the whole shot. 0-1.3s: the camera starts moving slowly forward from the head-and-neck profile framing, the inner ear behind the jaw still the same soft pale cyan as the brain and the neck bones. 1.3-2.7s: the push-in continues until the area behind the jaw fills the centre of the frame, and a faint warm amber glow flickers on inside the three looping semicircular canals of the inner ear. 2.7-4s: the camera eases to a stop as all three loops and the spiral cochlea beside them swell to full bright amber and pulse once, and they stay fully lit in bright amber until the very last frame; the brain, the sinuses, the airway, the neck bones and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. The face stays smooth and featureless. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `어지럼증_*`(이석증·전정신경염·기립성 어지럼)·`귀_*`(이석증)

---

## 미세먼지 (12편) · 코골이

### part_lungs ⏱ 4초 [프레임: cu_lungs.jpg 단독 — 신규]

**미드저니 (신규 스틸)**
```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A close-up of a translucent chest seen from the front, from the base of the throat down to the bottom of the ribs, filling the frame, showing both lungs filling the rib cage, the windpipe coming down the middle and splitting into two main branches, the branching airway tree spreading through each lung down to fine twigs, and the heart faint between the lungs slightly left of centre. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, head, face, full body
```

**Flow**
```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent chest stays completely still. The camera never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward from the chest framing, both lungs and the branching airway tree inside them still uniformly soft pale cyan. 1.3-2.7s: the push-in continues until both lungs fill the frame, and a faint warm amber glow flickers on in the windpipe and runs down the two main branches into the airway tree. 2.7-4s: the camera eases to a stop as the whole branching airway tree out to its finest twigs in both lungs swells to full bright amber and pulses once, and it stays fully lit in bright amber until the very last frame; the lung tissue around the branches, the heart, the ribs and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `미세먼지_*`(호흡기 노출·실내공기·오존)·`코_3`(코골이·기도)·`고령_11`

---

## 계절질환 (13편) · 피로 (10편) — 전신

### part_whole_body ⏱ 4초 [프레임: canon_organs.jpg 단독]

```
One continuous axial push-in in a single unbroken scene with no scene cuts, eye-level, the camera travelling straight forward along the lens axis while the translucent figure stays completely still, standing upright with arms at the sides. The camera moves forward only a little, from the full-body framing to a head-to-knees framing, and never rolls, never tilts and never shakes. 0-1.3s: the camera starts moving slowly forward, every organ inside the glass body still uniformly soft pale cyan. 1.3-2.7s: the push-in continues and a faint warm amber glow flickers on deep in the core of the torso, around the stomach and the intestines, then spreads outward toward the chest and the pelvis. 2.7-4s: the camera eases to a stop as the whole core of the body glows full bright amber, spreading up into the head and down into the thighs, and pulses once, and it stays fully lit in bright amber until the very last frame; the bones, the arms, the lower legs and the glass skin stay soft pale cyan, the dark slate blue-grey void stays empty. The face stays smooth and featureless. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft low synth hum and one deep heartbeat thump as the glow pulses, no music, no dialogue.
```

쓰는 topic: `계절질환_*`(온열질환·열탈진·저체온증·탈수)·`피로_*`(만성피로·번아웃)·`고령_8`(탈수)

---

## 부위 → 스틸 대응표 (조립할 때 여기만 보면 됨)

| part | 프레임 | 신규 여부 |
|---|---|---|
| part_stomach | `cu_torso_organs.jpg` | 기존 |
| part_intestines | `cu_torso_organs.jpg` + region | 스틸 불필요(2026-09-20 코드 생성으로 확인) |
| part_esophagus | `cu_torso_organs.jpg` | 기존 |
| part_spine_lumbar | `cu_spine_lumbar.jpg` | 기존 |
| part_knee | `cu_knee.jpg` | 기존 |
| part_shoulder | `cu_shoulder.jpg` | **신규** |
| part_muscle_whole | `canon_muscle_front.jpg` | 기존 |
| part_skeleton | `canon_skeleton_front.jpg` | 기존 |
| part_skin | `cu_skin_section.jpg` | 기존 |
| part_eye | `cu_eye.jpg` | 기존 |
| part_uterus_ovary | `cu_pelvis_female.jpg` | 기존 |
| part_nose_sinus | `cu_nose_sinus.jpg` | **신규** |
| part_heart | `cu_heart.jpg` | **신규** |
| part_vascular_whole | `canon_vascular_front.jpg` | 기존 |
| part_legs_veins | `cu_legs_veins.jpg` | 기존 |
| part_hand | `cu_hand.jpg` | 기존 |
| part_foot | `cu_foot.jpg` | 기존 |
| part_nerve_limbs | `canon_nervous_back.jpg` | 기존 |
| part_liver | `cu_liver_pancreas.jpg` | **신규** |
| part_pancreas | `cu_liver_pancreas.jpg` | **신규**(같은 스틸) |
| part_thyroid | `cu_neck_thyroid.jpg` | 기존 |
| part_mouth_teeth | `cu_mouth.jpg` | 기존 |
| part_tongue_throat | `cu_mouth.jpg` | 기존(같은 스틸) |
| part_brain | `cu_head_front.jpg` | 기존 |
| part_scalp | `cu_scalp.jpg` | **신규** |
| part_bladder | `cu_bladder.jpg` | 기존 |
| part_kidney | `canon_organs_back.jpg` | 기존 |
| part_ear_inner | `cu_ear.jpg` | 기존 |
| part_vestibular | `cu_head_side.jpg` | 기존 |
| part_lungs | `cu_lungs.jpg` | **신규** |
| part_whole_body | `canon_organs.jpg` | 기존 |

저장 경로: 클립 `clips/part_<이름>.mp4`, 신규 스틸 `stills/<파일명>.jpg`(후보는 `stills/_candidates/<파일명>/`).
