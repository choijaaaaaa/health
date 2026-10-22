# 입_27 구내염 — 대본 주장별 출처 (2026-10-23)

원문 사본: 코디네이터 스크래치패드 `hdraft2/ulcer_src/`(nhs.txt·nhs_teeth.txt — 페이지 curl 본문, pubmed_sls.txt — PubMed 초록 묶음),
상품 상세 `hdraft2/ulcer_page/`(info.jpg 「제품 상세 정보」 전성분·주의사항). 문자열 대조 완료.

| 약칭 | 출처 | URL |
|---|---|---|
| NHS | 영국 국민보건서비스 「Mouth ulcers」 (Page last reviewed: 11 March 2024) | https://www.nhs.uk/conditions/mouth-ulcers/ |
| NHST | 영국 국민보건서비스 「How to keep your teeth clean」 (Page last reviewed: 30 June 2025) | https://www.nhs.uk/live-well/healthy-teeth-and-gums/how-to-keep-your-teeth-clean/ |
| Shim | Shim YJ, Choi JH, Ahn HJ, Kwon JS. Effect of sodium lauryl sulfate on recurrent aphthous stomatitis: a randomized controlled clinical trial. Oral Dis 2012;18(7):655-60. PMID 22435470 (연세대 치과대학 구강내과) | https://pubmed.ncbi.nlm.nih.gov/22435470/ |
| Alli | Alli BY et al. J Oral Pathol Med 2019;48(5):358-64. PMID 30839136 (체계적 문헌고찰·메타분석, RCT 4편 n=124) | https://pubmed.ncbi.nlm.nih.gov/30839136/ |
| Herlofson | Herlofson BB, Barkvoll P. Acta Odontol Scand 1994;52(5):257-9. PMID 7825393 | https://pubmed.ncbi.nlm.nih.gov/7825393/ |
| Healy | Healy CM et al. Oral Dis 1999;5(1):39-43. PMID 10218040 | https://pubmed.ncbi.nlm.nih.gov/10218040/ |

## 주장별 원문

1. **"구내염, 볼 안쪽이 하얗게 패여서 칫솔만 닿아도 따끔하신가요?"** (훅 증상)
   - NHS: "Mouth ulcers usually appear inside the mouth on the cheeks or lips." / "damaging your gums with a toothbrush or irritating toothpaste"(원인 목록) / Do: "use a soft-bristled toothbrush"
2. **"평소 쓰던 치약으로 그냥 닦는 분이 많은데요. 그 치약의 거품이 헌 곳을 더디게 낫게 할 수 있어요"** (통념 반박)
   - NHS(Don't): "do not use toothpaste containing sodium lauryl sulphate" — 같은 목록의 목적 "speed up the healing process / reduce pain".
   - Shim: "Only duration of ulcers and mean pain score was significantly decreased during the period using SLS-free."
3. **"거품을 내는 성분, 라우릴황산나트륨 … 치약에 가장 흔히 넣는, 때를 씻어 내는 성분"**
   - Healy: "Sodium lauryl sulphate (SLS) is the most commonly used detergent in dentifrices."
4. **"입안 살갗을 덮은 얇은 보호막까지 벗겨 낸다고 봐요. 보호막이 벗겨지면 헌 곳이 그대로 드러나요"** (기전 — 가설이라 "봐요")
   - Herlofson: "It is suggested that the denaturing effect of SLS on the oral mucin layer, with exposure of the underlying epithelium, induces an increased incidence of RAU."
5. **"연세대 치과대학 연구팀이 구내염이 자주 나는 90명에게 이 성분이 든 치약과 뺀 치약을 8주씩 번갈아 쓰게 해 봤어요"** [기관명 1/2]
   - Shim(소속 "Department of Oral Diagnosis & Oral Medicine, College of Dentistry, Yonsei University"): "double-blind crossover trial. The 90 subjects" / "used one of the two assigned dentifrices for 8 weeks and then the other for the following 8 weeks"
6. **"뺀 치약을 쓴 동안 구내염이 덜 생기지는 않았지만, 생긴 곳은 더 빨리 낫고 덜 아팠어요"**
   - Shim: "The number of ulcers and episodes did not differ significantly between SLS-A, SLS-B, and SLS-free. Only duration of ulcers and mean pain score was significantly decreased during the period using SLS-free."
   - 초록에 구체 수치 없음(전문 유료) → 수치 안 씀.
7. **"치약부터 라우릴황산나트륨을 뺀 것으로 바꿔 보세요. 고를 땐 성분표에 이 이름이 없는지 보고, 충치를 막는 불소는 들어 있는지도"** (해결책·고르는 기준)
   - NHS: "do not use toothpaste containing sodium lauryl sulphate"
   - NHST: "Brush your teeth with fluoride toothpaste twice a day" / "Check the packaging to find out how much fluoride each brand contains." (영국 기준 1,350ppm은 한국 글에 숫자로 안 씀)
   - 상품(베르단테 클래식 덴탈케어 치약 100g, ㈜케이보은제약) 상세 이미지 직접 확인: 전성분에 라우릴황산나트륨 없음(거품 성분은 코코일글루타민산나트륨), 주의사항 "이 치약의 불소 함유량은 1,450ppm임". 의약외품.
8. **"이 성분을 뺀 치약 중엔 불소까지 뺀 것이 많거든요"**
   - 브랜드커넥트 "계면활성제 없는 치약"·"SLS 없는 치약" 검색 상위 10개 중 무불소가 7~8개(제로치약·덴티헬시·그란츠·쉼표365 등) 실측(`hdraft2/ulcer_src/bc_hits.json`).
9. **"구내염이 자주 나는 분이라면 평소 치약으로 아예 바꿔 두는 게 좋아요"**
   - Alli: "The available evidence suggests that patients with RAS may benefit from using SLS-free dentifrices for their daily oral care. However, future well-designed trials are still required"
10. **"구내염은 보통 1~2주면 나아요"**
    - NHS: "Mouth ulcers are common and should clear up on their own within a week or 2."
11. **"영국 국민보건서비스는 3주가 지나도 안 낫거나, 평소보다 크거나, 피가 나며 점점 더 아프면 치과나 병원에 가라고 해요"** [기관명 2/2]
    - NHS: "see a GP or dentist if you have a mouth ulcer that lasts longer than 3 weeks" / "is different to other mouth ulcers you've had before, for example if it's bigger than usual or near the back of your throat" / "bleeds or becomes more painful and red – this may be a sign of an infection"
12. **"오래 안 낫는 헌 곳은 드물게 구강암 신호일 수 있어요"** (목숨·안전)
    - NHS: "Although most mouth ulcers are harmless, a long-lasting mouth ulcer is sometimes a sign of mouth cancer. It's best to get it checked."

## 쓰지 않는 것 (금지선)
- "SLS 무첨가 치약이 구내염을 치료·예방한다", "덜 생긴다" — Shim·Healy는 개수 차이 없음(Healy "None of the ulcer parameters measured was significantly affected"), Alli 메타분석만 개수 감소. 대본은 "더 빨리 낫고 덜 아팠다"까지만.
- 상품 판매자 주장(잇몸질환·시린이·17종 식물 성분·HAP·유기농), 무불소 치약 권장.

## 블로그 보충(영상에 없는 정보, 같은 출처)
- NHS Do/Don't: 부드러운 칫솔, 찬 음료는 빨대로, 부드러운 음식, 정기 치과 검진 / 아주 맵고 짜고 신 음식·토스트·과자처럼 거친 음식·아주 뜨겁거나 신 음료(과일주스) 피하기.
- NHS 원인: 볼 안쪽을 깨묾, 잘 안 맞는 틀니·교정기·거친 충전물·날카로운 이, 뜨겁거나 딱딱한 음식에 다침, 칫솔이나 자극적인 치약으로 잇몸이 다침, 피곤·스트레스. 철·아연·엽산·비타민B·비타민D 부족, 일부 약, 금연 직후.
- NHS: 구내염은 전염되지 않고, 입술 주변에 물집으로 생기는 입술 헤르페스와 다르다. 여러 개가 한꺼번에 나면 수족구병·구강 편평태선·크론병 같은 다른 병의 증상일 수 있음.
- NHS: 약사가 항균 가글·진통 젤·스프레이·소금물 가글 등을 권할 수 있음, 심하거나 오래가면 의사·치과가 스테로이드 등을 처방.
- NHST: 양치 뒤 바로 물로 헹구지 말 것(남은 불소가 씻겨 나감).
- Shim: 이중맹검 교차 시험, 두 기간 사이 2주 쉬는 기간, 비교한 것은 궤양 개수·발생 횟수·지속 기간·평균 통증.

## 목숨·안전 출처 줄
- "구강암 신호" 문장(병원 신호 문단) → xray.json `sources`에 NHS 「Mouth ulcers」. 블로그 본문 끝·유튜브 설명란 끝 `출처:` 목록에 NHS·Shim, 클립 캡션엔 이름만.
