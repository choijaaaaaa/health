# 아기 이미지 시험 — 미드저니 4장 (2026-09-20)

육아 트랙에 아기 몸을 직접 쓸 수 있는지 확인용. **4장만 돌려보고 결과를 알려주면 된다.**
막히는 게 있으면 그 번호만 말해주면 문구를 바꿔서 다시 준다.

왜 시험하냐면: Flow(Veo)는 `infant`·`child` 단어만 들어가도 미성년자 안전필터로 막힌 전례가 있다.
미드저니도 같은지는 안 해봤다. **막히면** 기전 클립(몸속 확대라 사람이 안 나온다)과 사물·부모 손 중심으로 간다.

저장 위치: `stills/baby/01.jpg` ~ `04.jpg`

---

## 01. 아기 전신 (캐논과 같은 톤)

기존 성인 캐논(`canon_organs.jpg`)의 아기 버전. 이게 되면 부위 점등 클립을 아기 몸으로 만들 수 있다.

```
Medical holographic visualization of a translucent glass-like 3D anatomical model of a human baby, about one year old, lying on its back with arms and legs relaxed, the skin rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, the whole body visible from the top of the head to the feet, centered with clear margins on all sides, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. Visible inside: the brain, the lungs and heart, the stomach and the coiled intestines, the bladder, with the full skeleton faintly visible. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, photo, photorealistic skin, real child
```

## 02. 아기 몸통 클로즈업 (배·장 부위용)

영유아 변비·복통·수유 topic에서 배를 켜는 데 쓴다.

```
Medical holographic visualization of a translucent glass-like 3D anatomical model, a close-up of the torso of a human baby seen from the front, framed from the collarbones down to the hips with the head and legs outside the frame, the surface rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. Visible inside: the small rounded stomach, the coiled small intestine and the large intestine framing it, the liver above on one side, the rib cage and the spine behind. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, head, face, photo, photorealistic skin, real child
```

## 03. 아기 머리·귀 단면 (중이염·코막힘용)

영유아 중이염·코막힘은 검색량이 큰데, 어른 머리 스틸로는 이관 각도가 달라 설명이 어긋난다.

```
Medical holographic visualization of a translucent glass-like 3D anatomical model, a close-up of the head of a human baby seen from the side, the surface rendered as an almost fully transparent thin glass shell, every internal structure rendered in the same soft pale cyan glow, none brighter or differently colored than the others, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. Visible inside: the nasal cavity, the short nearly horizontal tube running from behind the nose to the middle ear, the middle ear cavity with its three tiny bones, the throat below, and the skull bones around them. Smooth featureless face. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, opaque skin, glowing highlight, amber, orange, red, facial features, photo, photorealistic skin, real child
```

## 04. 사람 없이 사물만 (막혔을 때의 대안)

01~03이 다 막혀도 이건 될 것이다. 육아 topic의 도입부를 사물로 가는 안.

```
Medical holographic visualization, translucent glass-like 3D still life, a baby bottle, a folded cloth diaper and a digital thermometer arranged on an empty surface, every object rendered in the same soft pale cyan glow as if made of thin glass, in a dark empty slate blue-grey studio void, cinematic soft rim lighting, shallow depth of field, the objects centered and filling most of the frame, vertical 9:16 portrait frame, absolutely no text, letters, numbers, labels, arrows, logos, or watermarks anywhere in the image. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, people, hands, face, body, amber, orange, red
```

---

## 결과 보고 방법

번호별로 되는지만 알려주면 된다.
- 다 되면: 아기 몸으로 부위 점등 클립을 만든다(코드로 생성하므로 Flow 불필요).
- 01만 막히면: 02·03 같은 부분 클로즈업으로 대체한다(머리·배만 나오면 필터를 덜 건드린다).
- 다 막히면: 04번 방식(사물)과 기전 클립으로 간다. 기전 클립은 몸속 확대라 사람이 안 나와서 그대로 쓸 수 있다.
