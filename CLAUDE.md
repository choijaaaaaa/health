# health-shorts

건강 정보를 **카드뉴스(네이버 블로그) + 숏폼 영상(네이버 클립)**으로 만드는 파이프라인. 채널명은
「건강만사전」. 이 파일은 **지금 지켜야 할 규칙만** 담는다 — 결정 경위·사고 기록·옛 규칙 전문은
`CLAUDE_ARCHIVE.md` 맨 끝 "2026-09-24 정리 직전 CLAUDE.md 전문"에 있다.

## 문서 지도 — 이 셋이 정본이다

| 문서 | 다루는 것 |
|---|---|
| `XRAY_FORMAT.md` | 영상 화면 구성·시간표·조립 전후 검사(견본 `소화_14`). 6절은 육아 트랙 |
| `PIPELINE_METHOD.md` | 원고를 어떻게 쓰는가 — 검색어·공공데이터·구조·클립 색인 |
| 이 파일 | 채널 운영 규칙·파이프라인 순서·도구 사용법 |

영상·원고 규칙이 이 파일과 위 두 문서에서 어긋나면 **위 두 문서가 이긴다**(견본과 함께 갱신된다).
육아 트랙·댕냥사전도 같은 문서를 따른다.

## 🚨 완료 = 완성본을 재고 눈으로 본 뒤다

`scripts/preflight_xray.py`(조립 전 스펙) 0건 → `scripts/xray_build.py`(조립 후 deploy·대시보드·미션컨트롤까지
자동) → `scripts/verify_output.py`(완성된 mp4) 0건 → 도입부·칸 구간·칠판 구간 **프레임을 직접 확인**.
검사 통과는 영상이 맞다는 뜻이 아니다 — 2026-09-24 하루에 "0건 통과 = 완료"로 보고했다가 사용자가 결함을 다섯 번 먼저 찾았다.

---

## 채널·배포

- **배포처는 네이버 블로그(카드뉴스)와 네이버 클립(영상) 둘뿐이다.** 유튜브·인스타·틱톡·페북·쓰레드는
  안 올린다. `_ALLOWED_PLATFORMS`(`lib/dashboard.py`·`lib/mission_control_sync.py`)가 이 둘만 띄운다.
- **채널명 「건강만사전」** — 엔딩 카드(`video_assembler.BRAND_NAME`)·카드 CTA·해시태그 `#건강만사전`(태그 줄 맨 앞)·
  대시보드 제목. **내부 식별자는 안 바꾼다**(폴더명 `health-shorts`, R2 프리픽스 `health-shorts/card_news/`,
  DB `source_project`) — 다른 프로젝트가 이 문자열로 경로를 맞춘다.
- 상품 링크는 **네이버 브랜드커넥트만** 쓴다(쿠팡 기능은 제거 상태 유지).
- **업로드용 모음**: `../ai-video-network/deploy/health-shorts/<topic>/`에 `shorts.mp4` + `card_news/*.jpg`.
  `scripts/stage_for_deploy.py`(`xray_build`가 끝에서 자동으로 돌린다, 손으로 돌릴 땐 `--dry-run` 가능),
  `scripts/cleanup_deploy.py --commit`(두 플랫폼 다 체크된 topic 사본만 지운다).
- **나간 건 지운다** — 카드는 R2가 서빙하므로 로컬은 사본이다. `scripts/prune_published.py --commit`.
  🚨 `posting_log`는 **절대 지우지 않는다**(지우면 "안 올린 topic"으로 되살아나 다시 만든다).
  `data/<topic>/` 스펙 JSON은 남긴다. **영상은 카드뉴스가 블로그에 아직 안 나간 topic만** 만든다.

## 인프라

- **DB는 Cloudflare D1**이다(2026-09-13 Supabase 폐기). 환경변수 이름은 옛 그대로 `SUPABASE_URL`·
  `SUPABASE_SERVICE_ROLE_KEY`지만 PostgREST 문법을 D1 SQL로 번역하는 Worker
  (`d1-postgrest.choijaaaaaa.workers.dev`)를 가리킨다. 소스 `~/Desktop/project/infra/d1-postgrest/`.
  `BLOG_NETWORK_SUPABASE_*`도 같은 Worker다.
- **이미지는 Cloudflare R2**(`https://img.vernhaven.com/health-shorts/card_news/`). `lib/card_news.py`가 렌더 직후
  `_sync_to_r2()`로 자동 업로드한다 — stderr에 경고가 뜨면 그 topic은 배포본에서 이미지가 안 뜬다.
  키: `health-shorts/card_news/<topic>/<파일>`(ko·루트 공용), 다른 언어는 `<topic>/<lang>/`. URL 정본은
  `lib/dashboard.py._card_news_r2_base()` — 키를 바꾸려면 이 함수와 `_sync_to_r2()`를 **같이** 고친다.
  `_sync_to_r2()`는 저장소 `output/` 밖 렌더를 건너뛴다(테스트 픽스처가 실버킷에 올라간 사고 방지).
- **배포는 Vercel**(`health-shorts.vercel.app`, 자동배포는 켜둔다). `middleware.js`가 Basic Auth, `/api/*.js`가
  service role 키로 DB 쓰기를 전담한다 — 브라우저 JS는 읽기만 한다. 🚨 **GitHub Pages는 켜지 말 것**
  (Basic Auth를 우회하고 `/api/*`가 404라 쓰기가 조용히 실패한다).
- 카드 이미지는 git에 추적되지만 Vercel 배포에선 빠진다(`.vercelignore`). mp4·`assets_library/{real,motion,music}/`는
  git에 안 올린다.
- 동기화가 안 먹으면 **먼저 `.env` 값이 비었는지** 본다 — 빈 값이면 에러 없이 아무것도 안 하고 끝난다:
  `.venv/bin/python3 -c "from dotenv import dotenv_values; print([k for k,v in dotenv_values('.env').items() if not v])"`.
  `MISSION_CONTROL_INGEST_URL`은 `localhost:3011`이라 mission-control dev 서버가 떠 있을 때만 기록된다.

## 트랙과 폴더

- 기본(건강) topic은 `data/<topic>/`·`output/<topic>/`에 평평하게 둔다.
- **육아 트랙**만 한 단계 접는다: `data/육아/<topic>/`·`output/육아/<topic>/`·`assets_library/xray/작업_육아/`·
  `stills/baby/`. 🚨 **topic 이름은 `육아_1`로 평평하다 — 접히는 건 경로뿐**이다. 이 저장소에서 topic 안의
  `/`는 **언어**를 뜻해서(`가슴쓰림_1/en`), `육아/육아_1`로 부르면 언어 코드로 읽혀 조용히 깨진다.
  경로는 반드시 `lib/tracks.py`(`data_dir`·`output_dir`·`iter_topic_dirs`·`glob_topic_files`)로 푼다.
  `tests/test_tracks.py`가 이 규약을 막는다.
- 한국어 캡션 파일은 topic마다 **한 곳에만** 있다 — 옛 topic은 `data/<topic>/platform_captions.json`,
  언어 폴더가 생긴 topic은 `data/<topic>/ko/`. flat만 보고 "없다"고 판단하지 말 것(`test_korean_caption_lives_in_one_place`).

---

## 새 topic 파이프라인 — 이 순서로

"다음 topic 해줘"류 요청은 **소재 선정부터 커밋·푸시까지 승인 없이 끝까지** 간다. 품질·안전 체크리스트는
그대로 지킨다(생략되는 건 사용자 승인 절차뿐). 정기 스케줄(cron)로 돌리라는 뜻은 아니다.

1. **세션 락** `.venv/bin/python3 lib/session_lock.py check <topic>` → `acquire`, 끝나면 `release`.
2. **소재·검색어** — 아래 "소재와 검색어" 절. 번호는 `ls data/ | grep "^<카테고리>_"`로 확인.
3. **원고**(`narration.txt`) — 아래 "원고 규칙" 절 + `PIPELINE_METHOD.md`.
4. **품목** — 브랜드커넥트 스윕 결과를 보고 고른다(아래 절).
5. **카드 스펙**(`card_news_spec.json`)·**캡션**(`platform_captions.json`) — 아래 절.
6. **검사** — `.venv/bin/python3 -m lib.content_review <topic>` 0건 + `MANUAL_REVIEW_CHECKLIST`(파일 상단) 직접
   재검토. 🚨 **TTS 전에** 끝낸다(글자수 과금). 폴더가 없으면 `content_review`가 실패로 답한다.
7. **TTS** — 아래 "보이스" 절.
8. **카드 렌더** `.venv/bin/python3 lib/card_news.py <spec> assets_library/illust <out>/card_news <topic> kor`
   (🚨 lang은 `ko`가 아니라 **`kor`** — `ko`면 한글이 전부 깨진다).
9. **영상** — `data/<topic>/xray.json` 시간표 → `preflight_xray.py <topic>` 0건 → `xray_build.py <topic>` →
   `verify_output.py <topic>` 0건 → 프레임 확인. 규칙은 `XRAY_FORMAT.md`. 없는 클립이 있으면 여기서 멈춘다(아래 "영상" 절).
10. **대시보드·동기화** — `xray_build`가 끝에서 돌린다. 영상 없이 카드만 낼 땐 손으로:
    `.venv/bin/python3 lib/dashboard.py <data>/platform_captions.json <out>/card_news <out>/shorts.mp4 <out>/dashboard.html`
    (🚨 첫 인자는 **`platform_captions.json`** — `card_news_spec.json`을 넘기면 업로드 플랫폼 섹션이 통째로 사라진다)
    → `.venv/bin/python3 -m lib.mission_control_sync --commit`.
11. **커밋·푸시**. 카드뉴스·캡션·영상은 먼저 끝나는 대로 바로 커밋한다.

**완료 기준**: 네이버 블로그 트랙(카드+캡션) + 영상 트랙(TTS+영상, 위 "완료" 절까지) — 한국어 하나.
blog_seo 서브트랙이 붙은 topic은 9개 언어 전부(아래 절).

### DB `topics` — 목록에 뜨는 자리

`index.html` 목록은 DB `topics`만 읽는다. `mission_control_sync --commit`이 `output/topics.json`의 업로드 전 topic을
그대로 upsert한다. 직접 넣어야 할 때(리네임 등)는 `topics.json` 행을 `topics?on_conflict=topic`에
`Prefer: resolution=merge-duplicates`로 POST한다(예제 코드는 아카이브).

- 🚨 **`updated_at`을 payload에 넣지 말 것** — 목록 정렬이 "처음 들어간 시각"으로 폴백한다. 넣으면 옛 topic이 맨 위로 튄다.
- **리네임 뒤엔** 필터 없이 `topics.json` 전체로 돌린다 — `url`·`thumbnail`에 옛 폴더명이 박혀 있다.
- 파이썬을 stdin으로 돌릴 땐 `load_dotenv("<저장소 절대경로>/.env")`로 경로를 준다(`find_dotenv`가 실패한다).

---

## 소재와 검색어

- **제목은 검색어부터, 검색량으로 고른다.** 의미는 자동완성이, 숫자는 검색광고 API가 준다:
  `-m lib.naver_keywords "<검색어>"` / `-m lib.naver_searchad "후보1" "후보2"`(연관 키워드가 섞여 나오니
  `data/_audit/naver_search_volume.json`에서 물어본 키워드 값을 확인) / `-m lib.topic_search_rank --topics <topic>`.
- 고른 검색어는 `card_news_spec.json`의 `search_keyword`에 적고 제목 첫 줄·네이버 캡션 첫 줄을 그 말로 시작한다
  (`check_search_keyword()`).
- `~부작용` 복합어는 검색량이 항상 0이다(광고 불가 키워드) — 수요 없음이 아니다. 자동완성으로 판단한다.
- 검색량이 낮으면 **표기를 먼저 의심**한다(오표기·학술어·신조어 — 반월**상**연골파열, 헬리코박터**균**, 월요병).
- **자동완성 상위가 곧 원고의 항목**이어야 한다(`PIPELINE_METHOD.md` 1절).
- 트렌드 소재는 "화제"라는 기사를 믿지 말고 회고형 기사인지·검색량 추이를 교차 확인한다.
  `-m lib.trend_check --show|--daily|--related <키워드>|--hidoc`(하이닥은 그 사이트 조회수 랭킹일 뿐이다).
- **topic 폴더명** = 카테고리 + `_N`(서술형 접미사·품목명 금지). 카테고리는 **느끼는 부위** 기준:
  눈·입·귀·코·손발·머리·냄새·피부·소화·순환·근골격·수면·비뇨기·어지럼증·혈당·대사·여성. 계절 자체가 원인이면
  계절질환, 어디에도 안 맞으면 단독(피로·고령·미세먼지). 육아는 `육아_`.

## 원고 규칙 (`narration.txt`)

본보기는 `data/소화_14/narration.txt`. 구조와 근거는 `PIPELINE_METHOD.md` 1~3·9·13절.

- **구조**: 검색어로 시작해 증상을 구체적으로 묘사하고 질문으로 끝나는 훅(공백 제외 40자 가까이) →
  훅 직후 **독립 문장으로 통념 반박**(독자가 실제로 하는 행동을 뒤집는다) → **항목 이름을 먼저 깐다**
  ("~의 갈림길은 A, B, C예요") → 각 항목은 **행동 → 원인 → 아이템** → "오늘부터는 …" 결론 →
  병원에 가야 할 신호 한 줄. 항목 사이엔 "먼저·두 번째는·마지막은" 같은 연결어(나열할 때만).
- ⚠️ **"3가지"는 틀이 아니다(2026-09-24)** — 항목 수는 소재가 정한다(최대 3개). 칸을 채우려고 제목·훅의 증상과
  **상관없는 항목을 끌어오지 않는다**(대사_14: 구토 영상에 탈모·췌장). 하나를 깊게 풀어야 하면 하나로 가고, 칸은
  **기전의 층위**로 나눈다(위 → 뇌 → 언제 몰리나). 임상 수치는 숫자만 던지지 말고 언제·얼마나·누구에게·그래서
  뭘 예상하나까지 푼다. 제목·상단 띠·썸네일·표지도 같은 한 증상을 가리킨다. 상세 `XRAY_FORMAT.md` 2절.
  `content_review --hook-pattern`(훅 문형 랜덤)과 어긋나면 **이 견본 구조가 이긴다**(2026-09-24).
- **6가지 필수**: 실행 가능한 수치 3개 이상(단위까지) · 통념 반박 1개 · 기전 한 줄 · 해결책은
  얼마나·언제·어떻게 중 2개 이상 · 병원 신호 1줄 · 기관명을 문장 안에. `card_news_spec.json`에
  `"content_v2": true`가 있어야 `check_content_depth()`가 검사한다(없으면 조용히 통과한다).
- **분량 62~85초 = 공백 제외 380~521자**(통일 보이스·배속 1.0 실측 6.13자/초, topic마다 5.83~6.40으로 흔들린다).
  mp3가 있으면 상수 말고 `ffprobe`로 잰다. **도입부(훅 + 통념 반박)는 14초 안팎** — 길면 전체 화면 도입 클립을
  4배 넘게 늘려야 해서 정지 화면이 된다.
- **기관명은 한 원고에 2번까지**, 수치를 받치는 문장에만. 통계만 말하는 구간을 따로 만들지 않는다.
- **해결책이 문제를 푸는가, 숨기는가**를 스스로 묻는다(수치를 낮게 나오게 하는 법은 해결책이 아니다 — 기계로 못 잡는다).
- **말투**: 존댓말, 해요체로 통일(합니다체를 섞지 말 것) · 단정형으로 끝낸다("~수 있어요"는 진단·치료처럼 개인차가
  있는 의학적 진술에만) · "~대요" 금지 · "저장하세요·주목하세요" 금지 · 마무리 반문 금지 · 대체품 추천 금지
  (술→무알코올 식) · 숫자는 아라비아 숫자로(TTS 변환은 `lib/korean_numbers.to_speech()`가 한다).
- **TTS 재생성**: 길이가 마음에 안 들어서 다시 뽑지 않는다(글자수 과금, 이미 뽑은 topic은 preflight가 길이로 안 막는다).
  사실 오류를 고쳤을 땐 다시 뽑는다 — 녹음에 오류를 남기지 말 것.

## 사실 검증

- 수치는 **공공데이터**(`~/Desktop/project/public-data/`에서 `python3 find.py <말>`, `○`가 받아둔 것)나 **기관 원문**에서
  캔다. 🚨 **WebSearch/WebFetch 요약을 믿지 말 것** — 원문에 없는 문장을 지어낸 사례가 반복됐다. 핵심 주장은
  `curl`로 원문을 받아 문자열로 대조한다. 403·캡차·SPA면 그 출처를 버리고 다른 공신력 기관으로.
- 의심할 실패 유형: 출처 없는 수치 · 존재 확인 안 된 논문 · 실존 논문 수치 부풀리기 · 무관한 연구 끌어오기 ·
  맥락 오용 · 전제 자체가 반박됨 · 보도자료 수치를 논문처럼 · 원문 오독 · **다른 나라 기준값을 한국 글에**.
  실존 논문은 (a) 본문에 그 수치가 있는지 (b) 이 주제·이 인구집단 연구인지 둘 다 본다.
  정부 사이트에 올라온 글도 **원출처**를 본다(사기업 기사 재게시였던 사례가 있다).
- 공식 출처끼리 충돌하면 **섞지 말고 하나만** 고르고(소관 기관 우선) 근거를 커밋 메시지에 남긴다.
- **"기관명 없는 귀속"**("~가이드는", "한 연구에 따르면")은 그 자체가 신호다 — 기관을 적거나 수치를 뺀다.
- 권고가 특정 질환자에게 위험하지 않은지 본다(저염 소금 = 염화칼륨 → 신장질환자 고칼륨혈증).
- 판정은 `data/_audit/ko_known_issues.json`에 적는다 → `test_no_known_false_claims`가 재발을 막는다.
  `-m lib.claim_audit <topic>` / `--all --warnings`.
- 🚨 `pytest -k`에 한글을 쓰면 **조용히 0건 수집**된다(exit 5가 성공처럼 보인다). topic 단위는 `claim_audit <topic>`으로.

## 품목 — 브랜드커넥트에 있는 것만

```
.venv/bin/python3 -m lib.brandconnect login                  # 전용 Chrome(127.0.0.1:9333, 프로필 ~/.config/health-shorts/brandconnect-chrome)
.venv/bin/python3 -m lib.brandconnect check <topic>          # products 검사 → data/<topic>/brandconnect.json
.venv/bin/python3 -m lib.brandconnect sweep [--baby] [품목…]  # 카탈로그 + 빈 링크 발급·저장
```

- **스윕 결과의 `chosen` 상품명을 직접 보고 품목을 고른다.** 일반 품목명은 엉뚱한 걸 물어온다 —
  "투약기"→고양이 필건, "저자극 보습제"→강아지 세럼, "생리식염수"→렌즈 세척액(2026-09-24 육아 실측).
- 품목명은 **실제로 검색창에 치는 상품 카테고리**로. 설명형 수식어("~용 텀블러")·"가정용"·"고농도"·가운뎃점으로
  두 품목 잇기 금지(`test_products_no_unsearchable_prefix`).
- **대체품 말고 도움 되는 영양제·도구**(`WEAK_SUBSTITUTES`가 경고). 일반의약품·약국 품목은 링크를 못 단다.
  원고가 반박하거나 근거 없다고 적은 품목은 걸지 않는다(원고와 상품이 반대 말을 하게 된다).
- "없음"은 **검색 결과 0건일 때만** 찍는다(추천 금지 목록이 된다 — 거짓 "없음"이 더 해롭다). 상품은 있는데 기준에
  안 걸리면 "확인필요". 카탈로그 `data/_audit/brandconnect_catalog.json`(health)·`_baby.json`·`_pet.json`,
  금지 목록 `data/brandconnect_unavailable.json`.
- 도메인은 `tracks.domain_of(topic)`이 정한다 — 육아(`baby`)는 `_KID_WORDS`(유아용품 제외)를 안 걸고, `content_review`도
  도메인 카탈로그를 본다. 육아 계정은 health와 같아 링크 발급·저장까지 한다. **댕냥사전(pet)은 계정이 달라 발급 금지**.
- 링크는 `global_product_links`(market=naver)에 저장된다. 사용자가 직접 넣은 링크는 덮어쓰지 않는다. 입력값 `-`는 링크
  없음과 같다. 검색 간격은 2.5~5초. 로그인 세션을 서버·저장소에 두지 말 것.

## 카드뉴스 (`card_news_spec.json`)

- 본보기 `data/소화_14/card_news_spec.json`. `content_v2: true` · `search_keyword`/`search_volume` 필수.
- `thumb_word` — 썸네일에 박히는 **병명·증상 한 덩어리**(8자 이하면 화면 폭 88%까지 확대). 문장 금지. 검색어가
  물질·제품·음식이면(크레아틴·위고비) 썸네일과 영상 상단 띠는 **증상**으로.
- `title` 배열의 **마지막 줄은 독립 라벨**이다 — 표지·타이틀 카드는 `title[:-1]`만 훅으로 쓴다. 라벨은 해결책을
  미리보는 명사구("재발 줄이는 습관 3가지"), CTA형("저장부터 하세요") 금지(`check_title_closing()`이 전 줄을 본다).
  제목엔 가운뎃점·이모지 금지(본문은 괜찮다).
- `cover_scrim_color`는 topic마다 다른 hex(기존 값은 grep으로 확인) — 없으면 전부 같은 핑크가 된다.
- **아이템 수를 7개로 고정하지 말 것**(5~9개가 정상). 나레이션이 선언한 항목은 카드에 다 있어야 한다.
- **이미지는 실사진만**(AI 일러스트 신규 생성 중단). 공용 풀 `~/Desktop/project/assets-shared/`: 품목↔영어 검색어
  `queries/items_ko_en.py`(인물 품목은 `PEOPLE`에 넣어 `asian`이 붙게), 소싱 `sourcer.py --queries <json>`
  (`--target`은 카탈로그 총량 기준이라 이미 넘었으면 바로 끝난다 — 올려서 돌린다), 배정 `assign.py build --project health-shorts`.
  배정은 한 번 정해지면 고정. `test_char_files_resolve_to_images`가 누락을 잡는다.
- 원고를 고치면 **카드·캡션·제목을 같이** 고친다(`-m lib.card_article_diff <topic>`은 숫자만 본다 — 기전이 뒤집힌 건
  직접 읽어 대조). 이미지 배정을 바꾸면 alt도 사진을 직접 보고 다시 쓴다.

## 캡션 (`platform_captions.json`)

- `platforms`는 **네이버 블로그 + 네이버 클립** 둘. 새 topic은 `data/social_accounts.json`에서 복사한다.
- **네이버 블로그**: `network: "naver"` · `rich_paste: true` · 본문 링크. 1000자 이상. 이미지 자리 표시는
  `01 · 소제목`(아래 빈 줄 두 줄). **나레이션의 확장판이 아니다** — 영상에 못 담은 것(분량·빈도·타이밍·예외 상황·
  흔한 오해·병원 갈 때)으로 채운다. **수치에는 기관명을 그 문장 안에**(`check_naver_blog_quality()` — 새 위반은
  즉시 실패, 옛 위반 채무는 `data/_audit/naver_blog_quality_debt.json`, 고치면 거기서 지운다).
- **네이버 클립**: 캡션에 링크를 넣지 않는다(앱의 쇼핑 커넥트 버튼으로 붙인다). `suppress_product_block`은 걸지 않는다.
  `[광고]` + 고지문은 대시보드가 캡션 **맨 아래 한 덩어리**로 자동으로 붙인다(원고에 넣지 말 것).
- 해시태그 전 플랫폼 필수. 블로그 제목(`title`) 25~50자.
- 🚨 **댓글→DM 자동화 CTA는 어떤 언어·플랫폼에도 쓰지 않는다**(`comment_keyword` 필드 포함). 마무리 CTA는 "팔로우/구독" 류.
- 최상위 `title` 필드는 캡션 첫 줄과 **다른 게 정상**이다(옛 유튜브 매칭 키) — 캡션 제목을 고칠 때 건드리지 말 것.
- 영상에는 `rebuild_video`가 우상단 `[광고]` 오버레이를 기본으로 붙인다(`ad_tag=True`, 공정위 표시 의무 — 댓글 표시는 인정 안 된다).

## 보이스 (TTS)

- 한국어는 **`30대 남자 인터뷰어` 하나만**(`lib/fish_tts.py` `DEFAULT_VOICE_BY_LANG` — 다른 이름을 넘기면 예외).
  ai-video-network/1biteinfo와 같은 보이스다 — 여기만 바꾸지 말 것. 배속 1.0.
- 보이스·배속을 바꾸면 발화 속도를 다시 잰다.

## 영상 — 세부는 `XRAY_FORMAT.md`

- 포맷은 **반투명 인체 + 칠판** 하나(`lib/rebuild_video.py` `_FORMAT_WEIGHTED_POOL = ["chalkboard"]`).
- 맨 앞 썸네일 카드 **0.2초**(병명 한 덩어리). 도입 클립은 `xray_splice`가 0.2초부터 얹는다.
- 폐기된 것 — 되살리지 말 것: 훅 직후 무음 요약 카드, 상단 후킹 배너, "~라면 주목하세요" 조건절 도입.
- **네이버 클립 안전영역**: 양옆 약 48px이 잘리고, 오른쪽 x>900(y≈990~1720)에 버튼, y<100·y>1455에 UI가 얹힌다.
  칠판은 가운데 세로 띠를 잘라 **폭만** 좁히고(균일 축소 금지), 얹는 요소는 `_board_xy()`를 거친다.
  레이아웃을 바꾸면 `scripts/rerender_all_videos.py`로 전량 재조립한다.
- **광고 배너 CTA**(`lib/ad_cta.py` 정본) — 세로 위치는 칠판 상단 기준(`CTA_CY_FROM_BOARD_TOP`), 등장은
  `CTA_START_SEC=5.0`(썸네일 후보 프레임을 가리지 않게. `enable`로 건다 — fade는 안 먹는다). `.pre_cta.mp4`는 쓰지 말 것.
- 🚨 **없는 클립은 요청한다, 비슷한 걸로 때우지 않는다** — `data/<topic>/clip_requests.json`에 적고 그 topic은 조립을
  멈춘다. 렌더 시트는 `scripts/prep_clip_worksheet.py`가 트랙별로 만든다(`작업/0_작업지시.md`·`작업_육아/0_작업지시.md`
  — 이름 고정, `tests/test_xray_worksheet_path.py`). 받은 클립은 `2_완성클립/`에 넣고 `scripts/collect_clips.py --commit`.
  스틸만 받는 요청은 `"kind": "still"`. 아무 topic도 안 쓰는 요청은 지운다(사람 렌더 시간 낭비).
- 클립은 **색인으로 찾는다**(`-m lib.clip_index --for <증상어>`, `--show <이름>`) — 이름이 실제와 다른 클립이 많다.
  `avoid`를 어기지 말 것.
- **부위 클립**은 Flow로 안 뽑는다 — `scripts/make_part_clip.py`가 스틸에서 만든다. 전신·몸통 스틸은 **`--region` 필수**
  (`assets_library/xray/part_regions.json`) — 없으면 피사체 전체가 호박색이 된다.
- Flow 규칙: **start 프레임만**(end를 주면 피사체가 변형된다), 길이는 4·6·8·10초뿐, 프롬프트는 영어, 화면 속 글자·숫자
  금지. 🚨 미성년자 안전필터는 `infant`·`child` **단어만으로도** 막는다 — 아기가 보이는 장면은 Flow에 보내지 않는다.
  주사·백신 같은 의료 처치도 기구를 빼고 몸 안 변화만 요청한다(기구는 스틸로).
- `opening_until`은 원고 **세 번째 문단(항목 예고) 직전** 자막의 끝이다 — `xray_build`가 그 경계로 다시 잰다.

## 육아 트랙 (2026-09-24 착수, 시험 배치 10편)

시청자가 20~30대 부모로 갈리므로 10편 올려보고 조회수로 확장을 판단한다. 포맷 차이는 `XRAY_FORMAT.md` 6절.

- **영유아 정보는 틀리면 위험도가 다르다** — 해열제 용량·이유식 시기·수면 자세 같은 건 대한소아청소년과학회·
  질병관리청·식약처 **원문을 curl로 대조**해 기관명을 문장 안에 쓰고, 확인 못 한 용량·간격은 쓰지 말고 행동으로
  돌린다. 같은 기관 문서 안에서도 엇갈리는 지침(땅콩: 알레르기 절 "미루지 마라" / 도입순서 절 "돌 무렵" — 질식 때문)은
  단정하지 말고 이유를 갈라 쓴다. 공식 출처가 충돌하면 소관 기관을 따른다(열성경련 대처 — 중앙응급의료센터).
- 제목 검색어: 해열제교차복용·수족구(🚫 "수족구병")·이유식시작시기·신생아황달·돌발진(+열꽃)·기저귀발진·
  **RSV 바이러스**·아기설사(+아기탈수증상)·**신생아 배앓이**·**신생아 변비**. 조사 원본 `data/_audit/baby_track_keywords.md`.
- 아기는 **미드저니 정지 스틸 + `make_part_clip.py`**로만 움직인다. 행위 칸은 보호자 — 비접촉(사물·손만)은 Flow,
  아기에게 해주는 동작은 스틸+코드.
- **현황**: 10편 원고·카드(90장)·TTS·대시보드·DB 등록·품목(32종, 링크 보유) 완료. **영상만 클립 대기** —
  `작업_육아/0_작업지시.md` 35종을 받으면 `collect_clips.py --commit` → 부위 클립(region은 스틸 보고 실측) →
  `xray_build.py` → `verify_output.py`.

## blog_seo 서브트랙 (9개 언어)

영상 트랙과 별개로 vernhaven 계열 SEO 블로그에 **카드뉴스 + `blog_seo` 본문**을 공급한다. 대상 언어는
**ko/en/ja/de/fr/it/es/nl/sv 9개**(한국어 포함). 영상의 en/ja는 폐기됐지만 이 트랙은 계속한다.

- 산출물: `data/<topic>/<lang>/card_news_spec.json` + `platform_captions.json`(`blog_seo` 항목, 필드는 seo-blog
  `CLAUDE.md` "Track B 데이터 계약"). 카드 렌더 `output/<topic>/<lang>/card_news/`, 반영은 vernhaven
  `ingest_health_shorts.py --commit`(몇 topic씩 쪼개 돌린다 — 통짜로 돌리면 절전에 소켓이 죽는다).
- **완료 기준 = 9개 언어 전부.** 언어별 카드 렌더를 빼먹지 말 것(hero가 영영 빈다).
- **번역 금지 — 언어마다 독립 리서치**(그 언어권 공식기관 원문). 기존 언어 캡션을 "주장 후보 목록"으로 삼아
  타겟 검색해도 되지만 본문 문장은 새로 쓴다. 국가별 기준값이 다르다(하나를 옮기면 나머지가 틀린다).
- **ko는 네이버 캡션과 다른 글**이어야 한다 — 겹침 `-m lib.ko_overlap_audit`, 20%를 넘으면 다시 쓴다.
- 본문: 도입 → H2 원인/기전 → H2 현지 해결책 → 선택 FAQ/요약, 시맨틱 HTML, `<img>` 최소 1장(플레이스홀더는
  인입 스크립트가 치환), 문단마다 핵심 어구 하나를 `<strong>`. 수치엔 **출처와 조건**(비교 대상·하위집단·기간),
  관찰연구는 "연관됐다", 무작위 시험만 "낮췄다". PubMed는 WebFetch가 막힌다 — europepmc·저널·기관 페이지로.
- 쓰기 전에 아키타입을 뽑는다: `--title-archetype <topic> <lang>`, `--closing-archetype <topic> <lang>`,
  `select_section_header_archetype(topic, lang, "summary"|"actual_fix")`. 아키타입은 문구가 아니라 스타일이다.
- 품질 게이트 `pytest tests/test_blog_seo_quality.py` — 라틴 500단어/일본어 1000자, 제목 65자(ja·ko 35자,
  인입 스크립트 상수와 동기화). 채무 `data/_audit/blog_seo_quality_debt.json`(고치면 지운다). 제목을 줄여도
  **`slug`는 바꾸지 말 것**. 증량은 물타기 금지.
- 글로벌 topic에는 `products`·`suppress_product_block`을 넣지 않는다.

## 같은 틀로 수렴하지 않게

구조 쏠림은 몇 편 읽어서는 안 보이고 전수로 세야 보인다. `-m lib.repetition_audit`(계기판, 게이트 아님).
쓰기 전에 `content_review --card-structure <topic>`·`--connectives <topic>`을 확인한다. "왜 이런 문제가 생길까요"로
여는 습관을 경계한다. 의료 안전 라벨(`받아야 할 때`)은 반복돼도 그대로 둔다.

---

## 세션 운영·동시성

- 여러 세션이 이 저장소를 동시에 쓴다. **worktree는 `~/Desktop/project/.worktrees/health-shorts/<설명>/`**
  (루트 CLAUDE.md 규칙). 병합하면 바로 `git worktree remove` + `git branch -d`. worktree엔 gitignore 대상
  (`.venv`·`.env`·`assets_library/xray/{output,stills}`·`assets_library/real`)이 없다 — 심볼릭 링크로 붙였다면
  **지우기 전에 링크부터 끊는다**.
- 커밋은 **경로를 지정해서** add 한다(`git add -A`는 다른 세션 산출물까지 쓸어 담는다). 커밋 직후 `git show --stat HEAD`로
  확인하고 미커밋 상태로 오래 두지 않는다. 공유 파일(이 파일, `scripts/prep_clip_worksheet.py`, 작업 시트)은 고치기 전에
  main을 당겨 합친다.
- 🚨 `git stash`는 모든 worktree가 공유한다 — bare `stash pop` 금지.
- 🚨 **`assets_library/{real,motion,music}/`는 로컬 유일본, 백업 없음** — 이 경로 대상 삭제는 **절대경로 + 직전 `pwd` 확인**,
  웬만하면 지우지 말고 이름을 바꿔 보관한다(상대경로 `rm -rf`로 726MB가 날아간 전례).
- 🚨 `git clean`에 `-x`/`-X`를 쓰지 않는다(`.env*`가 같이 지워진다 — 루트 CLAUDE.md).
- 파이썬은 항상 **`.venv/bin/python3`** — bare `python3`는 의존성이 없어 죽는다(새로 만들 땐
  `python3.11 -m venv .venv && .venv/bin/pip install -r requirements.txt`).

## 대시보드

- `lib/dashboard.py`가 topic별 `dashboard.html`과 `output/topics.json`을 만든다. 트랙 배지("숏츠"/"카드뉴스")는
  `platforms[]`에 `type: "video"`가 있는지로 자동 파생된다.
- 상품 링크는 대시보드 입력창이 `/api/product-links.js`·`/api/global-product-links.js`로 DB에 직접 쓴다.
  `output/all_products.json`은 대시보드 생성마다 갱신된다.
- `lib/card_news_hub.py`(babbleroot/furrowly/sparelow 네이버 포스팅 허브)는 **2026-08-21 중단된 워크플로우**다 — 코드만 남아 있다.

## 테스트

```bash
.venv/bin/python3 -m pytest tests/ -q
```

- topic 작업 뒤엔 `tests/test_content_rules.py`부터 — 전 topic을 훑어 해시태그·필수 플래그·금지 표현·`char_file` 실존 등을 잡는다.
- 유료 API(Fish Audio·Gemini 등)는 테스트에서 호출하지 않는다(`tests/conftest.py` 합성 픽스처만).
- 외부 저장소에 쓰는 코드를 렌더 함수 안에 붙일 땐 테스트 경로(tmp_path)에서도 실행된다는 걸 먼저 확인한다.

## 자료 위치

| 종류 | 위치 |
|---|---|
| topic 데이터 / 산출물 | `data/<topic>/` / `output/<topic>/` (육아는 `data/육아/<topic>/`) |
| 클립 라이브러리 | `assets_library/xray/` — `output/`(클립) · `stills/` · `clip_index.json` · `README.md` |
| 공용 실사진 풀 | `~/Desktop/project/assets-shared/` |
| 공공데이터 | `~/Desktop/project/public-data/` |
| 감사·카탈로그 | `data/_audit/` |
| 채널별 URL | `data/social_accounts.json`(새 topic은 여기서 복사) |
| 비밀키 | `.env`(커밋 금지, `.env.example` 최신 유지) |
| 결정 경위·옛 규칙 | `CLAUDE_ARCHIVE.md` |
