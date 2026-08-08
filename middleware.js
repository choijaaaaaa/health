// WHY(2026-08-08, "비밀번호 게트 추가"): Vercel Hobby 플랜은 비밀번호 보호가
// Pro 전용("Advanced Deployment Protection")이라 못 쓴다 — 대신 프레임워크
// 상관없이 동작하는 Edge Middleware로 Basic Auth를 직접 구현한다. 상품 링크·
// 미공개 topic 목록까지 보이는 관리 페이지라, URL만 알면 누구나 들어올 수 있는
// 상태를 막는 게 목적이라 사용자 구분 없이 비밀번호 하나만 확인한다.
export const config = { matcher: "/(.*)" };

export default function middleware(request) {
  const expected = "Basic " + btoa(`admin:${process.env.HS_ADMIN_PASSWORD}`);
  const auth = request.headers.get("authorization");
  if (auth === expected) {
    return;
  }
  return new Response("Authentication required", {
    status: 401,
    headers: { "WWW-Authenticate": 'Basic realm="health-shorts"' },
  });
}
