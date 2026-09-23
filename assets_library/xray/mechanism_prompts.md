# mechanism_prompts.md — 기전 컷어웨이 라이브러리 (9:16)

칠판 설명 중 "왜 그런지" 문장에 **4초 통째로** 끼우는 미시 장면. 부위 캐논과 같은 청록 유리 톤에,
**해로운 것(위산·세균·과한 물질)만 호박색** — 부위 점등과 같은 색 규칙이라 한 세계로 읽힌다.

🚨 **4초 안에 컷 3개(약 1.3초씩)로 넘긴다(2026-09-19 사용자 "4초로 가면 되지… 3개정도로 쪼개서 넘기는게")** —
한 장면을 4초 끄는 것보다 리듬이 산다. 컷이 넘어가는 클립이라 **끝 프레임은 쓰지 않는다**(끝 프레임은 한 장면이
연속으로 변할 때 쓰는 것이고, 컷을 나누면 오히려 방해가 된다). 그래서 이 파일의 Flow 프롬프트엔 `no scene cuts`가
없다 — 의도적으로 컷을 요청하는 예외다.

미드저니: **시작 이미지 1장만**. `stills/canon_organs.jpg`를 **Style Reference**로(색·질감만).
⚠️ Omni Reference 금지 — "이 대상을 넣어라"라서 위벽 클로즈업에 전신 인체가 끼어든다.

Flow: 시작 이미지를 첫 프레임으로(end 비움), 4초. 저장: `stills/mech/<이름>.jpg` / 결과 `output/<이름>.mp4`

## 1차 — 위염 편(소화_9) 시험용 3종

### m_acid_secretion ⏱ 4초 · 3컷 — 위산 분비 증가

⚠️ 1차 시안(2026-09-19) 탈락: "위벽 단면"만 적었더니 세포 덩어리 위에 불투명한 흰 크림층이 얹힌 빵 같은 모양이 나왔고, 위샘 구멍이 안 보이고 피사체가 모서리에 쏠렸다. → 케이크 조각처럼 옆에서 본 판, 위로 열린 구멍, 그 아래 관 모양 샘, 표면 위 빈 공간을 모양으로 명시하고 흰 층을 --no에 넣었다.

들어갈 문장: "카페인은 위벽의 산 분비 세포를 직접 자극해서, 위산이 평소보다 더 많이 나오게 만들어요"

**미드저니 (시작 이미지)**
```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A thick slab of stomach wall seen from the side at eye level, like a slice cut out of a cake, centered in the lower half of the frame with open dark empty space above it. The top surface of the slab faces straight up and is dotted with dozens of small round pit openings; below each opening a narrow tube-shaped gland runs straight down into the tissue, clearly visible through the translucent cut face. A thin glossy film of warm amber liquid lies across the top surface. Everything except the amber liquid is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, sausage
```

**Flow** (첫 프레임만, end 비움)
```
Three quick shots cut together, about 1.3 seconds each. Shot 1 (0-1.3s): the cross-section of the stomach lining, tiny bright amber droplets starting to bubble up out of the gland pits, slow push-in. Shot 2 (1.3-2.7s): cut to an extreme close-up looking straight down into a single gland pit as a thick jet of bright amber acid gushes upward toward the lens. Shot 3 (2.7-4s): cut to a wide high-angle view of the whole lining completely flooded under a deep, rippling pool of glowing amber acid. Keep the exact same translucent pale cyan glass tissue style and dark slate blue-grey void in all three shots; only the harmful substance glows warm amber. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a rising bubbling gurgle and a hissing surge, no music, no dialogue.
```

### m_mucus_barrier ⏱ 4초 · 3컷 — 점막 보호막 약화

⚠️ 1차 시안 탈락(2026-09-19): 층 순서가 뒤집혀(조직→호박색→흰 크림 덩어리) 보호막이 안 보였고 속이 장 주름처럼 나왔다. → 위산 컷에서 성공한 판 구도를 그대로 쓰고 층을 아래→위로 명시했다. **`stills/mech/m_acid_secretion.jpg`를 Image Prompt로** 넣으면 두 컷이 같은 판으로 이어져 보인다(Style Reference `canon_organs.jpg`는 그대로).

들어갈 문장: "진통제 성분이 위 점막을 보호하는 프로스타글란딘의 합성을 막아서, 점막이 위산에 그대로 노출돼요"

**미드저니 (시작 이미지)**
```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A thick slab of stomach wall seen from the side at eye level, like a slice cut out of a cake, centered in the lower half of the frame with open dark empty space above it. Stacked from bottom to top: the translucent pale cyan tissue with small round pit openings on its top surface; directly on that surface one smooth, thick, perfectly continuous layer of clear pale cyan protective gel; and resting on top of the gel a thin film of warm amber liquid that never touches the tissue. The gel is the same translucent pale cyan glass as the tissue, only the amber liquid is colored. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap
```

**Flow** (첫 프레임만, end 비움)
```
Three quick shots cut together, about 1.3 seconds each. Shot 1 (0-1.3s): the smooth pale cyan protective gel layer over the stomach lining begins to thin and ripple, slow push-in. Shot 2 (1.3-2.7s): cut to a close-up of the gel as holes tear open across it and spread outward, amber acid pressing through the holes. Shot 3 (2.7-4s): cut to an extreme close-up of bare lining cells as warm amber acid pours over them and they glow faintly amber where it touches. Keep the exact same translucent pale cyan glass tissue style and dark slate blue-grey void in all three shots; only the harmful substance glows warm amber. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a slow tearing stretch and a sizzling hiss, no music, no dialogue.
```

### m_cell_damage ⏱ 4초 · 3컷 — 점막 세포 손상

✅ 1차 시안 3번 채택(2026-09-19) — 통통한 세포 벽 위에 호박색 층이 바로 얹힘. 나머지는 흰 크림층이 덧씌워짐.

들어갈 문장: "나트륨 농도가 높아지면 위 점막 세포가 삼투압 자극으로 손상되고, 그 틈으로 위산과 헬리코박터균이 더 쉽게 침투해요"

**미드저니 (시작 이미지)**
```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. An extreme close-up of tightly packed plump pale cyan lining cells forming one smooth unbroken wall, a warm amber acid layer resting above them. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap
```

**Flow** (첫 프레임만, end 비움)
```
Three quick shots cut together, about 1.3 seconds each. Shot 1 (0-1.3s): the plump lining cells begin to shrink and wrinkle as water drains out of them, slow push-in. Shot 2 (1.3-2.7s): cut to a side view as dark cracks split open between the shriveled cells. Shot 3 (2.7-4s): cut to an extreme close-up of one crack as warm amber acid and tiny wriggling amber rod-shaped bacteria slide down into it and push deeper. Keep the exact same translucent pale cyan glass tissue style and dark slate blue-grey void in all three shots; only the harmful substance glows warm amber. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a dry crackling shrink and a faint wet seep, no music, no dialogue.
```

## 2차 — 범용 12종 (2026-09-20 작성)

1차 3종(`m_acid_secretion`·`m_mucus_barrier`·`m_cell_damage`)과 같은 규칙이다:
미드저니는 **시작 이미지 1장만**, `stills/canon_organs.jpg`를 **Style Reference**로만 쓴다
(⚠️ Omni Reference 금지 — 클로즈업에 전신 인체가 끼어든다). Flow는 시작 이미지를 첫 프레임으로
넣고 **end는 비운다**. 4초 안에 컷 3개(약 1.3초씩). 저장: `stills/mech/<이름>.jpg` / `output/<이름>.mp4`.

🚨 **1차 시안 탈락 사유를 그대로 반영했다** — "단면"만 적으면 (a) 불투명한 흰 크림층이 얹힌 빵/케이크가
나오고 (b) 층 순서가 뒤집히고 (c) 피사체가 모서리로 쏠린다. 그래서 12종 전부 **옆에서 본 판인지 위에서
본 면인지 / 층을 아래→위 순서로 / 화면 어디에 놓을지**를 문장으로 못 박았고, `--no`에 `white layer,
cream layer, crust, opaque cap, bread`를 공통으로 넣었다.

색 규칙: **해로운 것(산·세균·과한 물질·결정)만 warm amber**, 나머지 조직·체액은 전부 translucent pale
cyan glass, 배경은 dark slate blue-grey void. 압박·수축·경련처럼 **물질이 아닌 기전은 호박색을 쓰지 않고**
모양 변화로만 보여준다(통증이 실제로 발생하는 순간만 아주 옅은 amber 글로).

## 12종 선정 근거 — narration 152편 실측

`data/*/narration.txt` + `data/*/*/narration.txt` 152편 전수 grep. 괄호는 그 기전 어휘가 등장한 편수.

| 이름 | 한국어 | 편수 | 주로 쓰는 topic 계열 |
|---|---|---|---|
| `m_inflammation` | 염증 반응 | 37 | 귀·코·근골격·피부·소화·눈 |
| `m_nerve_compression` | 신경 압박 | 38 중 압박 계열 | 손발·근골격·머리·눈(녹내장)·소화 |
| `m_nerve_overdrive` | 신경 신호 과흥분 | 38(카페인) | 수면·피로·비뇨기·머리·귀 |
| `m_fluid_retention` | 수분 정체·부종 | 38 | 눈·근골격·순환·여성·귀·고령 |
| `m_dehydration` | 표면 수분 마름 | 35 | 눈·입·코·피부·귀·냄새 |
| `m_toxin_load` | 독성물질 유입·해독 부담 | 41(알코올) | 소화·대사·순환·수면·피로 |
| `m_blood_flow_drop` | 혈류 감소 | 30 | 순환·어지럼증·손발·귀·고령·계절질환 |
| `m_pressure_buildup` | 압력 상승·배출로 막힘 | 29 | 눈·코·비뇨기·귀·머리 |
| `m_bacteria_growth` | 세균 증식 | 29 | 입·냄새·피부·귀·비뇨기·코 |
| `m_glucose_spike` | 혈당 급상승 | 28 | 혈당·대사·피로·수면 |
| `m_muscle_tension` | 근육 긴장·경련 | 27 | 근골격·손발·머리·계절질환·순환 |
| `m_waste_buildup` | 노폐물·결정 축적 | 22 | 근골격(통풍)·비뇨기·순환·고령·대사·미세먼지 |

**뺀 것**: 지방 축적(24편으로 잡혔지만 대부분 "포화지방이 많은 음식"이라는 **식품 서술**이고 지방세포가
부푸는 기전을 설명하는 건 소수라 범용성이 낮다), 알레르기·면역(9편), 자외선 손상(7편), 콜라겐 감소(4편) —
셋 다 편수가 적어 전용 컷으로 만드는 게 낫다.

---

### 미드저니 — 시작 이미지 12장

`canon_organs.jpg`를 Style Reference로(Omni Reference 금지).

**m_inflammation ⏱ 4초 · 3컷 — 염증 반응**
```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A flat slab of tissue seen from the side at eye level, its top surface facing straight up, filling the lower two thirds of the frame with open dark empty space above it. One single translucent tube runs horizontally straight through the middle of the slab from the left edge to the right edge, its wall clearly visible through the cut face; a few small round warm amber cells drift inside the tube. The tissue above and below the tube is smooth, flat and evenly packed with plump pale cyan cells. Everything except the amber cells inside the tube is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, red glow, orange gradient, fire, flames
```

**m_nerve_compression ⏱ 4초 · 3컷 — 신경 압박**
```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A thick nerve cord made of many long parallel fibres bundled inside a smooth outer sheath, running straight from the top edge of the frame to the bottom edge through the exact centre. Halfway down, the cord passes through a narrow gap between two hard dense blocks, one pressing in from the left and one from the right, their surfaces flat and facing each other. At this moment the gap is still wide and the cord is perfectly round and uncompressed. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, cables, wires, electronics
```

**m_nerve_overdrive ⏱ 4초 · 3컷 — 신경 신호 과흥분**
```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D nerve tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. Two thick nerve endings face each other across a narrow empty gap in the middle of the frame, one coming down from the top, one rising from the bottom, both seen from the side. The flat face of the lower ending is covered with dozens of small round open sockets, clearly visible through the translucent surface. A few tiny warm amber particles drift in the gap between the two endings, none of them touching the sockets yet. Everything except those particles is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, diagram, cross-section chart, flat illustration
```

**m_fluid_retention ⏱ 4초 · 3컷 — 수분 정체·부종**
```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A block of tissue seen from the side at eye level, its flat top surface facing straight up, filling the lower two thirds of the frame with open dark empty space above it. Inside the block, plump rounded pale cyan cells are packed tightly together with only hairline gaps between them, the gaps clearly visible through the cut face. A scattering of tiny warm amber grains sits on the top surface of the block. Everything except those grains is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, foam, bubbles
```

**m_dehydration ⏱ 4초 · 3컷 — 표면 수분 마름**
```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A slab of tissue seen from the side at eye level, like a slice cut out of a cake, sitting in the lower half of the frame with open dark empty space above it. Stacked from bottom to top: the translucent pale cyan tissue with plump cells; on its flat top surface one thin, smooth, perfectly continuous sheet of clear watery film with a glossy wet highlight running along it; nothing above the film but empty dark void. The film is the same translucent pale cyan glass as the tissue. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, thick gel, foam
```

**m_toxin_load ⏱ 4초 · 3컷 — 독성물질 유입·해독 부담**
```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. An extreme close-up of large plump pale cyan cells packed tightly together in a block, each cell holding one clearly visible round nucleus. A single narrow channel winds between the cells from the top left of the frame down to the bottom right, its walls smooth and clear, and a thin stream of warm amber liquid is just beginning to flow into it from the top left corner. Everything except that amber stream is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, whole organ, liver silhouette, bottle, glass of drink
```

**m_blood_flow_drop ⏱ 4초 · 3컷 — 혈류 감소**
```
Medical holographic visualization, extreme microscopic close-up of a translucent glass-like 3D vessel, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One thick vessel runs straight down the centre of the frame from the top edge to the bottom edge, sliced open lengthwise so the open channel inside is fully visible along its whole length. The channel is wide and evenly round, and dozens of small smooth disc-shaped cells drift down it in a steady single file. A ring of banded muscle fibres wraps around the outside of the vessel wall, relaxed and loose. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, blood colour, pipe, plumbing
```

**m_pressure_buildup ⏱ 4초 · 3컷 — 압력 상승·배출로 막힘**
```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. One rounded closed chamber sits in the middle of the frame, seen from the side and cut open so its hollow inside is visible, filled with clear pale cyan fluid. A single narrow drain channel leaves the chamber from its lower right side and runs off toward the right edge of the frame, open and clear, with a thin trickle of the same clear fluid leaving through it. Directly behind the chamber, pressed against its back wall, lies a soft bundle of long parallel fibres. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, balloon, sphere on a stand, machinery
```

**m_bacteria_growth ⏱ 4초 · 3컷 — 세균 증식**
```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A wide flat tissue surface seen from a low skimming angle just above it, running from the bottom edge of the frame back toward the horizon line in the upper third, with open dark empty space above. The surface is a mosaic of plump pale cyan cells, damp and glossy. Scattered across it lie about a dozen small warm amber rod-shaped bacteria, well separated from each other, each one casting a tiny soft shadow. Everything except those rods is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, petri dish, mould, hair
```

**m_glucose_spike ⏱ 4초 · 3컷 — 혈당 급상승**
```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. Two layers stacked with a clear gap between them, both seen from the side at eye level. The lower layer is a slab of gut wall whose top surface is covered in tall thin finger-like folds standing upright; a loose scatter of small warm amber spheres rests among the folds. The upper layer is one thick vessel running horizontally across the frame, sliced open lengthwise so the empty channel inside is visible, almost clear at this moment. Everything except the amber spheres is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, sugar cubes, candy, food
```

**m_muscle_tension ⏱ 4초 · 3컷 — 근육 긴장·경련**
```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D muscle tissue, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. A bundle of long parallel muscle fibres runs diagonally across the whole frame from the lower left corner to the upper right corner, each fibre marked with fine evenly spaced crosswise bands along its length. The fibres lie loose, straight and evenly spaced, with narrow dark gaps between them and open empty void in the corners. Everything is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, amber, orange, red, whole muscle, anatomy chart, rope, braid
```

**m_waste_buildup ⏱ 4초 · 3컷 — 노폐물·결정 축적**
```
Medical holographic visualization, extreme microscopic close-up of translucent glass-like 3D human anatomy, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, shallow depth of field, the subject centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. Two smooth rounded surfaces face each other across a narrow fluid-filled space that runs horizontally across the middle of the frame, one surface curving down from above and one curving up from below, both glossy and unmarked. The space between them is filled with clear pale cyan fluid, and a few tiny warm amber needle-shaped crystals drift slowly in it without touching either surface yet. Everything except those crystals is translucent pale cyan glass. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, face, full body, white layer, cream layer, crust, opaque cap, bread, smoke, fog, dust cloud, gemstones
```

### Flow — 모션 프롬프트 12개

시작 프레임은 위에서 만든 `stills/mech/<이름>.jpg`, 끝 프레임은 비움. 전부 4초.

**m_inflammation ⏱ 4초 · 3컷 — 염증 반응**
```
Three quick shots cut together, about 1.3 seconds each. Shot 1 (0-1.3s): the small warm amber cells inside the horizontal tube crowd against the tube wall and start squeezing through it into the surrounding tissue, slow push-in. Shot 2 (1.3-2.7s): cut to a close-up of the tissue just outside the tube as more amber cells pour out and clear fluid floods the gaps between the pale cyan cells, pushing them apart. Shot 3 (2.7-4s): cut to a wide side view of the whole slab as its top surface swells upward into a thick rounded dome, the amber cells scattered all through the swollen tissue. Keep the exact same translucent pale cyan glass tissue style and dark slate blue-grey void in all three shots; only the harmful immune cells glow warm amber. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a low swelling throb and a soft wet surge, no music, no dialogue.
```

**m_nerve_compression ⏱ 4초 · 3컷 — 신경 압박**
```
Three quick shots cut together, about 1.3 seconds each. Shot 1 (0-1.3s): the two hard blocks slide toward each other and the round nerve cord between them begins to flatten, slow push-in. Shot 2 (1.3-2.7s): cut to an extreme close-up of the squeezed section as the parallel fibres inside are crushed flat against each other and the outer sheath buckles. Shot 3 (2.7-4s): cut to a view along the cord below the squeeze as erratic warm amber sparks shoot down the flattened fibres in quick irregular bursts and scatter off the end. Keep the exact same translucent pale cyan glass style and dark slate blue-grey void in all three shots; only the misfiring pain signal glows warm amber, the tissue never changes colour. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a deep grinding press and a sharp crackling snap, no music, no dialogue.
```

**m_nerve_overdrive ⏱ 4초 · 3컷 — 신경 신호 과흥분**
```
Three quick shots cut together, about 1.3 seconds each. Shot 1 (0-1.3s): a dense cloud of tiny warm amber particles pours into the gap between the two nerve endings from the left, slow push-in. Shot 2 (1.3-2.7s): cut to an extreme close-up of the round sockets as amber particles drop into them one after another and plug them shut, each plugged socket sealing over. Shot 3 (2.7-4s): cut to a pulled-back view of the whole nerve branching away into the dark, its fibres flashing over and over in fast restless bursts that never settle. Keep the exact same translucent pale cyan glass style and dark slate blue-grey void in all three shots; only the incoming stimulant particles glow warm amber. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a rushing swarm and a fast ticking pulse that will not slow, no music, no dialogue.
```

**m_fluid_retention ⏱ 4초 · 3컷 — 수분 정체·부종**
```
Three quick shots cut together, about 1.3 seconds each. Shot 1 (0-1.3s): the tiny warm amber grains sink down into the tissue and clear fluid begins seeping in behind them, slow push-in. Shot 2 (1.3-2.7s): cut to an extreme close-up of two neighbouring cells as the hairline gap between them fills with clear fluid and widens, pushing the cells apart while the cells themselves keep their shape. Shot 3 (2.7-4s): cut to a wide side view of the whole block as every gap is flooded and the block swells thicker and heavier, its flat top surface bulging upward and quivering. Keep the exact same translucent pale cyan glass tissue style and dark slate blue-grey void in all three shots; only the salt grains glow warm amber, the retained water stays clear pale cyan. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a slow heavy swelling and a dull sloshing weight, no music, no dialogue.
```

**m_dehydration ⏱ 4초 · 3컷 — 표면 수분 마름**
```
Three quick shots cut together, about 1.3 seconds each. Shot 1 (0-1.3s): the thin watery film on the surface thins out and tiny droplets lift off it into the dark void above, its glossy highlight fading, slow push-in. Shot 2 (1.3-2.7s): cut to a close-up of the surface as the last of the film pulls back into shrinking islands and the bare tissue between them turns matte and dull. Shot 3 (2.7-4s): cut to an extreme close-up looking straight down at the bare surface as it tightens and splits into a web of dry cracks, and a few small warm amber specks settle down into the open cracks. Keep the exact same translucent pale cyan glass tissue style and dark slate blue-grey void in all three shots; only the harmful specks that land at the end glow warm amber. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a faint evaporating hiss and a dry tightening creak, no music, no dialogue.
```

**m_toxin_load ⏱ 4초 · 3컷 — 독성물질 유입·해독 부담**
```
Three quick shots cut together, about 1.3 seconds each. Shot 1 (0-1.3s): the thin stream of warm amber liquid floods the whole winding channel until it runs full from corner to corner, slow push-in. Shot 2 (1.3-2.7s): cut to a close-up of the channel wall as amber liquid soaks through it and creeps into the plump cells on both sides, the amber spreading cell by cell. Shot 3 (2.7-4s): cut to an extreme close-up of a single soaked cell as it bloats, its round nucleus pushed off to one side and its once bright pale cyan glow going dim and murky. Keep the exact same translucent pale cyan glass tissue style and dark slate blue-grey void in all three shots; only the toxic substance glows warm amber. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a thick pouring flood and a slow laboured drag, no music, no dialogue.
```

**m_blood_flow_drop ⏱ 4초 · 3컷 — 혈류 감소**
```
Three quick shots cut together, about 1.3 seconds each. Shot 1 (0-1.3s): the ring of banded muscle fibres around the vessel tightens and the open channel inside begins to narrow, the disc-shaped cells slowing down, slow push-in. Shot 2 (1.3-2.7s): cut to an extreme close-up of the narrowest point as the disc cells jam and stack up behind it, only a few squeezing through one at a time. Shot 3 (2.7-4s): cut to a wide view of the far end of the vessel beyond the squeeze, almost empty now, its thin side branches going still and their glow fading down to a faint dim outline. Keep the exact same translucent pale cyan glass style and dark slate blue-grey void in all three shots; nothing in this clip is amber, the whole scene stays pale cyan and only the brightness drops. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a squeezing rubbery strain and a rushing flow that thins to near silence, no music, no dialogue.
```

**m_pressure_buildup ⏱ 4초 · 3컷 — 압력 상승·배출로 막힘**
```
Three quick shots cut together, about 1.3 seconds each. Shot 1 (0-1.3s): thick warm amber sludge creeps into the narrow drain channel from the right and packs it solid, the trickle leaving the chamber stopping dead, slow push-in. Shot 2 (1.3-2.7s): cut to a wider side view of the chamber as clear fluid keeps pouring in from above with nowhere to go, the chamber filling past full and its walls stretching taut and round. Shot 3 (2.7-4s): cut to an extreme close-up of the back wall as it bows outward and crushes the bundle of parallel fibres behind it flat against the surrounding tissue. Keep the exact same translucent pale cyan glass style and dark slate blue-grey void in all three shots; only the sludge blocking the drain glows warm amber, the trapped fluid stays clear pale cyan. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a gurgle that chokes off and a slow straining creak under pressure, no music, no dialogue.
```

**m_bacteria_growth ⏱ 4초 · 3컷 — 세균 증식**
```
Three quick shots cut together, about 1.3 seconds each. Shot 1 (0-1.3s): the scattered warm amber rods twitch and each one pinches in the middle and splits into two, slow push-in low over the surface. Shot 2 (1.3-2.7s): cut to an extreme close-up of one patch as the rods double again and again into a crawling amber cluster that spreads outward across the cells. Shot 3 (2.7-4s): cut to a wide skimming view as the whole surface disappears under a thick sticky amber mat, and faint wisps rise off it into the dark void above. Keep the exact same translucent pale cyan glass tissue style and dark slate blue-grey void in all three shots; only the bacteria glow warm amber. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a dry skittering multiplication and a thick wet spreading squelch, no music, no dialogue.
```

**m_glucose_spike ⏱ 4초 · 3컷 — 혈당 급상승**
```
Three quick shots cut together, about 1.3 seconds each. Shot 1 (0-1.3s): the warm amber spheres among the finger-like folds are drawn down through the gut wall in a rush, slow push-in. Shot 2 (1.3-2.7s): cut to a close-up of the vessel above as a dense torrent of amber spheres bursts up into its open channel and packs it from wall to wall. Shot 3 (2.7-4s): cut to an extreme close-up inside the crowded channel as the amber spheres grind against the vessel wall in a thick slow-moving flood, the wall itself scuffing and dulling where they scrape. Keep the exact same translucent pale cyan glass tissue style and dark slate blue-grey void in all three shots; only the sugar particles glow warm amber. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a rushing granular pour and a heavy grinding surge, no music, no dialogue.
```

**m_muscle_tension ⏱ 4초 · 3컷 — 근육 긴장·경련**
```
Three quick shots cut together, about 1.3 seconds each. Shot 1 (0-1.3s): the crosswise bands along the fibres draw closer together as the whole bundle pulls tight and straightens, slow push-in. Shot 2 (1.3-2.7s): cut to a close-up of one stretch of the bundle as a group of fibres bunches into a hard knot, shortening and thickening while the fibres on either side are dragged in toward it. Shot 3 (2.7-4s): cut to an extreme close-up of the knot as it locks and judders in place, refusing to release, a faint warm amber glow rising at its very centre and nowhere else. Keep the exact same translucent pale cyan glass tissue style and dark slate blue-grey void in all three shots; the tissue stays pale cyan throughout and only the final pain point glows faintly amber. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a tightening creak and a hard locking judder, no music, no dialogue.
```

**m_waste_buildup ⏱ 4초 · 3컷 — 노폐물·결정 축적**
```
Three quick shots cut together, about 1.3 seconds each. Shot 1 (0-1.3s): the drifting warm amber needle crystals slow, sink and settle down onto the lower surface, slow push-in. Shot 2 (1.3-2.7s): cut to a close-up of the lower surface as far more crystals rain down and lock together into spiky amber clusters that pile up higher and higher. Shot 3 (2.7-4s): cut to an extreme close-up as the two smooth surfaces press together and the sharp amber crystal clusters caught between them dig into both, scoring bright torn grooves across the once glossy surfaces. Keep the exact same translucent pale cyan glass style and dark slate blue-grey void in all three shots; only the waste crystals glow warm amber. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft settling patter and a sharp gritty scrape, no music, no dialogue.
```

