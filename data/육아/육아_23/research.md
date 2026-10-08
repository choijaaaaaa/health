# 아기 코막힘 (어른 감기약·약 든 코 스프레이 → 식염수 + 콧물흡입기) — 원문 검증 팩트 (2026-10-09)

- 검색어: **아기 코막힘**(검색량은 코디네이터가 확인, 이 세션에서는 재측정 안 함).
- 바꿔 쓸 제품: **감기약·약 든 코 스프레이 → 아기 콧물흡입기**(식염수 몇 방울과 같이). 제품은 하나뿐 — 식염수는 사용법이지 연동 품목이 아님.
- 인용은 전부 `curl -A "Mozilla/5.0 (Macintosh…)"`나 EuropePMC REST(resultType=core)로 받은 원문을 텍스트로 바꿔 **문자열 대조 50건 전부 통과**(`verify.py`). WebFetch 요약은 쓰지 않았다. 원문 사본은 세션 스크래치패드 `ev23/`(임시).

## URL 약칭

| 약칭 | URL | 비고 |
|---|---|---|
| FDA | https://www.fda.gov/drugs/special-features/use-caution-when-giving-cough-and-cold-products-kids | 미국 FDA 「Use Caution When Giving Cough and Cold Products to Kids」, Content current as of 02/08/2018. fda.gov가 봇 차단(Akamai 302)이라 **Wayback 2026-01-12 사본**(web.archive.org/web/20260112151134/…)으로 받음 |
| MFDS25 | https://nedrug.mfds.go.kr/eBook/catImage/182/25.pdf | 식약처 「의약품 안전사용 매뉴얼 ㉕ 어린이 감기약 올바로 먹이기」 PDF |
| KR2016 | https://www.korea.kr/news/policyNewsView.do?newsId=148807875 | 정책브리핑 「"만 2세 미만 영유아 종합감기약 먹이지 마세요"」 식약처 '감기약 안전사용 길라잡이' 2016-01-07 |
| KPS | https://www.pediatrics.or.kr/bbs/index.html?code=disease_info&category=A&number=8966&mode=view | 대한소아청소년과학회 질환상식 「감기」 |
| KDCA | https://health.kdca.go.kr/healthinfo/biz/health/gnrlzHealthInfo/gnrlzHealthInfo/gnrlzHealthInfoView.do?cntnts_sn=5423 | 질병관리청 국가건강정보포털 「감기」, 업데이트 2026-05-12 (⚠️ 아래 충돌 참고) |
| AAP-REM | https://www.healthychildren.org/English/health-issues/conditions/chest-lungs/Pages/Coughs-and-Colds-Medicines-or-Home-Remedies.aspx | 미국소아과학회 「Coughs and Colds: Medicines or Home Remedies?」 Last Updated 12/2/2022 |
| AAP-COLD | https://www.healthychildren.org/English/health-issues/conditions/ear-nose-throat/Pages/Children-and-Colds.aspx | 미국소아과학회 「Children and Colds」 Last Updated 1/27/2025 |
| NHS-CH | https://www.nhs.uk/baby/health/colds-coughs-and-ear-infections-in-children/ | NHS 「Colds, coughs and ear infections in children」 reviewed 21 May 2025 |
| NHS-BR | https://www.nhs.uk/conditions/bronchiolitis/ | NHS 「Bronchiolitis」 reviewed 19 February 2026 |
| NHS-FEV | https://www.nhs.uk/conditions/fever-in-children/ | NHS 「Fever in children」 reviewed 03 January 2024 |
| SCH | https://www.seattlechildrens.org/conditions/a-z/colds/ | 시애틀아동병원 「Colds」(Schmitt Pediatric Guidelines) Last Reviewed 05/06/2025 |
| SCH-PE | https://www.seattlechildrens.org/globalassets/documents/for-patients-and-families/pfe/pe1732.pdf | 시애틀아동병원 환자교육지 PE1732 「How to Suction Your Baby's Nose」 5/25 |
| NCH | https://www.nationwidechildrens.org/family-resources-education/health-wellness-and-safety-resources/helping-hands/suctioning-the-nose-with-a-bulb-syringe | 네이션와이드아동병원 「Suctioning the Nose with a Bulb Syringe」 HH-II-24, revised 2022 |
| NCH-SPRAY | https://www.nationwidechildrens.org/family-resources-education/family-resources-library/take-care-with-nasal-decongestant-sprays | 같은 병원 「Take Care with Nasal Decongestant Sprays」(AAP 권고 인용) |
| CC | https://health.clevelandclinic.org/nasal-aspirator-and-phlegm-in-your-babys-throat | 클리블랜드클리닉 소아과 Noah Schwartz 인터뷰 — 고르는 기준 보조 출처 |

버린 출처: fda.gov 직접 접근(봇 차단 → Wayback), healthychildren.org Nasal-Congestion·Caring-for-Your-Child's-Cold(404), Mayo Clinic·CHOP(403), Köksal 2016 전문 PDF(TÜBİTAK Cloudflare 챌린지 → 초록만 사용).

## ⚠️ 먼저 알아야 할 충돌 — 질병관리청은 식염수 "세척"에 근거 불명확

- KDCA 「감기」: "식염수로 코를 세척하는 것은 효과가 없거나 근거가 불명확하며" — 연령 구분 없는 일반(주로 성인) 감기 페이지, '세척(irrigation)' 이야기.
- 반면 영아 대상 기관 문서(AAP·FDA·NHS·시애틀·네이션와이드)는 전부 **식염수 몇 방울 + 흡입**을 권한다. 근거 수준은 아래 연구처럼 약하다(Cochrane 2015 "too small … high risk of bias").
- 그래서 대본은 **질병관리청을 식염수 근거로 끌어오지 않는다.** 기관명은 감기약 경고에만(식약처·미국 식품의약국) 쓰고, 식염수는 영아 대상 무작위 연구 한 줄 + 원리로 받친다. "식염수가 감기를 낫게 한다"는 말은 쓰지 않고 "굳은 콧물이 풀려 쉽게 빠져요"(기전)까지만.

## 대본 문장별 근거

**1. 훅** "아기 코막힘, 젖을 빨다 자꾸 떼고 우는 아기에게 감기약부터 찾으시나요?" — 공백 제외 31자. 상황 묘사.
- AAP-REM: "Infants with a common cold may feed more slowly or not feel like eating because they are having trouble breathing."

**2. 통념 반박(감기약)** "그런데 두 살 전 아기에게 약국 감기약은 오히려 위험해요. 미국 식품의약국에는 경련과 사망까지 보고됐고, 식약처도 두 살 전엔 진료 없이 먹이지 말라고 해요. 약이 든 코 스프레이도 마찬가지예요."
- FDA: "Children under 2 years of age should not be given any kind of cough and cold product that contains a decongestant or antihistamine because serious and possibly life-threatening side effects could occur. Reported side effects of these products included convulsions, rapid heart rates and death."
- FDA: "Children should not be given medicines that are packaged and made for adults."
- MFDS25: "2세 미만의 영·유아가 감기에 걸린 경우에는 반드시 의사의 진료를 받아야 하며, 꼭 필요한 경우가 아니면 일반의약품으로 구입한 감기약(비충혈제거제, 거담제, 항히스타민제, 기침약)은 복용시키지 않도록 합니다."
- KR2016(식약처): "특히, 만 2세 미만의 영·유아에게는 콧물, 재치기 등 증상완화를 위해 종합감기약을 임의로 투여해서는 안되며 꼭 필요한 경우 의사의 진료를 받아야 한다."
- KPS: "진해제, 거담제, 항히스타민제가 감기에 효과가 있다는 증거는 없으며, 소아에게는 오히려 해가 될 수도 있다."
- 보강: AAP-REM "Under age 4: Over-the-counter cough and cold medicine is not recommended for babies and young children." · NHS-CH "Children under 6 should not have over-the-counter cough and cold remedies, including decongestants , unless advised to by a GP or pharmacist."
- 코 스프레이: NCH-SPRAY(AAP 권고 인용) "Never use nonprescription nose drops that contain any medicine." + NHS-CH decongestants 문장.
- ⚠️ "진료 없이 먹이지 말라"는 식약처 문구 범위(진료 받고 처방받으면 먹일 수 있음)를 넘지 않게 썼다. "절대 금지"로 바꾸지 말 것. 해열제(아세트아미노펜·이부프로펜)는 이 문장 대상이 아니다.

**3. 연구 수치(별도 문단)** "실제로 두 살 안 된 감기 아기 109명을 나눠 보니, 코에 식염수를 넣어 준 아기들이 코가 덜 막히고 더 잘 먹고 더 잘 잤어요."
- **Köksal T, Çizmeci MN, Bozkaya D, et al. Turk J Med Sci 2016;46(4):1004-1013. PMID 27513397. doi:10.3906/sag-1507-18**
  - "The effectiveness of isotonic and hypertonic saline solutions used to open the nasal passage and improve clinical symptoms was compared in children under 2 years of age admitted with the common cold."
  - "The study was performed as a randomized, prospective, and double-blind study. The study included 109 children."
  - "The mean age of the patients was 9.0 ± 3.9 months"
  - "However, a significant difference was found between the control group and Groups A and B (P < 0.05)."
  - "Relief was seen in nasal congestion, weakness, sleep quality, and nutrition with the use of both saline and seawater in children with the common cold."
- ⚠️ **근거가 약하다는 걸 알고 쓴다**: 초록만 확인(전문은 Cloudflare 차단), 효과 크기 숫자가 초록에 없음, 설계가 특이함("Seventy-four patients received nasal drops from package A (seawater) in single days and from package B (physiological saline) in double days." — 식염수군 74명 vs 무처치 대조군 약 35명), 잘 먹음·잘 잠은 결론 문장에만 있음. 그래서 대본은 **퍼센트·배수를 지어내지 않고** 초록 결론 범위(코막힘·먹기·잠)만 옮겼다. 109명은 대조군 포함 전체 인원이라 "109명을 나눠 보니"로 썼다("109명이 좋아졌다" ✗).
- 이 연구는 **식염수 방울** 연구다. 흡입기 자체의 효과 수치가 아니므로 "흡입기를 쓴 아기가 ~"로 바꾸지 말 것.
- 화면 출처 줄: `출처: Köksal 외, Turk J Med Sci 2016 (2세 미만 109명 무작위 시험)`

**4. 원리** "아기는 젖을 빨면서 코로 숨을 쉬어요. 그래서 코가 막히면 숨을 쉬려고 젖을 놓아야 해요. 게다가 아직 코를 풀 줄 몰라서, 말라붙은 콧물을 스스로 빼지 못해요."
- Di Cicco M, et al. Pediatr Pulmonol 2021 (PMID 33179415): "The anatomic peculiarities of the upper airway make infants preferential nasal breathers between 2 and 6 months of life."
- SCH: "Also, babies can't nurse or drink from a bottle unless the nose is open."
- NCH: "Suctioning mucus out of the nose makes it easier for them to breathe, suck, and eat."
- SCH: "Teach your child how to blow the nose at age 2 or 3. For younger children, gently suction the nose with a suction bulb."
- SCH: "Reason for nose drops: suction or blowing alone can't remove dried or sticky mucus."
- ⚠️ "아기는 코로만 숨 쉰다(obligate)"는 쓰지 않는다 — 원문은 "preferential(주로)"이다. 대본은 "젖을 빨면서 코로 숨을 쉬어요"까지만.

**5. 해결책·고르는 기준** "그러니 감기약 대신 콧물흡입기로 빼 주는 게 먼저예요. 젖 먹이기 전에 식염수를 콧구멍에 몇 방울 넣고 잠깐 기다리면, 굳은 콧물이 풀려 쉽게 빠져요. 다만 하루 4번 넘게 빼면 오히려 코 안이 자극받아요. 고를 땐 끝이 콧구멍 입구에서 멈추는 구조인지, 분해해서 씻을 수 있는지를 보세요. 아기 콧구멍은 짧아서 끝이 깊이 들어가면 코 안이 다치거든요."
- 흡입 권고: FDA "Nasal suctioning with a bulb syringe -- with or without saline nose drops -- works very well for infants less than a year old." · AAP-REM "Try to suction baby's nose before attempting to breast or bottle-feed."
- 수유 전: AAP-REM "For infants who bottle-feed or breastfeed, use nose drops before feedings." · NCH "If done after feeding, suctioning may cause vomiting (throwing up)."
- 식염수 먼저: AAP-REM "Use salt water (saline) nose spray or drops to loosen up dried mucus." · NHS-CH "Saline nose drops can help loosen dried snot and relieve a stuffy nose." · SCH-PE "Let the saline remain in the nose for 1 to 2 minutes before suctioning."
  - 방울 수는 출처마다 다름(SCH 1살 미만 "use 1 drop" / SCH-PE·AAP 2~3방울 / NCH 3~4방울) → 대본은 숫자 대신 "몇 방울".
- 하루 4번: NCH "Limit suctioning to no more than 4 times each day to avoid irritating the nose." · SCH "Limit: if under 1 year old, no more than 4 times per day or before every feeding."
  - ⚠️ 원문은 "irritating(자극)"이다. 브리프의 "점막이 붓는다"는 확인한 원문에 없어 쓰지 않았다 → "코 안이 자극받아요".
- 고르는 기준(깊이 막는 끝·분해 세척): CC "It's easy to put the tip in too far. Babies have very short nostrils, and sticking the tip of the bulb in too far can damage nasal tissues." · CC "Safe. There's a guard that keeps you from pushing the tip too far into your baby's nostril." · CC "Cleanable. You can take them apart and clean them." · CC "It's pretty much impossible to clean the inside of a suctioning bulb unless you find one that unscrews," · SCH-PE "Put no more than ½ inch of the aspirator tip up the nose."
- 대본에 안 넣은 참고(블로그용): 고무 스포이트형보다 입으로 빠는 관 흡입기가 부작용이 적었다 — Schwarz WW, et al. Pediatr Emerg Care 2022 (PMID 35100758) "More adverse events were seen with the bulb compared with the nasal-oral aspirator (bulb vs nasal-oral, 50.0% vs 17.5%; P < 0.01)." 전동 vs 스포이트 — Schuh S, et al. JAMA Netw Open 2023 (PMID 37856126, 1~11개월 모세기관지염 367명) "Compared with minimal suctioning, enhanced suctioning after ED discharge with bronchiolitis did not alter the disease course because there were no group differences in revisits or feeding and sleeping adequacy." → **전동이 병을 더 빨리 낫게 한다고 쓰지 말 것.** 다만 스포이트 쪽 부모가 다른 흡입기를 따로 사서 쓴 비율이 높았다("33 of 184 … (17.9%) … vs 11 of 183 … (6.0%)").

**6. 병원 신호** "코를 빼 준 뒤에도 숨이 빠르거나 갈비뼈 사이가 쑥쑥 들어가거나 입술이 파래지면 바로 119에 전화하세요. 생후 3개월 전이라면 열이 38도 이상일 때 진료부터 받으세요."
- SCH: "Trouble breathing, but not severe. Exception: gone after cleaning out the nose." → "코를 빼 준 뒤에도"의 근거(코만 막혀 숨이 찬 건 빼 주면 풀린다).
- AAP-COLD: "the skin between and around the ribs and breastbone sucks in with each breath (retractions) as the child inhales; or your child is breathing fast or having any trouble breathing. The lips or nails turn blue."
- NHS-BR: "Call 999 if: your child is having difficulty breathing – you may notice grunting noises, their tummy sucking under their ribs or they may be breathing quickly" · "your child's skin, tongue or lips are blue or grey"
- NHS-FEV: "is under 3 months old and has a temperature of 38C or higher" (Call 111 urgent advice) · AAP-COLD "If a child is 3 months or younger , call the pediatrician at the first sign of illness."

## 목숨·안전 출처 줄(화면) 제안

- 2문단(감기약 사망·경련): `출처: 미국 FDA 「Use Caution When Giving Cough and Cold Products to Kids」 · 식약처 「의약품 안전사용 매뉴얼 ㉕ 어린이 감기약 올바로 먹이기」`
- 6문단(호흡곤란·발열): `출처: 미국소아과학회 「Children and Colds」 · NHS 「Bronchiolitis」 「Fever in children」`
- 3문단(연구): `출처: Köksal 외, Turk J Med Sci 2016 (2세 미만 109명 무작위 시험)`
- 블로그·설명란 출처 목록에는 위 전부 + 시애틀아동병원 「Colds」, 네이션와이드아동병원 「Suctioning the Nose with a Bulb Syringe」, Cochrane 2015(King, PMID 25892369).

## 브랜드커넥트 후보 메모(코디네이터 선택용, 대본엔 브랜드 없음)

고르는 기준 = ① 끝이 콧구멍 입구에서 멈추는 구조(깊이 가드·둥근 실리콘 팁) ② 분해 세척 가능(투명하면 덤). 전동 여부는 기준이 아님(Schuh 2023).
- **수동식 노시부류(닥터웰스 노시부 호환 팁)**: 입으로 빠는 관 방식이면 CC가 꼽은 장점(분해 세척·투명·가드·세기 조절)과 Schwarz 2022 부작용 적음에 가장 잘 맞음. 상세 페이지에서 팁이 깊이 막는 원뿔형인지, 필터 교체 구조인지 확인 필요.
- **예꼬맘 노스클린 전동(NS1)**: 카탈로그 `data/_audit/brandconnect_catalog_baby.json` 「콧물흡입기」 chosen(리뷰 4,542, 평점 4.47) — 육아_7에서 이미 연동. 팁 모양·분해 세척 여부를 상세 페이지에서 확인. 전동이 더 잘 낫게 한다는 근거는 없음.
- **베베노 무선 전동 의료용**: 의료기기 허가 표시는 장점이나 기준 ①②를 상세 페이지로 확인해야 함.
- 이 세션에선 상품 페이지를 직접 열어 보지 않았다(로그인 리다이렉트 이력) — 고르는 기준 대조는 코디네이터 단계에서.

## 버린 근거

- Cochrane 2015 King(PMID 25892369): 어린이 3개 연구 포함이나 대부분 6~10세(Slapak), "too small … high risk of bias", 효과(4점 척도 −0.33)가 임상적으로 작다 → 대본 수치로 부적합, 블로그 맥락용.
- Cabaillot 2020 Paediatr Respir Rev(PMID 32312677): 3개월~12세 4개 시험, SMD −0.29 — 표준화 평균차라 말로 옮길 수 없음.
- Chen 2026 Eur Arch Otorhinolaryngol(PMID 42747526): 3~48개월 220명, 10일째 회복 75.3% vs 58.5% — 구리·망간 넣은 고장성 바닷물 스프레이(특정 제품), 공개 시험, 잠은 차이 없음("Sleep quality and secondary infection rates were comparable between groups.") → 일반 식염수 방울 근거로 옮기면 과장.
- Schreiber 2016 Acta Paediatr(PMID 26607495): 모세기관지염 영아 산소포화도 95% vs 93% — 감기 코막힘이 아니고 숫자가 시청자에게 안 들어옴.
- Schuh 2023 JAMA Netw Open(PMID 37856126): 흡입 방식 비교(전동 vs 스포이트)로 먹기·잠 차이 없음 → 흡입 효과 수치가 아님(고르는 기준 참고로만).
- Ringer 2020 Respir Care(PMID 32071129): 입원 모세기관지염 16명 생리 지표 — 가정 사용과 무관.
- KDCA 「감기」 식염수 문장: 위 충돌 절 참고 — 대본 근거로 안 씀.
