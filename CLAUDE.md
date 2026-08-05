# health-shorts

건강 상식 정보를 카드뉴스 + 숏폼(캐릭터 나레이션) + 플랫폼별 캡션으로 만드는 파이프라인.
`shopping-shorts-video`와는 완전히 별도 프로젝트.

**이 파일은 "지금 지켜야 할 활성 규칙"만 담는다.** 결정 배경(WHY)·과거 버그 상세·
사용자 인용문·뒤집힌 결정의 히스토리는 전부 `CLAUDE_ARCHIVE.md`(이 파일의 이전
전체 버전, 2026-08-04 분리)에 그대로 남아있다 — "왜 이렇게 했더라" 싶으면 거기서
같은 제목으로 찾을 것. 새 결정을 추가할 땐 여기엔 결론만 한 줄로, 자세한 경위가
필요하면 archive 쪽에 이어서 적을 것(둘 다 git 추적됨).

## 세션 운영

- **역할 고정 없음** — 세션 하나가 신규 topic·기존 topic 수정·설정 변경 전부 처리.
- **완전 자동화 모드** — "다음 topic 해줘"류 요청은 소재 선정→리서치→콘텐츠 작성→
  이미지/TTS/영상 조립→대시보드→git commit·push까지 중간 승인 없이 끝까지 진행.
  단, 유튜브 외 플랫폼 업로드는 API 연동이 없어 사람이 대시보드에서 수동으로 함.
- **topic 폴더명** = 핵심 카테고리 단어 + `_N`(예: `가슴쓰림_1`). 서술형 접미사
  금지. 새 topic 시작 전 `ls data/ | grep "^<카테고리>_"`로 기존 번호 확인.

## 동시 세션 안전장치 — 매번 필수

1. **세션 락**: 작업 전 `python3 lib/session_lock.py check <topic>` →
   `UNLOCKED` 아니면 사용자에게 확인. 진행 시 `acquire`, 끝나면 `release`.
   락 파일명 제약상 다국어 topic도 언어 세분화 없이 `<주제>` 단위로 건다.
2. **git worktree** — 새 작업 시작할 때마다:
   ```
   git worktree add ../health-shorts-worktrees/<짧은-설명> -b session/<짧은-설명> main
   ```
   그 안에서 작업·커밋까지 끝내고, 메인 워크트리로 돌아가
   `git pull --ff-only && git merge session/<설명> && git push` → 정리
   (`git worktree remove` + `git branch -d`). 다른 세션의 `git add`/`commit`과
   완전히 격리되므로 인덱스 레이스가 안 생긴다.
3. worktree를 못 쓰는 상황이면 커밋 직후 `git show --stat HEAD`로 의도한 파일이
   맞는지 항상 확인 — 다른 세션 파일이 섞여 들어갔으면 데이터 손실은 아니니
   되돌리지 말고 새 커밋으로 바로잡기만 하면 됨.
4. `assets_library/`(공용 자산) 새로 만들기 전엔 `session_lock.py list`로 활성
   락 확인.

## 배포

- 카드뉴스·캡션·영상 중 뭐든 먼저 끝나는 대로 바로 commit·push — 셋 다 끝날 때까지
  안 묶는다. `dashboard.py`가 영상 없으면 자동으로 "준비 중" placeholder 보여줌.
- **서브에이전트로 여러 topic 병렬 생성 시**: 영상 조립(`video_assembler.py`)·
  대시보드 생성은 별도 2단계로 미룬다 — 1단계(리서치~TTS~캐릭터 일러스트/모션)
  전부 끝나면 커밋·push, 그다음 2단계로 영상 일괄 조립.

## 에셋 라이브러리

- `assets_library/{illust,real,motion}/<품목>_*` — 캐릭터 일러스트/실사진/모션
  루프. 새 캐릭터 만들기 전 `ls assets_library/illust/`로 비슷한 시각 카테고리
  기존 파일 있는지 먼저 `Read`로 확인 — 있으면 그대로 재사용, 새로 만들지 말 것.
  - ⚠️ **파일명은 topic 언어와 무관하게 항상 한국어로 짓는다**(2026-08-05
    확정). 예전엔 topic 언어를 따라 지어서(포르투갈어 세션은
    `fone_de_ouvido_illust.jpg`처럼) 같은 물건인데 언어마다 파일이 따로
    생성되는 사고가 실제로 다수 발생했다(이어폰·면봉·바나나·용안·알약류 등
    — 파일 크기 전부 달라 진짜 중복 생성, API 비용 낭비 확인 후 전부 한글
    이름으로 통합·병합함). 한국에 없는 품목이라도 번역하지 말고 한글로
    새로 이름 짓는다(예: `nopal`→`백년초`, `avena`→`귀리`) — 그래야
    `ls assets_library/illust/`만 보고도 다른 언어 세션이 이미 만든 걸
    알아볼 수 있다.
  - ⚠️ **약/보충제류는 "품목명"이 아니라 "물리적 형태"로 먼저 재사용 확인**
    (2026-08-05, 시각 감사로 진통제≈아스피린·칼슘보충제≈영양제가 사실상
    동일 이미지였음을 발견 후 병합·삭제 — Gemini 비용 낭비). 음식·음료·
    기기류는 품목명 그대로 생성해도 Gemini가 실제 형태 차이(용기·색·소품)를
    반영해서 자연스럽게 구분되지만, 정제/캡슐/보충제 병처럼 실제 모양이
    거의 똑같은 것들은 이름만 다르면 새로 그려도 시각적으로 구분이 안
    된다. 새 항목이 아래 형태 중 하나면 반드시 먼저 해당 캐릭터부터
    확인·재사용할 것(진짜 시각적으로 다른 게 확실할 때만 예외):
    - 정제(원형 알약) → `아스피린_illust.jpg`
    - 캡슐(알약) → `알약_illust.jpg`(색만 다른 변형은 만들지 말 것)
    - 보충제/영양제 병 → `영양제_illust.jpg`
- **실사진 소싱**: `lib/real_photo_sourcing.py <영어검색어> <후보수> <pexels|unsplash|both>`
  → Read로 골라서 `assets_library/real/<품목>_real_NN.jpg`로 저장.
- **크로마키 배경색**: 기본 초록(`#00FF00`)이되, 캐릭터 자체가 초록 계열(오이·
  상추 등)이면 겹치므로 `lib/gemini_illust.py`의 `pick_bg_color(avoid=[...])`로
  파란/마젠타/시안/보라 중 하나 고르고 `video_assembler.py --bg-color`도 동일하게 맞출 것.

## 캐릭터 모션 — 생성 중단 (2026-08-05)

- **새 캐릭터는 모션을 만들지 않는다** — Kling도, `build_static_motion_loop`
  정지 루프 mp4도 더 이상 호출하지 않는다("모션을 생성하지 않는거로 하자,
  영상에서 모션 없는 일러스트 jpg 파일만 쓰자" — 사용자 확정). 캐릭터는
  일러스트(jpg) 생성까지만 하고 끝 — `lib/video_assembler.py`의
  `_build_character_loop`/`_build_character_segment`가 확장자를 보고
  자동으로 정지 이미지 코너 오버레이로 처리한다(`--motion`에 `*_motion.mp4`
  대신 `*_illust.jpg` 경로를 그대로 넘기면 됨, `lib/rebuild_video.py`의
  `_char_media_path()`가 이미 이렇게 자동 분기).
- 과거(2026-08-05 이전)에 만들어진 Kling 모션 mp4(77개)는 그대로 자산으로
  남아있고 재사용 가능 — 새로 만들지만 않으면 됨. 정지 루프로 만들어졌던
  가짜 모션(움직임 전혀 없이 "모션"이라고만 불리던 mp4, 90개)은 전수조사
  후 전부 삭제함(illust jpg는 유지).

## 영상 조립 (`lib/video_assembler.py`)

- **배경 기본값은 칠판 스타일**(`--bg-style chalkboard`, 기본값이라 생략 가능,
  `--images` 불필요) — 실물 칠판 사진 + 분필체 자막 + 랜덤 낙서(별·하트 등
  93종, seed 고정이라 topic마다 재현 가능)+ 명패(26종, 0~2개 랜덤)+칠판 색상
  변형(26종). `--bg-style photo`는 과거 topic 재조립 등 특수한 경우에만.
- **표준 호출 예시**:
  ```
  python3 lib/video_assembler.py \
    --motion "assets_library/motion/<캐릭터>_motion.mp4" \
    --audio "output/<topic>/<topic>_narration.mp3" \
    --srt "output/<topic>/<topic>_narration.srt" \
    --out "output/<topic>/<topic>_shorts.mp4" \
    --title "<훅> <주제명, 자연어>" \
    --title-card-text "<훅만>" \
    --title-card-char "assets_library/illust/<캐릭터>_illust.jpg" \
    --title-banner-photo "assets_library/real/<대표품목>_real_01.jpg" \
    --bg-color 0x00FF00
  ```
  `--title`에 topic 폴더명(슬러그)을 그대로 넣지 말 것 — 자연어 문구만.
- 캐릭터 여러 명(품목 3개 이상)이면 `--motion` 대신 `--motion-schedule
  "시작-끝:경로,..."`(나레이션 기준 0초부터 빈틈없이).
- 실사진 없는 topic은 `--images`에 캐릭터 일러스트를 넣지 말고
  `make_gradient_bg()`로 그라디언트 배경 사용.
- **인스타그램 릴스용 안전 여백 영상**: 칠판 프레임이 캔버스 가장자리에 거의
  꽉 차서 인스타 UI 세이프존과 겹쳐 잘려 보인다 — `build_instagram_safe_video
  (source_path, out_path)`(기본 상하좌우 20% 여백, 실기기 테스트로 확정)로
  `<원본파일명>_instagram.mp4`를 같은 폴더에 만들어두면 `dashboard.py`가
  자동으로 찾아서 인스타그램 릴스 카드에만 연결한다(원본 `_shorts.mp4`는
  유튜브 자동 업로드용으로 그대로 둠 — 건드리지 않음).
- output 폴더 안 파일명은 전부 `<topic>_` 접두어 붙일 것(`card_news.py`/
  `--out`은 직접 지정, `typecast_tts.py` 결과는 필요시 rename).

## 배경음악(BGM) (`lib/bgm.py`)

- **소스는 유튜브 오디오 보관함**(studio.youtube.com > 오디오 보관함)에서
  사용자가 직접 다운로드한 무보컬 트랙만 `assets_library/music/`에 둔다
  (2026-08-05) — 저작권 클레임 걱정 없는 유일한 무료 소스로 확정, 새 트랙
  추가 시에도 반드시 무보컬(장르 Ambient/Cinematic/Classical/Jazz&Blues/
  Folk&Acoustic 위주, 다운로드 전 미리듣기로 보컬 여부 확인) — Pixabay
  `/api/audio/`는 엔드포인트는 있지만 일반 API 키 계정엔 403으로 막혀있어
  못 씀, Suno는 무료 플랜이 비상업적 용도로 약관에 못박혀 있어 제외.
  `assets_library/music/`는 대용량이라 git엔 안 올라간다(`.gitignore`).
- **선택**: `lib.bgm.pick_track(seed)`가 seed(topic 폴더명 등) 기준 결정론적
  시드로 트랙 하나를 고른다(같은 topic은 항상 같은 곡, 진짜 랜덤 아님) —
  트랙이 하나도 없으면 `None`, 호출부는 BGM 없이 조용히 폴백.
- **믹싱**: 항상 `BGM_VOLUME_DB=-24dB` + 앞뒤 `FADE_SEC=1.5초` 페이드로
  "내레이션 절대 방해 안 하는 은은한 밑바탕" 용도로만 깐다(사용자 확정,
  값 조정은 이 두 상수만 바꾸면 전체 파이프라인에 일괄 반영). `amix`엔 항상
  `normalize=0`을 명시할 것 — 기본값(1)이면 입력 개수만큼 자동으로
  볼륨을 나눠서 내레이션까지 같이 작아진다.
- 단순 케이스(내레이션 길이만큼만 깔면 되는 3개 신규 템플릿)는
  `lib.bgm.mix_bgm(narration_path, out_path, duration, seed)` 하나로 끝 —
  리턴값을 기존 최종 mux 단계의 `audio_path` 자리에 그대로 넣으면 되고,
  비디오 코덱/트림 로직은 안 건드려도 된다.
- 복합 케이스(`video_assembler.py`의 `assemble()` — 제목 카드·엔딩 카드
  무음 구간까지 포함한 전체 영상 길이 동안 계속 깔아야 해서 기존
  `adelay`/`apad` 필터와 한 filter_complex 안에서 조립해야 함)는
  `lib.bgm.bgm_filter_segment(seed, duration, in_label, out_label)`로 필터
  조각만 받아서 직접 조립할 것.

## 영상 포맷 다각화 (`lib/templates/`)

- **로스터 4개**: 판서형(기존, `video_assembler.py`) + `before_after_transition`/
  `checklist`/`ranking_countdown`(`lib/templates/proto_*.py`). `timeline`은
  2026-08-05 제외(진행 라인/스톱 애니메이션 타이밍이 나레이션과 안 맞음) —
  코드는 `lib/templates/proto_timeline.py`에 남아있고 `rebuild_video.py`의
  `FORMAT_ROSTER`에서만 빠짐, 타이밍 고치면 재편입 가능.
- **선택**: `lib/rebuild_video.py`의 `select_format(topic)`이 topic 문자열
  기준 결정론적 시드(`sum(ord(c)*(i*k+c0)...)  % len(options)`, 축마다 다른
  (k,c0))로 하나를 고른다 — 진짜 랜덤 아님(재생성해도 같은 topic은 같은
  포맷), 다른 topic·언어 참고 안 함(전역 상태 없음). `rebuild(topic)`이 그
  포맷대로 자동 분기 렌더링 — `python3 -m lib.rebuild_video <topic>`만
  실행하면 됨.
- 신규 4개 템플릿 공통 시그니처: `render(topic_dir, lang, audio_path,
  srt_path, spec_path, out_path)`. `card_news_spec.json`의 `items` 개수를
  그대로 읽어서 3개 고정 아님. 폰트는 `video_assembler.py`의
  `_title_font_for_lang`/`_wrap_text_for_lang` 재사용(16개 언어 자동 지원).
- **안전영역**: `_YT_SAFE_RIGHT=150`/`_YT_SAFE_BOTTOM=320`(유튜브 Shorts 앱
  UI가 가리는 영역) — 4개 템플릿 전부 이 값을 로컬 상수로 복제해서 모든
  텍스트 블록이 `(0,0,W-150,H-320)` 안에 들어오도록 강제 체크한다. 새
  템플릿 추가 시 반드시 넣을 것 — 빠뜨리면 실기기에서 텍스트가 잘려 보인다.
- 산출물이 코드보다 오래됐는지는 `python3 -m lib.check_video_staleness`로
  확인(미게시 topic만 대상, 재생성은 자동으로 안 함).
- ⚠️ 이 영상 포맷 시스템(코드+문서) 전체가 2026-08-04에 한 번 커밋 안 된 채
  통째로 유실됐다가 재구축됨 — **이 종류 작업(대규모 신규 코드)은 완성되는
  즉시 커밋할 것**, 리뷰용이라고 미루지 말 것.
- **오프닝(프레임 0) = 사실상 피드 썸네일**(커스텀 썸네일 업로드 없음,
  `youtube_upload.py` 확인됨) — `before_after_transition`/`checklist`/
  `ranking_countdown` 3개 전부 프레임 0 전용 훅 화면 렌더러를 따로 둔다
  (`_render_hook_screen`/`render_title`/`_render_hook_frame`, 2026-08-05).
  새 템플릿도 아이템 화면을 프레임 0에 그대로 쓰지 말고 별도 훅 화면을 만들 것.
  - 훅 화면 노출 시간은 SRT 첫 구간(`entries[0]`) 길이를 그대로 쓸 것 — 그
    구간이 실제 훅 나레이션 문장이라(오디오 실측 검증됨), 임의 비율로
    잡으면 나레이션과 화면이 어긋난다.
  - 중앙정렬은 안전영역 중심이 아니라 캔버스 진짜 중앙(`VISUAL_CX = W/2`)
    기준으로: 안전박스 자체가 좌우 비대칭(왼쪽 50 vs 오른쪽 150)이라 안전
    영역 중심에 맞추면 화면상 왼쪽으로 쏠려 보인다. `VISUAL_CENTER_MAX_WIDTH
    = 2*min(VISUAL_CX-SAFE_LEFT, SAFE_RIGHT-VISUAL_CX)`로 폭을 캡핑하고
    `VISUAL_CX`에 정렬하면 두 조건(안전영역 준수 + 시각적 중앙) 동시 만족.
  - 오프닝 프레임 리뷰 이미지는 `output/_thumbnail_review/`에 모아둠(git
    추적) — 검증 끝난 뒤에도 지울 필요는 없음, 다음 오프닝 수정 때 비교용.

## TTS (`lib/typecast_tts.py`)

- `synthesize(topic, text)` — 보이스 미지정 시 `data/typecast_voices.json`에서
  랜덤 선택. **캐릭터 여러 명 topic도 항상 단일 보이스로 간다** — 세그먼트별
  멀티보이스(`synthesize_segments`)는 반복적인 싱크 버그로 폐기 결정, 코드는
  남아있지만 새 topic에 기본으로 쓰지 말 것.
- 캐릭터 전환 구간 경계는 SRT에서 다음 아이템 문단 첫 문장 타임스탬프를 손으로
  찾아서 `--motion-schedule`에 반영.

## 플랫폼 캡션 (`platform_captions.json`)

- **로테이션**: 브런치·핀터레스트·인스타그램 카드뉴스는 항상 제외. 한국어
  topic은 네이버 블로그·티스토리·인스타그램 릴스·유튜브 쇼츠·네이버 클립·
  쓰레드·틱톡. **글로벌(비한국어) topic은 YouTube Shorts + Instagram Reels
  두 항목만**(유튜브는 자동 업로드라 대시보드 UI에서 제외됨).
- ⚠️ **글로벌(비한국어) topic은 제휴/상품 관련 필드 자체를 안 쓴다**(2026-08-05,
  "쿠팡 DM 자동화라는거 자체가 필요가없어 일단 유튜브든 인스타든 건강정보만
  주는 형태로 운영할거야. 채널이 커지면 알리나 아마존 붙일거고" — 확정).
  `comment_keyword`·`comment_dm_automation`·`products`·`suppress_product_block`
  등 아래 플래그는 **한국어 topic 전용**이다 — 글로벌 topic은 이 필드들을
  아예 넣지 않고 순수 건강정보 콘텐츠로만 작성할 것(채널이 커지면 그때
  아마존/알리익스프레스 제휴로 전환 예정, 아직 아님).
- **필수 플래그**(한국어 topic, 빠짐없이):
  - `no_caption_link: true` — 인스타 릴스·틱톡(URL 클릭 안 되는 플랫폼)
  - `comment_dm_automation: true` — 인스타 릴스만(실제 자동화 연동된 곳)
  - `comment_keyword: "쿠팡"` — **한국어 topic 공통 고정값**
  - `network: "naver"` — 네이버 블로그 + 네이버 클립 둘 다(URL 없이 상품명만
    나열하는 로직 트리거)
  - `rich_paste: true` — 네이버 블로그·티스토리만(클립보드 이미지 붙여넣기)
  - `suppress_product_block: true` — 유튜브 쇼츠(구독자 500명 전까지) +
    현재 모든 인스타(채널 성장 우선, 나중에 `comment_dm_automation`으로 전환 예정)
  - `link_in_comment: true` — 쓰레드·페이스북(본문 링크 대신 댓글에), 항상
    `no_caption_link`와 같이 씀. 제휴 고지문구는 본문 맨 아래 한 곳만.
- 해시태그 전 플랫폼 필수 — 새 topic 후 `python3 -c "..."` (아래 "테스트" 절
  content_rules로 자동 검사됨).
- **`products` 필드**: 특정 요리·조리형태(예: "저나트륨 사골육수")가 아니라
  실제 쿠팡/네이버에서 검색되는 **식품 카테고리**로("저나트륨 식품"). "·"(가운뎃점)로
  두 품목 이어붙이지 말고 하나만 남길 것. 습관/타이밍처럼 식품이 아닌 항목은
  아예 빼거나 관련 식품명만 남길 것.
- 네이버 블로그 캡션은 최소 1000자(`test_content_rules.py`가 자동 검사).
- 네이버 블로그·티스토리는 같은 원고 금지(도입부·설명 문장을 다르게 재작성,
  번호/이미지 순서는 유지).
- 이미지 삽입 위치 표시는 `01 · 소제목` 형식(카메라 이모지·대괄호·"삽입" 금지),
  마커 아래는 빈 줄 두 줄.
- 쓰레드는 별도 포맷 — 이미지 1장, 이모지 리스트형, 질문형 마무리, 50~200단어.

## 콘텐츠 톤

- **구조**: 훅(구체적 증상 호출) → 원인 설명 → 해결책. 장기/질환명 걱정형
  훅 금지("콩팥 건강 걱정되는 분들"❌) — 실제 증상으로("얼굴·발이 붓고
  소변에 거품이 보인다면"⭕). 제목/캡션 첫 줄까지 전부 동일 톤 통일.
- **훅 문장 형태를 topic마다 다르게 로테이션** — 호출형("~주목!")만 반복하지
  말 것. 질문형·원인예고형·반전형·통계제시형 등 12종 골격 참고
  (`CLAUDE_ARCHIVE.md`의 "훅 어미를 주목으로만 고정하지 말 것" 절에 전체 목록).
- 항목 여러 개 설명 전엔 "~~, ~~, ~~야."로 먼저 이름만 나열(“때문이야”로 끝내지
  않기), 그다음 각각 설명.
- 금지 표현: "~대요"(전언체, "~것으로 나타났어요"로), "무조건 다 끊을 필요는
  없어"류 헷지 문장(원인 설명 뒤 바로 해결책으로).
- ⚠️ **TTS는 언어 상관없이(한국어 포함) topic당 예외 없이 딱 1회만 호출한다**
  (2026-08-05 재확정 — "tts 여러번 뽑지말라고... tts 너무 길어도 무조건
  그냥 그대로 쓰라고" 재지적). **내용을 고쳐야 하는 경우도 예외가 아니다** —
  이전에 "content_review가 진짜 오류를 잡으면 1회 더 재생성 허용"이라는
  예외를 뒀었는데, 이게 실제로는 매 topic마다 재생성이 반복되는 구멍으로
  작동해서 완전히 폐기함. **순서를 바꿔서 애초에 재생성이 필요 없게 만든다**:
  narration.txt 작성 → **TTS 호출 전에** `content_review`로 텍스트 자체를
  검증·수정 → 그 다음에만 TTS 호출. 길이든(45초 초과, 1분 넘음) 톤이든
  사후에 발견된 문제든, TTS를 이미 호출했다면 그 결과를 그대로 쓴다 — 텍스트만
  참고용으로 고쳐두더라도 오디오는 재생성하지 않는다(TTS는 글자수 과금이라
  "뽑고→마음에 안 들면 재작성→다시 뽑고" 반복이 API 호출 배수로 이어짐).
  대신 `lib/typecast_tts.py`의 `estimate_duration(text, lang)`으로
  **작성 전에** 예상 길이를 가늠해서 애초에 적당한 분량으로 쓴다 —
  `data/tts_pacing.json`(언어별 초당 단어/글자수)은 `synthesize()` 호출마다
  실제 결과로 자동 갱신되는 경험 기반 누적 데이터라 topic이 쌓일수록
  정확해진다(수동 유지보수 불필요, 손대지 말 것).
- 콘텐츠 작성 순서: 자료조사 → 네이버 블로그(마스터, 1000자+) 완성 →
  narration.txt/카드뉴스는 거기서 압축 → 티스토리는 다르게 재작성 → 쓰레드는
  별도 재구성.
- 원본 기사 요약만으로 끝내지 말고 WebSearch로 메커니즘·연구 수치까지 보강.
- 엔딩 CTA(구독/좋아요/팔로우)는 카드뉴스·영상 둘 다 기본 자동 삽입
  (`end_card_duration` 기본 2.0초, 끄려면 0).

## 콘텐츠 QA — 완료 전 필수

```
python3 -m lib.content_review <topic> [lang]   # 논리 오류·과장·성의없는 대체재 검사
python3 -m lib.content_review --lang-check <base_topic>   # 다국어: 진짜 독립 리서치인지
```

- **새 topic은 narration.txt/card_news_spec.json 완성 시점에 `content_review` 통과가
  완료 조건**(다른 언어 추가 시 `--lang-check`도 함께). 플래그된 문제는 자동
  수정 안 됨 — 사람/세션이 판단해서 직접 고칠 것.
- ⚠️ **순서 고정: `content_review`/`--lang-check` 통과를 먼저 끝내고 나서 TTS를
  호출한다**(TTS 먼저 → 리뷰 → 재생성 순서 금지). "TTS는 1회만" 규칙(위
  "콘텐츠 톤" 절)과 짝인 규칙 — 리뷰를 나중에 하면 문제 발견 시 재생성
  압박이 생기니, 애초에 오디오화하기 전에 텍스트를 확정 짓는다.
- `--lang-check`에서 `is_translation: true`가 나오면 그 세션이 스스로 판단해서
  그 언어권 상황에 맞는 진짜 다른 각도로 다시 쓸 것(번역 금지 원칙, 아래 참고).

## 글로벌 확장

⚠️ **언어 범위 축소(2026-08-05)**: 진행 언어는 **한국어·영어·일본어·스페인어·
포르투갈어·러시아어 6개로 확정**("이렇게만 남기자"). 그 외 언어(대만어·
프랑스어·독일어·베트남어·아랍어·벵골어·터키어·태국어·인도네시아어·힌디어)는
data/output 콘텐츠 전부 삭제, `data/global_research_rules.md`·
`typecast_voices_global.json`·`global_channels.json`도 5개 언어(영/일/스/포/러)만
남기고 정리함. 새 topic·언어는 이 6개 범위 안에서만 진행할 것 — 확장이 다시
필요해지면 git 히스토리에서 복원.

- **번역 금지 — 언어마다 독립 리서치**(원인·해결책·이미지 전부 그 지역
  원문 자료 기준). topic(다룰 주제) 자체는 공통, 실질 콘텐츠만 독립.
- **글로벌 topic은 카드뉴스 없이 숏츠만** — `card_news.py generate()` 생략.
- **폴더 구조**: `data/<주제>/<lang>/`, `output/<주제>/<lang>/` 중첩(기존
  한국어 단일 topic은 flat 구조 그대로 유지, 소급 이전 안 함).
  `platform_captions.json`의 `"topic"` 필드는 `<주제>_<lang>` 형식으로 언어
  접미사 필수(localStorage 키 충돌 방지).
- 언어별 리서치 체크리스트는 `data/global_research_rules.md`(1차 타겟 국가,
  광고법·종교적 금기 식품 등) — 작성 전 필독. TTS 보이스는
  `data/typecast_voices_global.json`, 채널 인프라 상태는
  `data/global_channels.json`(언어별 `instagram_url` 포함 — Instagram Reels
  platform_captions.json의 `url` 필드는 항상 이 값으로 채울 것, 한국어 계정
  URL을 재사용하지 말 것).
- 폰트: 라틴 문자권은 `NotoSans-Bold.ttf`, 스크립트별 별도 폰트
  (`NotoSansArabic/Bengali/Devanagari/Thai/JP/TC-Bold.ttf`) 이미 연결 완료 —
  `_chalk_font_for_lang(lang)`/`_title_font_for_lang(lang)` 사용.
- 칠판 명패 풀은 14개 언어 문화별로 리서치 반영됨(`_NAMEPLATE_POOL_BY_LANG`).
- 유튜브: 채널당 별도 GCP 프로젝트, 계정은 한국+신규 4개 그룹으로 분리,
  발행 페이스 언어당 하루 2개(현지 시간 오전 10시·오후 6시,
  `--daily-per-channel`). 상세 근거는 archive의 "유튜브 정책 리스크 대응" 절.

## 대시보드 (`lib/dashboard.py`)

- `generate(spec_path, card_news_dir, video_path, out_path)` — 플랫폼별 카드
  HTML 생성, `output/topics.json` 자동 갱신. 유튜브 쇼츠/틱톡은
  `_UI_EXCLUDED_PLATFORMS`로 카드 자체가 안 뜬다(업로드 자동화됨/제외 결정).
- 다국어 topic은 `output/<topic>/dashboard.html`(통합 탭 페이지)이 언어별
  `output/<topic>/<lang>/dashboard.html`을 iframe으로 보여준다 — 영상 없는
  언어는 경량 폴백 카드(`_light_platform_card`).
- 완료 기록: `output/completed_topics.json`(topic 전체), 유튜브는
  `output/youtube_uploaded.json`, 상품 링크는 `output/product_links.json`
  (상품명→쿠팡 링크, 사용자가 채팅으로 주면 직접 추가), 포스팅 기록은
  `output/posting_log.csv`(브라우저 CSV 내보내기 → 커밋).

## GitHub Pages

`index.html`은 정적 에디터 — 실제 생성(PIL/TTS/ffmpeg)은 전부 로컬 세션에서.
서버 로직 불가 전제.

## 테스트

```bash
source .venv/bin/activate
python3 -m pytest tests/ -v
```

- `test_content_rules.py`는 `data/*/`의 모든 topic을 스캔해서 이 문서 규칙
  위반을 자동으로 잡는다(해시태그, 필수 플래그, 금지 표현, `char_file` 실존
  등) — **topic 작업 후 항상 이 테스트부터 돌릴 것.**
- Gemini/Kling/Typecast 등 유료 API는 테스트에서 절대 호출 안 함
  (`tests/conftest.py`의 합성 픽스처만 사용).

## 유튜브 쇼츠 자동 업로드 (`lib/youtube_upload.py`)

- 단일 topic: `python3 lib/youtube_upload.py <topic> [private|unlisted|public] [예약시각]`
- 하루 배치(사용자가 "업로드해" 지시할 때만 직접 트리거):
  `python3 lib/youtube_upload.py --daily-batch [privacy]` — 4개를
  10/13/16/19시(KST) 예약 게시. `select_daily_topics`가 다른 플랫폼에 이미
  포스팅된 topic을 우선 선택.
- 업로드 성공 시 자동으로: 카테고리 재생목록에 추가(중복 삽입 방지 확인 후),
  `output/youtube_uploaded.json`에 기록. 커스텀 썸네일 자동 설정은 하지 않음
  (결과 품질 문제로 제거) — 유튜브 자동 제안 또는 Studio 수동.
- OAuth 1회 설정은 archive의 "유튜브 쇼츠 자동 업로드" 절 참고(사용자가 직접
  해야 하는 단계 포함).

## 자료 위치

| 종류 | 위치 |
|------|------|
| 재사용 에셋 | `assets_library/{illust,real,motion}/` |
| 주제별 데이터 | `data/<주제>/` 또는 `data/<주제>/<lang>/` |
| 주제별 산출물 | `output/<주제>/` 또는 `output/<주제>/<lang>/` |
| 라이브러리 코드 | `lib/*.py` |
| 채널별 URL | `data/social_accounts.json` — 새 topic은 여기서 복사(예전 topic 복사 금지) |
| 비밀키 | `.env`(커밋 안 함), `.env.example` 최신 유지 |

## 대용량 미디어는 git에 안 올림 (2026-08-05)

레포 용량이 2.35GB까지 불어나서, 아래는 **로컬에만 유지하고 git엔 커밋하지
않는다**(`.gitignore`에 이미 반영됨 — `git add`해도 자동으로 무시됨):

- `assets_library/{illust,real,motion}/` 전부
- `output/**/*.mp4`(원본·인스타그램 안전여백 버전 둘 다)
- `output/**/card_news/*.jpg` 중 표지(`*_00_표지.jpg`)를 제외한 나머지
  (표지는 루트 목록 페이지 썸네일용으로 계속 추적)

사용자가 대시보드 미리보기/다운로드로 업로드하지 않고 로컬 `output/` 폴더에서
직접 파일을 가져다 쓰는 방식이라, git으로 서빙할 필요가 없어져서 내린 결정.
**영상·이미지 생성 코드는 그대로다** — 파일은 여전히 로컬에 정상적으로
만들어지고, git이 추적만 안 할 뿐이다. `assets_library/{backgrounds,fonts,
channel_banners}/`는 코드가 직접 참조하는 공용 리소스라 계속 추적한다.

⚠️ **여러 워크트리를 쓸 때 이 파일들을 다른 워크트리로 병합하지 말 것** —
`git rm --cached`(추적만 해제, 로컬 파일 보존)로 만든 커밋을 다른 워크트리에
`git merge`로 반영하면, 그 워크트리 디스크에 있던 실제 파일이 통째로
삭제된다(2026-08-05 실제 발생 — merge가 "트리에서 사라진 파일"을 일반
삭제로 처리해서 벌어짐, `git checkout <이전커밋> --pathspec-from-file=...`로
복구함). 이런 종류(파일은 남기고 추적만 빼는) 변경은 항상 메인 워크트리에서
직접 `git rm --cached` + commit + push로 끝낼 것 — 워크트리에서 만들어서
병합하지 말 것.

⚠️ 이미 커밋된 과거 버전은 git 히스토리에 그대로 남아있어서, 위 조치만으로는
레포의 실제 저장 용량(2.35GB)이 안 줄어든다 — 앞으로의 증가만 막는다.
히스토리 자체를 줄이려면 `git filter-repo` + force-push가 필요한데, 여러
세션이 동시에 이 레포를 쓰고 있어서 그건 각 세션의 로컬 클론을 깨뜨리는
파괴적 작업이다 — 사용자 확인 없이 진행하지 말 것.

## 주의사항

- `bin/`(Rhubarb), `.venv/`는 gitignored.
- `.venv/` 새로 만들 때: `python3.11 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
- 커밋 시 `.env` 포함 여부 항상 재확인.
- 로컬 확인은 `open output/<주제>/dashboard.html` — Pages 푸시는 모바일 업로드
  때만 필요, 매번 기다릴 필요 없음.
