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

create table if not exists completed_topics (
  base_topic text primary key,
  completed_at timestamptz not null default now()
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

create table if not exists youtube_uploaded (
  topic text primary key,
  uploaded_at timestamptz not null default now()
);

alter table topics enable row level security;
alter table completed_topics enable row level security;
alter table posting_log enable row level security;
alter table product_links enable row level security;
alter table global_product_links enable row level security;
alter table youtube_uploaded enable row level security;

-- WHY anon 롤에 전체 권한을 주는지: 이 프로젝트는 다수 사용자를 상대하는
-- 공개 서비스가 아니라 index.html이 Vercel Basic Auth로 페이지 자체를 가린
-- 1인 운영 관리 도구다 — anon key는 클라이언트에 그대로 노출되는 게 전제라
-- RLS로 세밀한 사용자별 권한을 나눌 대상이 없다. 실제 접근 제어는 Vercel
-- 미들웨어의 비밀번호 게이트가 담당한다.
create policy "anon full access" on topics for all to anon using (true) with check (true);
create policy "anon full access" on completed_topics for all to anon using (true) with check (true);
create policy "anon full access" on posting_log for all to anon using (true) with check (true);
create policy "anon full access" on product_links for all to anon using (true) with check (true);
create policy "anon full access" on global_product_links for all to anon using (true) with check (true);
create policy "anon full access" on youtube_uploaded for all to anon using (true) with check (true);
