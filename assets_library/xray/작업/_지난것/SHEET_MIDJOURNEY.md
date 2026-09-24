# 미드저니 147장 (2026-09-21)

**번호 = 파일 이름.** 결과 저장: 부위·기전(24~29, 71~170)은 `RENDER/<번호>_start.jpg`, **행위(30~70)는 끝 자세라 `RENDER/<번호>_end.jpg`**.

| 구간 | 무엇 | 장수 | Style Reference |
|---|---|---|---|
| 24~29 | 부위 클로즈업 스틸 | 6 | 넣음 |
| 30~70 | 행위 끝 자세 | 41 | 넣음 |
| 71~170 | 기전 시작 이미지 | 100 | 넣음 |

**전부 `stills/canon_organs.jpg`를 Style Reference로 넣는다**(Omni Reference는 금지 — 미시 장면에 전신 인체가 끼어든다). 유리 질감이 일정해진다.

---

## 24. cu_kidney

쓰는 topic 0편 · part_kidney·part_adrenal_gland 공용이고 part_urinary_tract(신장→요관→방광)까지 흡수. 전신 후면 canon_organs_back에선 신장이 다른 장기와 겹쳐 좌표로 못 가르므로 후면 클로즈업 전용 스틸로 뽑는다 — 겹침 방지로 --no에 intestines/liver/stomach를 넣었다.

```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A close-up of a translucent mid-back and lower abdomen seen from directly behind, from the bottom ribs down to the hips, filling the frame, showing both bean-shaped kidneys standing clearly apart on either side of the lumbar spine with their internal filtering structure visible through the wall, one small cap-shaped adrenal gland sitting on top of each kidney, one long narrow ureter leaving each kidney and running down to the rounded bladder low in the pelvis, and the lumbar spine, the bottom ribs and the pelvic bones faint behind them. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, head, face, full body, intestines, liver, stomach, organs overlapping the kidneys, front view
```

## 25. cu_nail

쓰는 topic 0편 · 손발_1·9·14·20·21 + 피부_23. cu_foot은 발 전체 점등이라 발톱이 주인공이 아니다. 조갑박리(m_layer_separation)·보우선(m_growth_arrest)이 이 스틸을 쓰므로 조갑상과 조모(성장 기질)가 반드시 따로 보여야 해서 둘 다 문장으로 못박았다.

```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. An extreme close-up of one single translucent toe seen at a three-quarter angle from above, the toe tip filling the frame, showing the hard flat nail plate covering the whole top of the toe tip with its thin stacked layers visible at the cut edge, the nail bed tissue directly beneath the plate with its fine lengthwise vessels running under it, the growth matrix tucked in under the fold of skin at the base of the nail, the fold of skin running around the sides of the plate, and the small toe bone beneath it all. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, full foot, full body, face, hand, fingers, nail polish, dirt, shoe
```

## 26. cu_eyelid

쓰는 topic 0편 · 눈_4·15·19·22. 기존 cu_eye는 안구 단면이고 프롬프트에 --no eyelashes가 박혀 있어 눈꺼풀을 못 쓴다 → 이 스틸은 반대로 속눈썹 뿌리를 명시하고 --no에서 eyelashes를 뺐다. 마이봄샘(기름샘) 줄이 주인공이라 다래끼·안검염 계열이 여기 붙는다.

```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. An extreme close-up cross-section of one upper and one lower translucent eyelid seen from the side, the two lids filling the frame and meeting almost closed, showing inside each lid a vertical row of about a dozen long narrow oil glands running from the lid margin up through the lid with their tiny openings along the margin, the row of lash roots set into the lid margin with short lashes growing out of them, the thin smooth membrane lining the inner face of each lid, and the band of muscle running through the lid; only a sliver of the eyeball surface is faintly visible behind the lids. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, face, full head, full body, makeup, mascara, eyeshadow, iris, pupil, skin pores
```

## 27. cu_lips

쓰는 topic 0편 · 입_16(구각염)·입_19(입술 헤르페스). cu_mouth 프롬프트에 --no lips가 박혀 있어 입술이 없는 스틸이라 대체 불가 → 여기선 입술이 주인공이고 입꼬리(구각)가 반드시 프레임 안에 들어가야 구각염 점등 위치를 가리킬 수 있다.

```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A close-up of a pair of translucent lips seen straight on from the front, the closed lips filling the frame with only the chin below them and a short stretch of upper lip skin above, showing the full thickness of both lips, the dense network of fine blood vessels packed just under the thin outer layer, the ring of muscle running all the way around the mouth beneath them, the sharp raised border line around the outer edge of the lips, and the two corners of the mouth; the teeth and gums are faint behind the closed lips. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, eyes, nose, full face, full head, full body, lipstick, makeup, open mouth, tongue, teeth showing
```

## 28. cu_elbow

쓰는 topic 0편 · 근골격_24·28. 테니스엘보(바깥쪽)와 골프엘보(안쪽) 구별이 콘텐츠의 핵심이라 두 부착부가 한 프레임에 또렷이 따로 보여야 한다 — 좌표로 안쪽/바깥쪽을 따로 점등시킬 것이므로 겹치면 못 쓴다. cu_hand는 손·손목까지라 대체 불가.

```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A close-up of one translucent elbow joint seen from the front at a slight angle, the upper arm entering the frame at the top and the forearm leaving at the bottom, the joint filling the frame, showing the lower end of the upper arm bone with its two rounded knobs standing out clearly, one on the inner side and one on the outer side, the two forearm bones meeting it, the joint capsule and the cartilage between the bones, and one thick tendon attachment fanning onto each of the two knobs with the forearm muscles running down away from them, the inner attachment and the outer attachment both clearly visible and clearly separate from each other. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, full body, face, hand, fingers, shoulder, machinery, robot joint
```

## 29. cu_breast_ducts

쓰는 topic 0편 · 여성_19(유선염). 라이브러리에 가슴 부위가 아예 없어 신규. 미드저니 세이프티 필터를 피하려고 breast 대신 해부 용어 mammary gland를 쓰고 젖꼭지는 central opening으로 표현했으며, --no에 nudity·torso silhouette을 넣었다. branching network가 진짜 나무로 나오는 사고 방지로 tree/plant/roots도 --no.

```
Medical holographic visualization, translucent glass-like 3D anatomy, the outer skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, floating in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. An extreme close-up cross-section of one translucent mammary gland seen from the front at a slight three-quarter angle, the gland filling the frame, showing the branching network of narrow milk ducts converging inward from the deep tissue toward one small central opening at the front of the gland, a cluster of small rounded lobules at the far end of every branch, the even fatty tissue faint between the branches, and the chest wall with two ribs faint behind it. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, face, full body, torso silhouette, nudity, skin texture, tree, plant, roots, coral
```

## 30. act_cover_ear — 한쪽 귀를 손바닥으로 덮어 누르고 고개를 기울인다

쓰는 topic 12편 · 소품: 없음. 귀 20편 공용 — 점등은 덮은 쪽 속귀 하나만.

```
A closely framed view, the top edge of the frame just above the top of the head and the bottom edge cutting across the hips, so that the legs and the feet are completely outside the frame and not visible anywhere in the image. Medical holographic visualization of a translucent glass-like 3D human body, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, centered with clear margins on both sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same body as the reference, seen from the front at eye level, now with one palm cupped flat over the whole of one ear and pressed hard against the side of the head, the fingers wrapped back around the skull above that ear, that elbow lifted out to the side at shoulder height, the head tilted far over toward the covering hand and the opposite shoulder dropped low, the free arm hanging straight down against the ribs. Visible inside: the brain, the inner ear and its spiral canals behind the jaw on the covered side, the ear canal, the jaw bone and the teeth, the neck vertebrae, the collarbones and the upper ribs, the hand and wrist bones of the covering hand. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, full body, whole figure, legs, feet
```

## 31. act_rub_eyes — 가렵거나 뻑뻑해서 두 손 또는 손가락 마디로 눈을 문지름

쓰는 topic 12편 · 소품: 없음. 손가락 마디로 눌러 비비는 자세라 손바닥으로 얼굴 전체를 덮는 act_cover_face와 화면이 갈린다.

```
A closely framed view, the top edge of the frame just above the top of the head and the bottom edge cutting across the hips, so that the legs and the feet are completely outside the frame and not visible anywhere in the image. Medical holographic visualization of a translucent glass-like 3D human body, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, centered with clear margins on both sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same body as the reference, seen from the front at eye level, now with both hands curled into loose fists and the flat middle joints of the fingers pressed into both eye sockets and screwed hard against them, both elbows lifted forward and drawn in close together in front of the chest, the head bowed down into the fists, the shoulders pulled up around the ears and the upper back rounded. Visible inside: the brain, both eyeballs deep in their sockets behind the pressing knuckles, the optic nerves running back from them, the sinuses and the nasal cavity, the teeth in the jaw, the finger and wrist bones of both hands, the collarbones and the upper ribs. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, full body, whole figure, legs, feet
```

## 32. act_check_skin — 옷·양말을 걷고 피부·손발톱 상태를 가까이 들여다봄

쓰는 topic 9편 · 소품: 없음. 캐논 인물은 옷이 없어 '양말을 걷는다'가 성립 안 함 — 바닥에 앉아 자기 발을 들어 들여다보는 자가점검 자세로 바꿨다.

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, sitting low in the lower half of the frame with open dark empty space above, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the front from slightly above eye level, now sitting on the floor with one leg stretched straight out along the ground and the other knee folded in toward the body, that outstretched foot lifted a little off the floor and cradled in both hands with the thumbs pressed into the sole and the fingers spread over the top of the foot, the back rounded, the shoulders drawn forward and the head bowed low and close over the foot as if peering at the skin of the toes. Visible inside: the brain, the spine curving from the neck to the pelvis, the lungs and heart, the stomach and coiled intestines, the pelvis, the leg bones, the small bones of the foot and the toes, and the fine branching vessels and nerves running down the leg and out into every toe. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features
```

## 33. act_clutch_chest — 선 자세에서 한 손 주먹으로 가슴 한복판(흉골 아래)을 누르며 상체를 살

쓰는 topic 9편 · 소품: 없음. 통증 위치가 가슴 한복판이라 점등도 흉골 뒤(하부 식도+심장)로 한정 — pilot_B의 배꼽 주변과 겹치지 않는다.

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, centered with clear margins on all sides, the figure filling about eighty-five percent of the frame height, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the front at eye level, standing with both feet flat on the floor side by side and both legs straight, now with one hand closed into a tight fist and pressed hard into the centre of the breastbone and the other hand clamped flat over that fist, both elbows drawn in tight against the ribs, the shoulders hunched forward and the chest caved in around the fist, the upper body bent slightly forward and the head dropped toward the hands. Visible inside: the heart behind the breastbone, both lungs, the windpipe and the oesophagus running down the middle of the chest behind the heart and into the stomach below, the rib cage and the breastbone, the collarbones, the spine, the liver and the stomach. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, walking, mid-stride, raised knee, lifted leg
```

## 34. act_grab_belly — 고개를 숙여 불룩한 배를 내려다보며 양손으로 뱃살을 잡아 쥔다

쓰는 topic 9편 · 소품: 없음. 통증 반응이 아니라 체형 확인이라 급격한 동작·굽힘 없이 시선만 내려간다(pilot_B와 톤 구분).

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, centered with clear margins on all sides, the figure filling about ninety percent of the frame height, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the front at eye level, standing with both feet flat on the floor side by side and both legs straight, now with the head bowed forward and tipped down so the face points straight at the belly, both hands reaching down and gripping the soft flesh at the front of the waist just above the hip bones, the fingers sunk in and pulling that flesh gently forward away from the body, both elbows flared out to the sides, the shoulders rounded and the chin tucked to the chest. Visible inside: the brain, the lungs and heart, the liver, the stomach and the coiled intestines, the thick layer of soft tissue lying over the front of the belly wall, the lower ribs, the spine and the pelvis, with the leg bones faintly visible. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, walking, mid-stride, raised knee, lifted leg
```

## 35. act_rub_nose — 코 옆을 손가락으로 문지르며 훌쩍이고 고개를 뒤로 젖힌다

쓰는 topic 9편 · 소품: 없음. 코 23편 공용 — 비강에서 부비동으로 번지는 점등 순서를 지킬 것.

```
A closely framed view, the top edge of the frame just above the top of the head and the bottom edge cutting across the hips, so that the legs and the feet are completely outside the frame and not visible anywhere in the image. Medical holographic visualization of a translucent glass-like 3D human body, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, centered with clear margins on both sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same body as the reference, seen from the front at eye level, now with the head tipped far back so the throat is stretched long and the chin points upward, one hand raised with the index finger and thumb pinching and rubbing hard along both sides of the bridge of the nose, that elbow lifted high out to the side, the other hand pressed flat against the base of the throat, the shoulders pulled up toward the ears. Visible inside: the nasal cavity and the passages behind it, the four sinus hollows in the forehead and cheekbones, the brain, the eye sockets, the teeth in the jaw, the throat and the windpipe running down the stretched neck, the neck vertebrae, the collarbones and the upper ribs. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, full body, whole figure, legs, feet
```

## 36. act_hold_cheek — 한쪽 볼을 손바닥으로 감싸 쥐고 인상을 쓴다(얼굴 한쪽이 이상할 때 포함

쓰는 topic 8편 · 소품: 없음. 점등을 한쪽 어금니→턱관절로 좁혀서 얼굴 전체를 덮는 act_cover_face와 읽힘을 분리.

```
A closely framed view, the top edge of the frame just above the top of the head and the bottom edge cutting across the hips, so that the legs and the feet are completely outside the frame and not visible anywhere in the image. Medical holographic visualization of a translucent glass-like 3D human body, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, centered with clear margins on both sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same body as the reference, seen from the front at eye level, now with one palm cupped hard over one whole cheek, the heel of that hand pressed under the jawbone and the fingers spread upward from the jawline to the temple, that elbow tucked down against the ribs, the head tilted over and sunk into the cupping hand, the opposite arm folded across the chest with that hand gripping the elbow of the cupping arm, the shoulders hunched up. Visible inside: the lower jaw bone and the full row of molars in it on the cupped side, the jaw joint just in front of the ear, the upper teeth, the sinus hollow in that cheekbone, the brain, the neck vertebrae, the collarbones and the upper ribs, the hand and finger bones of the cupping hand. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, full body, whole figure, legs, feet
```

## 37. act_scratch_skin — 팔뚝·목을 손톱으로 긁다가 멈추고 붉어진 자리를 들여다본다

쓰는 topic 8편 · 소품: 없음. 붉어진 자리는 --no에 red가 있어 색으로 못 쓴다 — 유리 피부가 뿌옇게 흐려지는 질감 변화로 대체했다.

```
A closely framed view, the top edge of the frame just above the top of the head and the bottom edge cutting across the hips, so that the legs and the feet are completely outside the frame and not visible anywhere in the image. Medical holographic visualization of a translucent glass-like 3D human body, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, centered with clear margins on both sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same body as the reference, seen from the front at eye level, now with one forearm lifted and held up horizontally across the chest with the inner side turned upward, the other hand hovering just above it with the fingers still hooked into claws, the head bowed down and forward and tipped close over the lifted forearm as if studying one patch of it, the shoulders rounded, and on that patch the thin glass shell of the skin clouded into a denser frosted texture where it has been raked. Visible inside: the layer of skin itself as a distinct thin outer shell over the forearm and the side of the neck, the fine vessels and nerve endings branching just beneath that surface, the arm bones and the tendons running into the fingers, the collarbones and the upper ribs, the lungs faintly visible behind. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, full body, whole figure, legs, feet
```

## 38. act_sniff_self — 어깨 쪽 옷깃을 당겨 코를 묻고 냄새를 맡다가 굳는다

쓰는 topic 8편 · 소품: 없음. 캐논 인물은 옷이 없어 '옷깃을 당긴다'가 성립 안 함 — 어깨를 끌어올려 코를 묻는 자세로 바꿨다. '굳는다'는 마지막 비트의 완전 정지로 표현.

```
A closely framed view, the top edge of the frame just above the top of the head and the bottom edge cutting across the hips, so that the legs and the feet are completely outside the frame and not visible anywhere in the image. Medical holographic visualization of a translucent glass-like 3D human body, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, centered with clear margins on both sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same body as the reference, seen from a three-quarter angle turned toward its own left side at eye level, now with one shoulder hitched up high toward the face and the head turned down and buried into the front of that raised shoulder so the nose presses against the upper arm, that arm bent and folded across the chest with the hand gripping the opposite ribs, the other arm hanging straight down, the whole upper body frozen mid-turn with the back slightly rounded. Visible inside: the nasal cavity and the passages behind it, the sinus hollows, the brain, the jaw and the teeth, the shoulder joint and the upper arm bone pressed against the face, the collarbones, the rib cage, the lungs and the heart. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, full body, whole figure, legs, feet
```

## 39. act_take_supplement — 보충제 파우더를 물에 타 마시거나 영양제를 한 줌 삼키는 모습

쓰는 topic 6편 · 소품: 청록 반투명 유리 텀블러 1개 + 캡슐 3알(같은 재질, 무표시). 점등은 위→신장 순서로 옮겨가야 비뇨기 topic에서 맞는다.

```
A closely framed view, the top edge of the frame just above the top of the head and the bottom edge cutting across the hips, so that the legs and the feet are completely outside the frame and not visible anywhere in the image. Medical holographic visualization of a translucent glass-like 3D human body, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, centered with clear margins on both sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same body as the reference, seen from the front at eye level, now with the head tipped back and one hand raising a plain straight-sided tumbler to the mouth, the tumbler shaped from the same translucent pale cyan glass as the body and left as a bare simple form with no markings, no pattern and no brand of any kind, that elbow lifted high, the other hand lowered to chest height with the palm open and empty, the throat stretched long, and three small smooth capsule shapes of the same pale cyan glass visible inside the body partway down the oesophagus behind the breastbone. Visible inside: the mouth cavity and the teeth in the jaw, the throat and the oesophagus running down behind the breastbone with the three capsule shapes inside it, the windpipe beside it, the lungs and heart, the stomach below, both kidneys low at the back, the rib cage and the neck vertebrae. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, full body, whole figure, legs, feet
```

## 40. act_cough — 주먹으로 입을 막고 몸이 앞으로 꺾이도록 기침한다(사레 들려 목을 감싸 

쓰는 topic 5편 · 소품: 없음. 사레 들린 경우까지 이 클립 하나로 커버(빈 void라 식탁 유무로 화면이 갈리지 않음).

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, centered with clear margins on all sides, the figure filling about ninety percent of the frame height, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the front at eye level, now jackknifed forward from the waist mid-cough: one hand closed into a fist and pressed hard against the mouth with that elbow lifted high and forward, the other forearm wrapped tight across the belly bracing it, the upper back rounded hard, the head thrust down and forward ahead of the shoulders, the chest squeezed in, both knees slightly bent with both feet flat on the floor side by side. Visible inside: the windpipe running down the neck, the two main airways branching from it into both lungs, both lungs squeezed narrow, the heart, the dome of the diaphragm pushed upward, the rib cage crowded together, the spine curved forward, the jaw and the teeth, the hand bones of the fist. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, walking, mid-stride, raised knee, lifted leg
```

## 41. act_hold_head — 한쪽 관자놀이나 눈 주위를 손으로 감싸 쥐고 찡그리는 모습

쓰는 topic 5편 · 소품: 없음. 편측성이 핵심이라 뇌의 한쪽 반구만 켜지고 반대쪽은 청록으로 남아야 한다 — 두 발은 붙박아 두고 카메라만 들어간다(pilot_C의 휘청임과 구분).

```
A closely framed view, the top edge of the frame just above the top of the head and the bottom edge cutting across the hips, so that the legs and the feet are completely outside the frame and not visible anywhere in the image. Medical holographic visualization of a translucent glass-like 3D human body, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, centered with clear margins on both sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same body as the reference, seen from the front at eye level, standing upright and still, now with the heel of one hand pressed hard into the temple above and in front of one ear and the fingers of that hand curled over and dug into the side of the skull, that elbow lifted out and forward, the head tilted over into that hand and pulled down toward that shoulder, the other arm folded across the chest with that hand clamped around the opposite upper arm, both shoulders drawn up and forward. Visible inside: the brain with the whole half nearest the pressing hand clearly separated from the other half, the branching blood vessels running across the surface of that half and down through the temple, the skull, both eye sockets, the sinus hollows, the jaw and the teeth, the neck vertebrae and the collarbones. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, full body, whole figure, legs, feet
```

## 42. act_limp — 한쪽 발을 아껴 디디며 절뚝이며 걸음

쓰는 topic 5편 · 소품: 없음. 이동 방향은 act_rush_to_toilet과 같은 좌→우(180도 규칙) — 비대칭 보행이 핵심이라 두 발이 같은 리듬으로 움직이면 실패.

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, the figure filling about eighty-five percent of the frame height, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference at the same size, now placed in the right third of the frame and caught in a heavy uneven step moving toward frame right: the leading leg planted flat and straight with the whole sole down and the body stacked over it, the other leg trailing far behind with the knee half bent and only the toes brushing the floor, the hips dropped and twisted away from that trailing leg, the torso leaning sideways over the planted leg, one hand reaching down and laid flat on the thigh of the trailing leg, the other arm swung out wide for balance, the head level and facing the direction of travel. Visible inside: the knee joint and the ankle of the trailing leg, both thigh bones and shin bones, the pelvis tilted, the spine leaning with the torso, the lungs and heart, the coiled intestines, the bones of both feet. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features
```

## 43. act_hair_shedding — 정수리에서 머리카락을 쓸어내리거나 빗질한 뒤 손·빗에 머리카락이 한 움큼

쓰는 topic 4편 · 소품: 없음(빗 생략 — 손으로 쓸어내려도 화면이 같고, 빗을 넣으면 소품에 시선이 뺏긴다). ⚠️ 캐논 인물은 머리카락이 없으므로 미드저니 프롬프트가 유리 재질 머리카락을 새로 지정한다 — 결과물에 모발이 안 나오면 재생성할 것.

```
A closely framed view, the top edge of the frame just above the raised hand and the top of the head and the bottom edge cutting across the chest just below the collarbones, so that the waist, the legs and the feet are completely outside the frame and not visible anywhere in the image. Medical holographic visualization of a translucent glass-like 3D human body, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, centered with clear margins on both sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same body as the reference, seen from the front from slightly above eye level, the crown of the head covered with fine hair strands drawn as thin threads of the same pale cyan glass as the body, now with one hand held out in front of the face at eye height with the fingers spread wide and a loose tangled clump of those glass hair strands caught between the fingers and hanging down from them, the other hand still resting flat on the crown of the head, the head bowed forward and tipped down so it is aimed straight at the clump in the raised hand, the shoulders drawn forward. Visible inside: the scalp as a distinct thin layer over the skull with a thinned row of hair roots set into it across the crown, the skull beneath it, the brain, the eye sockets, the jaw, the neck vertebrae and the collarbones, the hand and finger bones of both hands. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, full body, whole figure, legs, feet
```

## 44. act_slump_at_desk — 책상 앞에서 어깨가 무너지듯 엎드리거나 모니터를 멍하니 보는 모습

쓰는 topic 4편 · 소품: 청록 반투명 유리 책상 + 모니터 슬래브 + 등받이 없는 스툴(동작 성립에 필수). 화면엔 아무것도 띄우지 않는다(--no에 screen content 추가) — 글자가 읽히면 캐논 위반.

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, the whole figure and the desk visible with clear margins on all sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from a slight angle from the front at eye level, now seated on a plain backless stool at a plain rectangular desk with a thin flat upright screen standing on it, the stool, the desk and the screen all shaped from the same translucent pale cyan glass as the body and left as bare simple forms with no legs detail, no buttons, no markings, no pattern and no brand of any kind, the upper body slumped forward down onto the desktop with both forearms folded flat on it, the head laid down sideways on those forearms, the back curved into a long slack arc, the shoulders rounded up around the ears and both legs slumped loose under the desk with the feet flat on the floor. Visible inside: the brain, the spine curving in one long slack arc from the skull to the pelvis, the lungs and heart, the stomach and the coiled intestines, the pelvis and the leg bones, the arm bones folded on the desktop. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, screen image, screen content, keyboard
```

## 45. act_phone_in_bed — 불 끈 침실에서 이불 속에 누워 스마트폰 화면 불빛을 얼굴에 받는 모습

쓰는 topic 3편 · 소품: 청록 반투명 유리 슬래브 1개(스마트폰, 무표시·무발광). 화면 불빛은 슬래브를 빛나게 하는 대신 눈→뇌 점등으로 표현한다 — 액정에 뭔가 뜨면 캐논 위반.

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, centered with clear margins on all sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, now lying flat on its back on an unseen flat surface and seen from a high three-quarter angle above and beyond its head looking down along the body, both arms bent at the elbows and raised so that both hands hold a small thin flat rectangular slab horizontally about a forearm's length above the face, the slab shaped from the same translucent pale cyan glass as the body and left as a bare blank form with no buttons, no markings, no pattern and no brand of any kind, the head tipped slightly forward off the surface toward the slab, the chin tucked, both legs stretched out straight with the feet turned outward. Visible inside: the brain with its deep centre, both eyeballs in their sockets aimed up at the slab, the optic nerves running back from them into the brain, the neck vertebrae, the lungs and heart, the stomach and coiled intestines, the pelvis and the leg bones. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, screen image, screen content
```

## 46. act_rub_neck — 고개를 천천히 돌리며 뒷목과 승모근을 손으로 주무름

쓰는 topic 3편 · 소품: 없음. 목을 한 바퀴 돌리는 0~1.5초가 있어야 '목·어깨'로 읽힌다 — 바로 주무르기부터 시작하면 act_rub_hands와 손 모양이 겹친다.

```
A closely framed view, the top edge of the frame just above the top of the head and the bottom edge cutting across the hips, so that the legs and the feet are completely outside the frame and not visible anywhere in the image. Medical holographic visualization of a translucent glass-like 3D human body, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, centered with clear margins on both sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same body as the reference, seen from the front from slightly above eye level, now with the head dropped forward and rolled over toward one shoulder, one hand clamped over the back of the neck with the fingers dug deep into the thick muscle on one side and the thumb pressed into the other side, that elbow pointing forward and up above the shoulder, the other arm hanging straight down, both shoulders hunched up hard toward the ears and the upper back rounded. Visible inside: the seven neck vertebrae stacked and bent into a forward curve, the thick bands of muscle running from the base of the skull down across both shoulders, the base of the skull, the brain, the shoulder blades, the collarbones and the upper ribs, the hand and finger bones of the clamping hand. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, full body, whole figure, legs, feet
```

## 47. act_shift_uncomfortably_seated — 의자에 앉은 채 허벅지를 모았다 벌렸다 하며 자꾸 자세를 고쳐 앉고, 한

쓰는 topic 3편 · 소품: 청록 반투명 유리 스툴(등받이 없음 — 앉은 자세가 성립하려면 필수). 다리를 벌렸다 모으는 묘사는 심의 위험이라 '무릎은 붙인 채 엉덩이를 좌우로 고쳐 앉는다'로 바꿨다 — 안절부절 리듬은 그대로 읽힌다.

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, the whole seated figure visible from the top of the head to the feet, centered with clear margins on all sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the front at eye level, now seated upright on a plain backless stool shaped from the same translucent pale cyan glass as the body and left as a bare simple form with no markings, no pattern and no brand of any kind, both knees pressed tightly together and angled off to one side with both feet flat on the floor, the hips twisted so the weight rests on one side of the seat, the torso leaning away over the opposite arm whose hand is braced flat on the stool beside the thigh, the other hand laid flat low across the lower belly below the navel, both shoulders raised and the head turned down and away. Visible inside: the pelvis and both hip joints, the lower spine, the bladder low inside the pelvis, the coiled intestines above it, the large intestine framing them, the thigh bones angled to one side, the rib cage, the lungs and heart. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features
```

## 48. act_snore — 똑바로 누워 입을 벌린 채 코를 골고, 옆사람이 등을 돌려 귀를 막는 모

쓰는 topic 3편 · 소품: 없음(바닥은 act_toss_turn과 같은 '보이지 않는 평면'). ⚠️ 옆사람이 귀를 막는 컷은 뺐다 — 캐논은 단일 인물이고 이목구비가 없어 두 번째 인물이 화면을 흐린다. 대신 혀가 뒤로 넘어가며 좁아지는 기도 점등으로 코골이를 보여준다.

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, centered with clear margins on all sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, now lying flat on its back on an unseen flat surface and seen from a low three-quarter angle close to the surface beside its head, the chin tipped far up and the head rolled back so the throat is stretched long and open, the jaw bone hanging open inside the glass head, both arms lying loose and slightly away from the sides with the palms up, the chest lifted high and the belly sunken, both legs stretched straight with the feet turned outward. Visible inside: the nasal cavity, the mouth cavity and the tongue fallen back toward the throat, the airway running from the nose and mouth down the stretched neck into the windpipe with the soft tissue at the back of the throat sagging inward and pinching it narrow, the jaw bone and the teeth, the neck vertebrae, both lungs, the heart, the rib cage and the dome of the diaphragm. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features
```

## 49. act_strain_on_toilet — 변기에 앉아 상체를 앞으로 숙이고 양 무릎에 팔꿈치를 괸 채 배에 힘을 

쓰는 topic 3편 · 소품: 청록 반투명 유리 변기(형태만, 물탱크·뚜껑 디테일 없음 — 앉아서 힘주는 동작이 성립하려면 필수). 미드저니 심의를 피하려고 전신 구도 + 상체를 깊게 숙인 자세로 골반이 화면을 채우지 않게 했다.

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, the whole seated figure visible from the top of the head to the feet, centered with clear margins on all sides, the figure filling about eighty percent of the frame height, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the front at eye level, now seated on a plain simple toilet form shaped from the same translucent pale cyan glass as the body and left as a bare rounded shape with no tank details, no lid details, no markings and no brand of any kind, both feet flat on the floor and both knees apart at shoulder width, the upper body folded far forward over the thighs with both elbows planted on the knees and both hands clasped together in front, the back rounded into a deep hunch, the shoulders pushed up around the ears, the head dropped low between the arms and the belly compressed hard against the thighs. Visible inside: the coiled small intestine pressed together, the large intestine framing it with its lower stretch curving down low into the pelvis, the pelvis, the lower spine curved into a deep hunch, the thigh bones, the lungs and heart held high in the compressed chest, the dome of the diaphragm pushed down. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features
```

## 50. act_touch_neck — 목 앞 가운데를 손끝으로 눌러 만져보며 침을 삼킨다

쓰는 topic 3편 · 소품 없음

```
A close view framed from just above the top of the head down to the middle of the chest, so that the hips, the legs and the feet are completely outside the frame and not visible anywhere in the image. Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, centered with clear margins on both sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the front at eye level, the chin lifted and the head tipped back a little so the front of the neck is stretched open, now with the fingertips of one hand pressed into the hollow at the front of the base of the neck just below the voice box, the thumb laid along one side of the windpipe and the three fingertips along the other side, that elbow lifted out to the side, the other arm hanging relaxed, the throat drawn upward in mid-swallow. Visible inside: the butterfly-shaped thyroid gland wrapped around the front of the windpipe below the voice box, the windpipe and the food pipe behind it, the jaw and the teeth, the neck vertebrae, the collarbones and the upper ribs, with the brain faintly visible above. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, full body, whole figure, legs, feet
```

## 51. act_doze_off_sitting — 앉은 자세에서 고개가 툭 꺾이며 순간적으로 잠드는 모습

쓰는 topic 2편 · 소품: 등받이 없는 스툴(같은 청록 반투명 유리, 무늬·글자 없음)

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, centered with clear margins on all sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from a shallow three-quarter angle at eye level, now seated on a plain backless stool made of the same translucent pale cyan glass with no markings anywhere on it, both feet flat on the floor and the knees bent square, both hands lying loose palm-down on the thighs, the shoulders slumped forward and rounded, the spine sagging into a long C-curve, the head dropped forward and over to one side so the chin has sunk toward the collarbone. Visible inside: the brain, the neck vertebrae and the spine curving through the whole torso, the lungs and heart, the stomach and coiled intestines, the pelvis and the leg bones. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features
```

## 52. act_drink_caffeine — 지친 얼굴로 커피·에너지드링크·밀크티를 들이키는 모습

쓰는 topic 2편 · 소품: 원통형 컵(같은 청록 반투명 유리, 상표·글자 없음)

```
A close view framed from the top of the head down to the hips, so that the knees and the feet are completely outside the frame and not visible anywhere in the image. Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, centered with clear margins on both sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the front at eye level, the shoulders slack and pulled forward, now holding a plain smooth cylindrical cup made of the same translucent pale cyan glass with no handle markings and no lettering on it, one hand wrapped around the cup and tipping it steeply against the lower face, the other hand cupped underneath it, both elbows lifted, the head tilted back and the throat stretched open and drawn up in a long swallow. Visible inside: the brain, the throat and the food pipe running down behind the breastbone, the windpipe, the neck vertebrae, the collarbones and the rib cage, the heart and lungs, and the stomach under the left ribs. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, full body, whole figure, legs, feet
```

## 53. act_gasp_for_breath — 계단 중간에 멈춰 서서 난간을 짚고 어깨를 들썩이며 숨을 몰아쉼

쓰는 topic 2편 · 소품: 짧은 계단 + 곧은 난간(같은 청록 반투명 유리, 무늬·글자 없음)

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, the figure filling about eighty-five percent of the frame height, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the side at eye level, now stopped halfway up a short plain flight of steps made of the same translucent pale cyan glass with a simple straight handrail of the same glass and no markings anywhere on either, one foot planted on a higher step and the other left behind on a lower one, one hand clamped around the handrail with the arm locked straight and taking the weight, the other hand braced flat on the thigh of the forward leg, the torso pitched forward over that leg, the shoulders hiked up high around the ears and the head dropped between them, the chest visibly expanded. Visible inside: both lungs filling the rib cage, the heart between them, the windpipe and the branching airways, the ribs and the collarbones, the spine, the pelvis and the leg bones. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features
```

## 54. act_hold_elbow — 반대 손으로 팔꿈치를 감싸 쥐고 찡그림

쓰는 topic 2편 · 소품 없음

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, centered with clear margins on all sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the front at eye level, standing upright with both feet flat on the floor side by side and both legs straight, now with one arm bent tight and held in across the front of the body, that forearm pressed against the ribs and the hand curled into a loose fist, while the opposite hand reaches across and clamps over the bent elbow from the outside, the fingers wrapped right around the point of the elbow and the thumb dug into the crease below it, the shoulder on the held side hitched up and rolled inward, the head tipped down and over toward that arm, the torso twisted slightly away. Visible inside: the upper arm bone meeting the two forearm bones at the elbow joint, the tendons crossing that joint and running down into the hand, the nerve passing behind the elbow, the shoulder joint and the collarbones, the rib cage with the lungs and heart behind it, and the spine. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, walking, mid-stride, raised knee, lifted leg
```

## 55. act_press_one_side_lower_abdomen — 선 채로 한 손만 한쪽 아랫배에 대고 눌러 그 방향으로 상체를 살짝 기울

쓰는 topic 2편 · 소품 없음

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, centered with clear margins on all sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the front at eye level, standing with both feet flat on the floor side by side and both legs straight, now with only one hand pressed flat and deep into one side of the lower belly well below the navel, the fingers pointing down and inward and clearly off to that side of the midline, that elbow pinned tight against the ribs, the whole upper body leaning over toward the same side and folding slightly forward above the pressing hand, the opposite shoulder lifted and the free arm hanging away from the body, the head tipped down toward the pressing hand, the breath held. Visible inside: the stomach under the left ribs, the coiled small intestine, the large intestine framing it, the lower half of the coils crowding into the side of the pelvis where the hand presses, the bladder low in the pelvis, the lumbar spine and the pelvis. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, both hands on belly, symmetrical pose, walking, mid-stride, raised knee, lifted leg
```

## 56. act_scalp_care — 두피에 샴푸·오일을 덜어 손끝으로 마사지하듯 바르는 모습

쓰는 topic 2편 · 소품: 작은 병(같은 청록 반투명 유리, 라벨·글자 없음)

```
A close view framed from just above the top of the head down to the middle of the chest, so that the hips, the legs and the feet are completely outside the frame and not visible anywhere in the image. Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, centered with clear margins on both sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the front from slightly above eye level, the head bowed forward so the top of the scalp faces the camera, now with both hands raised onto the crown of the head, the fingers hooked and the fingertips of both hands pressed down into the scalp and spread apart over it, both elbows lifted wide and high to the sides, one small plain unlabelled bottle of the same translucent pale cyan glass held upright in the crook of one hand against the head. Visible inside: the brain under the skull, the skull bones, the layer of scalp over them with the roots of the hair follicles set into it, the network of fine vessels running across the scalp, the jaw and the teeth, the neck vertebrae and the collarbones. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, full body, whole figure, legs, feet
```

## 57. act_scratch_scalp — 손가락으로 두피를 벅벅 긁고 어깨에 흰 각질이 떨어지는 모습

쓰는 topic 2편 · 소품 없음(떨어지는 각질은 같은 청록 유리 조각으로 표현)

```
A close view framed from just above the top of the head down to the middle of the chest, so that the hips, the legs and the feet are completely outside the frame and not visible anywhere in the image. Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, centered with clear margins on both sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from a shallow three-quarter angle at eye level, the head tipped down and over to one side, now with one hand driven up into the side and back of the scalp above the ear, the fingers clawed hard with the fingertips dug in and dragging through the scalp, that elbow raised high above the shoulder, the other arm hanging down, and a scattering of tiny thin flakes of the same pale cyan glass breaking loose from the scalp and drifting down through the air onto the shoulder below. Visible inside: the skull bones and the brain under them, the layer of scalp over the skull with the roots of the hair follicles set into it, the outer ear and the jaw, the neck vertebrae, the shoulder joint and the collarbones. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, full body, whole figure, legs, feet
```

## 58. act_shield_eyes_from_light — 눈부셔서 손을 이마에 대 차양을 만들고 눈을 가늘게 뜸

쓰는 topic 2편 · 소품 없음

```
A close view framed from just above the top of the head down to the waist, so that the hips, the legs and the feet are completely outside the frame and not visible anywhere in the image. Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, centered with clear margins on both sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the front from slightly below eye level looking up, now with one hand held flat and edge-on above the brow like a visor, the palm turned down and the fingers pressed together and angled out over the forehead, that elbow raised to shoulder height and pushed forward, the head pulled back and turned a little away, the chin tucked down, the opposite shoulder hunched up toward the ear and the free arm crossing low in front of the body. Visible inside: both eyeballs in their sockets with the optic nerves running back from them into the brain, the brain, the sinuses and the nasal cavity, the skull and the teeth in the jaw, the hand and wrist bones of the raised hand, the collarbones and the upper ribs. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, full body, whole figure, legs, feet
```

## 59. act_sleep_paralysis — 누운 채 눈만 번쩍 떠지고 몸은 굳어 손끝 하나 못 움직이는 모습

쓰는 topic 2편 · 소품 없음

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, centered with clear margins on all sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, now lying flat on its back on an unseen flat surface and seen from high above and a little to one side looking down along the length of the body, rigid and perfectly straight: both arms locked straight down at the sides with the palms turned down and the fingers stiffly splayed apart, both legs straight and pressed together with the feet upright side by side, the shoulders flat, the spine dead straight, the chin pulled in and the head pressed back into the surface, the whole body held absolutely still. Visible inside: the brain and the brainstem running down into the top of the spine, the spine straight through the whole body, the lungs and heart, the stomach and coiled intestines, the pelvis and the leg bones, with the full skeleton faintly visible. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, curled up, bent knees, rolled onto side
```

## 60. act_slow_walk — 보폭이 짧고 느리게, 벽·가구를 짚으며 걸음

쓰는 topic 2편 · 소품: 곧은 벽 패널(같은 청록 반투명 유리, 무늬·글자 없음)

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, the figure filling about eighty-five percent of the frame height, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the side at eye level, now taking a very short shuffling step along a plain flat upright wall panel made of the same translucent pale cyan glass running down one edge of the frame with no markings anywhere on it, one flat hand pressed against that panel at shoulder height taking part of the weight and the arm bent, the leading foot set down only a little ahead of the trailing one with both soles staying low and close to the floor, the knees barely bent, the torso stooped forward and the shoulders rounded, the head pushed forward ahead of the chest, the free arm hanging almost still at the side. Visible inside: the brain, the spine curving from the neck down to the pelvis, the lungs and heart, the stomach and coiled intestines, the pelvis, the hip joints, the thigh and calf muscles and the leg bones down to the feet. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, running, long stride, raised knee, high step
```

## 61. act_squint_at_screen — 스마트폰을 얼굴 앞으로 바짝 당겨 고개를 내민 채 찡그리며 봄

쓰는 topic 2편 · 소품: 손바닥 크기 납작한 판(스마트폰 대용, 같은 청록 반투명 유리, 화면 이미지·아이콘·글자 없음)

```
A close view framed from just above the top of the head down to the waist, so that the hips, the legs and the feet are completely outside the frame and not visible anywhere in the image. Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, centered with clear margins on both sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from a shallow three-quarter angle at eye level, now holding a plain flat rectangular slab the size of a hand made of the same translucent pale cyan glass, completely blank with no screen image, no icons and no markings on it, gripped in one hand and drawn in close in front of the face barely a hand-span away, that elbow tucked hard against the ribs, the head craned forward ahead of the shoulders so the neck juts out at an angle, the chin pushed out, the brow pressed down toward the slab, both shoulders hunched up and rolled inward. Visible inside: both eyeballs in their sockets with the small ring of focusing muscle around each lens and the optic nerves running back into the brain, the brain, the neck vertebrae strained forward out of line with the spine below, the jaw and the teeth, the collarbones and the upper ribs. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, screen image, icons, full body, whole figure, legs, feet
```

## 62. act_stand_still_unaware — 반투명 인체가 정면으로 편하게 가만히 서 있고, 몸속 한 지점만 조용히 

쓰는 topic 2편 · 소품 없음

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, centered with clear margins on all sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the front at eye level, standing completely relaxed and at ease with both feet flat on the floor a shoulder-width apart and both legs straight, both arms hanging loose and easy at the sides with the fingers slightly curled, the shoulders level and dropped, the chest open, the spine upright and comfortable, the head level and facing straight ahead, the whole body calm and entirely untroubled, nothing held, nothing touched, no hand anywhere on the body. Visible inside: the brain, the lungs and heart, the liver, the stomach and the coiled intestines, the kidneys, the bladder and the small organs low in the pelvis behind it, with the full skeleton faintly visible. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, hands on body, clutching, hunching, grimacing, bent posture, walking, mid-stride
```

## 63. act_toilet_check — 화장실에서 물 내리기 전 변기 안을 내려다보며 색을 확인하는 모습

쓰는 topic 2편 · 소품: 변기(같은 청록 반투명 유리, 무늬·글자 없음)

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, the figure filling about eighty-five percent of the frame height, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from a shallow three-quarter angle at eye level, now standing squarely over a plain simple toilet bowl with a closed lid-less rim made of the same translucent pale cyan glass with no markings anywhere on it, both feet flat on the floor beside it, the body hinged forward from the hips and the head bowed low so the face is turned straight down into the bowl, one hand braced flat on the rim and the other resting on the thigh, the shoulders rounded and pushed forward, the knees very slightly bent. Visible inside: both kidneys on either side of the lumbar spine with the two narrow tubes running down from them, the bladder low in the pelvis, the large intestine and the coiled small intestine above it, the stomach and the liver, the lumbar spine and the pelvis, the leg bones. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, sitting, seated
```

## 64. act_wipe_sweat — 손등으로 이마 땀을 훔치고 숨을 몰아쉬며 몸을 숙인다

쓰는 topic 2편 · 소품 없음(땀방울은 같은 청록 유리 구슬로 표현)

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, the figure filling about eighty-five percent of the frame height, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the front at eye level, now bent forward from the hips with the back rounded and the chest heaving, one hand braced flat on the same-side thigh with that arm locked straight taking the weight, the other arm folded up so the back of that hand is dragged flat across the forehead from one side to the other, that elbow flung out wide and high, the head lifted just enough to clear the wiping hand, both knees slightly bent with both feet flat on the floor a shoulder-width apart, and a few heavy beads of the same pale cyan glass clinging along the forehead and the jaw. Visible inside: the brain, the lungs and heart in the rib cage, the branching network of vessels spreading out close under the surface of the chest, the arms and the forehead, the stomach and coiled intestines, the spine, the pelvis and the leg bones. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features
```

## 65. act_cough_leak — 기침하거나 크게 웃다가 흠칫하며 다리를 모으고 아랫배를 누르는 모습

쓰는 topic 1편 · 소품 없음

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, centered with clear margins on all sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the front at eye level, caught in a sudden flinch: both knees snapped together and turned inward with the thighs pressed tight against each other and both feet flat on the floor close side by side, the hips tucked under, one hand clamped flat and low across the front of the pelvis below the navel, the other forearm folded up across the mouth with that elbow raised in front of the chest, the shoulders hunched up hard and the upper body curled forward over the clamped hand, the head ducked down. Visible inside: the lungs and the windpipe, the diaphragm sheet under the lungs pushed downward, the stomach and the coiled intestines, the bladder low in the pelvis with the flat sheet of muscle slung underneath it across the floor of the pelvis, the pelvis and the leg bones. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, walking, mid-stride, raised knee, lifted leg
```

## 66. act_cycling_saddle — 안장에 앉은 자세 그대로 장시간 페달을 밟는 모습

쓰는 topic 1편 · 소품: 안장·안장 기둥·핸들바·페달(같은 청록 반투명 유리, 바퀴·프레임 없이 최소한만, 무늬·글자 없음)

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, the figure filling about eighty-five percent of the frame height, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the side at eye level, now seated on a plain narrow bicycle saddle set on a simple upright post with a straight handlebar and two pedals on a crank, all of it made of the same translucent pale cyan glass with no markings anywhere on it and no wheels, the whole weight settled down onto the narrow saddle at the base of the pelvis, both hands wrapped over the straight handlebar with the arms bent, the back rounded forward and the head low between the shoulders, one leg driving a pedal down at the bottom of its stroke and the other folded up with the knee high at the top of its stroke. Visible inside: the pelvis and the sit bones pressed down onto the saddle, the bladder low in the pelvis and the structures packed beneath it at the base of the pelvis, the bundle of nerves and vessels running through that area into both thighs, the lumbar spine, the coiled intestines and the stomach above, the lungs and heart, the thigh and calf muscles and the leg bones. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, wheels, bicycle frame, standing
```

## 67. act_hold_one_breast — 한 손으로 한쪽 가슴 아래를 받쳐 감싸고 반대 어깨를 안쪽으로 말며 얼굴

쓰는 topic 1편 · 소품 없음

```
A close view framed from just above the top of the head down to the waist, so that the hips, the legs and the feet are completely outside the frame and not visible anywhere in the image. Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, centered with clear margins on both sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the front at eye level, now with one open hand laid flat underneath one side of the upper chest and cupped up against it from below, that forearm held horizontal across the ribs and the elbow pinned in against the side, the shoulder on that side rolled forward and inward and hitched up toward the ear so the chest closes in over the supporting hand, the opposite arm hanging away from the body, the head tipped down and over toward the supported side, the upper body curled a little that way. Visible inside: the fan of glandular tissue and its branching ducts inside that one side of the upper chest, the ribs and the breastbone behind it, the lungs and the heart, the collarbone and the shoulder joint on that side, the small chain of nodes in the armpit above the supporting hand, and the spine. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, both hands, symmetrical pose, full body, whole figure, legs, feet
```

## 68. act_open_window — 닫혀 있던 창문을 열어 바깥 공기가 들어오게 하는 모습

쓰는 topic 1편 · 소품: 미닫이 창문 틀 한 짝(같은 청록 반투명 유리, 무늬·글자 없음, 창밖은 빈 void)

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, the figure filling about eighty-five percent of the frame height, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from a shallow three-quarter angle at eye level, now standing at a plain simple window frame with a single sliding panel made of the same translucent pale cyan glass with no markings anywhere on it, the panel pushed fully open to one side, one arm stretched up and out with that hand still resting on the open panel at shoulder height, the other hand hanging at the side, the chest opened and lifted toward the opening, the shoulders drawn back and down, the head tipped slightly back, both feet flat on the floor a shoulder-width apart. Visible inside: the nasal cavity and the windpipe, both lungs fully expanded inside the rib cage with the branching airways spreading through them, the diaphragm sheet pulled flat and low under them, the heart, the ribs and the collarbones, the spine, the pelvis and the leg bones. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, outdoor scenery, landscape, view through window
```

## 69. act_run_impact — 아스팔트를 달리며 착지 충격이 골반까지 전해지는 러닝 장면

쓰는 topic 1편 · 소품 없음

```
Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, the figure filling about eighty-five percent of the frame height, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the side at eye level, now caught at the hard landing moment of a running stride moving toward frame right: the leading foot slammed down flat on the floor with that knee bent and absorbing, the whole body weight driven down through it, the trailing leg swung far back with the heel kicked up high behind, the torso upright and leaning a little forward, one arm driven forward with the elbow bent square and the other pulled back behind the hip, the shoulders squared, the head level and facing the direction of travel. Visible inside: the bones of the landing foot and the ankle, the shin bone and the knee joint above it, the thigh bone driving up into the hip joint, the pelvis with the flat sheet of muscle slung across its floor, the bladder low inside it, the lumbar spine, the coiled intestines and the stomach, the lungs and heart. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, standing still, walking
```

## 70. act_shaky_hands — 물컵을 들거나 글씨를 쓸 때 손이 미세하게 떨림

쓰는 topic 1편 · 소품: 물컵(같은 청록 반투명 유리, 무늬·글자 없음)

```
A close view framed from the top of the head down to the hips, so that the knees and the feet are completely outside the frame and not visible anywhere in the image. Medical holographic visualization of a translucent glass-like 3D human figure, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, centered with clear margins on both sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The same figure as the reference, seen from the front at eye level, now holding a plain smooth straight-sided cup made of the same translucent pale cyan glass with no markings on it, half filled with liquid whose surface is tilted and rippling, gripped in one hand out in front of the breastbone with that arm extended and the elbow only slightly bent, the fingers stiff and splayed wide around the cup, that whole forearm and hand caught blurred in a fine rapid tremor while the rest of the body stays sharp and still, the other hand half raised toward the cup as if to steady it, both shoulders hitched up and the head tipped down watching the cup. Visible inside: the finger bones and the wrist bones of the shaking hand, the tendons running from the forearm into the fingers, the nerves passing through the wrist and up the arm, the arm bones, the collarbones and the rib cage, with the brain faintly visible above. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, full body, whole figure, legs, feet
```

## 71. m_hormone_surge — 샘에서 호르몬 입자가 평소보다 훨씬 많이 쏟아져 나와 건너편 수용체가 전

쓰는 topic 18편 · 기존 m_acid_secretion과 화면이 겹치지 않게 — 표면을 호박색으로 덮는 게 아니라 샘 → 통로 → 건너편 수용체가 켜진 채 안 꺼지는 순서로 짰다. m_hormone_drop과는 정반대 방향(쏟아짐·점등 vs 가늘어짐·소등)이라 두 클립을 같은 구도로 두고 방향만 뒤집었다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human glandular tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A rounded gland body sits in the lower third of the frame, seen from the side and cut open so its hollow inside is visible, its upper wall dotted with a row of open release pores facing straight up. Spanning the upper half of the frame, directly above the gland, one wide channel runs horizontally with its near wall cut away; the far wall of that channel is lined with a row of plump target cells, each with a small cup-shaped socket on its face. A thin trickle of small warm amber particles leaves two of the pores and drifts up into the channel, and only a couple of the sockets across the channel hold a particle and glow faintly. Everything except those amber particles and the two sockets they have filled is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, fire, flames, explosion, sparks, fountain, heart shape, whole organ, bottle
```

## 72. m_vessel_dilation — 혈관이 순식간에 넓어지며 혈류가 확 몰리고 압력이 떨어져, 위쪽으로 가던

쓰는 topic 18편 · 기존 m_blood_flow_drop과 정반대 방향이라, 시작 이미지부터 좁은 채널 + 조여진 근육 고리로 두고 넓어지는 쪽으로만 움직인다(저쪽은 넓은 채널 + 풀린 고리에서 좁아진다). 위로 갈라지는 가는 가지가 흐려지는 걸로 '위쪽으로 가던 피가 준다'를 같은 컷에서 보여준다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D a human blood vessel, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One thick vessel runs straight up the centre of the frame from the bottom edge, sliced open lengthwise so the channel inside is visible along its whole length, and near the top of the frame it splits into two much thinner branches that run on up out of frame. At this moment the main channel is narrow and tight, its walls drawn close together, and a ring of banded muscle fibres wraps around the outside of the wall, clenched tight and clearly ridged. A single file of small smooth disc-shaped cells drifts steadily up the narrow channel and on into the thin upper branches, which glow evenly bright. Everything is translucent pale cyan glass, nothing in the image is amber. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, blood colour, pipe, plumbing, hose, tree, roots
```

## 73. m_hormone_drop — 샘에서 흘러나오던 호르몬 입자 줄기가 가늘어지다 끊기고, 건너편 표적 세

쓰는 topic 12편 · m_hormone_surge와 한 쌍으로 만든 반대 방향 컷 — 같은 샘·줄기·수용체 구도를 쓰되 줄기가 가늘어지고 불이 꺼진다. 호르몬 자체는 해로운 물질이 아니라 호박색을 쓰지 않고 양과 밝기만 떨어뜨렸다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human glandular tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A rounded gland body sits in the lower third of the frame, seen from the side and cut open, with a single release pore open on its top. From that pore one continuous stream of small pale cyan particles rises straight up through the middle of the frame to a row of three large target cells spanning the upper third, each target cell holding a small round window that glows softly lit. The stream is thick and unbroken along its whole length and every window is lit. Everything is translucent pale cyan glass, nothing in the image is amber. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, fire, candle, fountain, whole organ, smoke
```

## 74. m_particle_deposition — 공기 흐름을 타고 들어온 미세 입자가 관을 따라 점점 깊이 내려가 표면 

쓰는 topic 11편 · m_toxin_load는 액체가 통로를 가득 채우고 세포로 스미는 그림이라, 이쪽은 '공기 흐름에 실린 고체 알갱이가 융모 사이에 하나씩 박혀 더는 안 움직인다'는 정지 과정으로 짰다. 뿌연 연기·먼지구름으로 뭉개지지 않게 --no에 넣었다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human airway tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A wide airway tube runs from the bottom edge of the frame away into the depth toward the upper third, cut open along its length so the inner surface is fully visible, and that surface is carpeted with fine upright hair-like fringes all leaning the same way. A stream of tiny warm amber specks drifts along the open air space above the fringes, carried deeper into the tube, and a few specks have already caught between the fringes near the front. The fringes and the tube are translucent pale cyan glass; only the drifting specks are warm amber. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, smoke, fog, haze, dust cloud, sand, snow, whole lung, grass field
```

## 75. m_electrolyte_imbalance — 칼륨·나트륨·마그네슘 같은 이온이 땀·체액으로 빠져나가 균형이 무너지고 

쓰는 topic 10편 · m_dehydration은 표면이 말라 갈라지는 그림이라 '물은 있는데 이온만 빠진' 상태를 못 보여준다 — 섬유의 형태·부피는 그대로 두고 안의 알갱이만 빠져나가게 해서 구분했다. 이온은 해로운 물질이 아니라 청록, 마지막 경련 지점만 옅은 호박색.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human muscle tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A thick muscle fibre runs horizontally across the middle of the frame, cut open along its length so its inside is visible, its surface marked with fine evenly spaced crosswise bands. Inside it a dense even scatter of tiny round pale cyan grains fills the fibre from end to end. One narrow channel leaves the fibre from its upper surface and runs up out of the top of the frame, wide open and full of clear fluid, and a few grains are already drifting up into it. The fibre itself still lies straight, full and relaxed. Everything is translucent pale cyan glass, nothing in the image is amber. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, salt crystals, sugar, powder, foam, bubbles
```

## 76. m_muscle_wasting — 나란히 묶인 근섬유 다발이 하나씩 가늘어지고 개수가 줄어들면서 다발 전체

쓰는 topic 10편 · m_muscle_tension은 다발이 뭉쳐 두꺼워지고 굳는 그림이라 정반대다 — 잘린 단면을 정면으로 보여줘서 '굵기와 개수가 준다'가 첫 컷에서 바로 읽히게 했고, 마지막에 늘어난 빈 껍질을 남겨 소실을 못 박았다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human muscle tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A thick bundle of long parallel muscle fibres runs from the bottom edge of the frame straight up to the top edge through the exact centre, and it is cut straight across near the middle so the flat cut face is turned toward the camera, showing dozens of round fibre cross-sections packed tight against one another with almost no space between them. The bundle is full and evenly thick along its whole length and its outer sheath is smooth and taut. Everything is translucent pale cyan glass, nothing in the image is amber. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, rope, braid, cable, wires, anatomy chart, whole muscle
```

## 77. m_tendon_degeneration — 반복 부하와 혈류 감소로 힘줄·근막에 미세손상이 쌓여 조직이 퇴행한다

쓰는 topic 10편 · m_inflammation(혈관에서 호박색 면역세포가 쏟아져 조직이 부풂)으로 때우면 급성 염증으로 읽힌다 — 이쪽은 부풀지도 않고 새 물질도 안 들어오고, 같은 자리가 반복 마찰로 닳아 섬유 결이 흐트러지는 것만 보여준다. 부종·면역세포를 --no에 넣었다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tendon tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A thick tendon cord made of many long parallel fibres runs diagonally across the whole frame from the lower left corner to the upper right corner, its fibres lying perfectly straight and packed tight all in one direction. Halfway along, the cord passes over the rounded edge of a hard dense block that presses up into it from below, and the cord bends there. At this moment the cord is smooth, evenly thick and unbroken and every fibre is still in line. Everything is translucent pale cyan glass, nothing in the image is amber. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, red glow, orange gradient, fire, swollen dome, immune cells, rope, frayed rope, wood
```

## 78. m_circadian_misalign — 몸속 24시간 시계 바늘과 바깥 시간표가 어긋나 리듬이 통째로 앞뒤로 밀

쓰는 topic 9편 · 기존 15종에 시간축 기전이 아예 없어 형태를 새로 만들었다 — 숫자 없는 눈금 고리 두 개가 어긋나는 것만으로 표현하고, 시계 숫자·문자반·손목시계를 --no에 넣어 글자 금지 규칙과 충돌하지 않게 했다. 마지막 컷에서 조직 자체의 리듬이 둘로 갈라지게 해서 추상 도형만 도는 그림이 되지 않게 했다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human body tissue with an abstract glass dial form, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. Two flat rings lie one inside the other in the exact centre of the frame, seen straight on and filling most of it, each ring marked with evenly spaced plain tick bars around its rim and one single longer pointer bar standing out from the rest. The outer ring is fixed in the surrounding tissue; the inner ring is a separate free-floating disc. At this moment the two pointer bars line up exactly, one directly over the other, and the tick bars of both rings sit perfectly in step all the way around. Below and behind the rings a soft band of translucent body tissue stretches across the lower part of the frame, pulsing evenly. Everything is translucent pale cyan glass, and there are no numerals or clock numbers of any kind anywhere. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, numerals, digits, clock numbers, roman numerals, dial numbers, wristwatch, watch brand, gears, sundial, compass
```

## 79. m_microvessel_damage — 머리카락보다 가는 모세혈관이 약해져 늘어나고 새거나 터져 주변으로 번진다

쓰는 topic 9편 · m_blood_flow_drop은 굵은 혈관 하나를 옆에서 본 흐름 감소 그림이다 — 이쪽은 위에서 내려다본 실핏줄 그물 자체가 여러 군데 터져 번지는 클로즈업이라 구도부터 다르다. 피는 캐논대로 청록으로 두고 호박색을 전혀 안 썼다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D a net of human capillaries, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A net of hair-thin capillaries spreads across the whole frame like fine branching threads lying over a flat field of translucent tissue, seen from straight above, the net densest in the centre and thinning toward the corners. Each thread is barely wider than the tiny disc-shaped cells running single file inside it, and every thread is smooth, evenly thin and unbroken along its length. The tissue beneath the net is clear and clean. Everything is translucent pale cyan glass, nothing in the image is amber. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, blood colour, roots, tree branches, lightning, river delta, cracked glass
```

## 80. m_nutrient_depletion — 철·아연·단백질·마그네슘 같은 저장고가 새거나 소모돼 바닥을 드러내, 조

쓰는 topic 9편 · m_hormone_drop(샘 → 줄기 → 수용체 소등)과 헷갈리지 않게 '저장고 재고가 바닥난다'는 다른 형태로 짰다. 끝 컷을 '만들다 만 조직이 재료가 없어 부서진다'로 둬서 결핍의 결과까지 한 클립 안에 들어간다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue with an internal storage chamber, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A rounded storage chamber sits in the lower half of the frame, seen from the side and cut open so its inside is visible, packed right up to the brim with small round pale cyan grains. One narrow channel leaves it from the lower left and runs off out of frame, and a few grains are trickling out through it. Directly above the chamber, in the upper half of the frame, a row of half-built tissue strands rises upward, each one broken off unfinished in mid-air with an open socket at its tip waiting for a grain. Everything is translucent pale cyan glass, nothing in the image is amber. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, sand, hourglass, sugar, pills, jar, barrel, coins
```

## 81. m_odor_compound_release — 표면의 세균이 땀·피지 방울을 분해하자 작은 냄새 분자가 떨어져 나와 표

쓰는 topic 9편 · m_bacteria_growth는 세균이 둘로 갈라져 수가 느는 데서 끝난다 — 이쪽은 이미 자리잡은 세균이 땀·피지 방울을 부수고 냄새 분자가 공기 중으로 떠오르는 다음 단계라, 마지막 컷에서 위로 올라가 퍼지는 게 핵심이다(냄새 topic의 결론).

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human skin surface tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A wide flat skin surface seen from a low skimming angle just above it, running from the bottom edge of the frame back toward a horizon line in the upper third, with open dark empty space above. The surface is a mosaic of plump pale cyan cells, and lying over it are several fat rounded droplets of clear pale cyan fluid. Warm amber rod-shaped bacteria are clustered thickly on and around every droplet, already settled and feeding, and a few tiny warm amber flecks have just begun to lift off the nearest droplet into the empty air above. Everything except the bacteria and those flecks is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, smoke, fog, steam, cloud, petri dish, mould, hair, flowers, perfume bottle
```

## 82. m_tissue_laxity — 팽팽하던 막·판막·괄약근이 늘어나 헐거워지면서 제자리를 못 잡고 벌어진다

쓰는 topic 9편 · m_pressure_buildup은 배출로가 막혀 압력이 오르는 반대 상황이라, 이쪽은 막아주던 구조가 늘어나 아예 안 닫히는 쪽으로 끝까지 민다. 늘어남은 물질이 아니라서 호박색 없이 형태·장력만 바꿨다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D a human sphincter ring of muscle, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A ring of taut muscle fibres wraps around the end of a wide tube in the exact centre of the frame, seen at a slight angle from in front so both the ring and the closed line it guards are visible. At this moment the ring is drawn tight and the two lips it presses together meet in one clean unbroken line with no gap at all, and the fibres of the ring are short, thick and evenly tensioned. Behind the ring the tube is full of clear pale cyan fluid held back. Everything is translucent pale cyan glass, nothing in the image is amber. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, rubber band, elastic, rope, drain, plughole, machinery, camera shutter
```

## 83. m_tissue_tear — 팽팽하게 당겨진 표면 조직이 한 지점에서 세로로 갈라지며 틈이 벌어지고 

쓰는 topic 9편 · m_cell_damage는 세포 사이 미세 균열이라 육안으로 벌어진 틈이 안 보이고, m_mucus_barrier는 보호막만 벗겨진다 — 이쪽은 표면이 한 줄로 쫙 갈라져 가장자리가 들린 채 남는 게 감별 포인트라 마지막 컷에서 틈을 안 닫는다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human surface tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A flat sheet of surface tissue stretches across the whole frame seen from straight above, pulled taut from both sides so fine parallel strain lines run across it, its surface smooth, glossy and completely unbroken. At the exact centre of the frame one short stretch is pulled tighter than the rest and has gone thin and pale with the strain, but it has not opened. Plump packed cells are visible through the surface from below. Everything is translucent pale cyan glass, nothing in the image is amber. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, blood, wound, cracked earth, dry mud, paper, fabric, stitches, canyon
```

## 84. m_barrier_leak — 표면을 덮은 세포들 사이 이음매가 벌어져 수분이 빠지고 그 틈으로 입자·

쓰는 topic 8편 · m_mucus_barrier는 세포 위에 얹힌 점액층이 얇아지는 그림이다 — 이쪽은 층을 아예 얹지 않고(--no에 gel layer·mucus layer를 넣음) 세포와 세포 사이 이음매가 지퍼처럼 풀리는 것만 보여줘서 다루는 층이 다르다는 게 한눈에 보인다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human surface cell layer, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A row of plump cells stands side by side across the middle of the frame, seen from the side at eye level and cut through so their full height is visible, forming one continuous surface layer with no gel, film or coating of any kind lying on top of them. Between each neighbouring pair of cells the seam is sealed shut by a tight zip-like band of interlocking bars, drawn sharp and clearly visible through the translucent walls. The cells are full and plump with clear fluid. Above them is open dark empty space with a scatter of tiny warm amber particles drifting in it, none of them touching the surface yet. Everything except those particles is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, gel layer, mucus layer, slime, foam, brick wall, metal zipper teeth, fence, tiles
```

## 85. m_fungal_growth — 둥근 포자가 실 같은 균사를 뻗으며 그물처럼 퍼지고, 균사 끝이 표면 각

쓰는 topic 8편 · m_bacteria_growth는 막대균이 둘로 쪼개져 늘어나는 그림이라, 막대 모양 자체를 --no로 막고 '포자 → 균사가 그물처럼 뻗음 → 각질 틈으로 파고듦'이라는 곰팡이 고유 형태로 못 박았다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human skin keratin surface, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. An extreme close-up of a surface made of flat overlapping scale-like plates, seen at a low angle from just above, filling the lower two thirds of the frame with open dark empty space above. Sitting on the plates are a few perfectly round warm amber spores, each clearly separate from the others, and one of them has just pushed out a single thin amber thread that runs a short way across the surface. There are no rod shapes anywhere. Everything except the spores and that one thread is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, rods, rod-shaped bacteria, bacilli, mushroom, mould fuzz, hair, petri dish, moss, spider web
```

## 86. m_uv_radiation_damage — 평행한 자외선 줄기가 표면층을 뚫고 들어가 활성산소를 만들고 섬유 다발·

쓰는 topic 8편 · m_melatonin_suppression도 호박색 빛을 쓰므로 구도를 갈라뒀다 — 이쪽은 '곧게 뻗은 평행 광선이 피부 단면을 관통해 깊은 섬유 다발을 끊는' 층 단면이고, 저쪽은 통로를 타고 들어와 샘을 덮는 넓고 부드러운 빛이다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human skin tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A thick slab of skin tissue seen from the side at eye level, like a slice cut out of a cake, filling the lower two thirds of the frame with open dark empty space above it. Stacked from bottom to top: a deep layer of long springy fibre bundles woven into a criss-cross mesh; above that a band of plump packed cells; and on top one flat unbroken surface facing straight up. Coming down from the top of the frame into that surface is a set of perfectly straight parallel warm amber beams, evenly spaced and slightly angled, their tips just touching the surface and not yet inside it. Everything except those beams is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, sun, sunset, sky, beach, lens flare, rainbow, spotlight fixture, lamp, laser gun
```

## 87. m_fat_accumulation — 지방세포 하나하나가 안쪽 기름방울을 채우며 부풀어 서로를 밀어내고 층 전

쓰는 topic 7편 · m_fluid_retention은 세포 사이 틈이 물로 차면서 세포를 밀어내는 그림 — 이쪽은 틈이 아니라 세포 안쪽이 차올라 세포 자체가 커진다. 시작 이미지부터 '세포마다 안에 작은 호박색 방울'을 명시해서 두 클립이 안 겹치게 했다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human fat tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A block of fat tissue seen from the side at eye level, its flat top surface facing straight up, filling the lower two thirds of the frame with open dark empty space above it. Inside the block, large round cells sit packed together in an even honeycomb, and each cell holds one small warm amber droplet floating at its centre with plenty of clear pale cyan space around it. The block is low, flat and even, its top surface level. Everything except the droplets inside the cells is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, bubbles, foam, soap, wax honeycomb, eggs, caviar, oil slick, butter
```

## 88. m_melatonin_suppression — 빛이 눈으로 들어오자 송과체의 멜라토닌 분비 곡선이 눌려 내려가는 그림

쓰는 topic 7편 · m_uv_radiation_damage와 둘 다 호박색 빛이라, 이쪽은 곧은 평행 광선을 --no로 막고 통로로 밀려드는 넓고 부드러운 빛 덩어리로 갔다. 멜라토닌 입자 자체는 해로운 게 아니라 청록 그대로 두고 줄기만 가늘어진다(m_hormone_drop과는 빛이라는 원인이 화면에 같이 나오는 점이 다르다).

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human brain gland tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A small rounded gland sits in the exact centre of the frame deep inside translucent tissue, seen from the side and cut open, releasing a steady stream of small pale cyan particles that flows downward out of the bottom of the frame. From the upper left, one wide soft wash of warm amber light spreads in through an open channel in the tissue and reaches toward the gland, its front edge still short of it. The gland itself is bright and working. Everything except that wash of light is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, sun, lamp, bulb, screen, phone, window, lens flare, straight parallel beams, brain diagram, eyeball photo
```

## 89. m_nutrient_absorption_block — 장에서 흡수되려던 영양소가 방해 물질에 붙잡혀 그대로 빠져나가는 그림

쓰는 topic 7편 · m_glucose_spike도 융모 사이에 입자가 떠 있는 그림이라, 이쪽은 입자를 두 종류(청록 영양소 + 호박색 방해물질)로 나누고 방향을 반대로 뒀다 — 저쪽은 입자가 벽을 뚫고 혈관으로 쏟아져 들어가고, 이쪽은 문 앞에서 못 들어간 채 그대로 지나간다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human gut wall tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A gut wall seen from the side at eye level, its top surface covered in tall thin finger-like folds standing upright, filling the lower two thirds of the frame with open dark empty space above. Each fold has small open doorways set into its sides. Drifting in the space between the folds are round pale cyan nutrient spheres and, mixed among them, a smaller number of angular warm amber blocker particles. A few of the pale cyan spheres are already slipping in through the doorways. Everything except the blocker particles is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, food, vegetables, pills, sugar cubes, candy, coral, seaweed, carpet
```

## 90. m_adenosine_block — 깨어있는 동안 졸음물질 아데노신이 쌓이고, 카페인이 그 수용체 자리를 대

쓰는 topic 6편 · 캐논 m_nerve_overdrive가 이미 '호박색 입자가 소켓을 막는' 그림이라 겹칠 위험이 가장 컸다 — ①시냅스 틈 측면도가 아니라 위에서 내려다본 넓은 수용체 면 ②청록 아데노신과 호박색 카페인 두 종류가 같이 나옴 ③결과가 '신호 난사'가 아니라 '어두워지던 면이 다시 밝아진 채 안 꺼짐' 세 군데를 다르게 못 박았고, --no에도 시냅스 구도를 넣었다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human nerve cell surface, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A wide flat cell surface seen from straight above, filling the whole frame, evenly studded with dozens of round open sockets in a regular field. Drifting just above the surface are many small pale cyan key-shaped particles, several of which are already seated down inside sockets, and those filled sockets have gone soft and dim. Mixed in among them a few angular warm amber wedge-shaped particles hover above the surface without having reached a socket yet. The surface is bright and wide awake everywhere except where the pale cyan keys have settled. Everything except the amber wedges is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, metal keys, keyhole, lock, padlock, coffee beans, coffee cup, puzzle pieces, buttons, synapse gap, two nerve endings facing each other
```

## 91. m_backflow_pooling — 판막이 닫히지 못해 혈액이 거꾸로 흘러 아래쪽에 고이고 혈관이 꽈리처럼 

쓰는 topic 6편 · m_blood_flow_drop은 좁아져서 흐름이 주는 그림이고 이쪽은 판막이 못 닫혀 흐름이 거꾸로 내려오며 혈관이 부푼다 — 방향이 반대라는 걸 1컷에서 바로 알 수 있게 역류를 맨 앞에 뒀다. 판막 한 쌍을 시작 이미지에 넣어 두 클립의 시작 프레임부터 구분된다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D a human vein with valves, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One wide vein runs straight up the centre of the frame from the bottom edge to the top edge, sliced open lengthwise so the channel inside is visible along its whole length. Partway up, a pair of thin cup-shaped valve flaps reaches in from the walls toward each other and at this moment they meet neatly in the middle and close the channel off cleanly, and the vein wall above and below them is the same even width all the way. Small smooth disc-shaped cells drift upward through the channel below the valve. Everything is translucent pale cyan glass, nothing in the image is amber. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, blood colour, balloon, pipe, plumbing, valve machinery, heart shape
```

## 92. m_follicle_weakening — 모낭이 가늘게 위축되고 성장기 모발이 한꺼번에 휴지기로 넘어가 빠지는 그

쓰는 topic 6편 · 기존에 모낭 단위 기전이 아예 없어 새로 만들었다 — 마지막 컷에서 모발이 떠올라 빠져나가고 빈 구멍이 남는 것까지 보여줘야 탈모 topic 나레이션('한꺼번에 휴지기로 넘어가 빠진다')과 맞는다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human scalp tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A slab of scalp tissue seen from the side at eye level, like a slice cut out of a cake, filling the lower two thirds of the frame with open dark empty space above. Sunk into the slab and clearly visible through the cut face are three deep flask-shaped follicles side by side, each one wide and full at its base, and out of each rises one thick strand that climbs straight up into the empty space above the surface. A fine net of hair-thin vessels wraps the base of each follicle. Everything is translucent pale cyan glass, nothing in the image is amber. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, hair colour, brush, comb, wig, plant roots, bulbs, flower, sprout
```

## 93. m_histamine_release — 표면에 앉은 이물 입자에 면역세포가 달라붙자 세포 안 알갱이가 한꺼번에 

쓰는 topic 6편 · m_inflammation은 혈관에서 면역세포가 천천히 빠져나와 조직이 부푸는 일반 염증 그림이라, 이쪽은 '닿는 순간 한꺼번에 터진다'는 알레르기 특유의 즉각성이 보이게 1컷부터 접촉→폭발로 붙이고 3컷 안에 부종까지 끝낸다(푸시인도 느린 게 아니라 빠르게).

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D a human immune cell in tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A single large round immune cell sits in the exact centre of the frame on a flat bed of tissue, cut open so its inside is visible, packed full of small tightly stored warm amber granules. One angular warm amber foreign particle has just landed on the cell's outer surface and is touching it. Running behind and past the cell is one translucent vessel, narrow and calm, and the tissue bed around the cell is flat and even. Everything except the granules inside the cell and the landed particle is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, flowers, pollen photograph, fireworks, explosion fire, smoke, dandelion, nuts, cat
```

## 94. m_mucus_overproduction — 점막에 박힌 분비세포들이 동시에 부풀어 점액을 쏟아내고, 통로가 끈끈한 

쓰는 topic 6편 · m_mucus_barrier는 청록 보호막이 얇아져 벗겨지는 그림이라 방향이 정반대다 — 여기선 넘치는 점액 자체를 '과한 물질'로 보고 호박색으로 칠해서 두 클립이 색부터 절대 안 헷갈리게 했다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human mucous membrane tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A narrow passage runs from the bottom of the frame away into the depth, cut open along its length so both inner walls are visible, and the passage is wide open and clear down its whole length. Both walls are lined with rows of small flask-shaped secreting cells set into the lining, each one plump and holding a warm amber load inside it. A thin film of warm amber liquid has just begun to seep out of a few of them and run down the wall. Everything except the amber inside and leaving those cells is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, honey, syrup, caramel, jelly, slime rope, cave, tunnel architecture, dripping paint
```

## 95. m_receptor_desensitization — 신호 분자가 수용체에 끊임없이 몰려드는데도 아래쪽 문이 열리지 않고, 못

쓰는 topic 6편 · m_hormone_surge는 수용체가 전부 켜지는 그림이고 m_adenosine_block은 경쟁 물질이 자리를 뺏는 그림이다 — 이쪽은 수용체에 제대로 붙는데도 그 아래 문이 안 열리고 세포 안이 계속 비어 있으며 바깥에만 분자가 쌓이는 게 요점이라, 시작 이미지 단면에 '닫힌 문 패널'을 명시했다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D a human cell with surface receptors, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One large cell fills the centre of the frame, seen from the side and cut open so both its outer surface and the space just inside it are visible. Along its outer surface stands a row of receptor stalks, and directly beneath each stalk, inside the cell, sits a shut gate panel pressed firmly closed. Small warm amber signal molecules are docked on several of the stalks already and more drift in the space outside. Inside the cell, beyond the shut gates, the space is empty and clear. Everything except the signal molecules is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, architectural doors, gates, fence, keys, padlock, machinery, switches, buttons, antenna, satellite dish
```

## 96. m_tissue_thinning — 여러 겹이던 조직 층이 얇고 납작해지고 그 안의 탄력·지지 섬유가 성글어

쓰는 topic 6편 · 호박색 없음(물질이 아닌 기전). m_mucus_barrier와 구분: 표면 보호막이 아니라 벽 전체 두께가 줄어드는 게 주인공이라 층을 아래→위 3단으로 못 박고 마지막 컷에서 '쉽게 눌린다'를 보여준다. m_muscle_wasting(5번)과도 구분: 근섬유 다발이 아니라 판 모양 층.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A thick slab of body wall seen from the side at eye level, like a slice cut out of a cake, sitting in the lower half of the frame with open dark empty space above it. Stacked from bottom to top: a deep base layer criss-crossed by dense springy support fibres packed tightly together; above it a thick middle layer of plump rounded cells; and on top one thin smooth surface layer. The slab stands tall and its flat top surface sits high above the base. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, cake, sponge, layered dessert, anatomy chart
```

## 97. m_arousal_spike — 깊이 잠든 뇌파 위로 각성 신호가 튀어올라 잠이 순간 끊기는(미세각성) 

쓰는 topic 5편 · 호박색 없음. m_nerve_overdrive와 구분: 시냅스 클로즈업이 아니라 넓은 뇌 표면의 '느린 큰 물결 → 날카로운 스파이크'라 수면 단계가 화면에 남는다. 차트로 렌더될 위험이 커서 graph·waveform·line plot·grid를 --no에 넣었다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D brain tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A wide sheet of translucent brain surface seen from a low skimming angle just above it, running from the bottom edge of the frame back toward a horizon line in the upper third, with open dark empty space above. Long slow smooth swells roll across the sheet from left to right, evenly spaced, their crests broad and rounded and their glow dim and steady. Everything is translucent pale cyan glass and the whole scene is calm and dark. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, graph, chart, waveform, line plot, grid, ocean, sea, beach, cloth, fabric
```

## 98. m_emptying_delay — 주머니 아래 출구가 좀처럼 열리지 않아 내용물이 그대로 고여 남고, 벽이

쓰는 topic 5편 · m_pressure_buildup과 가장 헷갈릴 항목 — 그쪽은 배출로가 호박색 슬러지로 막혀 압력이 오른다. 여긴 배출로가 텅 비어 있고 근육 고리가 안 열리는 것뿐이라, 세 컷 모두에서 '출구 튜브는 비어 있다'를 명시했다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One large rounded pouch sits in the middle of the frame, seen from the side at eye level and cut open lengthwise so its hollow inside is fully visible, filled two thirds of the way up with thick warm amber contents. At the bottom of the pouch one short narrow outlet tube points straight down; the mouth of that tube is ringed by a thick band of muscle clamped tightly shut, and the tube below the ring is completely empty and clear. The pouch wall is smooth and slightly stretched. Everything except the amber contents inside the pouch is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, balloon, bottle, jar, funnel, hourglass, machinery, valve handle
```

## 99. m_filtration_overload — 사구체로 걸러야 할 용질이 한꺼번에 몰려 여과 압력과 부담이 올라가는 그

쓰는 topic 5편 · m_waste_buildup과 구분 — 거긴 노폐물이 관절 틈에 쌓이는 정적인 장면, 여긴 '거르는 장치'가 화면 중앙에 공 모양으로 있고 부하가 걸려 부푼다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A tight knot of many looping translucent capillary tubes bunched into one round ball in the centre of the frame, wrapped in a thin smooth capsule, with one wide tube entering at the upper left, one narrower tube leaving at the lower left, and a single drain tube leaving the bottom of the capsule. A steady stream of small warm amber grains flows through the looping tubes, and fine clear droplets strain out through the tube walls into the space inside the capsule. Everything except the amber grains is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, yarn, wool, rope, knot of wire, brain, net, coral
```

## 100. m_friction_abrasion — 두 표면이 반복해 스치며 긁히고, 그 자극이 쌓여 표면이 거칠어지거나 두

쓰는 topic 5편 · 호박색 없음. m_cell_damage와 구분 — 손상이 한 번에 나는 게 아니라 '같은 자리를 왕복'하는 게 핵심이라 세 컷 전부 왕복 운동을 명시했다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. Two tissue surfaces meet in the middle of the frame, seen from the side at eye level: a flat tissue floor running across the lower half with its top surface facing straight up, and resting on it a smooth curved tissue body coming down from above, touching along one narrow line. Both surfaces are glossy, even and unmarked, with open dark empty space above. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, crystals, needles, particles, sand, grit, gears, machinery
```

## 101. m_haircell_damage — 줄지어 선 감각 털세포가 거센 진동에 눕고, 눕은 털이 부러진 채 되돌아

쓰는 topic 5편 · 호박색 없음. m_cell_damage와 구분 — 판판한 세포벽이 아니라 '줄지어 선 털'이 주인공이고, 꺼지는 것은 색이 아니라 불빛(줄 가운데가 어두워진다).

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A long straight row of tall thin hair bundles standing upright along a tissue ridge, seen from the side at eye level and running from the left edge of the frame to the right, filling the middle of the frame. Each bundle is a cluster of fine stiff hairs tapering to a point, all standing evenly and glowing softly from the base where they sit in the ridge. Beneath them the ridge is packed with plump cells; above them lies a shallow layer of clear fluid and open dark empty space. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, grass, wheat, field, brush, broom, feathers, eyelashes
```

## 102. m_immune_decline — 표면을 순찰하던 면역세포 수가 눈에 띄게 줄고 남은 것들도 움직임이 굼떠

쓰는 topic 5편 · ⚠️ m_inflammation과 색 배역이 반대다(거긴 호박색이 면역세포, 여긴 호박색이 침입자고 면역세포는 cyan) — 헷갈리지 않게 Flow 문장에 '면역세포는 cyan, 밝기와 수만 줄어든다'를 박아뒀다. 기전 자체도 정반대(과잉 vs 저하).

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A wide flat tissue surface seen from a low skimming angle just above it, running from the bottom edge of the frame back toward a horizon line in the upper third, with open dark empty space above. The surface is a mosaic of plump pale cyan cells. Standing on it, well spread out, are several large round patrolling immune cells with short stubby arms, each glowing brighter than the surface beneath them. Near the far edge of the surface sit a few small warm amber invader particles, not yet moving. Everything except the amber invaders is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, petri dish, insects, spiders, robots, cartoon characters, eyes
```

## 103. m_urine_overproduction — 수분 재흡수가 억제돼 신장이 소변을 과하게 만들고 방광이 빠르게 차오르는

쓰는 topic 5편 · m_fluid_retention과 물의 방향이 반대(조직으로 고이는 게 아니라 관으로 빠져나간다) — 구도부터 다르게 관을 화면 중앙 세로로 세우고 아래에 차오르는 방광 챔버를 뒀다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One long narrow tubule runs from the top edge of the frame straight down to the bottom through the exact centre, sliced open lengthwise so the channel inside is visible along its whole length, clear pale cyan fluid running down it. The tubule wall is lined with small round reabsorption pores, and clear droplets are passing outward through several of them from the channel back into the surrounding tissue. A few tiny warm amber particles drift in the fluid inside the channel. At the bottom of the frame the tubule empties into a rounded collecting chamber that is only lightly filled. Everything except those particles is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, toilet, bottle, pipe, plumbing, funnel, hose
```

## 104. m_vessel_occlusion — 정체된 혈류 속에서 혈소판·섬유소가 엉겨 굳어 한 지점을 완전히 막고, 

쓰는 topic 5편 · m_blood_flow_drop과 구분 — 그쪽은 호박색이 하나도 없고 바깥 근육이 조여 관이 좁아진다. 여긴 관 굵기는 그대로고 안쪽 호박색 덩어리가 한 지점을 완전히 막는다(대각선 구도로도 구분).

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D vessel, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One thick vessel runs diagonally across the frame from the upper left to the lower right, sliced open lengthwise so the open channel inside is fully visible along its whole length. The channel is wide and the flow inside is sluggish, small smooth disc-shaped cells drifting slowly and beginning to bunch together. At the midpoint of the vessel a small warm amber clump of sticky platelets is stuck low against one side of the channel wall, the channel still open past it. Everything except that clump is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, pipe, plumbing, rope, hose, red, blood colour, gore, wound
```

## 105. m_vision_field_loss — 1인칭 시야에서 가장자리 또는 한쪽이 서서히 검게 잠식되거나 커튼처럼 가

쓰는 topic 5편 · 호박색 없음. 라이브러리에서 유일하게 조직 단면이 아닌 1인칭 시야 컷이라, 세계가 튀지 않게 방·가구까지 같은 청록 유리로 렌더한다. m_double_vision과 같은 방·같은 시점을 써서 1인칭 두 컷이 한 세트로 읽히게 했다(구분은 '어두워짐' vs '둘로 겹침').

```
Medical holographic visualization, a first-person point-of-view looking straight ahead from inside a person's own eyes across a plain empty room toward a bright window, with one simple low table standing in the middle of the floor; the floor, walls, window frame and table are all rendered as translucent glass-like 3D forms in the same soft pale cyan glow, the space beyond the window a dark empty slate blue-grey void, cinematic soft rim lighting, the view filling the whole vertical 9:16 portrait frame, evenly lit and equally sharp all the way out to every edge and corner, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, hands, vignette, dark corners, frame, border, porthole, keyhole, binoculars, split screen
```

## 106. m_airway_collapse — 잘 때 늘어진 연구개와 혀뿌리가 기도를 눌러 좁아지다 완전히 막히는 그림

쓰는 topic 4편 · 호박색 없음. m_mucus_barrier·m_mucus_overproduction과 구분 — 점액이 한 방울도 안 나오고 두 연조직이 직접 맞닿아 닫히는 구조적 폐색이다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A side cutaway of the back of the throat filling the middle of the frame, seen from the side at eye level: a soft curtain of tissue hangs down from the roof at the top, the thick rounded back of the tongue rises from the bottom, and between them a clear open air passage runs from the upper left down to the lower right. The passage is wide and completely open, and both the hanging curtain and the tongue base are slack and rounded. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, head, profile portrait, teeth, lips, skull, anatomy chart, tunnel, cave
```

## 107. m_content_hardening — 관 속 내용물이 수분을 잃고 부피가 줄면서 단단한 덩어리로 굳어 벽을 긁

쓰는 topic 4편 · m_dehydration과 구분 — 그쪽은 주체가 '조직 표면'이라 위에서 내려다보며 갈라진다. 여긴 주체가 '관 속 내용물'이라 관을 가로로 눕혀 썰어 보여주고 덩어리가 벽을 긁으며 밀려간다. m_waste_buildup(결정이 조직에 쌓임)과도 다름.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One wide tube runs horizontally across the middle of the frame from the left edge to the right, sliced open lengthwise so the whole channel inside is visible, its wall lined with gentle rounded folds. Resting in the middle of the channel sits one large soft rounded mass of warm amber contents, moist and slumped, with a thin film of clear fluid between it and the wall. Everything except the amber mass is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, food, bread, dough, cake, rock, stone, gravel, chocolate
```

## 108. m_mucosa_irritant_contact — 관 벽 점막 표면에 자극 물질 입자가 내려앉아 닿는 자리마다 그 아래 감

쓰는 topic 4편 · m_cell_damage와 구분 — 세포가 깨지거나 갈라지는 장면이 절대 없다(수용체 자극만)고 Flow에 못 박았다. m_nerve_overdrive와도 구분: 신경 단독 클로즈업이 아니라 '점막 표면에 닿는 순간'이 화면에 있다. 호박색은 자극 물질 + 닿은 신경 끝뿐.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A slab of tube wall seen from the side at eye level, filling the lower two thirds of the frame with open dark empty space above, its top surface facing straight up and covered by one thin smooth moist film. Just beneath that surface, fine nerve endings branch upward through the tissue and stop right under the film, their tips clearly visible through the translucent cut face and all of them unlit. Drifting in the dark space above the surface are a few small warm amber irritant particles, none of them touching the film yet. Everything except those particles is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, pepper, chilli, spice, food, fire, flames, red glow, sparks
```

## 109. m_neurotransmitter_drop — 시냅스 틈을 건너가던 신호 입자가 눈에 띄게 줄어 건너편 수용체가 드문드

쓰는 topic 4편 · ⚠️ m_nerve_overdrive와 시냅스 구도가 같아 위험 — 구분 장치는 색 배역이다. 거긴 호박색 입자가 쏟아져 소켓을 틀어막고, 여긴 입자 자체가 cyan이고 수가 줄어 소켓 불이 꺼진다. Flow에 'nothing in this clip is amber'를 명시했다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D nerve tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. Two thick nerve endings face each other across a narrow empty gap in the middle of the frame, one coming down from the top and one rising from the bottom, both seen from the side. The flat face of the lower ending is covered with dozens of small round open sockets, clearly visible through the translucent surface, and a scatter of those sockets are lit and glowing. A steady thin stream of small round pale cyan signal particles crosses the gap from the upper ending down toward the sockets. Everything, the particles included, is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, diagram, chart, flat illustration, circuit board, wires
```

## 110. m_osmotic_water_pull — 관 속에 남은 흡수되지 않은 입자들이 장벽에서 물방울을 잡아당겨 내용물이

쓰는 topic 4편 · m_fluid_retention과 물 방향이 반대 — 조직이 쪼그라들고 관이 차오른다. m_dehydration과도 구분: 마르는 건 표면이 아니라 관 뒤 조직이고 화면 주인공은 묽어지는 관 속 내용물이다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One wide tube runs horizontally across the middle of the frame, sliced open lengthwise so the channel inside is visible, its wall lined with tall thin finger-like folds standing inward into the channel. Scattered through the channel are many small warm amber particles. The channel holds only a thin shallow layer of clear fluid, while the tissue behind the wall is plump and swollen with clear fluid. Everything except the amber particles is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, food, sugar cubes, candy, foam, bubbles, soup
```

## 111. m_oxygen_transport_drop — 적혈구 수와 헤모글로빈이 줄어 실어 나르는 산소량이 떨어지고, 도착한 조

쓰는 topic 4편 · ⚠️ m_blood_flow_drop과 가장 헷갈릴 항목 — 그쪽은 바깥 근육이 조여 관이 좁아지고 세포가 정체된다. 여긴 관 폭이 절대 안 변하고 막히지도 않으며, 운반체의 '수와 밝기'만 떨어진다는 걸 세 컷 전부와 색 규칙 문장에 명시했다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D vessel, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One thick vessel runs straight down the centre of the frame from the top edge to the bottom edge, sliced open lengthwise so the open channel inside is fully visible; the channel is wide, evenly round, and exactly the same width along its whole length. It is densely packed with small smooth disc-shaped cells drifting steadily down it, each disc glowing brightly, and the tissue on both sides of the vessel is lit softly by that glow. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, blood colour, pipe, plumbing, narrowing, valve, clot
```

## 112. m_pressure_imbalance — 통로가 닫힌 채 바깥쪽 기압만 올라가고, 얇은 막이 안쪽으로 빨려 들어가

쓰는 topic 4편 · 호박색 없음. m_pressure_buildup과 구분 — 액체가 한 방울도 안 나오고(--no와 Flow 양쪽에 명시) 주머니가 아니라 얇은 막 하나가 주인공이며, 압력은 바깥에서 안으로 걸린다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One thin taut circular membrane stretched across a ring of tissue sits in the middle of the frame, seen from the side at eye level and turned slightly toward the viewer so both its outer face and the hollow air space behind it are visible. On the far side of that hollow space a narrow tube leads away, its mouth pinched flat and sealed shut. The membrane is perfectly flat and evenly taut, and the space on both sides of it is empty air with no fluid anywhere. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, drum, drumhead, trampoline, water, liquid, fluid, bubbles, balloon
```

## 113. m_sensory_mismatch — 눈·귀·목이 뇌로 보내는 균형 정보가 서로 어긋나면서 뇌가 세상이 도는 

쓰는 topic 4편 · 호박색 없음. 라이브러리에 '어긋남' 그림이 없어 세 갈래 경로가 한 점에서 만나는 구도로 새로 잡았다 — 인포그래픽으로 렌더될 위험이 커서 diagram·chart·infographic·arrows를 --no에 넣었다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. Three separate translucent nerve pathways run upward from the lower part of the frame to one folded rounded mass at the top centre: one starting at a smooth round eye globe on the lower left, one at a small coiled spiral chamber on the lower right, and one at a short bundle of neck muscle fibres at the bottom centre. Each pathway is a smooth cord of fine fibres, and a train of small pale cyan light pulses travels up each cord, all three trains in perfect step with each other. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, diagram, chart, infographic, circuit board, robot, wires, map
```

## 114. m_virus_replication — 바이러스가 세포 안으로 들어가 증식하며 퍼진다

쓰는 topic 4편 · m_bacteria_growth와 구분 — 거긴 막대 세균이 표면에서 분열하며 퍼지고, 여긴 가시 달린 구체가 세포 '안으로' 들어가 터진다. 막대로 렌더되는 걸 막으려 --no에 rod-shaped bacteria·rods를 명시.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. An extreme close-up of a block of large plump pale cyan cells packed tightly together and filling most of the frame, seen from the side at eye level, each cell holding one clearly visible round nucleus. Drifting in the dark space just above the top surface of the block are several tiny warm amber spheres studded with fine spikes, far smaller than the cells, a few of them just touching the surface of the nearest cell. Everything except those spiked spheres is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, rod-shaped bacteria, rods, worms, petri dish, mould, spores, insects, virus poster
```

## 115. m_wall_stretch_pain — 주머니 벽이 갑자기 팽팽하게 늘어나면서 벽 속에 박힌 감각 신경 말단이 

쓰는 topic 4편 · m_pressure_buildup과 구분 — 배출로도 호박색 슬러지도 화면에 없고(--no에 drain·sludge), 주인공은 벽 속 신경 말단이다. 호박색은 마지막 신경 발화(통증 지점)뿐.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A section of pouch wall curves across the middle of the frame, seen from the side at eye level, with its hollow inside below and open dark empty space above. The wall is thick and relaxed, its surface gently wavy rather than taut, and woven between its layers are fine nerve endings coiled loose and slack, clearly visible through the translucent cut face and all of them unlit. The hollow below is partly filled with clear pale cyan fluid. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, balloon, sphere, drain, pipe, sludge, machinery
```

## 116. m_cartilage_wear — 관절 연골이 닳아 완충이 사라지고 뼈끼리 닿는다

쓰는 topic 3편 · ⚠️ m_waste_buildup과 구도가 거의 같아 가장 위험한 항목 — 그쪽은 두 면 사이에 호박색 결정이 쌓인다. 여긴 결정이 단 하나도 안 나오고(--no와 Flow 양쪽에 명시) 쿠션 층 두께가 줄어드는 것만 보여주며, 시작 이미지부터 '두꺼운 쿠션 층'을 두 뼈 끝에 얹어 구분을 만들었다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. Two bone ends face each other across a narrow gap that runs horizontally across the middle of the frame, one curving down from above and one curving up from below, both seen from the side at eye level. Each bone end is capped by a thick, smooth, glossy cushion layer, and the two cushions almost meet, with nothing between them but clear fluid. The cushion layers are noticeably thick, even and unbroken along their whole length. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, crystals, needles, spikes, grit, sand, particles, gemstones, smoke
```

## 117. m_double_vision — 두 눈의 시선 정렬이 어긋나 같은 사물이 두 개로 겹쳐 보임

쓰는 topic 3편 · 호박색 없음. m_vision_field_loss와 같은 방·같은 시점을 의도적으로 써서 1인칭 두 컷이 한 세트로 읽히게 했다 — 구분 장치는 어두워짐(시야결손) vs 상이 둘로 어긋남(복시). 흐릿함으로 뭉개지지 않게 --no에 blur·bokeh를 넣고 '두 상 모두 또렷하다'를 명시했다.

```
Medical holographic visualization, a first-person point-of-view looking straight ahead from inside a person's own eyes across the same plain empty room toward a bright window, with one simple low table standing in the middle of the floor; the floor, walls, window frame and table are all rendered as translucent glass-like 3D forms in the same soft pale cyan glow, the space beyond the window a dark empty slate blue-grey void, cinematic soft rim lighting, the view filling the whole vertical 9:16 portrait frame, every edge in the scene perfectly sharp and single with no doubling anywhere, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, hands, split screen, frame, border, mirror, reflection, blur, bokeh
```

## 118. m_duct_blockage — 분비샘의 관 입구가 굳거나 좁아져 막히고, 나가지 못한 분비물이 안에 고

쓰는 topic 3편 · 호박색 없음(분비물은 해로운 물질이 아니라 정체된 자기 분비물이라 cyan을 유지하고 탁해지는 것으로만 보여준다). m_pressure_buildup과 구분 — 호박색 슬러지도, 부풀어 터질 듯한 주머니도 없다(--no에 sludge·chamber).

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A cutaway of a small gland and its duct fills the middle of the frame, seen from the side at eye level: a rounded cluster of secreting sacs at the bottom, and one narrow duct rising straight up from it to a small round opening on a flat tissue surface at the top of the frame. The duct is clear and open along its whole length and a thin thread of clear pale cyan secretion is rising through it and spreading out at the opening. The tissue around the opening is smooth and thin. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, sludge, chamber, balloon, volcano, machinery, pipe
```

## 119. m_enzyme_deficiency — 관 벽 표면에 박혀 있어야 할 분해 효소가 거의 없어, 지나가는 덩어리가

쓰는 topic 3편 · m_nutrient_absorption_block(18번, 다른 배치)과 구분 — 거긴 방해 물질이 영양소를 붙잡는 장면이고, 여긴 벽에 효소 자리가 '빈 구멍'으로 남아 덩어리가 그대로 통과한다(크기가 처음과 끝이 같다는 걸 명시).

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A slab of tube wall runs along the bottom two thirds of the frame, seen from the side at eye level, its top surface facing straight up into the open channel above; that surface is covered with tall thin finger-like folds standing upright, and the tip of every fold is smooth and bare. Drifting in the open channel just above the fold tips sits one large warm amber lump, whole, rounded and unbroken. Everything except that lump is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, food, bread, milk, sugar cubes, scissors, knives, tools, machinery
```

## 120. m_fat_breakdown — 지방 방울이 잘게 쪼개져 빠져나가고 세포가 쪼그라들며, 떨어져 나온 조각

쓰는 topic 3편 · m_fat_accumulation(16번, 다른 배치)의 역방향이라 호박색 지방 방울이라는 색 배역을 일부러 맞췄다 — 구분 장치는 세포가 부푸는 게 아니라 쪼그라들며 벽이 주름지고, 방울이 잘게 쪼개져 옆 통로로 빠져나간다는 점.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. An extreme close-up of a cluster of large round fat cells packed together and filling most of the frame, seen from the side at eye level; each cell is swollen tight around one single big warm amber droplet that takes up nearly the whole cell, its thin pale cyan wall stretched around it. Along one side of the frame a narrow clear channel runs between the cells, empty. Everything except the droplets is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, food, butter, oil, honey, bubbles, foam, balloons
```

## 121. m_metabolic_slowdown — 세포 속 에너지 공장들의 불빛이 하나씩 어두워지고 주변으로 퍼지던 열 아

쓰는 topic 3편 · 호박색 없음 — 에너지 소비 감소는 물질이 아니라 밝기·열 아지랑이로만 표현. 구분 장치: m_blood_flow_drop(관 안의 흐름 감소)과 달리 혈관이 화면에 아예 없고 세포 내부 소기관의 발광만 다룬다 — 공급이 아니라 소비가 줄어드는 그림.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D cell interior, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The inside of one single large cell, its outer boundary curving just inside the frame edges, filled with clear fluid. Floating in that fluid, spread evenly through the middle of the frame, are about a dozen bean-shaped organelles seen from the side, each one cut open so the tightly folded ridges inside it are visible, and each one glowing brightly from within. A faint shimmer of rising heat ripples upward off every organelle into the fluid around it. Everything is translucent pale cyan glass and nothing in the image is amber or orange. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, fire, flames, factory, machinery, gears, light bulb, circuit
```

## 122. m_mineral_erosion — 산 방울이 단단한 광물 표면에 닿아 표면이 미세하게 녹아내리고, 아래로 

쓰는 topic 3편 · 호박색 = 산. 구분 장치: m_acid_secretion은 산이 '나오는' 위샘 컷, 여기는 산이 '무엇을 녹이는지' — 살아있는 세포(m_cell_damage)가 아니라 곧은 무기질 프리즘 기둥과 그 사이로 뚫리는 터널이 주인공이라 통통한 세포를 --no로 뺐다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D tooth enamel, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A thick slab of hard mineral enamel seen from the side at eye level, like a slice cut out of a cake, centered in the lower half of the frame with open dark empty space above it. The slab is built from dense straight mineral prisms standing upright side by side, packed tight, their long edges clearly visible through the translucent cut face, and the top surface facing straight up is perfectly smooth and glassy. Resting on that smooth top surface are a few separate round beads of warm amber liquid. Everything except the amber beads is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, whole tooth, row of teeth, smile, mouth, gums, dentist, soft tissue, cells, gemstone, ice cube
```

## 123. m_motility_slowdown — 관을 따라 내용물을 밀어내던 연동 수축파가 점점 느려지고 약해지다 멈춰,

쓰는 topic 3편 · 호박색 없음 — 움직임이 사라지는 기전이라 형태와 리듬으로만. 구분 장치: 긴 관을 따라 내려오는 '고리 수축파'가 주인공이라 m_emptying_delay(주머니 출구)·m_stasis_thickening(주머니 안 농축)과 화면이 다르고, 내용물이 관 중간에 멈춰 선 채 끝난다.

```
Medical holographic visualization, extreme microscopic close-up of a translucent glass-like 3D tube of gut, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One long tube runs straight down the centre of the frame from the top edge to the bottom edge, sliced open lengthwise so the channel inside is visible along its whole length. Wrapped around the outside of the tube at regular intervals are several separate ring-shaped bands of muscle fibres; the ring nearest the top is squeezed into a tight narrow waist while all the rings below it are loose and wide. Inside the channel, just under that tight waist, sits one rounded mass of soft pale cyan contents being pushed downward. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, pipe, plumbing, hose, worm, snake, anatomy chart
```

## 124. m_pathogen_ascent — 세균이 요도·요관 같은 통로를 타고 아래에서 위 장기로 거슬러 올라가는 

쓰는 topic 3편 · 호박색 = 세균. 구분 장치: m_bacteria_growth는 한 평면에서 분열·증식하는 컷이라 이동이 없다 — 여기서는 분열을 전혀 보여주지 않고 '아래에서 위로 거슬러 올라가는 이동'만 보여주며, 아래로 흐르는 액체와 반대 방향이라는 걸 화면에 넣어 상행임을 못 박았다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D urinary anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One narrow tube runs straight up the centre of the frame from the bottom edge, sliced open lengthwise so its inner wall is visible along its whole length, and at the top it opens out into the hollow inside of a larger rounded chamber that occupies the upper third of the frame and is also cut open. A thin trickle of clear pale cyan fluid runs down the inside of the tube. Clinging to the tube wall down at the bottom end is a tight cluster of small warm amber rod-shaped bacteria, all still low and none of them yet inside the chamber above. Everything except those rods is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, petri dish, mould, hair, worms, snakes, whole organ, kidney silhouette
```

## 125. m_plaque_buildup — 혈관 안벽에 기름때(죽상경화반)가 층층이 쌓여 통로가 점점 좁아짐

쓰는 topic 3편 · 호박색 = 죽상경화반(기름때). 구분 장치: m_waste_buildup은 두 표면 사이 공간에 뾰족한 바늘 결정이 '떨어져 쌓이는' 컷 — 여기는 결정이 아니라 부드러운 층이 혈관 안벽에 '눌어붙어' 내강을 좁히는 컷이라 바늘·결정 형태를 --no로 뺐다.

```
Medical holographic visualization, extreme microscopic close-up of a translucent glass-like 3D artery, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One thick vessel runs straight down the centre of the frame from the top edge to the bottom edge, sliced open lengthwise so the open channel inside is fully visible along its whole length. The channel is wide and evenly round and its inner wall is smooth and glossy, with small smooth disc-shaped cells drifting freely down it. Lying flat against the inner wall on the right side, halfway down, is one thin low streak of warm amber deposit, barely raised off the wall. Everything except that amber deposit is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, pipe, plumbing, rust, grease, food, needle crystals, spikes
```

## 126. m_rem_atonia_fault — 렘수면 중 몸을 잠가두는 스위치가 오작동해 늦게 풀리거나(가위눌림) 아예

쓰는 topic 3편 · 호박색 없음 — 스위치 오작동은 물질이 아니라 조임 고리의 형태와 신호 밝기로만. 대응 기전이 기존 라이브러리에 없어 비교 대상이 없다. 글자·UI 없이 '스위치'를 표현해야 해서 기계 부품(레버·스위치·기어)을 --no로 빼고 생체 조직으로 된 조임 고리로 그렸다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D nerve and muscle anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One thick nerve trunk descends from a rounded mass of tissue at the very top edge of the frame, running straight down through the exact centre. Halfway down, a single smooth collar of ring-shaped tissue wraps all the way around the trunk and is clamped shut on it, pinching it closed. Below the collar the trunk fans out into several loose muscle bundles that lie limp and slack across the bottom third of the frame, completely still and dim. Above the collar the trunk is bright and taut. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, metal clamp, gears, switch, lever, machinery, bed, sleeping person, whole brain
```

## 127. m_sebum_overproduction — 피지샘이 부풀어 기름을 과하게 밀어내고 모공 주변에 쌓이는 그림

쓰는 topic 3편 · 호박색 = 과하게 분비된 피지(과한 물질). 구분 장치: m_mucus_barrier는 조직 위에 '연속된 보호 젤 층'이 얹힌 그림 — 여기는 층이 아니라 모공이라는 구멍과 그 옆에 붙은 포도송이 샘이 주인공이고, 기름이 모공 밖으로 밀려 나와 고이는 방향이다. 층 구조를 안 쓰므로 빵/크림층 오답도 함께 차단했다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D scalp skin, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A thick slab of skin seen from the side at eye level, like a slice cut out of a cake, centered in the lower two thirds of the frame with open dark empty space above it. One narrow pore runs down into the slab from its flat top surface, clearly visible through the translucent cut face, with a single hair shaft standing straight up out of it. Attached to the side wall of that pore, halfway down, is a small tight bunch of rounded grape-like sacs. A thin film of warm amber oil coats the inside of the pore. Everything except the amber oil is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, head of hair, wig, scalp photograph, honey jar, bubbles, foam
```

## 128. m_vasoconstriction — 혈관 벽 근육이 오므라들며 통로가 확 좁아져 말단까지 가던 피가 줄어듦

쓰는 topic 3편 · 호박색 없음 — 수축은 물질이 아니라 형태·밝기로만. 구분 장치: m_blood_flow_drop은 관을 길게 갈라 '내강과 그 안의 원반 세포'를 보는 컷이라, 여기는 일부러 자르지 않고 겉에서 본 가지 전체의 바깥 지름이 한꺼번에 줄어드는 그림으로 잡았다(말단 모세고리까지 같이 조여드는 게 수족냉증의 핵심). 단면 컷 자체를 --no로 차단했다.

```
Medical holographic visualization, extreme microscopic close-up of a translucent glass-like 3D blood vessel seen from the outside, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One thick vessel enters from the top edge of the frame and branches downward into thinner and thinner limbs that end in tiny hairpin loops across the lower third. The vessel is shown whole from the outside, not cut open, its outer surface unbroken, and every limb is wide and roundly swollen. A continuous spiral band of muscle fibres winds around the outside of the trunk and each branch like a loose coil, its turns spaced far apart. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, blood colour, cut-open cross-section, sliced tube, rope, cable, tree roots, plant
```

## 129. m_volatile_exhalation — 혈류를 타고 온 냄새 분자가 폐포 벽과 땀샘 구멍을 통과해 몸 밖으로 빠

쓰는 topic 3편 · 호박색 = 냄새 분자. 구분 장치: m_toxin_load는 굽은 통로를 따라 호박색이 '들어와' 세포에 스며드는 방향 — 여기는 세 컷 모두 호박색이 조직에서 빠져나가 빈 공간·허공으로 향하는 바깥 방향이고, 마지막 컷을 폐포에서 땀구멍으로 옮겨 배출 경로가 둘이라는 걸 보여준다. m_odor_compound_release(피부 표면 세균)와 달리 세균이 한 마리도 안 나온다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D lung tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One rounded hollow air sac occupies the right half of the frame, cut open so that its inside is completely empty dark space, and one narrow vessel runs up the left half, also cut open lengthwise. Between them stands a single paper-thin shared wall, seen edge on down the middle of the frame. Drifting in the fluid inside the vessel on the left are a dozen tiny warm amber particles, all of them still on the vessel side and none of them in the empty air space yet. Everything except those particles is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, smoke, fog, steam, perfume bottle, nose, mouth, whole lung
```

## 130. m_airway_blockage — 음식물이 식도 대신 기도로 들어가 통로를 막는다

쓰는 topic 2편 · 호박색 = 기도로 잘못 들어간 음식물 덩어리. 구분 장치: m_pressure_buildup은 닫힌 주머니가 부풀어 압력이 오르는 컷 — 여기는 압력이 아니라 '두 갈래 중 잘못된 쪽'이 핵심이라, 연골 고리가 있는 관(기도)과 매끈한 관(식도)을 한 화면에 나란히 두어 어느 쪽으로 들어갔는지가 글자 없이 보이게 했고, 마지막 컷은 부풀지 않고 오히려 빨려 들어가 찌그러진다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D throat anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One wide passage comes down from the top edge of the frame and forks into two tubes that run side by side to the bottom edge, both sliced open lengthwise so their channels are visible. The left tube is ringed along its whole length by stacked hoops of stiff cartilage; the right tube has smooth soft walls and no rings at all. Sitting in the fork right where the two tubes divide is one rounded lump of warm amber mass, tipped slightly toward the ringed left tube. Everything except that lump is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, food photograph, meat, throat photograph, person choking, neck
```

## 131. m_autoimmune_attack — 면역세포들이 침입자가 아니라 자기 조직에 달라붙어 표면을 뜯어내고, 그 

쓰는 topic 2편 · 호박색 = 면역세포(캐논 m_inflammation과 같은 색 규칙). 구분 장치: m_inflammation은 화면 가운데를 가로지르는 관에서 호박색 세포가 '쏟아져 나와' 조직이 부풀어 오르는 컷이라 관을 아예 화면에서 뺐고(--no tube, vessel), 여기서는 조직이 부풀지 않고 뜯겨 패인다. 부풀어 오르는 돔 형태도 --no로 차단.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A wide surface of tightly packed plump pale cyan cells fills the lower two thirds of the frame, seen from a low angle so the surface runs back and away, every cell smooth and whole and the wall between them unbroken. Hovering in the dark space just above that surface are about eight small round warm amber cells, spread apart and none of them touching the surface yet. There is no tube and no vessel anywhere in the image. Everything except those amber cells is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, tube, vessel, blood vessel, bacteria rods, virus, fire, flames, red glow, swelling dome
```

## 132. m_blood_loss — 관 벽의 열린 자리에서 피가 계속 흘러 빠져나가고, 관 안을 채우던 붉은

쓰는 topic 2편 · 호박색 없음 — 빠져나가는 건 해로운 물질이 아니라 제 몸의 적혈구다. 구분 장치: m_blood_flow_drop은 관이 좁아져 흐름이 막히는 컷이라 여기서는 관 지름이 끝까지 그대로라는 걸 못 박았고(--no narrowed channel), 줄어드는 건 통로가 아니라 '남은 원반 개수'다. m_microvessel_damage(파열 순간)와 달리 터지는 장면 없이 계속 새어 나가는 지속 상태를 보여준다.

```
Medical holographic visualization, extreme microscopic close-up of a translucent glass-like 3D vessel, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One thick vessel runs straight down the centre of the frame from the top edge to the bottom edge, sliced open lengthwise so the channel inside is visible along its whole length. The channel is wide, evenly round and densely crowded with small smooth disc-shaped cells drifting downward shoulder to shoulder. Halfway down the right-hand wall there is one clean open gap in the wall, and two or three disc cells are just beginning to slip out through it into the dark empty void outside. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, blood colour, wound photograph, bandage, knife, narrowed channel, plaque
```

## 133. m_bone_density_loss — 뼈 속 격자 구조의 기둥들이 가늘어지고 끊기면서 구멍이 커져 성글어짐

쓰는 topic 2편 · 호박색 없음 — 쌓이는 물질이 아니라 조직이 비어가는 기전. 구분 장치: m_waste_buildup은 결정이 '쌓여' 공간을 채우는 정반대 컷이라, 여기서는 화면에 새로 들어오는 입자가 하나도 없고 원래 있던 격자가 가늘어지고 끊어지는 것만 보여준다. 납작한 벌집 무늬로 나오면 입체감이 죽어서 --no에 flat grid·honeycomb pattern을 넣었다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D bone interior, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A three-dimensional lattice of thick interlocking struts and flat plates fills the whole frame, seen from slightly above and to one side so that its depth is clear, layer behind layer receding into the dark. The struts are solid and heavy, the small hollow spaces between them tight and even, and the whole block sits square in the middle of the frame with dark void at the edges. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, coral, sponge, honeycomb pattern, flat grid, skull, skeleton, x-ray film
```

## 134. m_electrical_misfire — 심장을 도는 전기 신호가 흐트러져 박동 순서가 뒤엉키거나 한 박자 일찍 

쓰는 topic 2편 · 호박색은 '한 박자 일찍 튀는 이상 발화점' 딱 한 곳만 아주 옅게(캐논의 통증 지점 규칙과 같은 취급) — 나머지는 전부 청록. 구분 장치: m_nerve_overdrive는 두 신경 말단 사이 틈과 소켓이 주인공이라, 여기는 넓은 근육 면 위를 퍼지는 '원형 파면'과 그 충돌·소용돌이가 주인공이다. 심전도 그래프·번개 아이콘이 나오면 글자·기호 금지 규칙이 깨져서 --no에 넣었다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D heart muscle wall, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A broad sheet of heart muscle seen from just above its inner face, filling the frame, its fibres woven into long sweeping bands that curve across the surface. Spread over those bands lies a fine network of pale conducting strands that all branch outward from one small rounded node in the upper third of the frame. A single bright ring of light is spreading out from that node in one even circle across the sheet. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, ECG line, heartbeat graph, waveform, lightning bolt, circuit board, wires, electronics, whole heart organ, anatomical heart
```

## 135. m_eye_elongation — 안구의 앞뒤 길이가 늘어나면서 초점이 망막보다 앞쪽에 맺혀 상이 흐려짐

쓰는 topic 2편 · 호박색 없음 — 광학적 초점 어긋남이라 형태와 선명도로만. 기존 라이브러리에 대응 기전이 없어 구분 대상이 없다. 안구는 가로로 긴 피사체라 9:16에서 위아래 여백을 명시해 모서리 쏠림을 막았고, 실사 눈·안경·시력표가 끼어들지 않게 --no로 차단했다.

```
Medical holographic visualization, extreme microscopic close-up of a translucent glass-like 3D eyeball, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling the middle of the frame with open dark empty space above and below it, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One eyeball seen from the side and cut open along its length so its whole inside is visible, perfectly round in shape. A rounded lens sits just inside the front of the globe on the left, and the smooth thin inner rear wall curves across the back on the right. Three straight thin beams of light come in from the left, bend as they pass through the lens and meet at one sharp point exactly on the rear wall. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, eyelashes, eyebrow, iris photograph, realistic eyeball, glasses, spectacles, eye chart, diagram
```

## 136. m_glucose_crash — 혈당이 기준선 아래로 뚝 떨어져 뇌와 근육의 연료가 바닥나고 떨림·식은땀

쓰는 topic 2편 · 호박색 = 당 입자이되 '사라지는' 방향. 구분 장치: m_glucose_spike는 장벽 융모에서 호박색이 혈관으로 쏟아져 들어와 꽉 차는 컷이라, 여기는 시작 프레임부터 이미 꽉 찬 상태에서 출발해 빠져나가고, 마지막 컷에 호박색이 화면에 하나도 안 남는다 — 연료 고갈과 떨림이 결론이다. 그래프·화살표로 하락을 그리면 글자 금지 규칙이 깨져서 --no로 뺐다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. Two layers stacked with a clear gap between them, both seen from the side at eye level. The upper layer is one thick vessel running horizontally across the frame, sliced open lengthwise so its channel is visible, and that channel is crowded wall to wall with small warm amber spheres. The lower layer is a block of tissue made of plump rounded pale cyan cells, brightly lit and full. Everything except the amber spheres is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, sugar cubes, candy, food, graph, chart, gauge, arrow pointing down
```

## 137. m_joint_deformity — 반복 압박으로 관절 축이 틀어지고 뼈가 튀어나온다

쓰는 topic 2편 · 호박색 없음 — 축이 틀어지는 기전이라 형태로만. 구분 장치: m_cartilage_wear는 덮개가 닳아 얇아지는 게 주인공이라, 여기서는 덮개 두께가 아니라 '두 축이 일직선에서 어긋나는 각도'와 한쪽으로 튀어나오는 뼈 혹이 결론이다 — 시작 프레임에서 두 축이 일직선이고 양쪽 인대가 팽팽하다는 걸 못 박아 변화가 읽히게 했다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D joint anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. Two bone ends meet in the exact centre of the frame, one shaft coming down from the top edge and one rising from the bottom edge, seen from the side. Both facing ends are capped with a smooth glassy layer and a thin even gap separates them, the two caps perfectly parallel. The two shafts line up in one straight column, and a taut band runs down each side of the joint holding them in line. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, hand photograph, finger, x-ray film, skeleton, robot, hinge, machinery
```

## 138. m_keratin_thickening — 각질층이 겹겹이 두껍게 쌓여 딱딱해진다

쓰는 topic 2편 · 호박색 없음 — 각질은 해로운 물질이 아니라 제 조직이다. ⚠️ 1차 시안 탈락 사유(불투명한 흰 층이 얹힌 빵·케이크)가 가장 크게 재현될 항목이라 '층이 쌓인다'는 말을 쓰되 유리판이라는 걸 반복 명시하고 --no에 pastry·puff pastry·croissant·layered cake·paper stack까지 추가했다. 구분 장치: m_cell_overgrowth는 세포가 덩어리로 불어나는 컷, 여기는 납작한 판이 겹겹이 포개져 두꺼워지는 컷이다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D skin, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A thick slab of skin seen from the side at eye level, like a slice cut out of a cake, centered in the lower half of the frame with open dark empty space above it. Stacked from bottom to top: a base of plump rounded living cells; and directly above them only three or four flat thin plates lying stacked one on another like panes of clear glass, their cut edges visible through the translucent face. Every single layer, the plates included, is the same translucent pale cyan glass, all of it see-through, and no layer is white, pale, creamy or opaque. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, pastry, puff pastry, croissant, layered cake, sliced cake, paper stack, plywood, sandwich
```

## 139. m_lipid_oxidation — 피지 방울 속 지방산 사슬이 산소 알갱이와 만나 끊기고, 끊긴 조각이 새

쓰는 topic 2편 · 호박색 = 끊겨서 새로 생긴 냄새 분자(원래 지방 사슬은 청록 그대로). 구분 장치: m_bacteria_growth·m_odor_compound_release는 세균이 주인공이라 이 topic의 반전('안 씻어서가 아니다')이 무너진다 — 그래서 시작 이미지와 세 컷 모두 세균이 한 마리도 없다는 걸 명시하고 --no에도 bacteria·rods·microbes를 넣었다. 냄새가 생기는 순간이 세포가 아니라 사슬이 끊기는 순수 화학 반응임이 화면에서 읽힌다.

```
Medical holographic visualization, extreme microscopic close-up of a translucent glass-like 3D oil droplet, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One single large round droplet of oil sits in the exact centre of the frame and fills most of it. Inside the droplet, long straight chain-like molecules lie parallel to one another like fine threads, every chain whole and unbroken along its length, clearly visible through the droplet's clear skin. Drifting in the dark void around the droplet are a few tiny paired round particles. Everything is translucent pale cyan glass and nothing in the image is amber, and there are no bacteria anywhere. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, bacteria, rods, microbes, petri dish, mould, oil bottle, cooking pan, flame, smoke
```

## 140. m_motility_speedup — 관을 따라 연동 수축파가 평소보다 빠르고 강하게 몰아쳐 내용물이 흡수될 

쓰는 topic 2편 · 호박색 없음 — 방향과 속도만 다른 기전. 구분 장치: m_motility_slowdown과 같은 해부 구조를 일부러 그대로 쓰되 시작 프레임부터 반대 상태로 잡았다 — 고리가 둘이나 이미 조여 있고, 내용물이 덩어리가 아니라 묽은 액체이며, 융모가 눌려 있어 '흡수될 틈이 없다'가 화면에서 읽힌다. m_muscle_tension(뭉쳐 굳음)과 달리 근육은 한 번도 멈추지 않는다.

```
Medical holographic visualization, extreme microscopic close-up of a translucent glass-like 3D tube of gut, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One long tube runs straight down the centre of the frame from the top edge to the bottom edge, sliced open lengthwise so the channel inside is visible along its whole length. Wrapped around the outside are several ring-shaped bands of muscle fibres, and two of the rings near the top are already squeezed into tight narrow waists close behind one another. The channel inside holds thin watery contents rather than any solid mass, and the tall thin folds lining the channel wall are pressed flat by the rush. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, pipe, plumbing, hose, worm, snake, anatomy chart
```

## 141. m_ph_disruption — 표면을 덮고 있던 산성 보호막이 씻겨 벗겨지고, 그 자리를 지키던 막대 

쓰는 topic 2편 · 호박색 없음이 곧 구분 장치다 — m_bacteria_growth의 호박색 막대는 침입자라 늘어나지만, 여기 막대(유산균)는 이로운 쪽이라 색 규칙상 청록이고 숫자가 줄어든다. m_mucus_barrier는 젤 층이 얇아지는 게 주인공이라, 여기서는 막이 벗겨지는 건 1컷으로 끝내고 2·3컷을 '유산균이 쓸려나간 빈 표면'에 쓴다(여성_24의 감별 포인트).

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D mucosal tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A wide flat tissue surface seen from a low skimming angle just above it, running from the bottom edge of the frame back toward a horizon line in the upper third, with open dark empty space above. The whole surface is covered by one thin continuous film with a faint glossy sheen, and standing upright in that film, packed close together like a dense field, are dozens of long slender rod-shaped bacteria. Those rods are made of exactly the same translucent pale cyan glass as the tissue beneath them and nothing in the image is amber or orange. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, petri dish, mould, hair, yogurt, foam
```

## 142. m_pigment_loss — 색소 알갱이를 만들어 뿌리던 세포가 멈추고, 이미 뿌려진 알갱이가 흩어지

쓰는 topic 2편 · 호박색 없음 — 색소는 해로운 물질이 아니므로 색이 아니라 '진한 청록 vs 옅은 청록'의 명도 차로만 표현했다(색 규칙의 형태·밝기 조항). 구분 장치: 기존 15종에 색소 장면이 없어 비교 대상이 없고, 대신 '왜 그 자리만 밝아지는가'가 결론이 되도록 마지막 컷에서 주변은 어두운 채로 남기고 가운데 한 구역만 비워 대비를 만들었다. 갈색·잉크로 새면 규칙이 깨져서 --no에 brown·ink·paint를 넣었다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D skin, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A thick slab of skin seen from the side at eye level, like a slice cut out of a cake, centered in the lower two thirds of the frame with open dark empty space above it. Along the very bottom of the slab sits a row of wide flat cells, each one sending several fine branching arms upward between the plump cells stacked above them. Scattered along those arms and through the upper cells are dense grains of a much darker slate teal, far darker than everything around them, thickest in one patch at the centre of the slab. Every structure is the same translucent glass; only those grains are dark, and nothing in the image is amber or orange. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, brown, paint, ink, spray can, skin photograph, freckles, tattoo
```

## 143. m_protein_clouding — 투명하던 단백질이 활성산소에 변성돼 뭉치면서 뿌옇게 흐려지고 빛이 통과하

쓰는 topic 2편 · 호박색 = 활성산소 입자(해로운 물질). 단백질 자체는 끝까지 청록이고 '정렬→엉킴, 투과→산란'이라는 광학 변화만 일으킨다. 구분 장치: m_cell_damage는 세포가 쪼그라들고 갈라지는 컷이라 세포가 아예 안 나오고, 변화의 결론이 파괴가 아니라 '빛이 통과하지 못함'이다. 뿌옇게 그리다 흰 안개로 새면 캐논의 흰 층 오답이 되살아나서 --no에 milk·fog·white haze를 넣었다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D lens protein, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A block of lens tissue fills the middle of the frame, built from long thin protein strands lying in perfectly ordered parallel rows, evenly spaced and all pointing the same way, so clear that a single straight beam of light passes right through the block from the left edge to the right edge without spreading or scattering at all. A few tiny sharp-edged warm amber specks drift in the dark void just outside the block, none of them inside it yet. Everything except those specks is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, whole eyeball, iris, glasses, milk, smoke, fog, white haze
```

## 144. m_pump_failure — 펌프가 힘을 잃어 짜내는 양이 줄고, 내보내지 못한 피가 뒤로 밀려 고임

쓰는 topic 2편 · 호박색 없음 — 수축력 저하는 물질이 아니라 벽의 두께·수축 폭으로만. 구분 장치: m_blood_flow_drop은 관이 좁아지는 혈관 쪽 컷이라 여기는 관이 아니라 '주머니 벽 자체'가 주인공이고, 좁아지는 게 아니라 늘어나 헐렁해진다. m_pressure_buildup은 배출로가 막혀 압력이 오르는 컷인데 여기는 출구가 끝까지 열려 있고 밀어낼 힘이 없어서 뒤로 고인다는 게 차이다.

```
Medical holographic visualization, extreme microscopic close-up of a translucent glass-like 3D muscular chamber, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One rounded chamber sits in the middle of the frame, seen from the side and cut open so its hollow inside is visible. Its wall is thick and heavy with tightly woven muscle fibres running in sweeping bands, and right now the chamber is squeezed down small and nearly empty. One outlet tube leaves the top of the chamber with clear pale cyan fluid streaming strongly out through it, and one inlet tube enters at the lower left, full and waiting. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, blood colour, whole heart organ, anatomical heart, mechanical pump, piston, balloon
```

## 145. m_reflux_backflow — 관 끝의 조임근이 느슨하게 벌어지면서 아래 주머니의 내용물이 정상 흐름과

쓰는 topic 2편 · 호박색 = 위 내용물(산). 구분 장치: m_acid_secretion은 위샘에서 산이 분비되는 제자리 컷이라 방향이 없다 — 여기는 조임근이라는 경계와 그 위아래를 한 화면에 두어 '어디서 어디로' 올라가는지가 읽히게 했고, 세 컷 모두 호박색이 위쪽으로만 움직인다. m_pressure_buildup은 배출로가 막혀 흐름이 멈춘 그림이라 이쪽의 역류와 반대다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D digestive anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One long narrow tube runs down the centre of the frame from the top edge and meets the top of a rounded pouch that fills the lower third, both of them sliced open lengthwise so their insides are visible. Where the tube joins the pouch, a single thick ring of muscle wraps right around the tube's lower end and is drawn shut tight, so the whole length of tube above it is empty and clear. Lying in the bottom of the pouch below that closed ring is a still pool of warm amber liquid. Everything except the amber pool is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, whole stomach organ, anatomy chart, bottle, glass of drink, funnel
```

## 146. m_sensory_decline — 감각 수용기와 신호 전달이 둔해져 통증·갈증 신호가 늦게 온다

쓰는 topic 2편 · 고령_14·고령_8. 감각 저하는 물질이 아니라 호박색 없이 수용기 크기·펄스 밝기/속도로만. m_nerve_overdrive(과흥분)와 정반대 방향이라 펄스가 약해지고 느려지는 게 핵심.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A slab of tissue seen from the side at eye level, its flat top surface facing straight up, filling the lower two thirds of the frame with open dark empty space above it. Just under the top surface sits a cluster of about eight small bulb-shaped sensory endings, plump and bright, clearly visible through the translucent cut face. From the cluster one single nerve fibre runs down through the slab and off the bottom edge of the frame, wrapped along its whole length in a smooth thick even sheath. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, electronics, cables, wires, diagram, flat illustration
```

## 147. m_sweat_overproduction — 교감신경 신호에 땀샘이 과하게 반응해 땀이 쏟아진다

쓰는 topic 2편 · 손발_10·손발_2. 땀은 해로운 물질이 아니라 청록 유지, 과흥분 신호만 호박색(m_nerve_compression의 '오작동 신호만 amber' 선례). m_dehydration(표면이 마름)과 방향이 반대.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A cross-section block of skin seen from the side at eye level, its flat top surface facing straight up, filling the lower two thirds of the frame with open dark empty space above it. Inside the block sit three tightly coiled ball-shaped glands, each one a bundle of coiled tube deep in the tissue, and from each ball a single narrow duct spirals straight up to a tiny round pore on the top surface, all clearly visible through the translucent cut face. One fine nerve fibre enters from the left edge and wraps around each coiled ball in turn. The top surface is dry and unbroken. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, water droplets on glass, rain, foam
```

## 148. m_vagal_slowdown — 미주신경이 과하게 작동해 심장에 브레이크를 걸어 박동이 뚝 느려짐

쓰는 topic 2편 · 순환_11·순환_12. 부교감 과작동은 물질이 아니라 호박색 없이 박동 리듬·밝기로만. m_nerve_overdrive는 '켜짐이 과함', 이건 '과한 신호로 기능이 꺼짐'이라 리듬이 느려지는 게 구분점.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A thick nerve cord enters the frame at the top left and runs down to the middle of the frame, where it fans into fine branches that spread over the upper wall of one rounded hollow muscular chamber. The chamber sits in the lower half of the frame, seen from the side and cut open so its thick banded wall and its hollow inside are fully visible, the wall relaxed and evenly thick. Open dark empty space fills the upper right of the frame. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, blood colour, whole heart anatomy chart, machinery, pump
```

## 149. m_vitreous_floaters — 눈 속을 채운 젤이 묽어지며 생긴 혼탁 덩어리가 떠다니고 그 그림자가 망

쓰는 topic 2편 · 눈_26·눈_8. 부유물 자체가 아니라 '망막에 지는 그림자'가 주인공이라 Shot 3에서 그림자가 한 박자 늦게 따라오게 명시. 호박색 없음.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The view is from inside one large rounded chamber filled with clear gel. The far wall curves across the whole background as a smooth concave surface carpeted in a fine even mat of tiny light-sensing cells. The near half of the frame is open clear gel, and a few very fine transparent strands hang suspended in it, well separated and barely visible. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, eyeball exterior, iris, pupil, eyelashes, face, dust particles, bokeh lights
```

## 150. m_wake_signal_loss — 뇌를 깨워두는 신호물질(오렉신)을 내보내던 세포가 사라져 각성 스위치가 

쓰는 topic 2편 · 수면_20·수면_6(기면증 계열). 각성 신호물질은 해로운 게 아니라 호박색 금지 — 세포 수 감소와 밝기 소실로만. m_cell_damage와 달리 '신호가 끊긴다'는 연결까지 Shot 3에 담음.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A dense cluster of about forty small round cells is packed together in the exact centre of the frame, each cell lit brightly from within, and long thin fibres reach out of the cluster in every direction to all four edges of the frame. Everything around the cluster is open dark empty void. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, stars, galaxy, fireworks, network diagram, circuit board
```

## 151. m_acid_deficiency — 주머니 벽의 분비샘에서 산 방울이 거의 맺히지 않아 내용물이 분해되지 않

쓰는 topic 1편 · 소화_25. m_acid_secretion과 정확히 정반대 장면이라 같은 '케이크 조각' 판 구도를 일부러 재사용해 짝으로 읽히게 했다. 호박색은 쓰되 분량을 극단적으로 적게 — 산이 넘치는 컷과 착각되면 편의 반전이 화면에서 뒤집힌다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A thick slab of stomach wall seen from the side at eye level, like a slice cut out of a cake, centered in the lower half of the frame with open dark empty space above it. The top surface of the slab faces straight up and is dotted with small round pit openings; below each opening a narrow tube-shaped gland runs down into the tissue, and every gland is visibly shrunken, narrow and shallow, clearly visible through the translucent cut face. Resting on the top surface sit three large ragged unbroken lumps of undigested food matter. Only two or three tiny warm amber droplets cling at the mouths of a couple of pits, and there is no pool or film of liquid anywhere. Everything except those few droplets is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, sausage, cake, pool of liquid, flood, thick liquid layer, glossy film
```

## 152. m_blood_shunting — 피가 한 장기(소화기)로 한꺼번에 몰리면서 다른 부위(뇌)로 갈 몫이 부

쓰는 topic 1편 · 어지럼증_13(식후 저혈압). 총량은 그대로인데 배분이 쏠리는 게 핵심이라 두 갈래를 같은 굵기로 시작시키고 Shot 3에서 한쪽만 어두워지게 했다. 혈액은 캐논상 청록이라 호박색 없음(m_blood_flow_drop 선례).

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One thick vessel runs up the centre of the frame from the bottom edge and forks in the middle into two branches of equal width, one leaving to the upper left and one to the upper right, all of it sliced open lengthwise so the open channels inside are visible along their whole length. Dozens of small smooth disc-shaped cells flow up the trunk and split evenly into both branches. Behind the upper left branch lies a wide bed of tall thin finger-like folds; behind the upper right branch lies a fine dense web of thread-like fibres. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, blood colour, pipe, plumbing, tree, roots
```

## 153. m_bone_stress — 뼈와 골막에 반복 충격이 쌓여 미세골절로 진행한다

쓰는 topic 1편 · 근골격_25(피로골절). 반복 충격은 물질이 아니라 형태로만 — 마지막 통증 지점에만 옅은 amber(m_muscle_tension 선례). m_bone_density_loss(격자가 성글어짐)와 달리 격자는 그대로 두고 껍질에 금이 가는 컷.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A thick column of bone runs from the top edge of the frame to the bottom edge through the exact centre, seen from the side at eye level and cut open lengthwise so the dense outer shell and the fine honeycomb lattice filling the inside are both clearly visible. A thin smooth membrane sheathes the outer surface of the column along its whole length, with fine vessels running through it. The shell is unbroken, even and smooth everywhere. Open dark empty void fills both sides of the frame. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, skull, skeleton, full body, marble, stone texture
```

## 154. m_core_temp_drop — 잠들기 직전 심부체온이 내려가야 잠이 오는데, 더위·이불 다툼으로 그 하

쓰는 topic 1편 · 수면_13(열대야). 열을 호박색으로 쓰면 '해로운 물질만 amber' 규칙이 깨져 전 라이브러리가 흔들린다 → 밝기만으로 체온 표현, --no에 fire/thermal/heat map까지 박음. 이불은 in-world 유지 위해 'smooth featureless slab'으로.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A cross-section block of deep body tissue seen from the side at eye level, its flat top surface facing straight up, filling the lower two thirds of the frame with open dark empty space above it. Deep in the middle of the block sits a rounded core region that glows clearly brighter than everything around it. From that core, fine vessels branch outward and upward and end in dense tight loops just beneath the flat top surface; those loops are narrow and pinched shut. Everything is translucent pale cyan glass and nothing is a different colour, only a different brightness. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, fire, flames, thermal image, heat map, orange gradient, blanket, bed, fabric
```

## 155. m_dopamine_loop — 자극이 하나 끝날 때마다 보상물질이 새로 분비돼 계속 다음 자극을 찾게 

쓰는 topic 1편 · 수면_14(자기 전 숏폼). m_nerve_overdrive와 달리 '반복 순환'이 핵심이라 Shot 2~3에서 분비-소진-재장전 사이클이 점점 빨라지고 얇아지게. 보상물질은 '과한 물질'로 보고 amber 허용.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. Two thick nerve endings face each other across a narrow empty gap in the middle of the frame, one coming down from the top and one rising from the bottom, both seen from the side. The flat face of the upper ending is backed by a cluster of about a dozen small round sacs pressed up against it, and a few tiny warm amber particles are held inside those sacs. The flat face of the lower ending is covered in small round open sockets, all of them empty. Nothing has crossed the gap yet. Everything except the particles inside the sacs is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, diagram, cross-section chart, flat illustration, pills, capsules
```

## 156. m_ectopic_implantation — 떨어져 나온 조직 조각이 흘러가다 엉뚱한 표면에 내려앉아 달라붙고, 그 

쓰는 topic 1편 · 여성_10(자궁내막증). '위치가 틀렸다'가 질환의 정의라 떠다니는 동안은 청록, 착상 후에만 호박색으로 바뀌게 해 이동 자체가 읽히게 했다. m_tissue_invasion과 짝으로 방향이 반대.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A wide smooth glossy tissue surface runs across the lower third of the frame, seen from a low skimming angle just above it, with open dark fluid-filled space above it taking up the rest of the frame. One small ragged flake of tissue with torn edges drifts in that open space above the surface, tumbling slowly, not touching the surface yet and casting no shadow. The surface below is unbroken and featureless. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, leaf, petal, snow, feather, insect
```

## 157. m_fibrosis — 결합조직이 두껍고 질기게 변해 오그라들며 당긴다

쓰는 topic 1편 · 손발_22(듀피트렌 구축 계열). m_cell_overgrowth가 덩어리 증식이면 이쪽은 띠·끈이 굵어지며 당기는 수축이라 마지막 컷에서 표면이 오그라드는 게 구분점. 호박색 없음.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A block of tissue seen from the side at eye level, its cut face toward the camera and its flat top surface facing straight up, filling the lower two thirds of the frame with open dark empty space above it. Inside the block a few soft wavy fibre strands lie slack and well spaced, running loosely from the left edge of the block to the right edge, with soft even tissue filling the wide gaps between them. The top surface is flat and smooth from end to end. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, rope, braid, textile, wood grain
```

## 158. m_follicle_rupture — 표면에 부풀어 있던 투명한 물주머니가 한쪽 벽부터 얇아지다 터지며 안의 

쓰는 topic 1편 · 여성_12(배란통). 기존 15종에 없던 '파열' 순간 전담 — m_pressure_buildup은 차오르다 끝나고 터지지 않는다. 피는 캐논상 청록 유지(붉은색 금지), 통증 지점에만 옅은 amber.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A smooth rounded organ surface fills the lower half of the frame, seen from the side at eye level, with open dark empty space above it. Bulging up out of that surface near the centre is one clear round fluid-filled sac, taut and swollen, its thin wall stretched tight and fully translucent so the clear fluid inside is visible. The rest of the organ surface is smooth and unbroken. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, blood colour, soap bubble, balloon, egg, planet
```

## 159. m_growth_arrest — 조직을 만드는 기질이 잠시 멈췄다 재개되며 경계에 흔적이 남는다

쓰는 topic 1편 · 손발_20(보우선). '생성이 잠시 멈췄다 재개된 흔적이 바깥으로 밀려나간다'가 전부라 Shot 3에서 홈이 판을 따라 이동하는 걸 반드시 보여줘야 한다. 휴지기 탈모(part_scalp 계열)와 공용.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A cross-section seen from the side at eye level. Along the bottom of the frame lies a growth bed of small tightly packed busy cells running from the left edge to the middle; rising out of that bed and running up and away toward the right edge of the frame is a flat hard plate, made of thin stacked layers clearly visible through its cut edge, its outer surface perfectly smooth and even along its whole length with no marks or ridges anywhere. Open dark empty space fills the upper left of the frame. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, fingernail polish, hand, foot, ruler, ladder
```

## 160. m_indoor_air_buildup — 닫힌 공간에 날숨 이산화탄소·오염물질이 쌓여 신선한 공기가 밀려나는 그림

쓰는 topic 1편 · 피로_5(환기). 유일한 '몸 밖 환경' 기전이라 조직이 아니지만 같은 유리 톤·void를 유지했고, 방으로 읽히지 않게 --no에 furniture/window/architecture를 박았다. 오염물질은 해로운 물질이라 amber.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A sealed box-shaped chamber of still air seen from the side at eye level, filling most of the frame, its flat floor across the bottom and smooth featureless glass walls closing it on every side, with one narrow slit vent set high on the right wall. The air inside the chamber is clear and open, with a fine scattering of tiny bright pale cyan motes drifting evenly through it, and a thin layer of small warm amber specks lying low along the floor. Everything except those amber specks is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, furniture, bed, window frame, house, architecture, room interior, aquarium, fish
```

## 161. m_layer_separation — 위층이 아래 조직에서 들떠 분리되며 틈이 생긴다

쓰는 topic 1편 · 손발_21(조갑박리). m_cell_damage가 손상이면 이쪽은 멀쩡한 구조가 통째로 들뜨는 분리 — 조직이 깨지지 않고 '검은 빈 틈'만 생기는 게 유일한 변화라 그 점을 컬러 문구에 명시했다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A flat hard plate seen from the side at eye level in cross-section, running across the frame from the left edge to the right edge through the middle, resting on a bed of soft tissue that fills the space below it. Along their whole length the plate and the bed are joined by fine interlocking ridges, meshed tight and seamless with no gap anywhere. Open dark empty space fills the frame above the plate. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, hand, foot, fingernail, zipper, teeth, machinery
```

## 162. m_organ_ptosis — 장기를 아래에서 받치던 주변 지방·근육층이 얇아지면서 장기가 중력 방향으

쓰는 topic 1편 · 소화_16(위하수). 기존 15종은 전부 조직 내부 변화라 '장기가 통째로 내려앉는다'는 위치 변화가 없었다. 주변이 완전히 정지해 있어야 아래로 내려간 게 읽히므로 Shot 3에 명시. 호박색 없음.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One hollow pouch-shaped organ hangs in the upper middle of the frame, seen from the side and cut open so its hollow inside is visible. Directly beneath it, holding it up, sits a thick cushioning pad of tightly packed round fat cells, and beneath that pad a broad sheet of muscle fibres is slung taut from the left edge of the frame to the right edge. The pouch sits high, its lower end well clear of the bottom of the frame, with open dark empty space below and above. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, bag, balloon, hammock, fabric, sausage
```

## 163. m_otolith_displacement — 제자리에 붙어 있던 작은 돌 알갱이가 떨어져 나와 반고리관 속을 굴러다니

쓰는 topic 1편 · 어지럼증_16(이석증). 결정·이물은 캐논상 amber 허용(m_waste_buildup 선례). Shot 3에서 감각모만 격하게 흔들리고 나머지는 정지 — '실제로는 안 움직이는데 회전 신호가 온다'는 게 핵심이라 이 대비가 빠지면 안 된다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. Three narrow fluid-filled loops of tube joined together at their base, each loop curving in a different plane, seen at a three-quarter angle and filling the frame, cut open so the clear fluid inside them and the fine hair-like sensors standing upright at the base of each loop are visible. On a small flat patch off to one side, away from the loops, lies a bed of tiny warm amber grains packed together in an even layer, resting still where they belong. Everything except those grains is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, sand, gravel, jewellery, gemstones, snail shell, spiral staircase
```

## 164. m_ovarian_reserve_decline — 난소 안에 빽빽하던 작은 난포들이 하나씩 사라지며 수가 뚜렷이 줄고, 남

쓰는 topic 1편 · 여성_9(난소 나이). '수가 줄어 고갈된다'가 핵심이라 시작 스틸을 일부러 빽빽하게 채워 Shot 3의 빈 공간이 대비되게 했다. m_cell_damage로는 대체 불가. 호박색 없음.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One rounded organ fills the centre of the frame, seen from the side at eye level and cut open so its whole inside is visible. The inside is packed edge to edge with dozens of small round fluid-filled follicles of roughly even size, each one plump and brightly lit, with almost no empty space between them. Open dark empty void surrounds the organ on all sides. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, eggs, caviar, bubbles, foam, grapes, pomegranate
```

## 165. m_parasite_penetration — 실처럼 가는 유충이 점막 표면을 훑다 한 지점에 머리를 박고 조직 속으로

쓰는 topic 1편 · 소화_22(고래회충). m_bacteria_growth는 표면에서 수만 늘어나 '파고든다'가 없다. 원문 설명의 '붉게 부어오름'은 붉은색 금지라 부어오른 테두리의 옅은 amber로 옮겼다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A wide tissue surface seen from a low skimming angle just above it, running from the bottom edge of the frame back to a horizon line in the upper third, with open dark empty space above. The surface is a damp glossy carpet of tall thin finger-like folds standing upright. Lying across the tops of the folds near the centre of the frame is one long very thin thread-like worm, warm amber and smooth, its head end raised slightly off the surface. Everything except that worm is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, insect, legs, snake scales, hair strand, noodle, rope
```

## 166. m_posture_load — 자세가 무너지며 하중이 한 부위에 집중돼 관절·근육에 지속적인 부담이 실

쓰는 topic 1편 · 어지럼증_8(자세). 원안은 '숫자·화살표로 하중을 보여준다'였지만 이 세계관은 화면 내 글자·화살표 전면 금지 → 쿠션이 앞쪽만 납작해지는 형태로 하중 집중을 표현하고, 컬러 문구에 화살표 금지를 한 번 더 못박았다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A vertical stack of seven blocks runs from the top edge of the frame to the bottom edge through the exact centre, seen from the side at eye level, each block separated from the next by a soft cushion pad of even thickness. A band of long parallel fibres runs down the back of the stack from top to bottom. The stack is perfectly straight and evenly aligned and every cushion pad is the same thickness front and back. Open dark empty void fills both sides of the frame. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, full body, skeleton, spine chart, building, tower, blocks toy
```

## 167. m_tissue_invasion — 표면 층 조직이 아래 근육층 사이를 파고들며 층 경계를 허물고 들어가, 

쓰는 topic 1편 · 여성_20(선근증). m_ectopic_implantation과 나란히 쓰는 짝 클립이라 색 규칙(침범한 조직만 amber)은 맞추되 방향을 반대로: 저쪽은 떨어져 나가 밖에 내려앉고, 이쪽은 붙은 채 아래층을 뚫고 들어간다.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. Two layers stacked and seen from the side at eye level, the cut face toward the camera, filling the lower two thirds of the frame with open dark empty space above. The upper layer is a thin lining of small tightly packed cells; directly beneath it lies a thick wall of interwoven muscle fibre bundles. The boundary between the two layers is one clean straight unbroken line running from the left edge to the right edge. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, sandwich, cake, geological strata, brickwork
```

## 168. m_virus_persistence — 표면 세포 안으로 들어간 바이러스 입자가 세포 핵 근처에 자리 잡고 사라

쓰는 topic 1편 · 여성_22(HPV 지속감염). m_virus_reactivation과 합치지 않는 이유가 화면에 드러나야 한다 — 이건 '세포 안에 가만히 남아 분열할 때마다 따라 늘어남'이라 이동이 전혀 없고, 세포는 끝까지 정상으로 보이는 게 포인트.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. An extreme close-up of large plump surface cells packed tightly together in a block, seen from the side at eye level with their flat top surface facing straight up, filling the lower two thirds of the frame. Each cell holds one clearly visible round nucleus, all of them evenly lit and healthy looking. In the open dark space above the surface, a handful of tiny warm amber specks drift slowly down toward it, none of them touching yet. Everything except those specks is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, spiky virus model, coronavirus illustration, diagram, flat illustration
```

## 169. m_virus_reactivation — 신경 줄기 안쪽에 잠들어 있던 작은 입자들이 깨어나 신경 다발을 따라 표

쓰는 topic 1편 · 입_19(입술 헤르페스). 잠복-이동-발현 세 단계를 컷 3개에 그대로 배치했다. 물집은 몸의 반응이라 청록 유지, 바이러스만 amber. 대상포진 등 재발 계열 전부가 이 하나를 재사용.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One thick nerve cord runs from the bottom edge of the frame up to the top through the exact centre, seen from the side and cut open lengthwise so the long parallel fibres inside are visible. Low in the cord the fibres widen into a knot of rounded cell bodies, and packed motionless inside that knot sits a tight cluster of tiny warm amber particles. At the top of the frame the cord fans out into fine branches that reach up to a flat tissue surface running across the top edge. Everything except those particles is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, spiky virus model, coronavirus illustration, diagram, flat illustration, tree, roots
```

## 170. m_wall_outpouching — 관 벽의 근육층이 얇아진 한 지점이 안쪽 압력에 밀려 바깥으로 풍선처럼 

쓰는 topic 1편 · 소화_15(게실). m_pressure_buildup은 닫힌 챔버 안 압력이 차오르는 컷이고 이건 벽이 밖으로 빠져나오는 형태 변화라 호박색 없이 형태만으로. 압력이 풀려도 주머니가 남는 게 마지막 컷의 핵심.

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One thick tube runs horizontally across the middle of the frame from the left edge to the right edge, seen from the side and cut open lengthwise so the open channel inside and the layers of its wall are visible along the whole length. The wall has a thin inner lining and a thicker outer muscle layer, and at one point near the centre of the frame the outer muscle layer is noticeably thinner than everywhere else, with one fine vessel passing through it at that spot. The outer surface of the tube is smooth and even from end to end. Open dark empty void fills the frame above and below the tube. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, pipe, plumbing, hose, balloon, sausage
```

