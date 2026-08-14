// WHY(2026-08-08, "비밀번호 게트 추가"): Vercel Hobby 플랜은 비밀번호 보호가
// Pro 전용("Advanced Deployment Protection")이라 못 쓴다 — 대신 프레임워크
// 상관없이 동작하는 Edge Middleware로 Basic Auth를 직접 구현한다. 상품 링크·
// 미공개 topic 목록까지 보이는 관리 페이지라, URL만 알면 누구나 들어올 수 있는
// 상태를 막는 게 목적이라 사용자 구분 없이 비밀번호 하나만 확인한다.
export const config = { matcher: "/(.*)" };

// WHY rate limit 추가(2026-08-15, 보안 점검 중 발견): 이 Basic Auth엔 무차별
// 대입 시도를 막는 장치가 전혀 없었다 — vernhaven-blog 계열 admin 로그인엔
// 이미 있는데(lib/rate-limit.ts) 여긴 없어서 비대칭이었다. 같은 패턴(서버리스
// 인스턴스 메모리 기반 — 완벽하진 않지만 이 규모엔 충분, 인스턴스 재시작·
// 여러 인스턴스 분산 시 리셋됨) 그대로 이식.
const buckets = new Map();
const RATE_LIMIT = 10; // 창당 최대 시도 횟수
const WINDOW_MS = 10 * 60 * 1000; // 10분

function isRateLimited(key) {
  const now = Date.now();
  const bucket = buckets.get(key);
  if (!bucket || now > bucket.resetAt) {
    buckets.set(key, { count: 1, resetAt: now + WINDOW_MS });
    return false;
  }
  bucket.count += 1;
  return bucket.count > RATE_LIMIT;
}

function getClientIp(request) {
  const forwarded = request.headers.get("x-forwarded-for");
  return forwarded?.split(",")[0]?.trim() ?? "unknown";
}

export default function middleware(request) {
  // WHY 실패한 시도만 카운트하는지: Basic Auth는 브라우저가 한 번 입력한
  // 인증 헤더를 그 뒤 모든 요청(페이지+에셋+API 호출 전부)에 자동으로
  // 다시 실어 보낸다 — 성공한 요청까지 다 세면 정상적으로 페이지 하나
  // 여는 것만으로도 정상 사용자가 스스로 잠길 수 있다. 무차별 대입만
  // 막으면 되므로 실패한 시도만 버킷에 쌓는다.
  const expected = "Basic " + btoa(`admin:${process.env.HS_ADMIN_PASSWORD}`);
  const auth = request.headers.get("authorization");
  if (auth === expected) {
    return;
  }

  const ip = getClientIp(request);
  if (isRateLimited(ip)) {
    return new Response("Too many attempts. Try again later.", { status: 429 });
  }

  return new Response("Authentication required", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="health-shorts"' },
  });
}
