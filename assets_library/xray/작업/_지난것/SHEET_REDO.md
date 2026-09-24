# 다시 뽑을 40장 (2026-09-21)

앞서 147장 중 **106장은 채택**해서 `RENDER/<번호>_start.jpg`에 저장했다. 이 40장만 다시 뽑으면 된다.
번호는 그대로다. 결과도 `RENDER/<번호>_start.jpg`.

⚠️ **40장 전부 `stills/canon_organs.jpg`를 Style Reference로 넣는다**(Omni Reference는 금지 — 미시 장면에 전신 인체가 끼어든다). 행위든 기전이든 구분하지 말고 똑같이.

| 번호 | 무엇 | 지난번 왜 실패했나 |
|---|---|---|
| 45 | act_phone_in_bed | 누워서 폰 보는 자세인데 서서 판을 들고 있음 |
| 60 | act_slow_walk | 천천히 걷는 장면인데 판을 얼굴 앞에 들고 있음 |
| 62 | act_stand_still_unaware | 아무렇지 않게 서 있어야 하는데 컵 위로 몸을 숙이고 있음 |
| 72 | m_vessel_dilation | 혈관이 넓어지는 게 안 읽힘(고리 세 개 + 알 모양) |
| 73 | m_hormone_drop | 호르몬 감소가 안 읽힘(깃털 모양 원뿔) |
| 74 | m_particle_deposition | 먼지 입자가 호박색으로 안 나오고 무엇이 쌓이는지 안 보임 |
| 77 | m_tendon_degeneration | 힘줄 퇴행이 안 읽힘(동심원 고리) |
| 79 | m_microvessel_damage | 초록색 알갱이 — 캐논은 청록/호박색뿐 |
| 81 | m_odor_compound_release | 냄새 분자 방출이 안 읽힘 |
| 90 | m_adenosine_block | 위에서 본 수용체 면이어야 하는데 그냥 혈관 |
| 91 | m_backflow_pooling | 판막 역류·정체가 안 읽힘(모낭 모양) |
| 97 | m_arousal_spike | 호박색이 없어야 하는데 주머니가 호박색 액체로 가득 |
| 99 | m_filtration_overload | 여과 과부하가 안 읽힘(블록 두 개) |
| 104 | m_vessel_occlusion | 복도에 창문 있는 방이 나옴 — 완전히 다른 그림 |
| 105 | m_vision_field_loss | 시야 결손이 안 읽힘 |
| 106 | m_airway_collapse | 호박색이 없어야 하는데 기도에 호박색 덩어리 |
| 107 | m_content_hardening | 내용물이 굳는 게 안 읽힘(섬유 원기둥) |
| 110 | m_osmotic_water_pull | 삼투로 물이 끌려나오는 방향이 안 보임 |
| 111 | m_oxygen_transport_drop | 산소 운반 저하가 안 읽힘(고리 + 관) |
| 114 | m_virus_replication | 바이러스 증식이 안 읽힘(물결 무늬) |
| 116 | m_cartilage_wear | 복도에 창문 있는 방이 나옴 — 104번과 같은 오류 |
| 117 | m_double_vision | 복시가 안 읽힘 |
| 118 | m_duct_blockage | 호박색 금지인데 구슬이 호박색, 폐색도 안 보임 |
| 127 | m_sebum_overproduction | 피지 과분비가 아니라 나무뿌리처럼 나옴 |
| 131 | m_autoimmune_attack | 자가면역 공격이 안 읽힘 |
| 133 | m_bone_density_loss | 뼈 밀도 감소가 안 읽힘(방사형 무늬) |
| 134 | m_electrical_misfire | 전기 오발화가 안 읽힘(눈알 모양) |
| 135 | m_eye_elongation | 호박색 금지인데 혈관 안이 호박색 띠 |
| 136 | m_glucose_crash | 혈당 급락이 안 읽힘(뼈 모양) |
| 139 | m_lipid_oxidation | 122번(미네랄 침식)과 그림이 거의 같음 — 구분 안 됨 |
| 143 | m_protein_clouding | 수정체 혼탁이어야 하는데 코일 감긴 관 |
| 145 | m_reflux_backflow | 역류가 안 읽힘 |
| 148 | m_vagal_slowdown | 미주신경 둔화가 안 읽힘(돔 형태) |
| 151 | m_acid_deficiency | 위산 부족이 안 읽힘 |
| 155 | m_dopamine_loop | 형체 불명 조각 |
| 157 | m_fibrosis | 섬유화가 안 읽힘(매끈한 돔) |
| 159 | m_growth_arrest | 성장판 정지가 안 읽힘(빈 상자) |
| 160 | m_indoor_air_buildup | 실내 공기 오염 축적이 안 읽힘 |
| 165 | m_parasite_penetration | 기생충이 안 보임(마디 있는 관만) |
| 169 | m_virus_reactivation | 형체 불명(선 몇 개) |

---

## 45. act_phone_in_bed — 불 끈 침실에서 이불 속에 누워 스마트폰 화면 불빛을 얼굴에 받는 모습

지난번: 누워서 폰 보는 자세인데 서서 판을 들고 있음

고친 점: 서 있는 그림으로 읽힌 원인은 자세가 셋째 문장에 묻혀 있었던 것 — '반듯이 누워 있다'를 첫 문장에 박고 바닥 패널과 뒤통수·어깨·엉덩이·발뒤꿈치가 닿는 접촉점을 적고 --no에 standing, upright, walking, levitating을 추가

```
Medical holographic visualization of a translucent glass-like 3D human figure lying flat on its back, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The figure is lying flat on its back on a plain flat glass bed panel and the camera is directly overhead pointing straight down at the panel, so the body runs up the frame with the head at the top edge and both feet at the bottom edge. The back of the head, both shoulder blades, the buttocks, the backs of both thighs and both heels are all pressed flat down against the panel, and the panel spreads out under the whole body from the top edge of the frame to the bottom edge. Both elbows rest down on the panel beside the ribs and both forearms rise straight up toward the camera so the two hands hold one small thin blank rectangular glass slab flat and level about a forearm's length above the face, the slab parallel to the panel and left as a bare blank form with no buttons, no markings, no pattern and no brand of any kind. Both legs lie straight and slightly apart with both feet flopped outward to the sides. Visible inside: the brain with its deep centre, both eyeballs in their sockets aimed straight up at the slab, the optic nerves running back from them into the brain, the neck vertebrae, the lungs and heart, the stomach and coiled intestines, the pelvis and the leg bones. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, standing, standing up, upright, vertical posture, walking, mid-stride, floating, levitating, hanging, feet on the ground, slab held overhead like a sign, screen image, screen content, buttons, markings
```

## 60. act_slow_walk — 보폭이 짧고 느리게, 벽·가구를 짚으며 걸음

지난번: 천천히 걷는 장면인데 판을 얼굴 앞에 들고 있음

고친 점: 판을 얼굴 앞에 든 원인은 소품 문장과 프레이밍이 흐려 상반신 컷으로 잘린 것 — 벽 패널을 왼쪽 가장자리로 고정하고 '양손에 아무것도 들지 않았다'를 명시, 두 발 간격까지 적고 --no에 slab/tablet/bust shot/cropped legs 추가

```
Medical holographic visualization of a translucent glass-like 3D human figure seen from the side at eye level, its whole body from the top of the head down to both feet inside the frame, filling about eighty-five percent of the frame height, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The figure is mid-step, taking one very short shuffling stride along a plain flat upright glass wall panel that runs from the top of the frame to the bottom down the left edge with no markings anywhere on it. Its left hand is flat against that panel at shoulder height with the elbow bent, taking part of the weight; the leading foot is set down only about half a shoe-length ahead of the trailing foot and both soles stay low and skimming the floor; both knees are barely bent, the torso is stooped forward, the shoulders are rounded, the head is pushed forward ahead of the chest, and the free right arm hangs straight down at the side with the hand empty and open. Nothing at all is held in either hand and nothing is in front of the face. Visible inside: the brain, the spine curving from the neck down to the pelvis, the lungs and heart, the stomach and coiled intestines, the pelvis, the hip joints, the thigh and calf muscles and the leg bones down to the feet. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, held object, slab, tablet, phone, board, book, panel in front of the face, hand raised to the face, bust shot, waist-up crop, cropped legs, head and shoulders, running, long stride, raised knee, high step
```

## 62. act_stand_still_unaware — 반투명 인체가 정면으로 편하게 가만히 서 있고, 몸속 한 지점만 조용히 

지난번: 아무렇지 않게 서 있어야 하는데 컵 위로 몸을 숙이고 있음

고친 점: 컵 위로 몸을 숙인 원인은 소품이 끼어들 여지가 남아 있었던 것 — '똑바로 서 있다'를 첫 문장에 두고 '그림 안에 다른 물체가 하나도 없다'를 명시, --no에 cup/glass/container/bending over/leaning forward 추가

```
Medical holographic visualization of a translucent glass-like 3D human figure standing bolt upright, seen from the front at eye level, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, gender-neutral adult, full body visible from the top of the head to the feet, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. The figure stands straight up and perfectly still in an entirely empty void, its spine vertical, its head level and facing straight ahead, both feet flat on the floor a shoulder-width apart, both legs straight, both arms hanging straight down at the sides with the fingers slightly curled, the shoulders level and dropped and the chest open. It is calm, at ease and entirely untroubled. There is nothing else in the picture at all: no object, no furniture, no container, nothing held in the hands and no hand anywhere on the body. Visible inside: the brain, the lungs and heart, the liver, the stomach and the coiled intestines, the kidneys, the bladder and the small organs low in the pelvis behind it, with the full skeleton faintly visible. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, cup, glass, tumbler, jar, bowl, bottle, container, vessel, table, chair, prop, any object, bending over, leaning forward, stooping, bowing, crouching, hands on body, clutching, hunching, grimacing, walking, mid-stride
```

## 72. m_vessel_dilation — 혈관이 순식간에 넓어지며 혈류가 확 몰리고 압력이 떨어져, 위쪽으로 가던

지난번: 혈관이 넓어지는 게 안 읽힘(고리 세 개 + 알 모양)

고친 점: 고리 세 개 + 알 모양으로 나온 원인은 관을 정면에서 본 원형으로 렌더한 것 — '세로 종단면, 잘린 면이 카메라 쪽, 채널은 두 평행벽 사이의 직선 슬롯'을 첫 문장에 박고 --no에 ring, donut, torus, tube seen end-on, egg, bulb 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D a human blood vessel, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One single thick vessel runs straight up the exact centre of the frame from the bottom edge to the top edge, seen from the side and sliced open lengthwise with the cut face toward the camera, so the channel inside reads as a long straight-sided slot between two parallel walls, never as a circle. At this moment that slot is very narrow, barely wider than one cell, its two walls drawn close together and almost touching. Wrapped around the outside of the wall, halfway up, is one band of ridged muscle fibres clenched tight, squeezing the vessel in so the walls pinch visibly inward there. A single file of about twelve small smooth disc-shaped cells drifts up the narrow slot one behind another. Near the top edge the vessel tapers into two hair-thin threads that leave the frame at the top two corners. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, blood colour, ring, donut, torus, concentric circles, circular opening, tube seen end-on, three round holes, egg, pod, bulb, sphere, cluster of circles, pipe, plumbing, hose, tree, roots
```

## 73. m_hormone_drop — 샘에서 흘러나오던 호르몬 입자 줄기가 가늘어지다 끊기고, 건너편 표적 세

지난번: 호르몬 감소가 안 읽힘(깃털 모양 원뿔)

고친 점: 깃털 모양 원뿔로 나온 원인은 '입자 줄기(stream of particles)'를 털 다발로 그린 것 — 줄기를 '알갱이 약 40개가 이루는 곧은 기둥'으로 수를 세어 적고 샘·창문 세 개의 위치를 좌·중·우로 못 박고 --no에 feather, plume, fur, cone, spray 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human glandular tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A thick slab of glandular tissue seen from the side at eye level, like a slice cut out of a cake, sits across the bottom third of the frame with its flat top surface facing straight up. One round hollow sac the size of a walnut sits inside the slab just under that surface, clearly visible through the translucent cut face, and one small round opening in the surface sits directly above it. Out of that single opening a loose straight column of about forty small round pale cyan beads rises up through the middle of the frame, the column thick and unbroken from bottom to top. Standing in a row across the top third of the frame are three separate flat-faced blocks of tissue, evenly spaced left, centre and right, each block with one small round window in its front face and every window lit brightly from inside. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, feather, plume, fur, hair, whiskers, bristles, cone, funnel, tail, spray, fountain, grass, wheat, smoke, whole organ, candle, fire
```

## 74. m_particle_deposition — 공기 흐름을 타고 들어온 미세 입자가 관을 따라 점점 깊이 내려가 표면 

지난번: 먼지 입자가 호박색으로 안 나오고 무엇이 쌓이는지 안 보임

고친 점: 무엇이 쌓이는지 안 보이고 입자가 호박색으로 안 나온 원인은 '깊이로 멀어지는 관'이 혈관으로 렌더되며 융모와 알갱이를 다 삼킨 것 — 구도를 케이크 조각 판으로 바꾸고 호박색 알갱이를 '약 30개, 3분의 1은 이미 융모 사이에 박힘'으로 수와 위치를 세어 적고 --no에 vessel, blood cells 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human airway tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A thick slab of airway lining seen from the side at eye level, like a slice cut out of a cake, sits across the lower half of the frame with open dark empty space above it. Its flat top surface is carpeted edge to edge with short upright hair-like fringes, all the same height and all standing straight up. About thirty small round warm amber grains are in the picture and each one is a distinct solid bead: roughly a third of them are already wedged down between the fringes and stuck fast, sitting deep in the carpet, and the rest hang in the open dark space above the fringes, spread out and drifting sideways. Everything except those amber grains is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, blood vessel, vessel, blood cells, discs inside a tube, branching tube, smoke, fog, haze, mist, dust cloud, sand, snow, whole lung, grass field, hairy tube
```

## 77. m_tendon_degeneration — 반복 부하와 혈류 감소로 힘줄·근막에 미세손상이 쌓여 조직이 퇴행한다

지난번: 힘줄 퇴행이 안 읽힘(동심원 고리)

고친 점: 동심원 고리로 나온 원인은 힘줄을 종단이 아니라 단면(원형)으로 잡은 것 — '두 긴 모서리가 두 개의 직선으로 보이는 옆면 대각선 구도'를 명시하고 --no에 ring, concentric circles, clock, dial, spiral 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tendon tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A thick tendon cord runs diagonally across the whole frame from the lower left corner to the upper right corner, seen from the side along its length so its two long edges read as two straight parallel lines. The cord is made of dozens of long parallel fibres lying perfectly straight and packed tight, all running the same way along the cord, clearly visible through its translucent surface. Halfway along, the cord crosses the rounded top edge of one hard dense block that presses up into it from below, and the cord bends over that edge. At this moment the cord is smooth, evenly thick and unbroken and every fibre is still in line. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, ring, rings, concentric circles, target, clock, dial, spiral, coil, circular, tube seen end-on, red glow, orange gradient, fire, swollen dome, immune cells, rope, frayed rope, wood
```

## 79. m_microvessel_damage — 머리카락보다 가는 모세혈관이 약해져 늘어나고 새거나 터져 주변으로 번진다

지난번: 초록색 알갱이 — 캐논은 청록/호박색뿐

고친 점: 초록 알갱이가 박힌 모낭 모양으로 나온 원인은 '실핏줄 그물'이 뿌리·구근으로 해석된 것 — '바로 위에서 내려다본 평면, 모든 실이 같은 평면에 누워 있다'를 못 박고 캐논 색 위반을 막으러 --no에 green, follicle, bulb, seeds 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D a net of human capillaries, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. Seen from straight above, looking flat down onto a wide even field of translucent tissue that fills the whole frame like a flat floor. Lying flat on that field is a net of hair-thin capillary threads that branch and cross each other, densest in the centre and thinning out toward the four corners, every thread lying in the same flat plane with no thread rising toward the camera. Each thread is barely wider than the tiny pale cyan disc-shaped cells running single file inside it, and every thread is smooth, evenly thin and unbroken along its length. The tissue under the net is clear, flat and clean. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, green, teal green, yellow-green, blood colour, hair follicle, follicle, hair root, bulb, teardrop sac, seeds, beads, eggs, grapes, roots, tree branches, lightning, river delta, cracked glass, side view
```

## 81. m_odor_compound_release — 표면의 세균이 땀·피지 방울을 분해하자 작은 냄새 분자가 떨어져 나와 표

지난번: 냄새 분자 방출이 안 읽힘

고친 점: 관 끝을 정면에서 본 고리로 나온 원인은 표면 구도가 통째로 원통으로 뭉개진 것 — 낮은 스키밍 각도와 수평선 위치를 다시 못 박고 '방울 4개, 위로 올라가는 호박색 알갱이 기둥 약 20개'로 개수를 세어 적고 --no에 ring, torus, tube seen end-on 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human skin surface tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A wide flat skin surface seen from a low skimming angle just above it, running from the bottom edge of the frame back to a horizon line in the upper third, with open dark empty space above that horizon. The surface is a mosaic of plump pale cyan cells. Sitting on it are four fat rounded droplets of clear pale cyan fluid, each about the size of a marble, spread apart across the surface. Warm amber rod-shaped bacteria are clustered thickly on and around every droplet, packed shoulder to shoulder. Out of the nearest droplet a thin straight column of about twenty tiny warm amber flecks rises up into the dark empty space above, the column narrow at the droplet and spreading wider as it goes up. Everything except the bacteria and those flecks is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, ring, donut, torus, circular opening, tube seen end-on, funnel, cylinder, smoke, fog, steam, cloud, petri dish, mould, hair, flowers, perfume bottle
```

## 90. m_adenosine_block — 깨어있는 동안 졸음물질 아데노신이 쌓이고, 카페인이 그 수용체 자리를 대

지난번: 위에서 본 수용체 면이어야 하는데 그냥 혈관

고친 점: 혈관으로 나온 원인은 '수용체 면'이 관 단면으로 읽힌 것 — '바로 위에서 내려다본 포장 바닥, 수평선도 관도 없다'를 첫 문장에 박고 채워진 소켓 15개·호박색 쐐기 6개로 수를 세어 적고 --no에 vessel, tube, valve, side view 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D a human nerve cell surface, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. Seen from straight above, looking flat down onto one wide flat cell surface that fills the whole frame corner to corner like a paved floor, with no horizon and no tube anywhere. The floor is studded all over with dozens of round open sockets in an even regular grid, each socket a small round pit. Many small pale cyan key-shaped particles hang just above the floor, and about fifteen of them are already seated down inside sockets; every socket that holds one has gone soft and dim while every empty socket stays bright. Mixed in among them, six angular warm amber wedge-shaped particles hover above the floor with none of them yet reaching a socket. Everything except those six amber wedges is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, vessel, blood vessel, tube, channel, valve, valve flaps, blood cells, discs, side view, cross-section, synapse gap, two nerve endings facing each other, metal keys, keyhole, lock, padlock, coffee beans, coffee cup, puzzle pieces, buttons
```

## 91. m_backflow_pooling — 판막이 닫히지 못해 혈액이 거꾸로 흘러 아래쪽에 고이고 혈관이 꽈리처럼 

지난번: 판막 역류·정체가 안 읽힘(모낭 모양)

고친 점: 모낭 세 개처럼 나온 원인은 'cup-shaped valve flaps'가 물방울 모양 주머니로 그려진 것 — 판막을 '좌우 벽에서 나온 반달 두 장이 가운데서 맞닿는 여닫이문'으로 형태를 바꿔 적고 --no에 hair follicle, bulb, teardrop sacs, three identical shapes 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D a human vein with valves, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One single wide vein runs straight up the exact centre of the frame from the bottom edge to the top edge, seen from the side and sliced open lengthwise with the cut face toward the camera, so the channel inside reads as one long straight-sided slot between two parallel walls. Halfway up, two thin half-moon valve flaps reach in from the walls toward each other, one growing from the left wall and one from the right, their curved free edges meeting exactly in the middle like a pair of swing doors seen edge-on, closing the slot off cleanly across its full width. The vein wall is the same even width above and below the flaps. About ten small smooth disc-shaped cells drift upward through the slot below the flaps. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, blood colour, hair follicle, hair shaft, hair root, bulb, teardrop sacs, skin layer, three identical shapes, row of bulbs, balloon, pipe, plumbing, valve machinery, heart shape
```

## 97. m_arousal_spike — 깊이 잠든 뇌파 위로 각성 신호가 튀어올라 잠이 순간 끊기는(미세각성) 

지난번: 호박색이 없어야 하는데 주머니가 호박색 액체로 가득

고친 점: 호박색 액체가 찬 주머니로 나온 원인은 '느린 물결이 흐르는 넓은 시트'가 형태 없는 자루로 뭉개진 것 — 케이크 조각 판 위에 '같은 높이·같은 간격의 낮은 능선 5개'로 개수를 세어 적고 --no에 balloon, pouch, sac, liquid, golden, yellow 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D brain tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A thick slab of brain tissue seen from the side at eye level, like a slice cut out of a cake, sits across the lower half of the frame with open dark empty space above it. Its top surface is not flat: it rolls in five long low rounded ridges running from the left edge of the frame to the right edge, all five the same height, the same width and evenly spaced, each ridge broad and gently domed, their glow dim and steady and identical. The cut face of the slab toward the camera is solid, even and quiet. Everything is translucent pale cyan glass and the whole scene is calm and dark. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, golden, yellow, liquid, pool of liquid, balloon, bladder, pouch, sac, bulb, flask, graph, chart, waveform, line plot, grid, ocean, sea, beach, cloth, fabric
```

## 99. m_filtration_overload — 사구체로 걸러야 할 용질이 한꺼번에 몰려 여과 압력과 부담이 올라가는 그

지난번: 여과 과부하가 안 읽힘(블록 두 개)

고친 점: 블록 두 개로 나온 원인은 --no의 yarn·knot·net·coral이 의도한 '엉킨 관 뭉치' 질감까지 지워 민짜 덩어리만 남긴 것 — 그 단어들을 --no에서 빼고 '손가락 굵기 관 약 12개가 서로 얽힌 사과 크기 공, 매끈한 공이 아니다'로 본문에 적고 --no엔 smooth blob, solid sphere만 남김

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One round bundle the size of an apple sits in the exact centre of the frame with dark void around it. The bundle is built from about twelve separate translucent tubes, each tube as thick as a finger, each one looping over and under the others so that individual tube loops stay clearly readable all over the bundle's outside — it is a ball of tubes, not a smooth ball. A thin smooth capsule wraps the bundle like a loose bag. One wide tube enters the bundle at the upper left of the frame, one narrower tube leaves at the lower left, and one drain tube leaves straight down from the bottom of the capsule. A steady stream of small warm amber grains runs inside the looping tubes and is visible through their walls, and fine clear droplets are straining out through the tube walls into the space inside the capsule. Everything except the amber grains is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, smooth blob, featureless dome, solid sphere, two blocks, egg, marble, brain, cauliflower, flower
```

## 104. m_vessel_occlusion — 정체된 혈류 속에서 혈소판·섬유소가 엉겨 굳어 한 지점을 완전히 막고, 

지난번: 복도에 창문 있는 방이 나옴 — 완전히 다른 그림

고친 점: 복도에 창문 있는 방으로 나온 원인은 'long channel·open channel'이 건축 공간으로 읽힌 것 — '혈관, 살로 된 관'임을 첫 문장에 박고 대각선 종단면임을 명시, --no에 room, corridor, window, table, floor, architecture, interior 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D a vessel, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One single thick blood vessel, a tube of living flesh, runs diagonally across the frame from the upper left corner to the lower right corner, seen from the side and sliced open lengthwise with the cut face toward the camera, so the channel inside reads as one long straight-sided slot running corner to corner. Dark empty void fills the upper right and lower left corners around it. The slot is wide and the flow inside it is sluggish: about twenty small smooth disc-shaped cells drift slowly and are already bunching into clumps. At the exact midpoint of the vessel one warm amber clump of sticky platelets, about a third as wide as the slot, is stuck low against the lower wall, with the channel still open past it above. Everything except that amber clump is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, room, corridor, hallway, window, table, furniture, floor, walls, ceiling, architecture, interior, perspective room, building, long channel, pipe, plumbing, rope, hose, blood colour, gore, wound
```

## 105. m_vision_field_loss — 1인칭 시야에서 가장자리 또는 한쪽이 서서히 검게 잠식되거나 커튼처럼 가

지난번: 시야 결손이 안 읽힘

고친 점: 시야 결손이 안 읽힌 원인은 시작 이미지를 '전부 고르게 밝다'로 적어 결손을 아예 안 그린 것 — 왼쪽 3분의 1을 평평한 어둠으로 덮되 사방 비네팅과 구분되게 '세로 경계선 한 줄'로 적고 --no에 symmetric vignette, stomach, organ 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D a first-person view, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. This is a first-person point-of-view shot looking straight ahead from inside a person's own eyes, across a plain empty room toward a bright window in the far wall, with one simple low table standing in the middle of the floor; the floor, walls, window frame and table are all rendered as translucent glass-like 3D forms in the same soft pale cyan glow and the space beyond the window is a dark empty slate blue-grey void. The left third of the view, from the top edge to the bottom edge, is swallowed by flat solid darkness with one soft vertical edge, as if a dark curtain has been drawn in from the left side and stopped a third of the way across; the remaining right two thirds of the view are evenly lit and perfectly sharp all the way out to their edges and corners. The view fills the whole vertical 9:16 portrait frame. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, hands, symmetric vignette, dark corners on all sides, round frame, border, porthole, keyhole, binoculars, split screen, blur, bokeh, doubling, stomach, organ, tissue, cells, tube, microscopic, anatomy cutaway
```

## 106. m_airway_collapse — 잘 때 늘어진 연구개와 혀뿌리가 기도를 눌러 좁아지다 완전히 막히는 그림

지난번: 호박색이 없어야 하는데 기도에 호박색 덩어리

고친 점: 기도에 호박색 덩어리가 생긴 원인은 빈 통로를 '무엇이 없는지'로만 적어 덩어리가 채워진 것 — 통로를 '왼쪽 위가 넓고 오른쪽 아래로 좁아지는 쐐기꼴 빈 공간'으로 형태를 지정하고 --no에 amber, golden, yellow, liquid, lump, mass, bolus 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A side cutaway of the back of the throat fills the middle of the frame, seen from the side at eye level. A soft curtain of tissue hangs straight down from the roof at the top of the frame like a slack drape; the thick rounded back of the tongue rises from the bottom edge like a smooth hill; between those two shapes runs one clear empty wedge-shaped air gap, wide open at the upper left and narrowing as it runs down to the lower right. Nothing at all lies inside that gap: no liquid, no droplet, no lump, only empty dark space. Both the hanging curtain and the tongue hill are slack, smooth and rounded. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, golden, yellow, liquid, mucus, droplet, lump, mass, ball, bolus, food, blockage object, head, profile portrait, teeth, lips, skull, anatomy chart, tunnel, cave
```

## 107. m_content_hardening — 관 속 내용물이 수분을 잃고 부피가 줄면서 단단한 덩어리로 굳어 벽을 긁

지난번: 내용물이 굳는 게 안 읽힘(섬유 원기둥)

고친 점: 섬유 원기둥에 호박색 점 몇 개로 나온 원인은 관이 세로로 서 버리고 덩어리가 알갱이로 흩어진 것 — '옆으로 누운 관이 좌우 가장자리를 잇는다'와 '덩어리는 하나, 아래벽에 밑면 전체가 닿는다'를 못 박고 --no에 upright column, fibres, floating specks 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One wide tube lies horizontally on its side across the middle of the frame, running from the left edge to the right edge, sliced open lengthwise along its top so the whole channel inside is visible from above and from the side at once, its inner wall lined with gentle rounded folds. Dark empty void fills the top quarter and the bottom quarter of the frame. Resting in the middle of that channel, touching the lower wall along its whole underside, sits one large single rounded mass of warm amber contents, wider than it is tall, its surface still moist, glossy and slumped, with a thin film of clear fluid between it and the wall. Everything except that amber mass is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, upright column, vertical cylinder, standing tower, fibres, fibrous mass, threads, hair, floating specks, scattered dots, food, dough, cake, rock, stone, gravel, chocolate
```

## 110. m_osmotic_water_pull — 관 속에 남은 흡수되지 않은 입자들이 장벽에서 물방울을 잡아당겨 내용물이

지난번: 삼투로 물이 끌려나오는 방향이 안 보임

고친 점: 물이 끌려나오는 방향이 안 보인 원인은 물 이동을 '양'으로만 적어 그릴 형태가 없었던 것 — 구도를 '왼쪽 절반은 선 벽, 오른쪽 절반은 관'으로 바꾸고 벽 구멍에서 반쯤 빠져나온 물방울 15개가 전부 같은 방향을 향하게 적음(다른 항목과 시점도 겹치지 않음)

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A thick slab of gut wall stands upright and fills the left half of the frame from the top edge to the bottom edge, its flat cut face turned toward the camera; the right half of the frame is the open channel. Tall thin finger-like folds stand out sideways from the slab's right face into that channel, all pointing right. Inside the slab, behind the cut face, plump rounded cells are packed tight and visibly swollen with clear fluid. A row of about fifteen clear round droplets is caught halfway through small openings in the slab's right face, each droplet bulging out of the tissue and into the channel, all of them leaving the wall in the same direction. Along the bottom of the channel lies only a thin shallow film of clear fluid, and about twenty small warm amber particles sit scattered on that film. Everything except those amber particles is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, horizontal tube, vertical tube, ring, donut, tube seen end-on, vessel, blood cells, sugar cubes, candy, food, foam, bubbles, soup, waterfall
```

## 111. m_oxygen_transport_drop — 적혈구 수와 헤모글로빈이 줄어 실어 나르는 산소량이 떨어지고, 도착한 조

지난번: 산소 운반 저하가 안 읽힘(고리 + 관)

고친 점: 고리 + 관으로 나온 원인은 관 끝을 정면에서 본 원형으로 렌더한 것 — '잘린 두 벽 모서리가 위아래로 이어지는 평행 레일 두 줄'로 폭 불변을 형태로 적고 --no에 ring, torus, tube seen end-on, funnel, wheel 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D a vessel, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One single thick vessel runs straight down the exact centre of the frame from the top edge to the bottom edge, seen from the side and sliced open lengthwise with the cut face toward the camera, so its two cut wall edges run down the frame as two straight parallel rails exactly the same distance apart from top to bottom, never pinching and never bulging. The slot between those rails is packed densely with small smooth disc-shaped cells drifting steadily downward, shoulder to shoulder and several across, and every disc glows brightly. The tissue on both sides of the vessel is lit softly by that glow. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, blood colour, ring, donut, torus, circular opening, tube seen end-on, funnel, wheel, pipe, plumbing, narrowing, valve, clot, branching
```

## 114. m_virus_replication — 바이러스가 세포 안으로 들어가 증식하며 퍼진다

지난번: 바이러스 증식이 안 읽힘(물결 무늬)

고친 점: 물결 무늬로 나온 원인은 세포 덩어리가 형태 없이 뭉개진 것 — '자두 크기 다각형 주머니 약 15개, 각각 핵 하나'로 크기·개수를 세어 적고 바이러스는 '핀머리 크기 성게 모양 6개'로 명시, --no에 waves, cloth, drapery, folds 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A solid block of tissue seen from the side at eye level fills the lower two thirds of the frame, its flat cut face toward the camera and its flat top surface facing straight up, with open dark empty space above it. The cut face shows about fifteen large cells packed tightly together, each cell a rounded many-sided pocket about the size of a plum with clear firm walls between them, and each cell holds one clearly visible round nucleus at its centre. Hanging in the dark space just above the block are six tiny warm amber spheres, each one no bigger than a pinhead and studded all over with short blunt spikes like a sea urchin, far smaller than the cells; two of the six are just touching the top surface of the nearest cell. Everything except those six spiked spheres is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, waves, ripples, wavy pattern, cloth, drapery, folds, silk, sheet, curtain, smoke, rod-shaped bacteria, rods, worms, petri dish, mould, spores, insects, virus poster
```

## 116. m_cartilage_wear — 관절 연골이 닳아 완충이 사라지고 뼈끼리 닿는다

지난번: 복도에 창문 있는 방이 나옴 — 104번과 같은 오류

고친 점: 104번과 똑같이 방으로 나온 원인은 '두 면 사이의 좁은 공간'이 실내 공간으로 읽힌 것 — 뼈 끝 두 개가 위아래에서 들어오는 배치와 좌우 여백을 못 박고 쿠션을 '손가락 두께 아이싱 띠'로 두께를 적고 --no에 room, window, table, architecture 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. Two bone ends face each other across one narrow horizontal gap that runs across the middle of the frame, seen from the side at eye level: one bone comes down from the top edge and widens into a rounded end, the other rises from the bottom edge and widens into a rounded end, and dark empty void fills the left and right sides of the frame around them. Each bone end is capped by a thick smooth glossy cushion layer lying along it like a band of icing, each cushion clearly as thick as a finger, even and unbroken along its whole length. The two cushions almost meet, with nothing between them but a thin film of clear fluid. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, room, corridor, window, table, furniture, floor, walls, architecture, interior, crystals, needles, spikes, grit, sand, particles, gemstones, smoke
```

## 117. m_double_vision — 두 눈의 시선 정렬이 어긋나 같은 사물이 두 개로 겹쳐 보임

지난번: 복시가 안 읽힘

고친 점: 복시가 안 읽힌 원인은 시작 이미지를 '겹침이 전혀 없다'로 적어 복시를 아예 안 그린 것 — '같은 방이 손 한 뼘 오른쪽·조금 위로 밀린 두 벌로 겹쳐 보이고 창틀도 탁자 다리도 두 벌'로 어긋남의 방향과 양을 적고 --no에 blur, ghosting, gland, sacs 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D a first-person view, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. This is a first-person point-of-view shot looking straight ahead from inside a person's own eyes, across the same plain empty room toward a bright window in the far wall, with one simple low table standing in the middle of the floor; the floor, walls, window frame and table are all rendered as translucent glass-like 3D forms in the same soft pale cyan glow and the space beyond the window is a dark empty slate blue-grey void. The whole scene appears twice: two complete copies of the same room, the second one shifted about a hand's width to the right and a little upward from the first, laid over each other so that the window has two sharp frames and the table has two sharp sets of legs that cross. Both copies are equally bright and both are perfectly sharp, every edge in each copy crisp. The view fills the whole vertical 9:16 portrait frame. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, hands, blur, bokeh, soft focus, motion blur, ghosting haze, mirror, reflection, split screen, frame, border, gland, sacs, grape cluster, duct, tissue, cells, microscopic, anatomy cutaway
```

## 118. m_duct_blockage — 분비샘의 관 입구가 굳거나 좁아져 막히고, 나가지 못한 분비물이 안에 고

지난번: 호박색 금지인데 구슬이 호박색, 폐색도 안 보임

고친 점: 호박색 구슬 하나에 폐색도 안 보인 원인은 시작 이미지를 '관이 열려 있고 분비물이 잘 나온다'로 적은 것 — 막힘을 시작 프레임에 넣어 '핀홀로 좁아진 입구에 박힌 마개 + 꽉 찬 주머니 8개'로 그리고 --no에 amber, golden, sphere, bead, villi 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A side cutaway of one small gland and its duct fills the middle of the frame, seen from the side at eye level. At the bottom sits a rounded cluster of about eight secreting sacs, every sac stretched tight and full to bursting with cloudy pale cyan secretion. From the top of that cluster one narrow duct rises straight up like a drilled shaft to a small round opening on a flat tissue surface that runs across the top of the frame. The duct is packed solid along its whole length with thick cloudy pale cyan secretion that has stopped moving, and at the very top the opening has closed down to a pinhole with one stiff plug of that same cloudy secretion wedged in it, so nothing is coming out onto the surface. The tissue around the opening is thickened and puckered. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, golden, yellow, sphere, ball, bead, marble, floating particle, villi, finger-like folds, hairy surface, sludge, chamber, balloon, volcano, machinery, pipe
```

## 127. m_sebum_overproduction — 피지샘이 부풀어 기름을 과하게 밀어내고 모공 주변에 쌓이는 그림

지난번: 피지 과분비가 아니라 나무뿌리처럼 나옴

고친 점: 나무뿌리처럼 나온 원인은 모공과 포도송이 샘이 가지치는 뿌리로 읽힌 것 — 모공을 '벽이 평행한 곧은 우물'로 못 박고 샘을 '왼쪽 벽 중간에 붙은 주머니 약 10개'로 위치·개수를 적고 --no에 spiral, coil, roots, tentacles 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D scalp skin, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A thick slab of skin seen from the side at eye level, like a slice cut out of a cake, sits in the lower two thirds of the frame with open dark empty space above it and its flat top surface facing straight up. One straight narrow pore runs vertically down into the slab from that top surface like a drilled well, its two walls straight and parallel, clearly visible through the translucent cut face, with one single straight hair shaft standing up out of it. Attached to the left wall of that pore, halfway down, is one small tight bunch of about ten rounded grape-like sacs, each sac swollen and full. A thick film of warm amber oil coats the inside of the pore from the sacs all the way up to the mouth, and a small pool of the same amber oil has welled up out of the mouth onto the surface. Everything except the amber oil is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, spiral, coil, helix, corkscrew, twisted ribbon, roots, tree roots, branching roots, tentacles, vine, head of hair, wig, scalp photograph, honey jar, bubbles, foam
```

## 131. m_autoimmune_attack — 면역세포들이 침입자가 아니라 자기 조직에 달라붙어 표면을 뜯어내고, 그 

지난번: 자가면역 공격이 안 읽힘

고친 점: 혈관에서 세포가 새어나오는 그림으로 나온 원인은 본문에 쓴 'There is no tube and no vessel'이라는 부정문이 tube·vessel을 오히려 불러온 것 — 그 문장을 삭제하고 금지는 --no로만 처리, 면역세포는 '짧은 팔이 달린 공 8개'로 형태를 줘 붙어서 뜯는 동작이 읽히게 함

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A wide surface of tightly packed plump pale cyan cells fills the lower two thirds of the frame, seen from a low skimming angle so the surface runs back and away to a horizon line, every cell smooth and whole and the wall between them unbroken, with open dark empty space above the horizon. Hovering in that dark space just above the surface are eight small round warm amber cells, each one a ball with short stubby gripping arms reaching down out of it, spread well apart from each other and none of them yet touching the surface below. Everything except those eight amber cells is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, tube, vessel, blood vessel, channel, pipe, blood cells, discs, hole in a wall, leak, bacteria rods, virus, fire, flames, red glow, swelling dome
```

## 133. m_bone_density_loss — 뼈 속 격자 구조의 기둥들이 가늘어지고 끊기면서 구멍이 커져 성글어짐

지난번: 뼈 밀도 감소가 안 읽힘(방사형 무늬)

고친 점: 방사형 무늬로 나온 원인은 '격자'가 방향 없이 퍼지는 결로 렌더된 것 — '정육면체 블록, 기둥이 세 방향 직각으로 만나고 빈칸은 전부 같은 크기의 정사각형'으로 방향과 반복을 못 박고 --no에 radial lines, sunburst, swirl, dome, fibres 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D bone interior, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One cube-shaped block of bone interior floats in the exact centre of the frame with dark void at all four edges, seen from slightly above and to one side so that two of its flat square faces and its depth are all visible. Inside the cube, straight thick struts run in three directions at right angles to one another and meet at sharp square joints, forming a regular three-dimensional lattice layer behind layer receding into the dark. The struts are solid and heavy, as thick as pencils, and the small hollow spaces between them are square, tight and all the same size. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, radial lines, fan, sunburst, swirl, spiral, whirlpool, dome, hill, fibres, hair, fur, silk, coral, sponge, honeycomb pattern, flat grid, skull, skeleton, x-ray film
```

## 134. m_electrical_misfire — 심장을 도는 전기 신호가 흐트러져 박동 순서가 뒤엉키거나 한 박자 일찍 

지난번: 전기 오발화가 안 읽힘(눈알 모양)

고친 점: 눈알 모양으로 나온 원인은 '가운데 노드 + 퍼지는 밝은 고리'가 홍채와 동공으로 읽힌 것 — '카펫처럼 프레임을 가득 채운 평평한 시트를 바로 위에서 본다'를 첫 문장에 박고 노드를 위쪽 3분의 1로 치우치게 옮기고 --no에 eyeball, iris, pupil, globe, light rays 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D a heart muscle wall, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One broad flat sheet of heart muscle fills the frame from edge to edge like a woven carpet seen from straight above, its fibres running as long sweeping bands that curve across the surface. Lying flat on top of those bands is a fine network of pale conducting strands that all branch outward from one small rounded node sitting in the upper third of the frame. One single bright ring of light is spreading outward from that node across the sheet in one even circle, already about half as wide as the frame, its band thin and clean. One faint warm amber point glows low in the lower right of the sheet, small and soft, not yet firing. The sheet, the strands and the ring are translucent pale cyan glass; only that one faint point is amber. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, eyeball, eye, lens, iris, pupil, eyelid, globe, sphere, ball, light rays, beams, ECG line, heartbeat graph, waveform, lightning bolt, circuit board, wires, electronics, whole heart organ, anatomical heart
```

## 135. m_eye_elongation — 안구의 앞뒤 길이가 늘어나면서 초점이 망막보다 앞쪽에 맺혀 상이 흐려짐

지난번: 호박색 금지인데 혈관 안이 호박색 띠

고친 점: 혈관 안에 호박색 띠가 나온 원인은 안구가 관으로 뒤바뀐 것 — '안구 하나를 세로로 반 갈랐고 윤곽은 정원'을 첫 문장에 박고 위아래 여백을 지정, 캐논 색 규칙대로 --no에 amber, golden, beads, tube, vessel 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D an eyeball, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One single eyeball seen from the side and cut clean in half along its length so its whole hollow inside is visible, sitting across the middle of the frame with open dark empty space above it and below it. Its outline is a perfect circle, exactly as tall as it is long. A rounded lens sits just inside the front of the globe on the left; the smooth thin inner rear wall curves across the back on the right. Three straight thin beams of light come in from the left edge of the frame, bend as they pass through the lens and meet at one sharp single point exactly on that rear wall. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, golden, yellow, beads, spheres in a row, tube, vessel, blood vessel, channel, blood cells, eyelashes, eyebrow, iris photograph, realistic eyeball, glasses, spectacles, eye chart, diagram
```

## 136. m_glucose_crash — 혈당이 기준선 아래로 뚝 떨어져 뇌와 근육의 연료가 바닥나고 떨림·식은땀

지난번: 혈당 급락이 안 읽힘(뼈 모양)

고친 점: 뼈 관절 모양으로 나온 원인은 '위아래 두 층' 구도가 마주 보는 뼈 두 끝으로 읽힌 것 — 위층은 가로 관, 아래층은 세포 블록이라고 각각 프레임 3분의 1씩 자리를 못 박고 호박색 구체를 약 80개로 세어 적고 --no에 bone, joint, two bone ends 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. Two separate layers are stacked one above the other with one clear empty gap between them, both seen from the side at eye level. The upper layer is one wide tube lying horizontally across the top third of the frame from the left edge to the right edge, sliced open lengthwise so its channel is visible, and that channel is crowded wall to wall with about eighty small warm amber spheres packed shoulder to shoulder with no clear fluid left between them. The lower layer is a solid block of plump rounded pale cyan cells filling the bottom third of the frame from edge to edge, brightly lit and full. The gap between the two layers is empty dark void about as tall as the tube. Everything except the amber spheres is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, bone, joint, knee, skeleton, cartilage, two bone ends, hourglass, sugar cubes, candy, food, graph, chart, gauge, arrow pointing down
```

## 139. m_lipid_oxidation — 피지 방울 속 지방산 사슬이 산소 알갱이와 만나 끊기고, 끊긴 조각이 새

지난번: 122번(미네랄 침식)과 그림이 거의 같음 — 구분 안 됨

고친 점: 122번(마디 있는 관)과 거의 같은 그림이 된 원인은 '평행한 사슬 가닥'이 마디진 원통으로 렌더된 것 — '유리구슬처럼 정원인 방울 하나가 프레임 가운데, 사방이 빈 공간'을 첫 문장에 박고 --no에 tube, segmented tube, stack of discs, column 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D an oil droplet, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One single round droplet of oil sits in the exact centre of the frame like a glass marble, its outline a perfect circle, filling most of the frame with dark empty void all around it and touching nothing. Inside the droplet, about a dozen long straight chain-like molecules lie parallel to one another like fine threads sealed in glass, every chain whole and unbroken from one side of the droplet to the other, clearly visible through the droplet's clear skin. Drifting in the dark void outside the droplet are six tiny paired round particles, each pair two little balls stuck together. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, tube, pipe, segmented tube, rings around a tube, stack of discs, bamboo, column, cylinder, bacteria, rods, microbes, petri dish, mould, oil bottle, cooking pan, flame, smoke
```

## 143. m_protein_clouding — 투명하던 단백질이 활성산소에 변성돼 뭉치면서 뿌옇게 흐려지고 빛이 통과하

지난번: 수정체 혼탁이어야 하는데 코일 감긴 관

고친 점: 코일 감긴 관으로 나온 원인은 '가닥이 늘어선 블록'이 감긴 줄로 읽힌 것 — '직사각 블록, 앞 잘린 면이 카메라 쪽, 가닥은 좌→우 평행 줄'로 형태를 못 박고 --no에 coil, spring, helix, rope, cable, loop 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D lens protein, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One rectangular block of lens tissue sits square in the middle of the frame, its flat front cut face turned toward the camera and its flat top facing straight up, with dark void above it and below it. The cut face shows long thin protein strands lying in perfectly ordered parallel rows, evenly spaced and all pointing the same way from the left side of the block to the right, so ordered that one single straight beam of light enters at the left edge of the frame, passes right through the block and leaves at the right edge without spreading, bending or scattering at all. A few tiny sharp-edged warm amber specks drift in the dark void just outside the block, none of them inside it yet. Everything except those specks is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, coil, coiled tube, spring, helix, spiral, rope, cable, loop, knot, tube, pipe, whole eyeball, iris, glasses, milk, smoke, fog, white haze
```

## 145. m_reflux_backflow — 관 끝의 조임근이 느슨하게 벌어지면서 아래 주머니의 내용물이 정상 흐름과

지난번: 역류가 안 읽힘

고친 점: 역류가 안 읽힌 원인은 시작 프레임을 '조임근이 꽉 닫혀 있고 관은 비었다'로 적어 방향이 아예 안 보인 것 — 조임근을 벌어진 상태로 바꾸고 호박색 혀가 관 안쪽까지 이미 올라온 지점을 명시, --no에 gland, grape cluster, column 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D digestive anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One long narrow tube runs straight down the centre of the frame from the top edge and meets the top of one rounded pouch that fills the lower third, both of them sliced open lengthwise with the cut faces toward the camera so their insides are visible. Where the tube joins the pouch, one thick ring of muscle wraps right around the tube's lower end, and at this moment that ring has gone slack and hangs open, leaving a wide gap. A still pool of warm amber liquid lies in the bottom of the pouch, and out of that pool one tongue of the same amber liquid has already climbed up through the open ring and risen a short way into the bottom of the tube above it, its leading edge clearly inside the tube. Everything except the amber liquid is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, gland, secreting sacs, grape cluster, duct, cylinder with a flat top, column, tower, whole stomach organ, anatomy chart, bottle, glass of drink, funnel
```

## 148. m_vagal_slowdown — 미주신경이 과하게 작동해 심장에 브레이크를 걸어 박동이 뚝 느려짐

지난번: 미주신경 둔화가 안 읽힘(돔 형태)

고친 점: 매끈한 돔으로 나온 원인은 방을 '잘라서 속이 보인다'고만 적어 통짜 덩어리가 된 것 — '위아래로 반 갈라 앞쪽 절반을 들어낸 열린 그릇'이라고 자른 방식을 적고 벽 두께가 테두리에 잘린 면으로 보이게 명시, --no에 dome, egg, closed shell, pitted texture 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One rounded hollow muscular chamber sits in the lower half of the frame, seen from the side and cut clean in half from top to bottom with the near half taken away, so the camera looks straight into its hollow inside like an open bowl; its thick banded wall is visible all around the rim as a cut edge, relaxed and evenly thick, and the hollow space inside it is empty and dark. One thick nerve cord enters the frame at the top left corner and runs down to the middle of the frame, where it fans out into fine branches that spread over the upper wall of the chamber and lie flat against it. Open dark empty space fills the upper right of the frame. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, blood colour, dome, solid dome, egg, closed shell, pitted texture, foam, bubbles, honeycomb skin, whole heart anatomy chart, machinery, pump
```

## 151. m_acid_deficiency — 주머니 벽의 분비샘에서 산 방울이 거의 맺히지 않아 내용물이 분해되지 않

지난번: 위산 부족이 안 읽힘

고친 점: Y자 혈관 + 솔 모양으로 나온 원인은 케이크 조각 판 구도가 가지 친 관으로 읽힌 것 — 성공한 m_acid_secretion 판 문장을 그대로 재사용해 위치를 고정하고 샘이 '얕고 가늘게 쪼그라들었다'는 점과 마른 표면을 강조, --no에 branching tube, Y-shape, vessel, brush 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A thick slab of stomach wall seen from the side at eye level, like a slice cut out of a cake, sits centered in the lower half of the frame with open dark empty space above it and its flat top surface facing straight up. That top surface is dotted with small round pit openings; below each opening one narrow tube-shaped gland runs down into the tissue, and every one of those glands is visibly shrunken, thin and shallow, reaching only a little way down, clearly visible through the translucent cut face. Resting on the top surface sit three large ragged lumps of undigested food matter, each lump whole, solid and unbroken. Only two or three tiny warm amber droplets cling at the mouths of a couple of pits; the surface is otherwise bare and dry with no pool, no layer and no film of liquid anywhere. Everything except those few droplets is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, branching tube, Y-shape, fork, vessel, blood vessel, blood cells, brush, bristles, sausage, cake, pool of liquid, flood, thick liquid layer, glossy film
```

## 155. m_dopamine_loop — 자극이 하나 끝날 때마다 보상물질이 새로 분비돼 계속 다음 자극을 찾게 

지난번: 형체 불명 조각

고친 점: 형체 불명의 작은 조각으로 나온 원인은 피사체가 프레임을 못 채우고 떠 있는 부스러기로 렌더된 것 — 두 신경 말단을 '각각 위·아래 가장자리에서 들어와 좌우 끝까지 꽉 채우고 틈은 좁은 띠뿐'으로 크기를 못 박고 --no에 fragment, flake, mostly empty frame 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human nerve tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. Two thick nerve endings face each other across one narrow empty gap that runs horizontally across the middle of the frame. The upper ending hangs down from the top edge and the lower ending rises from the bottom edge, both seen from the side, and both are massive, filling the frame from the left edge to the right edge so the gap between them is only a narrow band. Pressed up against the flat lower face of the upper ending is a cluster of about a dozen small round sacs, and a few tiny warm amber particles are held inside those sacs, visible through their walls. The flat upper face of the lower ending is covered in small round open sockets, all of them empty. The gap itself is completely empty. Everything except the particles inside the sacs is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, small object in empty space, debris, fragment, flake, leaf, scrap, torn paper, mostly empty frame, diagram, cross-section chart, flat illustration, pills, capsules
```

## 157. m_fibrosis — 결합조직이 두껍고 질기게 변해 오그라들며 당긴다

지난번: 섬유화가 안 읽힘(매끈한 돔)

고친 점: 매끈한 돔으로 나온 원인은 블록이 둥근 언덕으로 뭉개지고 섬유가 안 보인 것 — '잘린 면이 정면, 좌우 끝이 프레임 가장자리에 닿는 각진 블록'을 못 박고 섬유를 '신발끈 굵기 6가닥이 좌→우로'로 수와 굵기를 적고 --no에 dome, hill, sphere, smooth blob 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A solid block of tissue seen from the side at eye level fills the lower two thirds of the frame, its flat cut face squarely toward the camera and its flat top surface facing straight up, with open dark empty space above it; the block's left and right edges reach the left and right edges of the frame. Inside the block, visible through the cut face, about six soft wavy fibre strands each as thick as a shoelace run from the left cut edge across to the right cut edge, lying slack, gently curved and well spaced, with soft even tissue filling the wide gaps between them. The top surface is flat, smooth and level from end to end with no bump and no pucker. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, dome, hill, mound, sphere, ball, bubble, planet, horizon, smooth blob, rope, braid, textile, wood grain
```

## 159. m_growth_arrest — 조직을 만드는 기질이 잠시 멈췄다 재개되며 경계에 흔적이 남는다

지난번: 성장판 정지가 안 읽힘(빈 상자)

고친 점: 빈 상자로 나온 원인은 '생성 기질 + 판'이라는 추상 서술에 그릴 덩어리가 없어 용기로 채워진 것 — 기질을 '어란 무더기처럼 쌓인 둥근 세포'로, 판을 '동전 세 개 두께에 잘린 모서리에 층 줄무늬가 보이는 평판'으로 바꿔 적고 --no에 box, cube, tank, container, room 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A cross-section seen from the side at eye level. Along the bottom left of the frame sits a growth bed of small tightly packed round cells heaped up like a mound of fish roe, running from the left edge to the middle of the frame. Growing straight out of that bed and running up and away toward the right edge of the frame is one flat hard plate about as thick as three coins stacked, built from thin layers that are clearly visible as fine stripes along its cut edge, its outer upper surface perfectly smooth and even along its whole length with no mark, no groove and no ridge anywhere on it. Open dark empty space fills the upper left of the frame. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, box, cube, tank, glass container, empty container, aquarium, room, chamber, shelf, fingernail polish, hand, foot, ruler, ladder
```

## 160. m_indoor_air_buildup — 닫힌 공간에 날숨 이산화탄소·오염물질이 쌓여 신선한 공기가 밀려나는 그림

지난번: 실내 공기 오염 축적이 안 읽힘

고친 점: 오염 축적이 안 읽힌 원인은 조직 표면(융모)으로 렌더돼 상자 자체가 사라진 것 — 상자를 '바닥·사방 벽·윗뚜껑이 다 있는 밀폐 유리 상자'로 면을 하나씩 적고 바닥 오염층을 '상자 높이의 5분의 1, 윗면이 수평선으로 읽힘'으로 두께를 지정, --no에 villi, carpet, cells 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D still indoor air, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One sealed box-shaped chamber of still air stands in the middle of the frame seen from the side at eye level, filling most of it: a flat floor across the bottom, smooth featureless glass walls closing it on every side and a flat glass lid across the top, with one narrow closed slit vent set high on the right wall. Dark void surrounds the box on all four sides. The air inside the upper part of the chamber is clear and open with a fine scattering of tiny bright pale cyan motes drifting evenly through it. Lying along the floor is a thick settled bank of countless small warm amber specks, packed dense and about a fifth as tall as the chamber, its top edge clearly readable as a level line. Everything except those amber specks is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, villi, finger-like folds, hairy surface, carpet, fur, tissue surface, cells, mucosa, furniture, bed, window frame, house, architecture, room interior, aquarium, fish, plants
```

## 165. m_parasite_penetration — 실처럼 가는 유충이 점막 표면을 훑다 한 지점에 머리를 박고 조직 속으로

지난번: 기생충이 안 보임(마디 있는 관만)

고친 점: 마디 있는 관만 나오고 기생충이 안 보인 원인은 유충이 관으로 커져 마디 구조가 된 것 — '머리카락 굵기, 길이는 화면의 3분의 1, 마디도 고리도 다리도 없는 매끈한 S자'로 굵기·길이·표면을 못 박고 --no에 segmented tube, stack of blocks, bamboo, vertebrae 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A wide tissue surface seen from a low skimming angle just above it, running from the bottom edge of the frame back to a horizon line in the upper third, with open dark empty space above the horizon. The surface is a damp glossy carpet of tall thin finger-like folds standing upright, thousands of them, all the same height. Lying across the tops of those folds near the centre of the frame is one single thread-like worm, warm amber, as thin as a hair and as long as a third of the frame, its body a loose smooth S-curve with no segments, no rings and no legs anywhere on it, and its head end lifted a little off the surface and angled down toward one gap between two folds. Everything except that worm is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, segmented tube, stack of blocks, bamboo, vertebrae, ladder, caterpillar, beads on a string, column, cylinder, insect, legs, snake scales, hair strand, noodle, rope
```

## 169. m_virus_reactivation — 신경 줄기 안쪽에 잠들어 있던 작은 입자들이 깨어나 신경 다발을 따라 표

지난번: 형체 불명(선 몇 개)

고친 점: 선 몇 개로 나온 원인은 신경 줄기가 가는 선으로 렌더돼 매듭도 입자도 사라진 것 — '엄지 굵기의 묵직한 줄기, 가는 선이 아니다'를 명시하고 매듭을 '호두 크기', 입자를 약 30개로 세어 적고 --no에 thin lines, wires, sparse, empty frame 추가

```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One thick nerve cord as wide as a thumb runs from the bottom edge of the frame straight up to the top edge through the exact centre, seen from the side and sliced open lengthwise with the cut face toward the camera, so the long parallel fibres packed solidly inside it are visible along its whole length; the cord is solid and heavy, not a thin line. A third of the way up, the fibres swell out into one round knot of cell bodies about the size of a walnut, and packed motionless inside that knot sits one tight cluster of about thirty tiny warm amber particles. At the top of the frame the cord fans out into fine branches that reach up and press against a flat tissue surface running across the top edge. Everything except those amber particles is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, thin lines, wires, strands, hair, sparse, empty frame, rope, string, spiky virus model, coronavirus illustration, diagram, flat illustration, tree, roots
```

