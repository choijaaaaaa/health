# 노로바이러스 (손소독제만 바르기 → 비누·물 20초 손씻기, 아이 손은 거품형 유아 손세정제) — 원문 검증 팩트 (2026-10-14)

- 검색어: **노로바이러스**(월 22,600) · 보조 **노로바이러스증상**(6,920) — 검색량은 코디네이터 수치, 재측정 안 함.
- 바꿔 쓸 제품: **알코올 손소독제 → 거품형 유아 손세정제(비누)**. 제품은 하나뿐.
  - 카탈로그 `data/_audit/brandconnect_catalog_baby.json` 「유아 손세정제」 chosen = 라이온코리아 「아이깨끗해 핸드워시 490ml 본품+450ml 리필x2개 / 거품형 손세정제」(리뷰 3,480, 평점 4.91, account baby, 링크 저장됨 https://naver.me/GjyXvyZg). 거품형 펌프 — 대본 기준과 맞음.
  - ⚠️ 상품 상세에서 "항균" 문구를 쓰는지 확인할 것 — 대본은 "항균 성분은 따로 없어도 돼요"라고 말하므로, 상품이 항균을 내세우면 대본과 상품이 반대 말을 하게 된다(그 경우 그 문장을 빼거나 무항균 제품으로 다시 sweep).
- 🚨 **제품 주장은 "비누 손씻기를 쉽게 하는 도구"까지만**이다. 이 제품이 노로를 더 잘 없앤다는 근거는 없다. 원리는 "비누와 물로 문질러 씻어 낸다"이고, 거품형은 아이가 문지르기 쉬운 편의.
- 인용은 전부 `curl -A "Mozilla/5.0 (Macintosh…)"`나 EuropePMC REST로 받은 원문을 텍스트로 바꿔 대조했다. WebFetch 요약은 쓰지 않았다. CDC는 봇 차단(Access Denied)이라 **Wayback 2026 사본**으로 대조. 원문 사본은 세션 스크래치패드 `ev2831/`(임시).

## 제목·태그·카드

- 유튜브 제목(제안): **노로바이러스, 손소독제로는 잘 안 지워지는 이유, 유아 손세정제**
- 해시태그: `#노로바이러스` `#노로바이러스증상` `#유아손세정제` `#육아만사전` · 업로드 태그에 띄어 쓴 "유아 손세정제"
- 썸네일(증상형): "아이 토한 뒤 손소독제?"
- 카드 items 순서 = 대본 순서
  1. 몇 알갱이만 들어가도 옮아요
  2. 손소독제는 노로에 잘 안 들어요
  3. 소독제 절반 남짓, 비누 80% 안팎 이상
  4. 죽이는 게 아니라 씻어 내기
  5. 기저귀 간 뒤 비누로 20초
  6. 거품형 유아 손세정제, 항균은 없어도
  7. 바로 진료받을 신호

## URL 약칭

| 약칭 | URL | 비고 |
|---|---|---|
| CDC-PREV | https://www.cdc.gov/norovirus/prevention/index.html | 미국 질병통제예방센터 「How to Prevent Norovirus」 January 13, 2025 (Wayback web.archive.org/web/2026/… 사본) |
| CDC-SPREAD | https://www.cdc.gov/norovirus/causes/index.html | CDC 「How Norovirus Spreads」 April 24, 2024 (Wayback 사본) |
| CDC-HS | https://www.cdc.gov/clean-hands/about/hand-sanitizer.html | CDC 「Hand Sanitizer Guidelines and Recommendations」 March 12, 2024 (Wayback 사본) |
| LIU | PMID 19933337 · PMC2805232 | Liu P, Yuen Y, Hsiao HM, Jaykus LA, Moe C. 「Effectiveness of liquid soap and hand sanitizer against Norwalk virus on contaminated hands.」 Appl Environ Microbiol 2010. **초록 확인** |
| NHS-NORO | https://www.nhs.uk/conditions/norovirus/ | NHS 「Norovirus (vomiting bug)」 |
| AAP-HAND | https://www.healthychildren.org/English/health-issues/conditions/prevention/Pages/Hand-Washing-A-Powerful-Antidote-to-Illness.aspx | 미국소아과학회 「Hand Washing: A Powerful Antidote to Illness」 Last Updated 2/7/2022 |

버린 출처: 질병관리청 국가건강정보포털·감염병포털 노로바이러스 항목(검색이 JS·빈 응답, 콘텐츠 번호를 못 찾음 — 이 편엔 질병관리청 인용 없음), cdc.gov 직접 접속(Access Denied).

## 대본 문장별 근거

**1. 훅** "노로바이러스, 아이 토를 치우고 손소독제만 바르고 계신가요?" — 상황 묘사.
- CDC-SPREAD: "You can get norovirus by accidentally getting tiny particles of feces (poop) or vomit in your mouth from a person infected with norovirus."

**2. 전염력 + 기관 반박** "노로바이러스는 몇 알갱이만 입에 들어가도 옮아요. 그런데 미국 질병통제예방센터는 손소독제가 노로에 잘 안 들어서, 비누 손씻기를 대신 못 한다고 해요."
- CDC-SPREAD: "If you get norovirus illness, you can shed billions of norovirus particles that you can't see without a microscope. It only takes a few norovirus particles to make you and other people sick."
- CDC-PREV: "Wash hands well with soap and water; hand sanitizer alone does not work well against norovirus." · "Hand sanitizer does not work well against norovirus. You can use hand sanitizers in addition to hand washing, but hand sanitizer is not a substitute for handwashing, which is best."
- NHS-NORO(보조): "(alcohol hand gels do not kill norovirus)"

**3. 연구("실제로") + 원리** "실제로 손가락에 노로바이러스를 묻혀 시험해 보니, 손소독제는 많아야 절반 남짓 줄였어요. 비누로 씻으면 80% 안팎에서 94%까지 줄었고요. 죽이는 게 아니라 문질러 씻어 내는 거예요."
- LIU: "we observed the greatest reduction in genomic copies of NV cDNA with the antibacterial liquid soap treatment (0.67 to 1.20 log(10) reduction) and water rinse only (0.58 to 1.58 log(10) reduction). The alcohol-based hand sanitizer was relatively ineffective, reducing the genomic copies of NV cDNA by only 0.14 to 0.34 log(10) compared to baseline." · "ethanol, regardless of concentration, was relatively ineffective, giving at most a 0.5 log(10) reduction"
  - 환산: 손소독제 0.14~0.34 log = 28%~54% 감소 → "많아야 절반 남짓". 비누 0.67~1.20 log = 79%~94% 감소 → "80% 안팎에서 94%까지".
  - ⚠️ 측정은 유전자 사본 수(RT-qPCR)이지 감염력이 아니다. 실험 비누는 **항균 액체비누**, 물로만 헹궈도 0.58~1.58 log가 줄었다 — 그래서 "죽이는 게 아니라 씻어 낸다"가 원리 문장(아래 CDC-HS와 일치). 바이러스는 노로바이러스 원형인 Norwalk virus.
- CDC-HS: "Soap and water work to remove all types of germs from hands, while sanitizer acts by killing certain germs on the skin." · "Soap and water are more effective than hand sanitizers at removing certain kinds of germs like norovirus, Cryptosporidium, and Clostridioides difficile, as well as chemicals."
- 화면 출처 줄: `출처: Liu 외, Appl Environ Microbiol 2010 · 미국 질병통제예방센터 「How to Prevent Norovirus」`

**4. 행동** "기저귀를 간 뒤엔 비누로 20초 넘게 씻으세요."
- CDC-PREV: "Wash your hands often with soap and water for at least 20 seconds, especially: After using the toilet or changing diapers. Before eating, preparing, or handling food."

**5. 바꿔 쓸 제품(제안형) + 고르는 기준** "아이 손은 거품형 유아 손세정제로 바꿔 두면 편해요. 누르면 거품이 나와서, 작은 손으로도 손가락 사이까지 금방 문지르거든요. 항균 성분은 따로 없어도 돼요. 미국소아과학회는 항균 비누가 보통 비누보다 낫지 않다고 해요."
- 문지르기: AAP-HAND(CDC 단계 인용) "Rub hands vigorously together. Scrub every surface completely. Keep rubbing and scrubbing for 20 seconds to effectively remove the germs."
- 항균: AAP-HAND "studies have shown that these antibacterial products are no better at washing away dirt and germs than regular soap." · "The best solution is to wash your child's hands with warm water and ordinary soap that does not contain antibacterial substances (eg, triclosan)."
- "거품이 나와 문지르기 쉽다"는 제품 형태(펌프식 거품) 묘사 — 효과 수치 주장 없음.
- 대본 미사용(블로그용): AAP-HAND "Regular use of soap and water is better than using waterless (and often alcohol-based) soaps, gels, rinses, and hand sanitizer rubs when your child's hands are visibly dirty" · CDC-HS "Supervise young children when they use hand sanitizer to prevent swallowing alcohol".

**6. 병원 신호** "계속 토해 물도 못 넘기거나, 기저귀가 덜 젖거나, 초록빛 토를 하면 바로 진료받으세요."
- NHS-NORO(Call 111): "you or your child keep being sick and cannot keep fluid down" · "a child under 5 years has signs of dehydration, such as fewer wet nappies" · (Call 999 or A&E) "have yellow-green or green vomit (children)"
- 대본 미사용(블로그용): NHS-NORO "you're worried about a baby under 12 months" · "your child stops breast or bottle feeding while they're ill" · "do not go to school, nursery or work until you have not been sick or had diarrhoea for 2 days" · CDC-PREV 토사물 청소 "use a chlorine bleach solution with a concentration of 1,000 to 5,000 ppm (5 to 25 tablespoons of household bleach [5% to 8%] per gallon of water)" · "Leave bleach disinfectant on the affected area for at least 5 minutes." · CDC-SPREAD "you can still spread norovirus for 2 weeks or more after you feel better."

## 목숨·안전 출처 줄(화면) 제안

- 2문단: `출처: 미국 질병통제예방센터 「How to Prevent Norovirus」·「How Norovirus Spreads」`
- 3문단: `출처: Liu 외, Appl Environ Microbiol 2010`
- 6문단(병원 신호): `출처: NHS 「Norovirus (vomiting bug)」`
- 블로그·설명란 출처 목록: 위 전부 + CDC 「Hand Sanitizer Guidelines and Recommendations」, 미국소아과학회 「Hand Washing: A Powerful Antidote to Illness」.
