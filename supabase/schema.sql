-- health-shorts 관리 데이터 스키마 (2026-08-08 도입)
-- WHY: completed_topics.json/posting_log.csv/product_links.json/youtube_uploaded.json이
-- git 파일이라 브라우저에서 직접 못 쓰고 CSV 왕복·채팅 갱신을 거쳐야 했다 —
-- index.html이 Vercel에 배포되면서 이 다섯 테이블로 옮겨 브라우저가 직접 읽고 쓴다.
-- asset/video/카드뉴스 이미지는 로컬 전용이라 DB로 옮기지 않는다.

create table if not exists topics (
  topic text primary key,
  title text,
  url text,
  thumbnail text,
  ad_tag boolean not null default false,
  tracks text[] not null default '{}',
  updated_at timestamptz not null default now()
);

-- WHY (base_topic, track) 복합키인지(2026-08-09, "숏츠 탭이랑 카드뉴스 탭이
-- 같이반영되는건데... 숏츠쪽 다 끝나면 눌러서 그쪽 목록에 반영하고 카드뉴스에서
-- 눌르면 카드뉴스쪽 목록에 반영하고 그래야지"): base_topic 하나가 숏츠·카드뉴스
-- 두 트랙을 동시에 가질 수 있는데, base_topic만 키였을 때는 완료 체크가
-- 트랙 구분 없이 topic 전체에 적용돼 한쪽만 끝내도 다른 쪽 목록에서도 사라졌다.
create table if not exists completed_topics (
  base_topic text not null,
  track text not null,
  completed_at timestamptz not null default now(),
  primary key (base_topic, track)
);

-- WHY (topic, platform) 복합키인지: 체크박스 하나가 "이 플랫폼에 이 topic을
-- 올렸다"는 상태 하나만 표현한다(누적 이력이 아니라 토글) — 체크 해제하면
-- 행 자체가 삭제된다. 이름은 posting_log지만 실제로는 posting_status에 가깝다.
create table if not exists posting_log (
  topic text not null,
  platform text not null,
  posted_at timestamptz not null,
  primary key (topic, platform)
);

create table if not exists product_links (
  topic text not null,
  market text not null,
  product text not null,
  url text not null,
  updated_at timestamptz not null default now(),
  primary key (topic, market, product)
);

-- WHY product_links와 별개 테이블인지: product_links는 index.html 개별 topic
-- 대시보드 입력창(hs_link_<topic>_<market>_<product>)에서 나온 topic별 링크고,
-- 이 테이블은 lib/dashboard.py가 대시보드 생성 시 참조하는 상품명→링크 전역
-- 캐시(output/product_links.json=쿠팡, output/naver_product_links.json=네이버)다
-- — 같은 상품이 여러 topic에 반복 등장해도 한 번만 등록해두면 재사용된다.
create table if not exists global_product_links (
  market text not null,
  product text not null,
  url text not null,
  updated_at timestamptz not null default now(),
  primary key (market, product)
);

-- WHY 컬럼 확장(2026-08-15, lib/youtube_upload.py 재작성과 함께): 이전엔
-- topic/uploaded_at 두 컬럼뿐이라 "이미 올렸다/안 올렸다"만 표현했는데, 그
-- 판단 근거가 로컬 output/youtube_uploaded.json(git 추적 파일)이었다가 실제로
-- 두 번 사고(무관한 커밋이 기록 유실 → backlog 재업로드, 동시 세션 경쟁)가
-- 나서 이 테이블을 Python 업로드 스크립트의 실제 판단 근거로 승격했다 —
-- video_id/privacy_status/publish_at은 그 근거로 쓰기 위한 실제 업로드 결과,
-- status는 'pending'(예약만 됨, API 호출 전/중)|'confirmed'(업로드 완료) 두
-- 값 — topic이 PRIMARY KEY라 이 테이블 자체가 유일성을 보장하고,
-- `_sb_reserve_upload()`가 실제 업로드 API를 부르기 전에 여기 INSERT를
-- 먼저 시도해서(PK 충돌 시 조용히 실패) 두 세션이 같은 topic을 동시에
-- 올리는 경쟁 조건을 막는다 — 상세는 lib/youtube_upload.py 상단 WHY,
-- health-shorts CLAUDE.md "유튜브 쇼츠 자동 업로드" 절 참고.
create table if not exists youtube_uploaded (
  topic text primary key,
  uploaded_at timestamptz not null default now(),
  video_id text,
  lang text,
  privacy_status text,
  publish_at timestamptz,
  status text not null default 'confirmed'
);

alter table topics enable row level security;
alter table completed_topics enable row level security;
alter table posting_log enable row level security;
alter table product_links enable row level security;
alter table global_product_links enable row level security;
alter table youtube_uploaded enable row level security;

-- WHY anon이 읽기 전용으로 바뀌었는지(2026-08-14, 이전엔 "anon 전체 허용"):
-- 이 Supabase 프로젝트를 vernhaven-blog 계열(공유 Supabase, 퍼블릭 사이트)과
-- 나눠 쓰게 되면서, 그쪽 앱들의 anon key가 브라우저에 그대로 노출된다는
-- 사실이 이 프로젝트에도 그대로 적용된다 — "anon 전체 허용"을 유지하면
-- 그 공유 anon key로 아무나 이 관리 테이블을 읽고 쓰고 지울 수 있는 구멍이
-- 생긴다(Vercel Basic Auth는 index.html 페이지 자체만 가릴 뿐, Supabase REST
-- API는 그 게이트를 우회해서 직접 두드릴 수 있음). 그래서 실제 쓰기는 전부
-- service_role 키를 쓰는 /api/*.js 서버 함수로 옮기고(그 함수들은
-- middleware.js의 matcher("/(.*)")가 이미 Basic Auth로 막아준다), anon은
-- index.html이 대시보드를 그리는 데 필요한 select만 남긴다.
create policy "anon read" on topics for select to anon using (true);
create policy "anon read" on completed_topics for select to anon using (true);
create policy "anon read" on posting_log for select to anon using (true);
create policy "anon read" on product_links for select to anon using (true);
create policy "anon read" on global_product_links for select to anon using (true);
create policy "anon read" on youtube_uploaded for select to anon using (true);
