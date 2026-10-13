# 신생아 수유량 (모유 양 불안·분유 보충 → 아기 체중계) — 원문 검증 팩트 (2026-10-14)

- 검색어: **신생아 수유량**(월 8,050) · 보조 **아기체중계**(3,490)·**아기몸무게**(2,230)·**신생아몸무게**(1,260) — 검색량은 코디네이터 제공값, 이 세션에선 재측정 안 함.
- 바꿔 쓸 제품: **수유 시간·젖병 ml 세기(눈대중) → 아기 체중계**(하나만). 브랜드커넥트 육아 계정 카탈로그 `data/_audit/brandconnect_catalog_baby.json` 「아기 체중계」 chosen = 아이워너 KS-BM520 아기 유아 반려동물 디지털 체중계(아리프 스포츠, 35,000원, 수수료 10%, 리뷰 129, 평점 4.61, 링크 https://naver.me/5dh4EA5P). 품목명은 브랜드 없이 "아기 체중계".
- ⚠️ **KS-BM520 최소 표시 단위(10g/20g 등)는 확인 못 함.** 다나와 상세 스펙(pcode=88197383)에 "측정범위 : 0.05~20kg / 용기무게제거기능 / 자동센서 / HOLD기능 / 자동전원차단 / 유아무게측정"까지만 있고 눈금 단위는 없다. 스마트스토어 상세는 JS라 본문을 못 받음. → 대본의 "10그램 단위" 기준은 일반 고르는 기준으로만 썼고, 이 제품이 10g이라고 말하지 않는다. **코디네이터가 상품 상세에서 표시 단위를 확인할 것**(10g 미만 확인 안 되면 칠판·블로그에 "10g 단위" 문구를 이 제품과 붙이지 말 것). 영점(용기무게제거) 기능은 다나와 스펙으로 확인됨.
- 🚨 제품 주장은 **"몸무게 변화를 숫자로 기록해 진료 때 보여 준다"까지**. 집 체중계가 병원 체중 측정을 대신한다거나, 수유 전후로 재서 먹은 양을 알아낸다는 주장은 하지 않는다(근거 원문 없음).
- 인용은 전부 `curl -A "Mozilla/5.0 (Macintosh…)"`로 받은 원문을 텍스트로 바꿔 문자열 대조. WebFetch 요약 안 씀. 원문 사본은 세션 스크래치패드 `ev30/`(임시).

## ⚠️ 브리프와 달라진 점

- 브리프의 "일주일에 한 번 재서 기록" → **NHS 원문이 "생후 2주 뒤엔 6개월까지 한 달에 한 번 이하"**라서 그대로 따랐다(대본 "생후 2주 뒤론 한 달에 한 번이면 충분해요"). 매주 재라는 기관 문장은 찾지 못했다. 강박적으로 재지 말라는 방향과도 맞는다.
- 브리프의 "생후 10~14일 출생 체중 회복"은 대본에 숫자로 안 넣었다. 원문은 AAP "2주에 출생 체중 아래면 경고 신호", NHS "대부분 3주까지 회복(3주까지 못 되찾으면 도움)"으로 갈린다 → 대본엔 더 보수적인 **AAP 2주를 병원 신호로만** 썼다.
- 황달·처짐은 병원 신호에서 뺐다(황달은 육아_4가 다룸, 처짐은 확인한 수유 원문에 없음).

## 제목·태그·카드

- 유튜브 제목(제안): **신생아 수유량, 모유가 모자랄까 불안할 때 보는 법, 아기 체중계**
- 해시태그: `#신생아수유량` `#아기몸무게` `#신생아몸무게` `#아기체중계` `#육아만사전` · 업로드 태그엔 띄어 쓴 `아기 체중계`·`신생아 수유량`도
- 썸네일(증상형, 전문용어 금지): "모유 모자랄까 불안?"
- **카드 items 순서 = 대본 순서**
  1. 모유는 양이 안 보인다
  2. 분유 보태면 젖이 준다
  3. 처음 며칠 10%까지 빠짐
  4. 일주일 140~200g 증가
  5. 젖은 기저귀 하루 6개
  6. 아기 체중계로 기록
  7. 2주에도 출생 체중 미만이면 진료

## URL 약칭

| 약칭 | URL | 비고 |
|---|---|---|
| AAP-ENOUGH | https://www.healthychildren.org/English/ages-stages/baby/breastfeeding/Pages/How-to-Tell-if-Baby-is-Getting-Enough-Milk.aspx | 미국소아과학회 「How to Tell if Your Breastfed Baby is Getting Enough Milk」 Joan Younger Meek, Last Updated 1/13/2025 |
| AAP-WARN | https://www.healthychildren.org/English/ages-stages/baby/breastfeeding/Pages/Warning-Signs-of-Breastfeeding-Problems.aspx | 「11 Warning Signs of Breastfeeding Problems」 Last Updated 3/25/2024 |
| AAP-LOW | https://www.healthychildren.org/English/ages-stages/baby/breastfeeding/Pages/low-breast-milk-supply.aspx | 「Low Breast Milk Supply」 Hailey Nelson, Last Updated 8/16/2024 |
| NHS-MILK | https://www.nhs.uk/baby/breastfeeding-and-bottle-feeding/breastfeeding-problems/enough-milk/ | 영국 국민보건서비스 「Breastfeeding: is my baby getting enough milk?」 last reviewed 30 April 2026 |
| NHS-WT | https://www.nhs.uk/baby/babys-development/height-weight-and-reviews/baby-height-and-weight/ | 「Your baby's weight and height」 last reviewed 20 September 2023 |
| DANAWA | https://prod.danawa.com/info/?pcode=88197383 | 아이워너 KS-BM520 상세 스펙(측정범위·영점 기능) |

버린 출처: CDC breastfeeding 페이지(Access Denied), 질병관리청 국가건강정보포털(검색이 JS라 해당 문서 번호를 못 찾음), 네이버 스마트스토어 상세(JS), WHO 성장표준(대본에 필요한 수치를 AAP가 이미 줌 — 안 받음).

## 대본 문장별 근거

**1. 훅** "신생아 수유량, 모유가 모자랄까 봐 수유 시간을 재고 분유까지 타 주시나요?" — 상황 묘사.
- AAP-ENOUGH: "Nearly all new parents worry about whether their babies are properly nourished."
- NHS-MILK: "When you first start breastfeeding, you may wonder if your baby is getting enough milk."

**2. 통념 반박** "모유는 먹은 양이 안 보여요. 그렇다고 분유를 보태면 오히려 젖이 덜 만들어져요."
- AAP-ENOUGH: "If you're breastfeeding, you can't measure exactly how much milk your newborn is taking. However, there are other ways to tell if your baby is getting enough to eat."
- NHS-MILK: "Introducing bottle feeds will reduce the amount of breast milk you produce." · (Things that can affect your milk supply) "Giving your baby bottles of formula or a dummy before breastfeeding is well established."
- ⚠️ "수유 시간을 재는 게 쓸모없다"고는 쓰지 않았다 — AAP-WARN은 늘 10분 미만·50분 초과를 경고 신호로 본다("Breastfeeding sessions that are consistently shorter than about 10 minutes … Sessions that are consistently longer than about 50 minutes are also cause for concern."). 대본은 "양이 안 보인다"까지만.
- ⚠️ 분유 보충 자체를 금지하지 않는다. 의사가 보충을 권한 경우 AAP-LOW: "If you are supplementing with formula, offer breast milk first." — 블로그엔 이 줄을 같이 쓸 것.

**3. 해결 기준(몸무게)** "그래서 양 대신 몸무게를 봐요. 갓난아기는 처음 며칠 몸무게가 10%까지 빠졌다가 다시 늘어요. 젖이 돌면 일주일에 140그램에서 200그램은 늘어야 해요."
- AAP-ENOUGH: "How fast babies gain weight, how many wet and dirty diapers they have, and how long they seem satisfied after nursing are good clues." · "Lose no more than 8%-10% of their birth weight in the first few days after birth, before starting to gain weight again." · "The weight check at that visit will help to know if your baby is getting enough milk from feedings."
- AAP-WARN: "By two weeks of age, your baby is under their birth weight or hasn't started gaining at least 5 to 7 ounces per week since your milk came in. Inadequate weight gain is one of the strongest signs that a baby is not getting enough milk." — 5온스 = 141.7g, 7온스 = 198.4g → "140그램에서 200그램". "젖이 돌면" = "since your milk came in".
- NHS-MILK: "Your baby gains weight steadily after the first 3 to 4 days – it's normal for babies to lose some of their birth weight in the first 3 to 4 days."
- NHS-WT: "Steady weight gain is one of the signs that your baby is healthy and feeding well."

**4. 기저귀** "기저귀도 단서예요. 생후 5일부터는 묵직하게 젖은 기저귀가 하루 6개는 나와야 해요."
- NHS-MILK: "From day 5 onwards, wet nappies should start to become more frequent, with at least 6 heavy, wet nappies every 24 hours. In the first 48 hours, your baby is likely to have only 2 or 3 wet nappies."
- AAP-ENOUGH: "Have 6 or more wet diapers per day, with nearly colorless or pale yellow urine, by 5 to 7 days old."
- 블로그용: NHS "take an unused nappy and add 2 to 4 tablespoons of water" (젖은 기저귀 감 잡기).

**5. 제품** "이 차이는 안아 봐선 몰라요. 그래서 아기 체중계를 갖춰 두면 편해요. 같은 시각, 기저귀만 채워 재고 적어 뒀다가 진료 때 보여 주면 돼요. 생후 2주 뒤론 한 달에 한 번이면 충분해요."
- "안아 봐선 몰라요" — 하루 20~30g(주 140~200g) 차이를 손 감각으로 구별하기 어렵다는 상식 표현(수치 주장 아님).
- 진료 때 보여 주기: AAP-LOW "Your pediatrician will start by looking at how your infant is growing. A baby who is tracking along their growth curve as they should is very reassuring." · AAP-WARN "keep a written record of your baby's wet diapers and bowel movements during the early days" (기록을 남기는 습관의 근거 — 원문은 기저귀 기록).
- "같은 시각, 기저귀만 채워" — 같은 조건 비교를 위한 측정 방법(사실 주장 아님, 기관 원문 미확인).
- 빈도: NHS-WT "After the first 2 weeks, your baby should be weighed: no more than once a month up to 6 months of age · no more than once every 2 months from 6 to 12 months of age · no more than once every 3 months over the age of 1" · "Your baby will be weighed during their first 2 weeks to make sure they're regaining their birthweight."
- ⚠️ 정확한 판정은 병원 몸무게: AAP-WARN "have your baby weighed by their pediatrician immediately. This is the most precise way to tell whether they are ingesting enough milk." → 집 체중계는 "기록해서 보여 주는 도구"로만 말한다.

**6. 고르는 기준** "고를 땐 10그램 단위로 재지는지, 담요 무게를 빼는 영점 기능이 있는지 보세요."
- 10g: 주 140~200g = 하루 20~30g 변화를 읽으려면 표시 단위가 그보다 촘촘해야 한다는 산수(기관 원문 아님). 50g·100g 단위 저울이면 하루 변화가 묻힌다.
- 영점: DANAWA "측정범위 : 0.05~20kg / 용기무게제거기능 / 자동센서 / HOLD기능 / 자동전원차단 / 유아무게측정".
- ⚠️ KS-BM520의 표시 단위 미확인(위 메모).

**7. 병원 신호** "생후 2주에도 태어날 때보다 가볍거나, 젖은 기저귀가 6개가 안 되면 진료를 받으세요."
- AAP-WARN 5: "By two weeks of age, your baby is under their birth weight …" · 6: "After 7 days, your baby has fewer than 6 wet diapers and 4 stools per day, their urine is dark yellow or specked with red, or their stool color is still dark rather than yellow and loose." · 머리말 "Contact your baby's pediatrician".
- NHS-WT(참고, 영국 기준): "Most babies are at, or above, their birthweight by 3 weeks. A midwife or health visitor will support you if your baby loses a large amount of weight or does not regain their birthweight by 3 weeks." — 대본은 더 이른 AAP 2주를 씀.
- 블로그용 추가 신호(AAP-WARN): 대부분 수유 뒤에도 배고파 보임("Consult your pediatrician and have them weighed right away"), 삼키는 소리가 안 들림, 소변이 진한 노란색.

## 겹침 확인
- 육아_4(황달): 물 주지 말 것·황달 경과·변 색 — 이 편은 황달·변 색 안 다룸.
- 육아_9(배앓이): "몸무게가 안 늘면 진료" 한 구절만 겹침 — 이 편은 몸무게를 판단 기준으로 깊게 다룸, 배앓이 내용 없음.

## 화면 출처 줄(제안)
- 목숨·안전 수준(사망·질식·중독·용량) 주장은 없음 → 필수 출처 줄 대상 아님. 다만 수치 칸에 넣는다면:
  - 3문단(10%·140~200g): `출처: 미국소아과학회 「How to Tell if Your Breastfed Baby is Getting Enough Milk」·「Warning Signs of Breastfeeding Problems」`
  - 4문단(기저귀 6개): `출처: 영국 NHS 「Is my baby getting enough milk?」`
  - 5문단(한 달에 한 번): `출처: 영국 NHS 「Your baby's weight and height」`
- 블로그·설명란 출처 목록: AAP-ENOUGH, AAP-WARN, AAP-LOW, NHS-MILK, NHS-WT.
