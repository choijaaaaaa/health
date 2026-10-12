# 아기 아구창 (세제로 씻기만 하던 젖병·쪽쪽이 → 젖병 소독기) — 원문 검증 팩트 (2026-10-12)

- 검색어: **아기 아구창**, 보조 **아기 혀 하얀 것**(검색량은 코디네이터가 확인, 이 세션에서는 재측정 안 함).
- 바꿔 쓸 제품: **세제로 씻기만 하던 젖병·쪽쪽이 → 젖병 소독기(스팀)**. 제품은 하나뿐.
  - 카탈로그 `data/_audit/brandconnect_catalog_baby.json` 「젖병 소독기」 chosen = 필립스아벤트 스팀건조 일체형 젖병소독기 SCF293/00(account baby, 링크 저장됨). 이 세션에선 링크 발급·상품 페이지 확인 안 함.
- 인용은 전부 `curl -A "Mozilla/5.0 (Macintosh…)"`나 EuropePMC REST(resultType=core / fullTextXML)로 받은 원문을 텍스트로 바꿔 **공백 정규화 후 문자열 대조**했다. WebFetch 요약은 쓰지 않았다. 원문 사본은 세션 스크래치패드 `ev26/`(임시).

## URL 약칭

| 약칭 | URL | 비고 |
|---|---|---|
| NHS-OT | https://www.nhs.uk/conditions/oral-thrush-in-babies/ | NHS 「Oral thrush (mouth thrush)」 Page last reviewed: 05 June 2023 (`/baby/health/oral-thrush-in-babies/`는 404 → 이 주소로 합쳐짐) |
| NHS-STER | https://www.nhs.uk/baby/breastfeeding-and-bottle-feeding/bottle-feeding/sterilising-baby-bottles/ | NHS 「Sterilising baby bottles」 Page last reviewed: 24 February 2023 |
| AAP-CAND | https://www.healthychildren.org/English/health-issues/conditions/infections/Pages/Thrush-and-Other-Candida-Infections.aspx | 미국소아과학회 「Thrush and Other Candida Infections」 Last Updated 10/21/2020 |
| SCH | https://www.seattlechildrens.org/conditions/a-z/thrush/ | 시애틀아동병원 「Thrush」(Schmitt Pediatric Guidelines) Last Reviewed: 05/01/2025 (⚠️ 아래 충돌 참고) |
| AMC | https://www.amc.seoul.kr/asan/healthinfo/disease/diseaseDetail.do?contentId=31589 | 서울아산병원 질환백과 「칸디다성 구내염(Candidal stomatitis)」 동의어 아구창 (이비인후과, 성인 위주 서술) |
| MANNING | PMID 4004318 · doi:10.1136/adc.60.4.381 | Manning DJ, Coughlin RP, Poskitt EM. 「Candida in mouth or on dummy?」 Arch Dis Child 1985;60(4):381. **초록만 확인**(PMC 스캔 PDF는 봇 차단) |
| MILLAR | PMID 33071208 · PMC7560255 · doi:10.1016/j.idh.2020.09.005 | Millar BC, et al. 「Re-purposing of domestic steam disinfectors within the hospital-at-home setting.」 Infect Dis Health 2021. **전문(fullTextXML) 확인** |
| MATTOS | PMID 11324404 | Mattos-Graner RO, et al. 「Relation of oral yeast infection in Brazilian infants and use of a pacifier.」 ASDC J Dent Child 2001 — 보조(초록) |
| COMINA | PMID 17081147 · doi:10.1111/j.1442-2018.2006.00282.x | Comina E, et al. 「Pacifiers: a microbial reservoir.」 Nurs Health Sci 2006 — 보조(초록) |

버린 출처: Mayo Clinic·CDC(봇 차단 302/403), healthychildren 「Thrush and Breastfeeding」(빈 응답), NHS 「Breast pain and breastfeeding」(아구창 문단 없음), 질병관리청 국가건강정보포털 검색(빈 응답), 대한소아청소년과학회 질환상식(아구창 항목 못 찾음), 서울대병원 N의학정보(아구창 항목 없음).

## ⚠️ 먼저 알아야 할 충돌 — 소독이 "필요 없다"는 기관도 있다

- **시애틀아동병원(SCH)은 반대 입장이다**: "Special washing or boiling of pacifiers or bottle nipples is not needed or helpful." · "Pacifiers and bottle nipples can be washed the usual way with soap and water." · "They do not need to be boiled or sterilized." · 이유: "Yeast is a germ that is found in normal mouths." · "It only causes thrush if the lining of the mouth is irritated or damaged." · "Get better results by reducing nipple time and pacifier time." (단 "Note: follow your doctor's advice if it is different.")
- **반면 NHS·미국소아과학회는 소독·삶기를 말한다**: NHS-OT 예방법 "sterilise dummies regularly" · "sterilise bottles after each use", AAP-CAND "Long-lasting thrush is sometimes related to pacifiers or bottles that have not been properly boiled to remove the fungus."
- 연구는 **연관(관찰)과 실험실 살균 효과**까지만 있다 — 젖병을 소독한 아기가 아구창에 덜 걸렸다/재발이 줄었다는 **무작위 시험은 찾지 못했다**(EuropePMC 검색: pacifier/dummy/teat × candida/thrush, steam/sterilization × pacifier × candida). Stoltz 2024(PMID 38567856, 젖병 세척법과 아구창) 초록도 "there were no statistically significant relationships".
- 그래서 대본은 **"소독하면 아구창이 낫는다/예방된다"고 쓰지 않는다.** 쓰는 건 ① 쪽쪽이에 칸디다가 흔히 붙어 있다(MANNING) ② 미국소아과학회: 오래가는 아구창은 덜 삶은 젖병·쪽쪽이 탓일 수 있다 ③ 세척 ≠ 소독(NHS-STER) ④ 가정용 스팀 소독기가 꼭지 속 칸디다까지 없앴다(MILLAR, 실험실). 제품은 "삶기·소독"을 손쉽게 하는 도구로만 제안한다.
- 코디네이터 판단 메모: 소관 기관 기준으로는 NHS(영국 보건당국)가 소독을 권하므로 주제를 버릴 정도는 아니라고 봤다. 다만 SCH 반대 의견이 있다는 점은 블로그 본문에 한 줄 밝히는 게 안전하다("빨기 시간 줄이기"도 같이).
- 닦으면 지워지나 충돌: NHS-OT·SCH는 "잘 안 지워진다", AMC는 "이 반점은 쉽게 제거할 수 있습니다." — AMC는 성인 위주 서술이라 아기 구별법은 NHS·SCH를 따랐다. 두 쪽 모두 "떼면 피가 날 수 있다"는 일치.

## 대본 문장별 근거

**1. 훅** "아기 아구창, 혀에 낀 하얀 게 우유 찌꺼기인 줄 알고 박박 닦아 내시나요?"
- SCH: "A milk diet often causes a white coated tongue."
- NHS-OT: "A baby with oral thrush will have a white coating on their tongue. It may look like cottage cheese and it cannot be rubbed off easily."

**2. 통념 반박(구별법)** "우유 자국은 닦으면 지워져요. 그런데 볼 안쪽까지 하얀 막이 붙어 잘 안 지워지면 아구창일 수 있어요. 문지르면 피가 날 수 있으니, 닦지 말고 소아과 진료를 받으세요."
- SCH: "Sticks to the mouth. It can't be washed away or wiped off easily like milk curds." · "Coats the inner cheeks or inner lips" · "If a white tongue is the only finding, it's not due to thrush." · "If white patches occur inside the lips or cheeks, call your child's doctor."
- NHS-OT: "it cannot be rubbed off easily." · (성인 사진 설명) "When you wipe off the white patches, they leave red spots that can bleed."
- AMC: "반점을 제거할 때 피가 나기도 합니다."
- 진료: SCH "Thrush, but none of the symptoms above. Reason: may need a prescription medicine to treat it." · NHS-OT "your baby is under 4 months and has signs of oral thrush" (See a GP) — 약국 젤은 "suitable for adults, children and babies over the age of 4 months." 한국은 아기 항진균제가 처방이라 대본은 연령 구분 없이 "소아과 진료".

**3. 원리·치료** "아구창은 입안에 원래 사는 곰팡이균, 칸디다가 불어나서 생겨요. 병원에선 곰팡이 약을 입안에 발라 줘요."
- AAP-CAND: "Candida is a type of yeast, part of the fungus family that normally lives in and on our bodies." · "However, when it overgrows, it can cause infections such as candidiasis."
- AMC: "곰팡이균 칸디다(Candida albicans)에 의해 발생한 구내염은 칸디다성 구내염 또는 아구창이라고 합니다." · "칸디다는 정상적으로 구강 내에 존재하다가"
- AAP-CAND: "Antifungal drugs are used to treat candidiasis." · "The antibiotic nystatin is often prescribed for children with infections such as oral thrush"
- SCH: "Your doctor will probably prescribe an anti-yeast liquid medicine." · "If the thrush isn't getting better, rub the medicine directly on the thrush."
- ⚠️ 용량(SCH 1mL/2mL, AMC 니스타틴 용량)은 대본에 안 쓴다 — 처방대로.

**4. 연구·기관(별도 문단)** "이 균은 쪽쪽이와 젖병 꼭지에도 붙어 살아요. 실제로 아기 100명을 살펴보니, 쪽쪽이 44%에서 칸디다가 나왔어요. 미국소아과학회도 아구창이 오래가면 제대로 삶지 않은 젖병이나 쪽쪽이 탓일 수 있다고 해요."
- MANNING: "Mouth and dummy swabs for Candida spp. were obtained from 100 children under 18 months old admitted with acute medical conditions." · "Forty four per cent of dummies were colonised by Candida spp." · "Children who sucked dummies had clinical thrush and positive mouth swabs for candida more frequently than those who did not."
  - ⚠️ 44%는 **쪽쪽이 기준**(100명 중 쪽쪽이를 쓰는 아이들의 쪽쪽이)이다 — "아기 44%가 아구창" ✗. 대상은 급성 질환으로 입원한 18개월 미만. 1985년 단면 관찰이라 인과 아님 → 대본엔 "더 많이 걸렸다"까지 안 넣고 44%만.
- 보조(대본 미사용): MATTOS "The use of a pacifier was positively associated with the frequency of yeast infection and with the levels of these microorganisms in the mouth." · COMINA "The presence of a biofilm was confirmed on 80% of the pacifier nipples studied." · "The two main genera isolated were Staphylococcus and Candida."
- AAP-CAND: "It is not uncommon for infections to return, however. Long-lasting thrush is sometimes related to pacifiers or bottles that have not been properly boiled to remove the fungus."
- 젖병 꼭지 직접 근거는 AAP의 "bottles"까지다. 젖병 꼭지 칸디다 검출률 수치는 못 찾았다(쪽쪽이 연구만).
- 화면 출처 줄: `출처: Manning 외, Arch Dis Child 1985 (18개월 미만 100명) · 미국소아과학회 「Thrush and Other Candida Infections」`

**5. 바꿔 쓸 제품(제안형)** "세제로 씻는 것만으론 소독이 안 돼요. 그래서 씻은 젖병과 쪽쪽이를 젖병 소독기에 넣어 두면 편해요. 뜨거운 수증기가 꼭지 속까지 들어가거든요. 영국 연구진의 시험에서도 스팀 소독기가 쪽쪽이 꼭지 속 칸디다까지 모두 없앴어요."
- 세척 ≠ 소독: NHS-STER "Putting feeding equipment through the dishwasher will clean it but it does not sterilise it." · 순서 "Rinse all your equipment in clean, cold running water before sterilising."
  - ⚠️ NHS 문장은 **식기세척기**에 대한 것이다. 손 세제 세척도 "세척(clean)" 단계라 같은 논리로 썼지만, 원문이 "세제 세척은 소독이 아니다"를 글자 그대로 말하진 않는다.
- 소독 방법: NHS-STER "It's important to sterilise all your baby's feeding equipment, including bottles and teats, until they're at least 12 months old." · 방법 목록 "steam sterilising" · "Steam sterilising (electric steriliser or microwave)"
- 수증기가 꼭지 속까지 + 칸디다 제거: MILLAR (영국 Belfast) "Steam disinfection eradicated all 62 non-spore-forming Gram-positive, Gram-negative and yeast organisms tested and eradicated all organisms in the inner teat space of contaminated babies' dummies, rendering safe steam disinfection of babies’ dummies." · 꼭지 실험 균 목록 "Initially, five organisms including Candida albicans (clinical), Escherichia coli O157:H7 (NCTC 12900), Listeria monocytogenes (NCTC 10527), Salmonella Nottingham (NCTC 7832) and Staphylococcus aureus (clinical)" · "Thermal penetration of the inner teat space was checked by filling the inner core space with water and inserting thermocouples"
  - ⚠️ 실험실 시험(균을 일부러 넣은 쪽쪽이, 가정용 스팀 소독기 한 기종)이다. 아기의 아구창이 줄었다는 결과가 아니다 → "아구창이 낫는다" ✗, "칸디다까지 없앴다"까지만.

**6. 고르는 기준** "고를 땐 스팀 방식인지, 젖병과 쪽쪽이가 같이 들어가는지 보세요. 물은 설명서만큼 채우고요. 모자라면 온도가 덜 올라가요."
- 스팀: MILLAR(위) + NHS-STER "steam sterilising".
- 같이 들어가는지: NHS-OT가 쪽쪽이·젖병 둘 다 소독을 말함("sterilise dummies regularly" · "sterilise bottles after each use") → 한 기계로 둘 다 들어가는 크기면 매번 하기 쉽다(상식 수준 기준, 수치 없음).
- 물 양: MILLAR "Additional notable temperature reductions occurred with device underfilling with suboptimal water volumes." · "There are risks to patient safety if device is not operated correctly (e.g. underfilling with water)." · NHS-STER "It's important to follow the manufacturer's instructions, as there are several different types of sterilisers."
- 건조 기능: 원문 근거 약함(NHS-STER "It's best to leave bottles and teats in the steriliser or pan until you need them."만) → 대본 기준에서 뺐다. 상세 페이지 설명용으로만.

**7. 병원 신호** "아기가 젖을 덜 먹거나, 입에서 피가 나거나, 열이 나면 하루 안에 진료받으세요."
- SCH "Contact Doctor Within 24 Hours": "Fever occurs" · "Bleeding in the mouth" · "Drinking less than normal"
- NHS-OT: "Babies with oral thrush may not want to feed."
- 대본 미사용(블로그용): SCH 즉시 진료 "Dehydration suspected. No urine in more than 8 hours, dark urine, very dry mouth and no tears." · "Age less than 1 month old and looks or acts abnormal in any way" · 기저귀 발진 SCH "If there's a bad diaper rash, it can also be due to yeast." · AAP-CAND "Candidiasis can make a diaper rash worse" · 엄마 젖꼭지 SCH "If the mother's nipples are red and sore, it might be a yeast infection." · 경과 SCH "With treatment, thrush usually clears up in 4 to 5 days." · AAP-CAND "Once treatment starts, most candidiasis infections get better within about 2 weeks."

## 목숨·안전 출처 줄(화면) 제안

- 4문단(연구·기관): `출처: Manning 외, Arch Dis Child 1985 · 미국소아과학회 「Thrush and Other Candida Infections」`
- 5문단(스팀 시험): `출처: Millar 외, Infect Dis Health 2021 · NHS 「Sterilising baby bottles」`
- 7문단(병원 신호): `출처: 시애틀아동병원 「Thrush」 · NHS 「Oral thrush」`
- 블로그·설명란 출처 목록: 위 전부 + 서울아산병원 「칸디다성 구내염」, Mattos-Graner 2001, Comina 2006. 블로그엔 SCH의 반대 의견("소독 불필요, 빠는 시간 줄이기")도 한 줄.

## 제목·태그·카드

- 유튜브 제목(제안): **아기 아구창, 혀 하얀 것 우유 자국과 구별하는 법, 젖병 소독기**
- 해시태그: `#아기아구창 #아기혀하얀것 #아구창 #젖병소독기 #육아만사전` · 업로드 태그에 "젖병 소독기"(띄어 쓴 것)도.
- 썸네일 단어(증상): "아기 혀 하얀 것"

카드 items 순서 = 대본 순서
1. 닦아도 안 지워지면 아구창
2. 입안 곰팡이균, 칸디다
3. 쪽쪽이 44%에서 칸디다
4. 씻기와 소독은 달라요
5. 고를 땐 스팀·크기·물 양
6. 하루 안에 진료받을 때
