# 장염 (이온음료를 컵째 → 경구수액을 몇 분마다 조금씩) — 원문 검증 팩트 (2026-10-14)

- 검색어: **장염**(월 19,720) · 보조 **이온음료**(9,160) · **경구수액**(3,020) — 검색량은 코디네이터 수치, 재측정 안 함.
- 바꿔 쓸 제품: **이온음료(스포츠음료) → 아기 경구수액(ORS)**. 제품은 하나뿐.
- 🚨 **블로커 — 카탈로그 제품이 경구수액이 아니다.** `data/_audit/brandconnect_catalog_baby.json` 「전해질 보충 음료」 chosen = 「구트할로 발포 포도당 밸런스 스포츠 이온 음료 전해질 보충 러닝 등산 86g」 — **스포츠 이온음료**다. 대본이 "이온음료가 아니라 경구수액이라고 적힌 제품"을 고르라고 하므로 이 링크를 걸면 대본과 상품이 반대 말을 한다. **걸지 말 것.**
  - 필요한 것: 육아 계정(`login --baby`)으로 "아기 경구수액"·"경구수분보충"·"유아 전해질" 등 sweep → 상품명·표시에 **경구수액(경구 수분 보충액, oral rehydration solution)** 이 명시된 식품 유형 제품. 국내 ORS 상당수는 일반의약품(약국)이라 링크가 안 될 수 있다(CLAUDE.md 품목 절). 걸 만한 제품이 없으면 이 주제는 각도 변경 또는 폐기 판단 필요(제품 없는 원고 없음 규칙).
  - 품목명 제안: **"아기 경구수액"**(건강 쪽 "전해질 보충 음료"와 이름 분리).
- ⚠️ **기존 육아_8(아기 설사)과 겹친다** — 육아_8도 "이온음료·주스 대신 약국 경구수액, 5mL씩 1~2분 간격"을 다뤘다. 이 편은 **구토 뒤 목말라하는 아이·먹이는 속도(조금씩 자주)·경구수액 효과 근거(코크란)** 쪽으로 각도를 옮겼지만, 같은 결론이라 업로드 간격·편성은 코디네이터가 판단할 것.
- 인용은 전부 `curl -A "Mozilla/5.0 (Macintosh…)"`나 EuropePMC REST로 받은 원문 대조. WebFetch 요약 미사용. 원문 사본 세션 스크래치패드 `ev2831/`(임시).

## ⚠️ 먼저 알아야 할 충돌 — 미국소아과학회 안에서도 이온음료 표현이 갈린다

- 「Diarrhea in Children」: "Soft drinks (soda, pop), soups, juices, sports drinks, and boiled milk have the wrong amounts of sugar and salt and may make your child sicker."
- 「Drinks to Prevent Dehydration When Your Child is Vomiting」(2023): 돌 이상 "commercial oral rehydration solutions (liquid form and popsicles) diluted apple juice or sports drink (half water/ half drink)" · "Note: Be careful with commercial sports drinks. They replace salts, but they can also contain large amounts of sugar, which can make diarrhea worse."
- → 대본은 "이온음료는 안 된다"고 단정하지 않고, 두 문서가 일치하는 부분(**당이 많아 설사를 더 심하게 할 수 있다**)만 썼다. 블로그엔 "돌 지난 아이는 물에 반 섞은 스포츠음료도 쓸 수 있다는 지침도 있다"를 한 줄 밝히는 게 정확하다.
- 돌 전 아기: 같은 문서 "6 months to 1 year: undiluted breast milk or formula. If not tolerated, consider a commercial rehydration solution that contains sugars and salts. Do not use water." — 대본엔 넣지 않았다(분량). 블로그·카드 각주용.

## 제목·태그·카드

- 유튜브 제목(제안): **아이 장염, 토한 뒤 이온음료 말고 조금씩 자주, 아기 경구수액**
- 해시태그: `#장염` `#아이장염` `#경구수액` `#아기경구수액` `#육아만사전` · 업로드 태그에 띄어 쓴 "아기 경구수액"
- 썸네일(증상형): "토한 뒤 목말라하는 아이"
- 카드 items 순서 = 대본 순서
  1. 이온음료는 당이 많아요
  2. 경구수액 = 소금·포도당 비율 맞춘 물
  3. 작은창자에서 흡수돼 채워요
  4. 스물다섯 명 중 한 명만 주사
  5. 몇 분마다 한 숟갈, 한 시간 30mL
  6. "경구수액" 표시 확인
  7. 바로 진료받을 신호

## URL 약칭

| 약칭 | URL | 비고 |
|---|---|---|
| AAP-DRINK | https://www.healthychildren.org/English/health-issues/conditions/abdominal/Pages/Drinks-to-Prevent-Dehydration-in-a-Vomiting-Child.aspx | 미국소아과학회 「Drinks to Prevent Dehydration When Your Child is Vomiting」 Last Updated 2/7/2023 |
| AAP-DIAR | https://www.healthychildren.org/English/health-issues/conditions/abdominal/Pages/Diarrhea.aspx | 미국소아과학회 「Diarrhea in Children」 Last Updated 5/25/2021 |
| AAP-VOM | https://www.healthychildren.org/English/health-issues/conditions/abdominal/Pages/Treating-Vomiting.aspx | 미국소아과학회 「Treating Vomiting」 Last Updated 2/24/2025 |
| AAP-DEHY | https://www.healthychildren.org/English/health-issues/injuries-emergencies/Pages/dehydration.aspx | 미국소아과학회 「Dehydration」 Last Updated 9/24/2019 |
| WHO | https://www.who.int/news-room/fact-sheets/detail/diarrhoeal-disease | 세계보건기구 「Diarrhoeal disease」 fact sheet |
| HARTLING | PMID 16856044 · PMC6532593 · doi:10.1002/14651858.cd004390.pub2 | Hartling L, et al. 「Oral versus intravenous rehydration for treating dehydration due to gastroenteritis in children.」 Cochrane Database Syst Rev 2006. **초록 확인** |
| NHS-DV | https://www.nhs.uk/conditions/diarrhoea-and-vomiting/ | NHS 「Diarrhoea and vomiting」(보조) |

버린 출처: healthychildren 「Oral-Rehydration-Solutions」·「Vomiting」 추정 주소(404), CDC(봇 차단).

## 대본 문장별 근거

**1. 훅** "장염, 토하고 나서 목말라하는 아이에게 이온음료를 컵째 주고 계신가요?" — 상황 묘사.
- AAP-DRINK: "When your child is throwing up (vomiting), it's easy for them to become dehydrated."

**2. 통념 반박** "이온음료는 소금은 채워 줘도 당이 많아서, 설사를 더 심하게 할 수 있다고 미국소아과학회는 말해요."
- AAP-DRINK: "Be careful with commercial sports drinks. They replace salts, but they can also contain large amounts of sugar, which can make diarrhea worse."
- AAP-DIAR: "sports drinks ... have the wrong amounts of sugar and salt and may make your child sicker."

**3. 경구수액 정의·원리** "이럴 땐 경구수액이 맞아요. 물에 소금과 포도당을 알맞게 녹인 음료라, 작은창자에서 흡수돼 빠져나간 물과 소금을 채워 줘요."
- WHO: "Rehydration with oral rehydration salts (ORS) solution. ORS is a mixture of clean water, salt and sugar." · "ORS is absorbed in the small intestine and replaces the water and electrolytes lost in the faeces."
- AAP-DIAR: "Electrolyte solutions are special fluids that have been designed to replace water and salts lost during diarrhea."
- AAP-DRINK: "Oral rehydration therapy is an effective and safe method for preventing dehydration at home."

**4. 근거("실제로")** "실제로 탈수된 아이들 시험 열일곱 개를 모아 보니, 경구수액으로 시작한 아이 스물다섯 명 중 한 명꼴만 결국 수액 주사가 필요했어요."
- HARTLING: "Seventeen trials (1811 participants), of poor to moderate quality, were included." · "There were more treatment failures with ORT (RD 4%, 95% confidence interval (CI) 1 to 7 ...; NNT = 25)." · "For every 25 children (95% CI 14 to 100) treated with ORT one would fail and require IVT." · "Although no clinically important differences between ORT and IVT"
- ⚠️ 시험 대부분 병원에서 의료진이 먹인 경우다. "집에서 먹이면 주사가 필요 없다" ✗. 대본은 원문의 "25명 중 1명 실패" 그대로.
- 화면 출처 줄: `출처: Hartling 외, 코크란 리뷰 2006 (시험 17개, 1,811명)`

**5. 먹이는 법** "먹일 땐 몇 분마다 숟가락이나 투약기로 조금씩, 한 시간에 30밀리리터 넘게가 목표예요."
- AAP-DRINK: "encourage them to suck or drink small amounts of fluids every few minutes over a few hours. The goal should be having them take in at least 1 ounce (30ml) per hour." · "If your child cannot sip from a bottle or cup, try using a medicine cup, syringe or teaspoon."
- AAP-VOM: "encourage them to suck or drink small amounts of electrolyte solution (ask your pediatrician which one)" · "Liquids not only help to prevent dehydration, but also are less likely than solid foods to stimulate further vomiting."

**6. 바꿔 쓸 제품(제안형) + 고르는 기준** "그래서 아기 경구수액을 갖춰 두면 편해요. 고를 땐 이온음료가 아니라 경구수액이라고 적힌 제품인지 보세요."
- AAP-DIAR: "Do not try to prepare your own electrolyte solutions at home. Use only commercially available fluids—store brand and name brand work the same."
- AAP-DRINK: "commercial oral rehydration solutions" · "consider a commercial rehydration solution that contains sugars and salts"
- 대본 미사용(블로그용): NHS-DV "oral rehydration powder that you mix with water to make a drink" — 가루형이면 정해진 물 양 지키기.

**7. 병원 신호** "계속 토해 물도 못 넘기거나, 하루 기저귀가 여섯 개도 안 젖거나, 축 처지면 바로 진료받으세요."
- AAP-DRINK: "Call your child's doctor right away if your child is too sick to drink, becomes lethargic, or shows any signs and symptoms of dehydration. These include: urinating less frequently (for infants, fewer than 6 wet diapers daily)"
- AAP-VOM: "If your child can't keep any clear liquids down, or if the symptoms get worse, notify your pediatrician."
- 대본 미사용(블로그용): AAP-DIAR 진료 신호 "Bloody stools" · "Vomiting that lasts more than 12 to 24 hours" · "Vomit that looks green, tinged with blood, or like coffee grounds" · AAP-DEHY 탈수 징후 "Sunken soft spot of the head" · "Fewer tears when crying" · AAP-DRINK "their small size means that it takes less fluid loss to lead to dehydration."

## 목숨·안전 출처 줄(화면) 제안

- 2문단: `출처: 미국소아과학회 「Drinks to Prevent Dehydration When Your Child is Vomiting」`
- 3문단: `출처: 세계보건기구 「Diarrhoeal disease」`
- 4문단: `출처: Hartling 외, Cochrane Database Syst Rev 2006`
- 7문단(병원 신호): `출처: 미국소아과학회 「Drinks to Prevent Dehydration When Your Child is Vomiting」·「Treating Vomiting」`
- 블로그·설명란 출처 목록: 위 전부 + 미국소아과학회 「Diarrhea in Children」·「Dehydration」, NHS 「Diarrhoea and vomiting」.
