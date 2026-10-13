# 아토피 아기 목욕 (일반 비누 → 약산성 아기 바디워시) — 원문 검증 팩트 (2026-10-14)

- 검색어: **아토피**(월 11,190) · 보조 **아기아토피**(1,990) · **아토피바디워시**(750) — 코디네이터 측정값, 이 세션에서 재측정 안 함.
- 바꿔 쓸 제품: **일반(알칼리성) 비누 → 약산성·무향 아기 바디워시**(하나만). 품목명 "아기 바디워시".
- 카탈로그 `data/_audit/brandconnect_catalog_baby.json` 「아기 바디워시」 chosen = [신생아실 실사용] 아토오겔 베이비 키즈 아기 샴푸 유아 바디워시 신생아 바스앤샴푸 1+1(리뷰 46,787, 평점 4.91, 링크 https://naver.me/xD8uwje2).
- ⚠️ **제품 확인 필요(코디네이터)**: 이 제품이 **약산성인지, 무향(향료 무첨가)인지 원문으로 확인 못 했다** — 스마트스토어 상세는 JS라 본문이 안 받아지고, 검색에도 pH 표기가 안 나왔다. 대본은 "약산성 아기 바디워시"·"향이 없는지 보세요"를 고르는 기준으로 말하므로, 상세 이미지에서 pH(또는 '약산성' 표기)와 전성분의 향료(Fragrance/향료) 유무를 확인할 것. 둘 중 하나라도 아니면 다른 카탈로그 후보로 바꿔야 한다(대본과 모순).
- 인용은 전부 `curl -A "Mozilla/5.0 (Macintosh…)"` 원문 또는 EuropePMC REST(전문 XML)로 받아 문자열 대조. WebFetch 요약 안 씀. 사본: 세션 스크래치패드 `ev3234/`(임시).

## 제목·태그·카드

- 유튜브 제목(제안): **아토피 아기 목욕, 비누로 뽀득하게 씻기면 더 도져요, 아기 바디워시**
- 해시태그: `#아토피` `#아기아토피` `#아토피바디워시` `#아기바디워시` `#육아만사전` · 업로드 태그엔 띄어 쓴 `아기 바디워시`도
- 썸네일(증상형, 전문용어 금지): "씻기면 더 빨개져요" 또는 "목욕 후 더 가려워요"
- **카드 items 순서 = 대본 순서**
  1. 목욕 미루기도, 뽀득 비누도 X
  2. 보호막이 약한 피부
  3. 알칼리 비누가 산도를 올림
  4. 미지근한 물 5분에서 10분
  5. 약산성 아기 바디워시
  6. 약산성·무향 확인
  7. 3분 안에 보습

## URL 약칭

| 약칭 | URL | 비고 |
|---|---|---|
| AAP-ECZ | https://www.healthychildren.org/English/health-issues/conditions/skin/Pages/Eczema.aspx | 미국소아과학회 「Eczema in Babies and Children」 |
| AAD-BABY | https://www.aad.org/public/diseases/eczema/childhood/treating/treat-babies | 미국피부과학회 「How to treat eczema in babies」 |
| AAD-TIPS | https://www.aad.org/public/diseases/eczema/eczema-child-tips | 미국피부과학회 「Eczema: Tips to help your child feel better」 |
| AAD-WIN | https://www.aad.org/public/diseases/eczema/childhood/itch-relief/winter-care | 미국피부과학회 「In winter, will my child need different eczema skin care?」 |
| NHS | https://www.nhs.uk/conditions/atopic-eczema/treatment/ | 영국 국민보건서비스 「Atopic eczema」 |
| PANTHER | Panther DJ, Jacob SE. The Importance of Acidification in Atopic Eczema. J Clin Med 2015;4(5):970-978. PMC4470210, PMID 26239459 | 총설 전문(EuropePMC fullTextXML) |

버린 출처: aad.org `/childhood/treating/bathing`·`child-relief` 옛 주소(404).

## 대본 문장별 근거

**1. 훅** "아토피 아기, 가려울까 봐 목욕을 미루거나 비누로 뽀득하게 씻기고 계신가요?" — 상황 묘사(흔한 두 행동).

**2. 보호막** "둘 다 피부를 더 힘들게 해요. 아토피 피부는 겉 보호막이 약해서 물은 잘 빠져나가고 자극은 잘 들어와요."
- AAP-ECZ: "Eczema is caused by problems with the skin barrier." · "Skin with too little of this protein has a harder time holding in water and keeping out bacteria and environmental irritants."

**3. 목욕을 미루면** "목욕을 미루면 땀이나 침 같은 자극이 그대로 남아요."
- AAD-BABY: "Bathing helps to eliminate dirt and other potential irritants from your baby's skin." · "Common triggers include bodily triggers, such as sweat, saliva and scratching; … or product triggers, such as … shampoos or soaps (particularly ones containing fragrance)…"

**4. 비누와 산도** "반대로 비누는 피부 산도를 흔들어요. 건강한 피부는 약한 산성인데, 알칼리성 비누로 손을 씻었더니 산도가 크게 올라 한 시간 반이나 갔어요. 이렇게 산도가 오르면 아토피가 도지기 쉬워요."
- PANTHER: "Normal pH for non-neonatal skin is acidic and ranges from 4 to 6. Skin pH in atopic dermatitis patients is often increased into the neutral to basic range, and the resulting cascade of changes contributes to the phenotype of atopic dermatitis." · "Hand washing with alkaline soap can increase the pH of the skin by 3 pH units, and that effect persisted for 90 min [38]." · "Alkaline soaps are known to induce lesions of atopic dermatitis in susceptible individuals [40, 41]."
- NHS: "Atopic eczema can be made worse by things like: coming into contact with an allergen or irritant such as soap…" · "wash with an emollient instead of soap"
- ⚠️ "손을 씻었더니"로 쓴 이유: 원문 수치는 손 씻기 실험(어른) — 아기 몸 목욕 수치로 옮기지 않음. "크게 올라" = 3 pH 단위(대본에선 숫자 대신 "크게").
- ⚠️ 원문: 갓난아기 피부는 중성에서 시작해 첫 1년에 걸쳐 산성이 된다("Newborn skin begins with a neutral pH, and the transition to acidity occurs during the first year of life, with larger incremental changes occurring in the first two months"). 대본의 "건강한 피부는 약한 산성"은 일반 피부 서술 — 블로그에선 이 단서를 덧붙일 것.

**5. 목욕법** "그래서 미지근한 물로 5분에서 10분만 살살 씻겨요."
- AAD-BABY: "When bathing your baby , use lukewarm water, and only wash your baby's dirty or smelly parts using a mild, fragrance-free cleanser. Avoid scrubbing your baby's skin, and limit your baby's bath to five to 10 minutes."
- AAD-TIPS: "Bathe your child in warm – not hot – water. Limit your child's time in the bath to 5 or 10 minutes."

**6. 제품** "이때 비누 대신 약산성 아기 바디워시로 바꿔 두면 편해요. 피부 원래 산도에 가까워 씻고 나서도 산도를 덜 흔들거든요."
- 원리: PANTHER 4번 인용(알칼리 비누가 산도를 올림)의 반대 — 피부 산도(4~6) 범위의 세정제는 산도를 그만큼 올리지 않는다는 추론. PANTHER는 "The two primary avenues of treatment opportunities for pH management are bathing parameters (soap, temperature, time) and the moisturizer" 라고 했지만, **약산성 세정제가 아토피를 줄였다는 비교 시험은 없다고 스스로 밝힘**("the utility of considering pH in cleansers would be solidified by well-designed studies comparing those of varying pH") → 대본에 효과 수치·"낫는다" 주장 안 씀.

**7. 고르는 기준** "고를 땐 약산성인지, 향이 없는지 보세요."
- AAD-TIPS: "Use cleanser only when needed and make sure the cleanser is mild and fragrance-free. Do not use bubble bath."
- AAD-BABY: "mild, fragrance-free cleanser" (5번).

**8. 보습·병원 신호** "씻긴 뒤엔 3분 안에 보습제를 발라 주세요. 노란 딱지나 진물, 고름 물집이 보이면 소아청소년과 진료를 받으세요."
- AAD-WIN: "Apply moisturizer within 3 minutes of bathing to all skin without eczema medicine."
- AAD-BABY: "Immediately after the bath, apply a fragrance-free moisturizer, keeping in mind that thick creams and ointments are generally more effective than lotions or oils."
- AAD-TIPS: "gently pat your child's skin partially dry."
- AAP-ECZ: "Talk to your child's doctor if you see: yellow or honey-colored crusting and scabbing, weepy or oozy skin, blisters or pus bumps, or rash that is not getting better even with the usual treatments."

## 출처 줄(화면) 제안

- 4번: `출처: Panther·Jacob, J Clin Med 2015`
- 5·8번: `출처: 미국피부과학회 「How to treat eczema in babies」`

## sources

- 미국소아과학회 「Eczema in Babies and Children」 — https://www.healthychildren.org/English/health-issues/conditions/skin/Pages/Eczema.aspx
- 미국피부과학회 「How to treat eczema in babies」 — https://www.aad.org/public/diseases/eczema/childhood/treating/treat-babies
- 미국피부과학회 「Eczema: Tips to help your child feel better」 — https://www.aad.org/public/diseases/eczema/eczema-child-tips
- 미국피부과학회 「In winter, will my child need different eczema skin care?」 — https://www.aad.org/public/diseases/eczema/childhood/itch-relief/winter-care
- 영국 국민보건서비스 「Atopic eczema」 — https://www.nhs.uk/conditions/atopic-eczema/treatment/
- Panther DJ, Jacob SE. J Clin Med. 2015. PMC4470210
