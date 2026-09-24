# 클립 요청 시트

**미드저니로 스틸을 뽑고 → Flow에 start 프레임 단독으로 넣고 → 모션 프롬프트**를 붙인다.
결과는 `assets_library/xray/RENDER/<이름>.mp4`로 저장하면 세션이 `scripts/publish_xray_clips.py`로 정리한다.

## 🚨 레퍼런스 이미지를 반드시 같이 넣는다

라이브러리 195종이 **같은 인체 모델**로 통일돼 있다. 텍스트 프롬프트만으로 뽑으면 톤·체형이 달라져
**다른 사람이 나온다.** 요청마다 아래에 어느 이미지를 어떤 방식으로 넣을지 적어뒀다. 갈래는 둘이다.

| 클립 | 붙이는 법 | 왜 |
|---|---|---|
| `act_`(행위) · `part_`(부위) | **Omni Reference** | 전신 인체가 그대로 나와야 한다 — 톤·체형 고정 |
| `m_`(기전) | **Style Reference**(색·질감만) | 🚨 Omni는 "이 대상을 넣어라"라서 **클로즈업에 전신 인체가 끼어든다** |

## 그 밖의 고정 규칙

- Flow는 **start 프레임만** 준다 — end를 주면 Veo가 사이를 맞추려고 피사체를 변형시킨다.
- 길이는 **4·6·8·10초** 네 가지뿐이다. 기전은 **4초 안에 컷 3개**(한 장면을 4초 끄는 것보다 리듬이 산다).
- 얼굴은 이목구비 없이 매끈하게. 점등은 **호박색 하나뿐**이고 나머지는 끝까지 청록 유리다.
- 미드저니 4장 중 1장 채택, 나머지는 `stills/_candidates/<파일명>/`에 보관.

이 파일은 `scripts/build_clip_request_sheet.py`가 각 topic의 `clip_requests.json`에서 다시 만든다.
**직접 고치지 마라** — 고칠 내용은 해당 topic의 `clip_requests.json`에 넣는다.

**2026-09-24 기준 21종**
---

## 1. `act_shingles_band` — 고령_15

**왜 필요한가**: 대상포진은 한쪽에 띠처럼 잡히는 물집이 유일한 시각 특징인데, 지금 쓰는 act_scratch_skin(팔 긁기)에는 물집이 전혀 없다. 증상이 화면에 안 보이면 무슨 병 이야기인지 알 수 없다. 동작은 그 병 특유로 — 닿기를 피하거나 멈칫하는 순간까지 넣는다.

✅ **start 스틸 준비됨**: `assets_library/xray/stills/act/act_shingles_band.jpg` — 미드저니 단계 생략, 아래 Flow만 돌린다.

### Flow (6초)
```
One continuous shot in a single unbroken scene with no scene cuts, the camera easing forward and arcing slightly to the side. 0-1.5s: from the very first frame one arm lifts away from the ribs and the head bows to look down at the bare flank, and the camera starts pushing in. 1.5-3s: the other hand starts toward the flank, stops short and hovers just above it, tracing the curve of the band without ever touching down, the raised arm locked out wide so nothing brushes the band and the chest holding its breath, while a hot amber glow flickers on inside a nerve root beside the spine on that side only. 3-4.5s: the glow runs outward along that single nerve as it curves around the ribs, and the clustered blisters under the glass shell light up one after another along the band, the camera stopping with the head-to-hips region filling the frame. 4.5-6s: the figure holds still, the nerve root and the whole band of blisters throbbing intense amber twice and staying fully lit until the very last frame, the opposite side of the body staying perfectly smooth and soft pale cyan. The body stays translucent glass with all structures visible inside throughout; the face stays smooth and featureless, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a low synth drone with a thin rising sting and two deep heartbeat thumps with the glow, no music, no dialogue.
```

---

## 2. `act_cover_blister_gauze` — 고령_15

**왜 필요한가**: 원고가 시청자에게 시키는 행동이 "물집이 딱지로 변할 때까지 옷이나 거즈로 덮어라"인데, 덮는 동작 클립이 라이브러리에 하나도 없다. 27.7~33.2초와 72.4~78.6초 두 구간이 그 행동을 말하는 동안 화면엔 기전만 돌아간다. act_scratch_skin(긁기)으로 대신하면 하지 말라는 행동을 보여주게 돼서 쓸 수 없다.

**레퍼런스**: `assets_library/xray/stills/canon_organs.jpg` — **Omni Reference**로 넣는다

### 미드저니 (start 스틸 → `assets_library/xray/stills/act/act_cover_blister_gauze.jpg`)
```
Medical holographic visualization of a single translucent glass-like human figure, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, vertical 9:16 portrait frame, smooth featureless face, full body visible from the top of the head to the feet, both feet flat on the floor. The figure stands turned slightly to one side, one arm lifted clear of the ribs, the other hand pressing a plain rectangular pad of soft opaque gauze flat against that bare flank, fingers spread over the pad. Along that one side of the torso only, a single narrow band of small clustered blisters runs from the spine around the ribs, and the gauze pad covers the middle of that band so only its two ends are still visible, the band stopping dead at the midline so the other side is perfectly smooth. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, amber, orange, red, blood colour, opaque skin, clothing, hair, facial features, tools, machine parts, glassware, duplicated limbs
```

### Flow (6초)
```
One continuous shot in a single unbroken scene with no scene cuts, the camera pushing in from a full-body framing to the chest-to-hips region and holding there. 0-1.5s: from the very first frame the band of clustered blisters along one flank is already glowing amber, and the free hand lifts a soft opaque gauze pad up toward it while the other arm stays locked out wide. 1.5-3s: the hand lays the pad flat over the middle of the band and presses it down with spread fingers, and the amber glow under the pad dims to a dull ember while the two uncovered ends of the band stay bright. 3-4.5s: the hand smooths the pad outward along the curve of the ribs until the whole band is covered, and every last amber point under it goes out one after another. 4.5-6s: the hand stays resting on the pad, the covered flank holding a single even soft pale cyan with no amber left anywhere, the opposite side of the body staying perfectly smooth. The body stays translucent glass with all structures visible inside throughout; the face stays smooth and featureless, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a low synth drone that settles into a calm sustained tone as the glow goes out, no music, no dialogue.
```

---

## 3. `act_vaccine_shot_arm` — 고령_15

**왜 필요한가**: 백신이 세 항목 중 하나이고 마무리도 "쉰 살이 넘었다면 사백신 일정을 잡으세요"인데, 접종 동작 클립이 없다. act_take_supplement는 알약을 삼키는 동작이라 주사제에 쓰지 말라고 색인에 명시돼 있고(경구↔주사 혼동), 48.2~67.4초 백신 구간 전체가 행위 칸 없이 기전만 돌아간다.

**레퍼런스**: `assets_library/xray/stills/canon_organs.jpg` — **Omni Reference**로 넣는다

### 미드저니 (start 스틸 → `assets_library/xray/stills/act/act_vaccine_shot_arm.jpg`)
```
Medical holographic visualization of a single translucent glass-like human figure, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, vertical 9:16 portrait frame, smooth featureless face, full body visible from the top of the head to the feet, both feet flat on the floor. The figure stands facing forward with one sleeveless shoulder turned slightly toward the camera and that arm hanging relaxed at its side, while a second bare hand enters from outside the frame holding a slim plain syringe with its short needle resting against the deltoid muscle high on that upper arm. The deltoid muscle itself is visible as a distinct rounded band of fibres inside the translucent shoulder. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, red, blood colour, opaque skin, clothing, hair, facial features, machine parts, glassware, duplicated limbs, second figure, face of the person holding the syringe
```

### Flow (6초)
```
One continuous shot in a single unbroken scene with no scene cuts, the camera starting on the full standing figure and easing in on the shoulder. 0-1.5s: from the very first frame the figure stands still with one arm relaxed at its side, and a hand holding a slim syringe comes in from the edge of the frame toward that upper arm. 1.5-3s: the needle tip touches the deltoid high on the arm and goes in, and the rounded band of deltoid fibres inside the translucent shoulder lights up amber at that one point, the camera stopping with the shoulder and upper chest filling the frame. 3-4.5s: the plunger presses down and the amber point spreads into a small even pool through the deltoid fibres, then the syringe lifts away and the hand leaves the frame. 4.5-6s: the figure holds still and the amber pool fades to a steady soft glow that stays lit in the deltoid until the very last frame, the rest of the body staying soft pale cyan. The body stays translucent glass with all structures visible inside throughout; the face stays smooth and featureless, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a low synth drone with one short soft click as the needle goes in, no music, no dialogue.
```

---

## 4. `m_shadow_contrast` — 눈_8

**왜 필요한가**: 항목 2의 핵심 문장이 "맑은 하늘이나 하얀 종이를 볼 때 점이 더 뚜렷해진다"(서울아산병원)인데, 라이브러리 115종에 '배경이 밝을수록 같은 그림자가 진해진다'는 장면이 없다. clip_index로 '그림자·대비·빛·시야'를 다 뒤졌지만 m_vitreous_floaters(덩어리가 떠다니며 그림자를 드리움)·m_vision_field_loss(시야가 까맣게 지워짐)·m_uv_radiation_damage(자외선이 조직을 때림)뿐이라, 여기에 m_vitreous_floaters를 한 번 더 끼우면 앞 구간과 똑같은 화면이 되어 '배경 밝기에 따라 달라진다'는 이 항목의 요점이 화면에서 사라진다. 개수가 늘어난 게 아니라 대비가 커진 것뿐이라는 게 이 topic이 시청자에게 주는 가장 실용적인 정보라 대충 넘길 수 없다. 받기 전까지 눈_8 조립을 멈춘다.

✅ **start 스틸 준비됨**: `assets_library/xray/stills/mech/m_shadow_contrast.jpg` — 미드저니 단계 생략, 아래 Flow만 돌린다.

### Flow (4초)
```
Three quick shots cut together, about 1.3 seconds each, the lumpy grey-blue clump never moving or changing size in any of them. Shot 1 (0-1.3s): the amber beam from above is dim and diffuse, and the shadow the clump throws on the pale cyan retinal sheet is faint and soft-edged, almost lost against the surface, the camera drifting slowly down towards the sheet. Shot 2 (1.3-2.7s): the amber beam brightens hard and turns into a clean flood of light filling the whole clear space, and on the sheet below the same shadow sharpens into a dark crisp oval with the two trailing threads now drawn as two thin black lines, the camera holding still so only the light and the shadow change. Shot 3 (2.7-4s): the amber beam dims right down to a low ember glow, the clump stays exactly where it is, and the dark oval on the sheet fades back until only the faintest smudge is left, the camera easing back to show the clump and the almost clean sheet together. Keep the exact same translucent pale cyan glass tissue style, the same dark slate blue-grey void and the same camera language in all three shots. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a low synth drone that swells with the brightening light and falls away as it dims, no music, no dialogue.
```

---

## 5. `act_chase_floater` — 눈_8

**왜 필요한가**: 항목 3(지켜보는 기간)의 왼쪽 행위 칸에 쓸 클립이 없다. 라이브러리 행위 48종에서 눈 관련은 act_rub_eyes(눈 비비기)·act_squint_at_screen(화면을 얼굴 가까이)·act_shield_eyes_from_light(손차양)뿐인데 셋 다 안구건조·눈 피로·눈부심 어디에나 붙는 뭉뚱그린 동작이라, 비문증 영상에 붙여도 무슨 병 이야기인지 화면에서 안 보인다(CLIP_NOTES 2026-09-24 '행위 클립은 동작이 디테일해야 한다'). 비문증인 사람만 하는 동작은 따로 있다 — 밝은 벽을 보다 고개는 그대로 둔 채 눈알만 굴려 떠다니는 점을 쫓고, 잡으려는 듯 손을 올리다 소용없다는 걸 알고 멈칫하는 것. 앞 구간에서 act_rub_eyes를 이미 썼으므로 같은 클립을 또 쓰면 항목이 바뀐 게 화면에 안 드러나기도 한다. 받기 전까지 눈_8 조립을 멈춘다.

✅ **start 스틸 준비됨**: `assets_library/xray/stills/act/act_chase_floater.jpg` — 미드저니 단계 생략, 아래 Flow만 돌린다.

### Flow (6초)
```
One continuous shot in a single unbroken scene with no scene cuts, the camera easing forward from a full-body framing towards the head and shoulders. 0-1.5s: the figure stands with its weight on one leg, the head completely still, and both amber eyeballs roll up and across twice in quick succession and then stop, as if following something drifting through the air; the head never turns to follow. 1.5-3s: the eyeballs hold at the top of that arc, then drift slowly back down and across once, more slowly than before, and the shoulders rise a little as the breath is held. 3-4.5s: one forearm lifts to chest height and the half-closed fingers reach out to pinch at empty air, then stop dead a hand's width short and stay hovering, the wrist going slack, the other arm staying loose at the side; the hand never touches the face and the figure never rubs or presses the eyes. 4.5-6s: the raised hand lowers slowly back to the side, the weight shifts onto the other leg so the hips level out, and both eyeballs throb intense amber twice and stay fully lit until the very last frame. The body stays translucent glass with all structures visible inside throughout; the face stays smooth and featureless, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a low synth drone with two soft rising stings on the eye movements, no music, no dialogue.
```

---

## 6. `act_inject_belly` — 대사_14

**왜 필요한가**: 위고비는 주 1회 피하주사인데 지금 쓰는 act_take_supplement는 알약을 삼키는 동작이다. 약을 먹는 것과 주사하는 것은 시청자가 바로 구별한다.

✅ **start 스틸 준비됨**: `assets_library/xray/stills/act/act_inject_belly.jpg` — 미드저니 단계 생략, 아래 Flow만 돌린다.

### Flow (6초)
```
One continuous shot in a single unbroken scene with no scene cuts, the camera easing forward and tilting down to follow the hands. 0-1.5s: from the very first frame the head bows and one hand pinches a fold of the lower belly beside the navel, and the camera starts pushing in and tilting down. 1.5-3s: the other hand brings the slim pen-shaped device up and presses its tip against the pinched fold, the thumb pushing down on the end, and a hot amber glow blooms in a small pool just under the glass shell at that spot. 3-4.5s: the device lifts away and the pinched fold releases, while the amber pool spreads outward under the skin and a thread of it travels up toward the stomach, the camera stopping with the chest-to-hips region filling the frame. 4.5-6s: the stomach fills with amber and the glow reaches back along the vagus nerve toward the base of the brain, the stomach and that nerve throbbing intense amber twice and staying fully lit until the very last frame, while every other organ, every bone and the glass skin stay soft pale cyan. The body stays translucent glass with all organs visible inside throughout; the face stays smooth and featureless, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a low synth hum, one short soft click and two deep heartbeat thumps with the glow, no music, no dialogue.
```

---

## 7. `act_nausea_push_plate_away` — 대사_14

**왜 필요한가**: 1번 항목(오심 43.9%·구토 24.5%)의 행위 클립. 라이브러리의 act_grab_belly는 배를 움켜쥐는 뭉뚱그린 동작이라 위경련·장염·생리통 어디에도 붙어 이 증상을 못 가리킨다. GLP-1 오심은 '배가 아파 웅크리는' 게 아니라 '한두 숟갈 뜨다 명치까지 차오른 느낌에 음식을 밀어내고 침을 삼키며 숨을 멈추는' 동작이다 — 증상 자체(먹다 만 그릇을 밀어내는 손, 입을 막는 손)가 동작 안에 보여야 한다.

✅ **start 스틸 준비됨**: `assets_library/xray/stills/act/act_nausea_push_plate_away.jpg` — 미드저니 단계 생략, 아래 Flow만 돌린다.

### Flow (6초)
```
One continuous shot in a single unbroken scene with no scene cuts, the camera holding on the seated upper body and easing slowly in. 0-1.5s: from the very first frame the figure is seated leaning toward the table having just taken a mouthful, the throat lifting once in a swallow, and the first faint amber flicker appears deep in the stomach. 1.5-3s: the swallow stalls halfway, the shoulders jerk up toward the ears and the whole torso freezes with the breath held, the chin tucking down while the amber in the stomach swells and climbs a short way up the oesophagus and stops there. 3-4.5s: the figure leans back away from the table and one flat palm pushes the half full bowl away across the table at arm's length in one slow continuous shove, the head turning slightly away from it, while the amber in the stomach sits still and heavy instead of moving down. 4.5-6s: the other hand comes up and the knuckles press against the lips, the shoulders drop, and the throat swallows twice more in a quick tight rhythm, the stomach throbbing intense amber twice with those swallows and staying fully lit until the very last frame, while every other organ, every bone and the glass skin stay soft pale cyan. The body stays translucent glass with all organs visible inside throughout; the face stays smooth and featureless so all the discomfort reads in the lifted shoulders, the held breath and the stalled swallow. The dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a low synth hum, one soft ceramic scrape as the bowl slides and two dull swallow sounds, no music, no dialogue.
```

---

## 8. `act_epigastric_bore_to_back` — 대사_14

**왜 필요한가**: 3번 항목(급성 췌장염 0.2%·담석증 1.6%)의 행위 클립이자 마지막 병원 신호('명치 통증이 등까지 뻗치면서 멎지 않으면')를 그대로 보여주는 동작. 라이브러리에 대체할 게 없다 — act_clutch_chest는 프레임 확인 결과 심장이 점등해 심근경색으로 읽히고, act_clutch_low_back은 콩팥이 점등해 신장 통증이다. 췌장염 통증은 명치에서 등으로 뚫고 나가는 형태라 사람이 앞으로 몸을 접고 반대 손으로 등 뒤 갈비뼈 아래를 받치며, 눕지 못하고 무릎을 끌어당긴다 — 이 '앞으로 접고 등을 받치는' 조합이 이 병의 사람만 하는 동작이다.

✅ **start 스틸 준비됨**: `assets_library/xray/stills/act/act_epigastric_bore_to_back.jpg` — 미드저니 단계 생략, 아래 Flow만 돌린다.

### Flow (6초)
```
One continuous shot in a single unbroken scene with no scene cuts, the camera holding at a three-quarter angle and drifting slowly around toward the back. 0-1.5s: from the very first frame the figure is upright on the floor and one fist drives knuckles-first into the pit of the stomach just below the breastbone, the torso folding sharply forward over the lap as the first amber bloom appears in the pancreas lying deep behind the stomach. 1.5-3s: the amber bores straight backward from the pancreas toward the spine in a narrow shaft, and the other arm reaches behind the back so the flat palm braces under the lower ribs on the same side, the shoulders hunching and the breath stopping mid-inhale so the ribcage locks. 3-4.5s: the figure tries once to lean back and straighten, gets a hand's width and stops short, then folds forward again harder and drags both knees up toward the chest, the fist grinding a slow half circle into the epigastrium while the amber shaft brightens along its whole length from the pancreas through to the spine. 4.5-6s: the body stays locked in that forward fold rocking twice in a slow tight rhythm, the pancreas and the shaft reaching the mid-back throbbing intense amber twice with the rocking and staying fully lit until the very last frame, while every other organ, every bone and the glass skin stay soft pale cyan. The body stays translucent glass with all organs visible inside throughout; the face stays smooth and featureless so all the pain reads in the sharp forward fold, the locked ribcage, the failed attempt to straighten and the hand bracing the back. The dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a low synth hum and two deep slow heartbeat thumps with the throbbing, no music, no dialogue.
```

---

## 9. `act_press_swollen_eyelid` — 대사_22

**왜 필요한가**: 이 영상의 간판 장면(훅 0~5초)이 '자고 일어나면 눈두덩이 붓는다'인데, 195종 색인을 '눈꺼풀·붓기·얼굴'로 뒤져도 눈 주위가 부은 장면이 하나도 없다. 지금 도입부에 임시로 쓰는 act_rub_eyes는 색인 fits가 '눈의 피로·안구건조'라 눈을 비비는 피로 장면이고(프레임 확인: 두 손으로 얼굴을 덮고 양쪽 안구만 점등), 부기가 화면에 전혀 없다. act_cover_face는 부비동, part_eyelid는 확대율이 너무 커서 눈꺼풀인 줄 모른다. ▶ 어디를 어떻게: 아래 눈꺼풀 바로 아래 눈두덩을 두 손 검지·중지 끝으로 각각 한 번 지그시 눌렀다 떼고, 눌린 자리가 자국 없이 곧바로 도로 부풀어 오르는 것까지 보여야 한다(점액부종은 눌러도 자국이 안 남는 게 진단 포인트라 '떼고 나서 되돌아오는' 구간이 이 클립의 전부다). 점등은 양쪽 눈꺼풀·눈두덩 연부조직만 — 안구는 켜지지 않는다. ▶ 피하는 동작: 눈을 비비지 말 것(act_rub_eyes와 같은 장면이 된다), 두 손으로 얼굴 전체를 덮지 말 것(act_cover_face), 안구가 앞으로 튀어나오게 하지 말 것(갑상선기능항진증의 안구돌출로 읽혀 이 원고의 통념 반박과 정면으로 어긋난다). ▶ 반복 리듬: 누른다-뗀다-되돌아온다를 두 번, 두 번째가 더 느리고 되돌아오는 속도가 눈에 띄게 굼뜨다. ▶ 무게중심: 발은 그대로 두고 턱만 살짝 들어 머리를 뒤로 조금 젖힌 채 눈두덩을 위에서 만지는 자세라 상체는 거의 움직이지 않는다 — 카메라만 얼굴로 밀고 들어와 마지막엔 눈두덩이 화면 위쪽 3분의 1을 채운다. 클립이 오면 xray.json opening 첫 항목(act_rub_eyes 1.4~3.8)을 이걸로 교체한다.

✅ **start 스틸 준비됨**: `assets_library/xray/stills/act/act_press_swollen_eyelid.jpg` — 미드저니 단계 생략, 아래 Flow만 돌린다.

### Flow (6초)
```
One continuous shot in a single unbroken scene with no scene cuts, the camera pushing slowly in on the face the whole way. 0-1.5s: from the very first frame the chin lifts a little and both hands come up, the index and middle fingertips of each hand settling on the puffy pad just under each lower lid, and the camera starts pushing in. 1.5-3s: both sets of fingertips press straight in and hold, denting the swollen pad into a shallow pit on each side while the upper body stays completely still, and a hot amber glow blooms inside the soft tissue ringing both eyes, the eyeballs themselves staying soft pale cyan and never moving forward. 3-4.5s: the fingertips lift clear and the two dents fill back out on their own with no mark left behind, slowly, the tissue rounding back into a smooth dome, then the fingertips press in a second time and hold longer. 4.5-6s: the fingertips lift away a second time and the pits fill back in even more slowly than before, the amber ring of swollen tissue around both eyes throbbing twice as it refills and staying fully lit until the very last frame, the camera stopping with the swollen eye region filling the upper third of the frame, while every other structure, every bone and the glass skin stay soft pale cyan. The body stays translucent glass with all structures visible inside throughout; the face stays smooth and featureless so everything reads in the domed swelling, the dents and how slowly they fill back in. The dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a low synth hum and two deep heartbeat thumps as the tissue refills, no music, no dialogue.
```

---

## 10. `m_peptide_breakdown` — 머리_14

**왜 필요한가**: 이 원고의 핵심 문장이 "먹은 콜라겐은 소화되면서 아미노산으로 쪼개져 온몸에 나눠 쓰여요. 피부로 직행하지 않고"인데, 라이브러리 115종 중 이 장면이 없다. clip_index로 '분해·흡수·단백질'을 전부 뒤졌지만 m_enzyme_deficiency(효소가 없어 분해가 안 됨)·m_nutrient_absorption_block(큰 분자가 표면에 남음)·m_muscle_wasting(근섬유가 가늘어짐)뿐이라 전부 뜻이 반대거나 다른 얘기다. 지금 이 구간에 남는 클립을 끼우면 '콜라겐이 흡수가 안 된다'로 정반대로 읽힌다 — 흡수는 되는데 피부로 직행하지 않고 온몸에 흩어진다는 게 요점이라, 가닥이 잘려 낱개가 되고 여러 갈래로 흩어지는 장면이 따로 필요하다. 받기 전까지 머리_14 조립을 멈춘다.

✅ **start 스틸 준비됨**: `assets_library/xray/stills/mech/m_peptide_breakdown.jpg` — 미드저니 단계 생략, 아래 Flow만 돌린다.

### Flow (4초)
```
Three quick shots cut together, about 1.3 seconds each. Shot 1 (0-1.3s): the long braided amber rope lying over the villi comes apart, the three twisted strands unwinding away from each other and then snapping crosswise into short stubby amber segments that drop down between the villi, the camera pushing in slowly along the length of the rope. Shot 2 (1.3-2.7s): cut to an extreme close-up of two short amber segments as they break down further into separate small round amber beads, the beads rolling into the side of a single pale cyan villus and slipping through its wall into the narrow vessel running up inside it. Shot 3 (2.7-4s): cut to a wide view of a pale cyan blood vessel that splits into five branches heading off in five different directions, the stream of round amber beads arriving from below and dividing evenly among all five branches so that only a small share goes down any one of them, the beads still moving apart as the shot ends. Keep the exact same translucent pale cyan glass tissue style and dark slate blue-grey void in all three shots; only the collagen material glows warm amber. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a dry fibrous snapping and a soft scattering rush, no music, no dialogue.
```

---

## 11. `act_apply_face_cream` — 머리_14

**왜 필요한가**: '먼저 바르는 콜라겐이에요. 콜라겐 분자는 각질층이 통과시키는 크기보다 커서 대부분 표면에 남아요' 구간(22.4~35.0초)의 왼쪽 행위 칸에 쓸 클립이 없다. 프레임으로 확인한 후보는 전부 어긋난다 — act_check_skin은 이름과 달리 허리를 숙여 무릎만 점등되는 장면이고, act_scalp_care는 통을 들고 바르긴 하지만 정수리·두피라 턱선·잔주름이 훅인 이 원고와 부위가 다르며, act_rub_hands는 손만 비비는 장면이다. 필요한 건 '얼굴(특히 턱선)에 크림을 펴 바르는 동작'이고, 오른쪽 칸의 m_nutrient_absorption_block(큰 금색 구슬이 구멍을 못 넘고 표면에 남음)과 한 장면으로 읽히려면 바른 것이 피부 표면에 얇은 막으로 얹혀 있어야 한다. 받으면 결론 구간(선크림)에도 쓸 수 있다. 받기 전까지 이 구간은 기전 단독으로 둔다.

**레퍼런스**: `assets_library/xray/stills/canon_organs.jpg` — **Omni Reference**로 넣는다

### 미드저니 (start 스틸 → `assets_library/xray/stills/act/act_apply_face_cream.jpg`)
```
Medical holographic visualization of a single translucent glass-like human figure, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, vertical 9:16 portrait frame, smooth featureless face, upper body visible from the top of the head to the waist. The figure stands facing the camera with the chin lifted and tilted a little to one side, one forearm raised so the fingertips of that hand rest flat against the jawline just below the cheekbone, the other hand held at chest height cradling a small plain lidless round jar with completely smooth blank sides and no markings of any kind. A thin warm amber film clings to the fingertips and lies in a smooth glossy sheet on the outermost surface of the jaw and cheek, sitting entirely on top of the skin with a clear bright boundary between the amber film and the pale cyan tissue underneath, nothing amber anywhere below that boundary. Inside the glass shell the skull and jawbone are faintly visible in the same pale cyan. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, brand, packaging, facial features, hair, clothing, tools, machine parts, duplicated limbs, amber inside the body, blood colour, red
```

### Flow (6초)
```
One continuous shot in a single unbroken scene with no scene cuts, the camera easing slowly in toward the jaw and cheek and never cutting away. 0-1.5s: the figure stands facing the camera holding the small blank jar at chest height in one hand, and dips two fingertips of the other hand into it so a small bead of warm amber material lifts out and clings to the fingertips. 1.5-3s: the chin lifts and tilts to one side and those two fingertips touch down on the jawline just below the cheekbone, the amber bead flattening on contact. 3-4.5s: the fingertips sweep in three slow strokes along the jawline from the chin back toward the ear, each stroke spreading the amber into a thinner and wider glossy sheet across the surface of the jaw and cheek, the sheet staying strictly on the outermost surface with a hard bright edge where it meets the pale cyan tissue below it. 4.5-6s: the hand lifts away and the camera pushes in close on the jaw, holding on the amber sheet sitting on top of the skin, the sheet thinning and dulling slightly at its edges but never sinking in, with the pale cyan layers of tissue clearly visible underneath and completely free of any amber. The body stays translucent glass with all structures visible inside throughout; the face stays smooth and featureless, the dark slate blue-grey void stays empty, and the jar has no markings of any kind. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a low synth drone with a soft dry sliding sound on each stroke, no music, no dialogue.
```

---

## 12. `act_urgent_watery_bowel` — 비뇨기_16

**왜 필요한가**: 크레아틴 배탈 항목(덜 녹은 가루가 장에 남아 장 안으로 물을 끌어당김)에 쓸 행위 클립이 없다. 프레임으로 직접 확인한 후보들은 전부 '배가 아파 화장실이 급하다'까지만 보여준다 — act_grab_belly는 두 손으로 배를 감싸고 위·장이 넓게 켜지는 뭉뚱그린 복통이고, pilot_B2는 한쪽 다리를 들어 참는 자세지만 역시 장이 넓게 켜질 뿐이며, act_rush_to_toilet은 4.5~6.0초에 장이 켜진 채 급히 걸어가는 구간이 있다. 셋 다 장염·과민성 장·생리통에 그대로 붙는 장면이라 이 항목이 크레아틴 이야기라는 걸 화면이 말해주지 못한다. 이 항목의 시각 특징은 '물이 찬 장'이다 — 장 고리가 액체로 팽창해 수면(waterline)이 보이고 그 물결이 왼쪽 아래 하행결장으로 내려가야, 오른쪽 칸의 m_osmotic_water_pull(장 안으로 물이 끌려 들어감)과 한 장면이 된다. 손도 배를 감싸는 게 아니라 누르면 더 아파서 닿기 직전에 멈칫하다 손바닥 아래쪽으로 왼쪽 아랫배만 납작하게 누른다. ⚠️ 이 클립을 새로 뽑을 만큼은 아니라고 판단하면 act_rush_to_toilet 4.5~6.0초를 차선으로 쓸 수 있다.

✅ **start 스틸 준비됨**: `assets_library/xray/stills/act/act_urgent_watery_bowel.jpg` — 미드저니 단계 생략, 아래 Flow만 돌린다.

### Flow (6초)
```
One continuous shot in a single unbroken scene with no scene cuts, the camera easing forward and drifting down toward the lower belly. 0-1.5s: the figure stands upright and still, then the shoulders lift and the chest locks as the breath stops; inside, the intestinal loops swell and a flat liquid surface rises inside each loop, and the camera starts pushing in. 1.5-3s: one hand starts toward the belly, stops short and hovers a hand's width above it, pulls back, starts again and stops again, three times in quick succession, never touching down, while the waist stays hollow and the trunk twists away from its own left side. 3-4.5s: the heel of that hand finally presses flat and low on the left lower belly with the fingers splayed and lifted clear, the body folding forward and the weight shifting onto the ball of the leading foot with the back heel peeling off the floor, the knees pressed together; a hot amber glow lights up inside the fluid in the swollen loops. 4.5-6s: the figure takes two short quick steps, and with each step the amber fluid sloshes and runs down the left side of the colon toward the bottom of the frame in two distinct surges, the waterline inside each loop tipping and settling, the glow staying fully lit until the very last frame. The body stays translucent glass with all structures visible inside throughout; the face stays smooth and featureless, the dark slate blue-grey void stays empty, no props or furniture of any kind enter the frame. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a low synth drone with a thin wet gurgling swell and two soft descending rushes with the surges, no music, no dialogue.
```

---

## 13. `act_large_meal_after_fasting` — 소화_11

**왜 필요한가**: 3번 항목('몰아 먹는 식사')의 행위 클립. 이 포맷은 왼쪽에 행동, 오른쪽에 기전을 나란히 놓아 '이 행동을 하면 몸이 이렇게 된다'를 읽히게 하는데, 라이브러리에는 먹는 동작 자체가 하나도 없다 — act_drink_caffeine은 컵을 들어 마시는 동작이라 '끼니를 거르다 한 끼를 몰아 먹는다'와 다르고, act_shift_uncomfortably_seated(앉은 채 들썩이다 아랫배를 누름)는 먹은 뒤의 결과라 원인 행동을 못 보여준다. act_grab_belly는 색인 avoid대로 어느 소화기 질환에나 붙는 뭉뚱그린 동작이다. 필요한 건 '빈 위가 한꺼번에 크게 늘어나는 순간'이 눈에 보이는 동작이다: 오래 비어 있던 위가 몇 번의 빠른 큰 입에 통째로 부풀고, 그 팽창이 아래 대장으로 이어지는 흐름. 피해야 할 동작은 천천히 음미하며 먹는 식사 장면과 배를 움켜쥐는 통증 동작이다(전자는 이 항목의 반대, 후자는 이미 라이브러리에 있고 주제를 못 가린다). 반복 리듬은 '크게 한 입 → 거의 안 씹고 삼킴'을 네 번, 갈수록 빨라지게. 무게중심은 앞으로 쏠려 식탁 위로 상체를 기울인 채 유지한다.

✅ **start 스틸 준비됨**: `assets_library/xray/stills/act/act_large_meal_after_fasting.jpg` — 미드저니 단계 생략, 아래 Flow만 돌린다.

### Flow (6초)
```
One continuous shot in a single unbroken scene with no scene cuts, the camera starting on the seated upper body and easing down and in toward the abdomen. 0-1.5s: from the very first frame the stomach is small, empty and collapsed to a thin flat pouch with no amber in it at all, and the figure leans far forward and drags the heaped bowl closer with one hand while the other hand lifts a heaped spoon to an already open mouth. 1.5-3s: four fast heaping mouthfuls go in one after another with almost no chewing between them, each getting faster than the last, and with each swallow a slug of amber drops down the oesophagus into the stomach, the stomach ballooning outward a stage at a time until it is stretched wide and taut and filled with amber. 3-4.5s: the figure keeps the spoon moving without pausing while the stretched stomach throbs, and a branching line of amber runs out from the swollen stomach down and across to the large intestine below it, lighting the colon in a bright wave that travels left to right. 4.5-6s: the spoon finally stops halfway to the mouth, the shoulders stay hunched forward over the table, and the taut stomach and the lit colon throb intense amber twice together and stay fully lit until the very last frame, while every other organ, every bone and the glass skin stay soft pale cyan. The body stays translucent glass with all organs visible inside throughout; the face stays smooth and featureless so the whole read comes from the forward-pitched weight, the elbows on the table and the speed of the mouthfuls. The dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a low synth hum, four quick dull swallow sounds and two deep heartbeat thumps with the throbbing, no music, no dialogue.
```

---

## 14. `m_crystal_precipitation` — 소화_13

**왜 필요한가**: 나레이션 "급하게 굶으면 간이 담즙으로 콜레스테롤을 한꺼번에 쏟아내서, 담즙이 과포화돼 콜레스테롤이 결정으로 굳어요" — 과포화된 액체에서 결정이 석출돼 한 덩어리 돌로 자라는 장면. 담석 말고 요로결석·타석 계열 topic에도 그대로 쓸 수 있다.

✅ **start 스틸 준비됨**: `assets_library/xray/stills/mech/m_crystal_precipitation.jpg` — 미드저니 단계 생략, 아래 Flow만 돌린다.

### Flow (6초)
```
Three quick shots cut together, about 1.3 seconds each. Shot 1 (0-1.3s): a dense stream of warm amber specks pours into the clear fluid from the top of the frame until the whole fluid inside the sac is thick and cloudy with them, slow push-in. Shot 2 (1.3-2.7s): cut to an extreme close-up inside the fluid as the drifting amber specks snap together into small hard faceted grains that sink and settle on the floor of the sac. Shot 3 (2.7-4s): cut to a low angle along that floor as the settled grains fuse into one smooth rounded amber stone that swells until it fills the frame. Keep the exact same translucent pale cyan glass style and dark slate blue-grey void in all three shots; only the cholesterol specks and the stone they form glow warm amber, the fluid itself stays clear pale cyan. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a fine granular hiss and a low grinding click as the stone locks together, no music, no dialogue.
```

---

## 15. `m_stasis_thickening` — 소화_13

**왜 필요한가**: 나레이션 "공복이 길어지면 담낭이 짜이지 않아 담즙이 고인 채 점점 걸쭉해져요"와 "지방이 거의 없으면 담낭을 수축시키는 신호가 안 나와 담즙이 더 오래 고여요" 두 문장에 함께 쓴다 — 주머니를 감싼 근육이 끝까지 수축하지 않아 안의 액체가 정체되고 농축되는 장면. m_pressure_buildup(배출로가 막혀 압력이 오르는 장면)과는 원인이 반대라 대체가 안 된다.

✅ **start 스틸 준비됨**: `assets_library/xray/stills/mech/m_stasis_thickening.jpg` — 미드저니 단계 생략, 아래 Flow만 돌린다.

### Flow (6초)
```
Three quick shots cut together, about 1.3 seconds each. Shot 1 (0-1.3s): the ring of muscle fibres around the sac stays completely slack and never squeezes, the fluid inside not moving at all and nothing at all leaving through the wide open outlet channel, slow push-in. Shot 2 (1.3-2.7s): cut to a close-up inside the sac as the motionless fluid slowly darkens and thickens into a heavy warm amber sludge that creeps down the inner wall in slow ropes. Shot 3 (2.7-4s): cut to an extreme close-up of the floor of the sac where the amber sludge has settled into a thick stagnant layer, its surface barely stirring as one slow bubble rises and dies. Keep the exact same translucent pale cyan glass style and dark slate blue-grey void in all three shots; only the thickened stagnant sludge glows warm amber, the muscle ring and the sac wall stay pale cyan and never contract. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a long held stillness with one slow viscous drip, no music, no dialogue.
```

---

## 16. `act_shared_pot_dipping` — 소화_18

**왜 필요한가**: 헬리코박터는 보균자 대부분이 평생 무증상이라 '아픈 동작'이 아예 없는 병이다. 지금 opening에 쓰던 act_grab_belly는 배를 움켜쥐고 대장이 점등하는 클립이라 장염·생리통에도 붙는 뭉뚱그린 동작인 데다 점등 장기(대장)까지 틀렸다. 이 병 고유의 장면은 증상이 아니라 전파 경로다 — 각자 쓰던 숟가락을 한 냄비에 번갈아 담갔다 입으로 가져가는 동작이 침이 섞이는 순간을 그대로 보여준다.

✅ **start 스틸 준비됨**: `assets_library/xray/stills/act/act_shared_pot_dipping.jpg` — 미드저니 단계 생략, 아래 Flow만 돌린다.

### Flow (6초)
```
One continuous shot in a single unbroken scene with no scene cuts, the camera easing forward low across the table and arcing slightly to one side. 0-1.5s: from the very first frame the left figure's spoon lifts out of the shared pot and travels up to its mouth while its shoulders round forward over the table, and the right figure's spoon lowers into the same pot; the camera starts pushing in on the pot. 1.5-3s: the left figure's spoon comes back down and enters the pot again just as the right figure's spoon lifts away toward its own mouth, the two spoons crossing directly over the pot, and a faint amber film lights up on the bowl of each spoon where it touched a mouth. 3-4.5s: the amber smears off both spoons into the shared liquid and the whole surface of the pot glows amber, the camera stopping with the pot and both torsos filling the frame. 4.5-6s: the right figure swallows, its throat drawing once, and a thread of amber runs down the oesophagus into its stomach, the stomach lining throbbing intense amber twice and staying fully lit until the very last frame, while both bodies, both spoons and the table stay soft pale cyan. The bodies stay translucent glass with all organs visible inside throughout; the faces stay smooth and featureless, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a low synth drone with two soft spoon taps against ceramic and two deep heartbeat thumps with the glow, no music, no dialogue.
```

---

## 17. `m_cell_overgrowth` — 소화_20

**왜 필요한가**: 대장 용종 편(소화_20) 기전 컷. 들어갈 문장: "대장 점막 세포가 비정상적으로 늘어나 혹처럼 솟아오른 조직이 용종이에요". 대장암·자궁근종·물혹처럼 '세포가 과하게 늘어나 덩어리가 된다'는 기전은 앞으로도 재사용된다(범용 12종에 증식 계열이 통째로 빠져 있다).

✅ **start 스틸 준비됨**: `assets_library/xray/stills/mech/m_cell_overgrowth.jpg` — 미드저니 단계 생략, 아래 Flow만 돌린다.

### Flow (6초)
```
Three quick shots cut together, about 1.3 seconds each. Shot 1 (0-1.3s): the small warm amber group of cells near the centre of the lining starts dividing over and over, each cell splitting into two and crowding its neighbours sideways, slow push-in. Shot 2 (1.3-2.7s): cut to a close-up of that spot as the amber cells stack on top of one another in a disordered pile and the once level surface above them lifts into a low rounded swelling. Shot 3 (2.7-4s): cut to a wide side view of the whole slab as the swelling keeps growing into a tall rounded lump on a narrow stalk standing above the flat pale cyan lining, its packed cells glowing warm amber all the way through. Keep the exact same translucent pale cyan glass tissue style and dark slate blue-grey void in all three shots; only the overgrown cells glow warm amber, the normal lining never changes colour. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft quickening tick of repeated splitting and a low rising swell, no music, no dialogue.
```

---

## 18. `m_gas_fermentation` — 소화_21

**왜 필요한가**: 소장 세균이 발효당(포드맵)을 먹어 가스를 뿜어내고, 그 가스가 장벽을 밀어 올려 배가 부푸는 장면. 소화_21 두 번째 항목('양파, 마늘, 밀가루 같은 발효당') 구간에 4초 통째로 들어간다. 소화·대사 계열 topic(복부팽만·과민성 장 증후군·유당불내증)에서 계속 재사용할 수 있는 범용 기전이다.

✅ **start 스틸 준비됨**: `assets_library/xray/stills/mech/m_gas_fermentation.jpg` — 미드저니 단계 생략, 아래 Flow만 돌린다.

### Flow (6초)
```
Three quick shots cut together, about 1.3 seconds each. Shot 1 (0-1.3s): the warm amber rod-shaped bacteria crawl onto the amber sugar granules and the granules shrink away beneath them, slow push-in. Shot 2 (1.3-2.7s): cut to a close-up of one shrinking granule as a stream of clear round bubbles pours upward out of it and rises between the finger-like folds, more bubbles joining from every side until they crowd the frame. Shot 3 (2.7-4s): cut to a wide side view of the intestine wall as the packed bubbles press against it and push the whole slab outward, the wall bowing upward and stretching thin. Keep the exact same translucent pale cyan glass tissue style and dark slate blue-grey void in all three shots; only the sugar granules and the bacteria glow warm amber and the bubbles stay clear. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a soft fizzing rise and a low stretching groan, no music, no dialogue.
```

> 미드저니 시작 이미지는 stills/canon_organs.jpg를 Style Reference로(Omni Reference 금지). 저장: assets_library/xray/stills/mech/m_gas_fermentation.jpg → Flow는 시작 프레임만 넣고 end는 비움, 4초 → assets_library/xray/output/m_gas_fermentation.mp4

---

## 19. `act_toilet_strain_faint` — 순환_12

**왜 필요한가**: 미주신경성 실신 topic(순환_12) 도입부 행위 클립. 기존 act_strain_on_toilet은 힘주는 자세만 있어 변비·치질·과민성대장 어디에나 붙고 실신이 안 보인다. act_sink_to_floor는 선 자세에서의 붕괴라 화장실 맥락이 없다. 나레이션 훅이 '화장실에서 힘주다가 눈앞이 하얘지고 식은땀이 난 적 있으신가요?'라 두 요소(힘주기 → 무너짐)가 한 동작 안에 이어져야 한다.

✅ **start 스틸 준비됨**: `assets_library/xray/stills/act/act_toilet_strain_faint.jpg` — 미드저니 단계 생략, 아래 Flow만 돌린다.

### Flow (6초)
```
Seconds 0.0-1.5: he holds his breath and bears down - shoulders ride UP toward his ears, the torso folds further forward over the thighs, the abdominal cavity and chest glow brighter amber as pressure builds, the left hand flattens harder against the tile wall. Seconds 1.5-2.2: the glow in the chest snaps off and the heart's pulse visibly SLOWS to two heavy beats, the vagus nerve line down the neck flashes once. Seconds 2.2-3.4: the strain releases - shoulders drop abruptly, the head falls forward FIRST as the neck gives out, then the torso tips sideways; the wall hand slides DOWN the tile leaving the wall, knees splay outward and the bare feet skid forward on the floor, weight shifting from the thighs onto one shoulder. Seconds 3.4-4.0: he is slumped sideways off the seat, brain glow dimming to near dark. Locked static camera at seated eye level, no zoom, no cuts. Face stays featureless - all distress is shown through the body: breath held, shoulders up then dropping, head leading the collapse, hand sliding, feet skidding.
```

---

## 20. `act_bulging_leg_veins` — 순환_3

**왜 필요한가**: 하지정맥류의 시각 특징은 종아리에 굵게 도드라진 핏줄인데, 지금 쓰는 act_rub_leg에는 그냥 다리를 짚는 동작만 있고 튀어나온 정맥이 안 보인다. 동작은 그 병 특유로 — 닿기를 피하거나 멈칫하는 순간까지 넣는다.

✅ **start 스틸 준비됨**: `assets_library/xray/stills/act/act_bulging_leg_veins.jpg` — 미드저니 단계 생략, 아래 Flow만 돌린다.

### Flow (6초)
```
One continuous shot in a single unbroken scene with no scene cuts, the camera easing forward and descending to follow the hands down. 0-1.5s: from the very first frame the figure bends forward from the hips and both hands reach down to the calf, the head bowing after them, and the camera starts pushing in and descending. 1.5-3s: the fingers press into the raised winding cords on that calf, drag slowly upward toward the back of the knee, then flinch off and settle more lightly the second time, the weight shifting onto the other leg so that calf takes no load, and a hot amber glow flickers on inside the thick veins under them. 3-4.5s: the glow runs up the cords and collects at a valve behind the knee where it pools and backs up, the cords swelling wider, the camera stopping with the hips-to-feet region filling the frame. 4.5-6s: the figure holds still, the whole knotted vein network on that calf throbbing intense amber twice and staying fully lit until the very last frame, while the other leg and every bone and the glass skin stay soft pale cyan. The body stays translucent glass with all structures visible inside throughout; the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a low synth drone with a slow liquid surge and two deep heartbeat thumps with the glow, no music, no dialogue.
```

---

## 21. `act_check_jaw_mirror` — 여성_7

**왜 필요한가**: 다낭성난소증후군은 통증 질환이 아닌데 지금은 act_press_one_side_lower_abdomen(아랫배 누르기)를 쓰고 있다. 실제로 사람이 알아채는 신호는 턱선 여드름과 굵은 털이라 그걸 확인하는 동작이 맞다. 동작은 그 병 특유로 — 닿기를 피하거나 멈칫하는 순간까지 넣는다.

**레퍼런스**: `assets_library/xray/stills/canon_organs.jpg` — **Omni Reference**로 넣는다

### 미드저니 (start 스틸 → `assets_library/xray/stills/act/act_check_jaw_mirror.jpg`)
```
Medical holographic visualization of a single translucent glass-like human figure, every structure rendered in the same soft pale cyan glow, dark empty slate blue-grey void, cinematic soft rim lighting, vertical 9:16 portrait frame, smooth featureless face, full body visible from the top of the head to the feet, both feet flat on the floor. The figure stands facing forward with the chin lifted and turned slightly to one side, one hand raised with the fingertips pressing along the jawline just under the ear, the other arm hanging relaxed. Along the jawline and under the chin the glass shell is raised into a scatter of small round bumps set deep under the surface. --ar 9:16 --no text, letters, numbers, labels, arrows, watermark, logo, UI, interface, amber, orange, red, blood colour, opaque skin, clothing, hair, facial features, tools, machine parts, glassware, duplicated limbs
```

### Flow (6초)
```
One continuous shot in a single unbroken scene with no scene cuts, the camera easing forward toward the head. 0-1.5s: from the very first frame the chin lifts and turns to one side and one hand comes up with the fingertips pressing along the jawline under the ear, and the camera starts pushing in. 1.5-3s: the fingertips drag slowly forward along the jaw toward the chin, stopping on each of the small deep bumps in turn and pressing each one twice before moving on, the chin tipping further up each time to get the angle, and a hot amber glow flickers on inside the oil glands packed under them. 3-4.5s: the head turns a little further and the other hand comes up to press the opposite jawline, the glow spreading into the deep glands along both sides, the camera stopping with the head-and-shoulders region filling the frame. 4.5-6s: the figure holds still, the glow travelling down from the jaw through the body to both ovaries low in the pelvis, and the jaw glands and both ovaries throb intense amber twice and stay fully lit until the very last frame, while every other organ, every bone and the glass skin stay soft pale cyan. The body stays translucent glass with all structures visible inside throughout; the face stays smooth and featureless, the dark slate blue-grey void stays empty. No text, no letters, no numbers, no labels, no arrows anywhere in the frame. The audio is a low synth drone and two deep heartbeat thumps with the glow, no music, no dialogue.
```

---
