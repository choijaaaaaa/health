# 이앓이 — 이앓이 젤 → 치발기 · 원문 검증 팩트 (2026-10-09)

검색어 **이앓이**. 해결책 도구 = **치발기**(잇몸에 바르는 이앓이 젤·마취 젤 대신). 브랜드커넥트 baby 카탈로그 "아기 치발기" 있음(`data/_audit/brandconnect_catalog_baby.json`, 2026-09-24 확인).

방법: 논문 초록은 EuropePMC REST(resultType=core) JSON, 기관 페이지는 `curl -A "Mozilla/5.0 (Macintosh)"`로 받은 원문을 텍스트로 바꿔 **스크립트로 문자열 대조**(29개 인용 전부 일치, WebFetch 미사용). FDA는 fda.gov가 봇 차단(Akamai 302 → abuse-detection)이라 **Wayback Machine 사본**(2025-12 스냅샷, 원문 그대로)으로 받았다. 식약처 안전성 서한은 식약처 사이트 원본 대신 메디포뉴스 기사에 첨부된 **식약처 배포 PDF 원본**(「의약품 안전성 서한」 2018. 5. 28.)을 받아 pdftotext로 대조했다(2단 편집이라 문장이 단 경계에서 끊겨 두 토막으로 대조). 원문 사본은 세션 스크래치패드 `ev22/`(임시).

## URL 약칭

| 약칭 | URL | 비고 |
|---|---|---|
| MASSIGNAN-2016 | https://www.ebi.ac.uk/europepmc/webservices/rest/search?query=EXT_ID:26908659%20AND%20SRC:MED&resultType=core&format=json | Massignan C, Cardoso M, Porporatti AL, Aydinoz S, Canto GL, Mezzomo LA, Bolan M. "Signs and Symptoms of Primary Tooth Eruption: A Meta-analysis." Pediatrics 2016;137(3):e20153501. PMID 26908659, doi 10.1542/peds.2015-3501. 초록만(전문 비공개) |
| FDA-BENZ-2018 | https://www.fda.gov/drugs/drug-safety-and-availability/risk-serious-and-potentially-fatal-blood-disorder-prompts-fda-action-oral-over-counter-benzocaine | FDA Drug Safety Communication, Safety Announcement 05-23-2018. 받은 사본 web.archive.org/web/20251231131533 |
| FDA-CU | https://www.fda.gov/consumers/consumer-updates/safely-soothing-teething-pain-and-sensory-needs-babies-and-older-children | FDA Consumer Update 「Safely Soothing Teething Pain in Infants and Children」, Content current as of 06/26/2024. 사본 web.archive.org/web/20251222010547 |
| MFDS-서한 | https://www.medifonews.com/news/download.html?no=138324&atno=27940 | 식약처 「의약품 안전성 서한」 2018. 5. 28. "미국 FDA, 치과･구강용 벤조카인 함유 제제 24개월 미만 사용 금지 조치"(PDF 2쪽, 기사 첨부 원본) |
| AAP-HC | https://www.healthychildren.org/English/ages-stages/baby/teething-tooth-care/Pages/Teething-Pain.aspx | AAP HealthyChildren 「Teething Pain Relief」, Last Updated 7/9/2025, Source AAP Section on Oral Health |
| NHS-SYM | https://www.nhs.uk/baby/babys-development/teething/baby-teething-symptoms/ | NHS 「Baby teething symptoms」, reviewed 14 May 2026 |
| NHS-TIPS | https://www.nhs.uk/baby/babys-development/teething/tips-for-helping-your-teething-baby/ | NHS 「Tips for helping your teething baby」, reviewed 23 October 2025 |

## 1. 바르는 젤은 몇 분 만에 씻겨 나간다 — 검증됨 (대본 반전)

대본: "그런데 잇몸에 바른 젤은 침에 씻겨 몇 분 만에 사라져요."
- FDA-BENZ-2018: "Topical pain relievers and medications that are rubbed on the gums are not useful because they wash out of a baby’s mouth within minutes."
- AAP-HC: "Numbing gels made for a baby's gums usually aren't helpful, since excess drool washes them away quickly."
- NHS-TIPS: "There's a lack of evidence that teething gels are effective."
- ⚠️ 국내 '이앓이 젤'은 마취 성분 없는 의약외품·화장품형도 많다. 그래서 "효과가 짧다"는 젤 전체에, "위험하다"는 **마취 성분이 든 젤**에만 붙였다(아래 2절).

## 2. 마취 성분(벤조카인) 젤의 위험 — 검증됨 (목숨·안전 → 화면 출처 줄 필요)

대본: "게다가 벤조카인 같은 마취 성분이 든 젤은 피가 산소를 못 나르게 만들 수 있어서, 식약처는 이가 나는 아기 잇몸엔 쓰지 말라고 해요."
- MFDS-서한(주요내용): "혈액을 통해 운반되는 산소의 양을 크게 감소시키는" / "메트헤모글로빈혈증을 유발할 수 있으며, 이는 사망까지 이르는 치명적인 결과를 가지고 올 수 있음"
- MFDS-서한(환자를 위한 권고사항): "24개월 미만 이가 나는 영아의 잇몸 통증 완화 등을 위하여 벤조카인 함유 제제를 사용하지 마시기 바람"
- FDA-BENZ-2018: "The U.S. Food and Drug Administration (FDA) is warning that over-the-counter (OTC) oral drug products containing benzocaine should not be used to treat infants and children younger than 2 years." / "Benzocaine, a local anesthetic, can cause a condition in which the amount of oxygen carried through the blood is greatly reduced. This condition, called methemoglobinemia, can be life-threatening and result in death."
- 리도카인 FDA-CU: "Topical medications (used on the surface of the gums) containing benzocaine or lidocaine offer little to no benefit and are associated with serious risks when used for teething pain in children." — 식약처 서한은 벤조카인만 다루므로 대본은 "벤조카인 같은 마취 성분"으로 쓰고, 기관 귀속(식약처)은 벤조카인에만 걸린다.
- "피가 산소를 못 나르게" = 메트헤모글로빈혈증의 쉬운 말(원문 "혈액을 통해 운반되는 산소의 양을 크게 감소").
- 화면 출처 줄: `출처: 식품의약품안전처 의약품 안전성 서한(2018.5.28)·미국 FDA 안전성 정보(2018)`

## 3. 연구 수치 — 이앓이 증상의 정체 — 검증됨

대본: "실제로 연구 16개를 모아 보니, 이가 날 때 아기 10명 중 7명이 불편한 티를 냈어요. 가장 흔한 건 잇몸 근질거림, 보챔, 침이었고요."
- MASSIGNAN-2016: "A total of 1179 articles were identified, and after a 2-phase selection, 16 studies were included." / "Overall prevalence of signs and symptoms occurring during primary tooth eruption in children between 0 and 36 months was 70.5% (total sample = 3506)." / "Gingival irritation (86.81%), irritability (68.19%), and drooling (55.72%) were the most frequent ones."
- 70.5% → "10명 중 7명". 86.81% 등 개별 증상 수치는 분모(전체 아이인지 증상 있는 아이인지)를 초록만으로 확정 못 해 **숫자 없이 순서만** 썼다(전문은 AAP 유료라 미확인).
- "Gingival irritation" → "잇몸 근질거림"(자극·가려움), "irritability" → "보챔".

## 4. 원리 — 이가 밀고 올라와 붓고, 누르면 가라앉는다 — 검증됨

대본: "이가 잇몸을 밀고 올라오면 그 자리가 붓고 근질거려요. 이때 뭔가를 꽉 깨물면 잇몸을 누르는 힘에 근질거림이 가라앉아요. 차갑게 하면 잇몸이 더 편해지고요."
- AAP-HC: "Fussiness is one signal that the gums around your baby's emerging teeth are swollen and tender, causing mild pain." / 달래는 법 "Light, focused pressure on the gums or a gentle gum massage"
- FDA-BENZ-2018(AAP 권고 인용): "Gently rub or massage the child’s gums with one of your fingers. Use a firm rubber teething ring."
- NHS-TIPS: "Some teething rings can be cooled first in the fridge, which may help to soothe your baby's gums."
- ⚠️ "누르는 힘에 가라앉는다"는 기관 권고(압박·마사지가 달랜다)를 원리로 옮긴 것이다. 압박 기전 자체를 잰 연구 수치는 없다 — 대본은 수치를 붙이지 않았다.

## 5. 해결책·고르는 기준 — 검증됨 (목숨·안전: 목걸이형)

대본: "그래서 젤 대신 치발기를 쥐여 주면 … 고를 땐 속에 물이 든 것보다 한 덩어리로 된 실리콘이 나아요. 물 든 건 찢어지면 세균 섞인 물이 샐 수 있거든요. 차게 할 땐 냉동실 말고 냉장고에 두세요. 얼면 딱딱해져 잇몸을 다치게 할 수 있어요. 목걸이처럼 목에 거는 치발기는 목이 졸리거나 숨이 막힐 수 있어 피하는 게 좋아요."
- 물 안 든 것 FDA-CU: "give the child a firm (not liquid-filled) teether made of rubber to chew on." / AAP-HC: "Liquid-filled teething toys that can tear or spring a leak, leaving sharp edges that might hurt your baby's mouth. Liquid escaping from a broken toy may also be contaminated with harmful bacteria."
- 냉장고·얼리지 말 것 NHS-TIPS: "Never put a teething ring in the freezer, as it could damage your baby's gums if it gets frozen." / FDA-CU: "Make sure the teething ring is not frozen. If the object is too hard, it can hurt the child’s gums." / AAP-HC: "Don't let your baby chew directly on anything that's frozen solid, since hard objects might hurt tender gums."
- 목걸이형 AAP-HC: "Teething necklaces made of amber, wood, marble or silicone pose serious risks for choking and strangulation." / FDA-CU: "The FDA also has received reports of death and serious injuries to infants and children, including strangulation and choking, caused by teething jewelry , such as amber teething necklaces." / NHS-TIPS: "Never tie a teething ring around your baby's neck, as it may be a choking hazard ."
- 화면 출처 줄(목걸이 문장): `출처: 미국 FDA 「Safely Soothing Teething Pain」(2024)·미국소아과학회 HealthyChildren(2025)`
- "한 덩어리로 된 실리콘"은 '물 안 든 것 + 조각이 떨어져 나갈 이음매가 없는 것'을 쉬운 말로 묶은 표현이다(원문은 "firm (not liquid-filled) teether made of rubber").

## 6. 병원 신호 — 검증됨

대본: "다만 38도가 넘는 열이나 하루 넘게 가는 설사는 이앓이 탓이 아니에요. 다른 병일 수 있으니 소아과 진료를 받으세요."
- MASSIGNAN-2016: "For body temperature analyses, eruption could lead to a rise in temperature, but it was not characterized as fever."
- NHS-SYM: "their temperature is slightly raised but less than 38C" / "Some people think that teething causes symptoms such as diarrhoea , but there's no evidence to support this."
- AAP-HC: "However, teething does not cause fever, diarrhea or excess crying. If you see these symptoms, call your child's doctor." / "Since diarrhea is a possible sign of infection, call your pediatrician if this symptom lasts more than a day."

## 브랜드커넥트 후보 메모 (코디네이터 선택용, 대본엔 브랜드 없음)

기준: ① 속에 액체 없음 ② 한 덩어리 실리콘(분리되는 작은 부품·구슬 없음) ③ 냉장 가능, 냉동 비권장 ④ 목·몸에 거는 줄/목걸이형 아님.
- **티지엠 실리콘 치발기(한 덩어리 실리콘)** — 기준 ①②에 가장 잘 맞음. **1순위.** 실물 상품명·상세에서 액체 충전 여부와 줄·클립 동봉 여부만 확인.
- **앙쥬 손목 치발기** — 카탈로그 chosen 「앙쥬 바나나 딸기 기린 치발기 아기 국민 신생아 손목」(링크 https://naver.me/xwoqKWcD 발급됨). ⚠️ '손목' 형태가 아기 손목에 차는 밴드형이면 FDA가 경고한 teething jewelry(necklaces·bracelets)와 같은 범주로 읽힐 수 있다 — 대본이 "목에 거는 치발기"를 피하라고 하므로, 손목 밴드형이면 대본과 상품이 어긋나 보일 위험. 손잡이를 쥐는 형태인지 상세에서 확인 필요.
- **퍼기 손목치발기** — 이름부터 손목 착용형. 위와 같은 이유로 **비추천**.

## 버린 근거

- Massignan 2016 개별 증상 % (86.81·68.19·55.72) — 분모 미확인(초록만), 대본엔 순서만.
- Macknin 2000 Pediatrics 고열 연구 — PMID 확인 실패(조회된 번호가 다른 논문), 열 근거는 Massignan·NHS·AAP로 충분.
- Parental beliefs 체계적 문헌고찰(Int J Paediatr Dent 2023, PMID 37017581) — 부모 인식 연구라 증상 근거 아님.
- 국가건강정보포털 이앓이 항목 — 검색으로 찾지 못함(잇몸병·치통 항목만).
- 리도카인 위험(FDA-CU 심장·뇌손상·경련) — 국내 기관 귀속이 벤조카인뿐이라 대본은 "벤조카인 같은 마취 성분"으로 묶고 리도카인은 블로그 출처 목록에만.
- AAP의 "아세트아미노펜 상담"·NHS 해열진통제 — 해결책 축(치발기)에서 벗어난 곁가지라 제외.
- AAP "젖은 손수건 얼려 씹기" — 대본의 '얼리지 말 것'과 헷갈려 제외.

## 출처 목록 (블로그 본문·유튜브 설명란 끝)

- 식품의약품안전처, 의약품 안전성 서한 「미국 FDA, 치과·구강용 벤조카인 함유 제제 24개월 미만 사용 금지 조치」(2018.5.28)
- U.S. FDA, Drug Safety Communication "Risk of serious and potentially fatal blood disorder prompts FDA action on oral over-the-counter benzocaine products used for teething and mouth pain"(2018.5.23)
- U.S. FDA, Consumer Update "Safely Soothing Teething Pain in Infants and Children"(2024)
- American Academy of Pediatrics, HealthyChildren.org "Teething Pain Relief"(2025)
- NHS, "Baby teething symptoms"·"Tips for helping your teething baby"
- Massignan C 외. Signs and Symptoms of Primary Tooth Eruption: A Meta-analysis. Pediatrics 2016;137(3):e20153501. PMID 26908659

## 추가 검증(2026-10-09)

- 인용 29개 스크립트 대조 통과(MFDS PDF는 2단 편집 경계에서 문장이 끊겨 두 토막으로 대조).
- 기관명은 식약처 1회(상한 2회 안).
- 숫자: 16개(연구 수), 10명 중 7명(70.5%), 38도 — 3개.
- `content_review` 6종(plain_language·connective_flow·content_depth·opening_hook·unsourced_claims·perceivable_units) 빈 결과. 단 `card_news_spec.json`이 아직 없어 `check_content_depth`는 content_v2 없이 통과한 것.
- 공백 제외 430자.
