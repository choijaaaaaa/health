// posting_log 쓰기 전용 엔드포인트. WHY 서버 경유인지: 이 write는 원래
// index.html이 anon key로 직접 했다 — anon key가 다른 프로젝트(vernhaven-blog
// 계열)와 Supabase 프로젝트를 공유하게 되면서 그쪽 퍼블릭 사이트 브라우저
// 번들에도 같은 anon key가 노출되므로, RLS를 "anon 전체 허용"으로 두면
// 누구나 이 테이블을 읽고 쓰고 지울 수 있게 된다. 인증은 이 함수 자체가 아니라
// middleware.js의 matcher("/(.*)")가 /api/*까지 포함해서 이미 Basic Auth로
// 막고 있다 — 여기서 다시 확인할 필요 없음.
const { upsert, deleteRows } = require("./_supabase");

module.exports = async (req, res) => {
  if (req.method === "POST") {
    const { topic, platform, posted_at } = req.body || {};
    if (!topic || !platform || !posted_at) {
      return res.status(400).json({ error: "topic/platform/posted_at 필요" });
    }
    try {
      await upsert("posting_log", [{ topic, platform, posted_at }]);
      return res.status(200).json({ ok: true });
    } catch (e) {
      return res.status(500).json({ error: String(e) });
    }
  }

  if (req.method === "DELETE") {
    const { topic, platform } = req.body || {};
    if (!topic || !platform) {
      return res.status(400).json({ error: "topic/platform 필요" });
    }
    try {
      await deleteRows(
        "posting_log",
        `topic=eq.${encodeURIComponent(topic)}&platform=eq.${encodeURIComponent(platform)}`
      );
      return res.status(200).json({ ok: true });
    } catch (e) {
      return res.status(500).json({ error: String(e) });
    }
  }

  res.setHeader("Allow", "POST, DELETE");
  return res.status(405).end();
};
