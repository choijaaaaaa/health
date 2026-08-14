// completed_topics 쓰기 전용 엔드포인트. WHY 서버 경유인지: api/posting-log.js
// 상단 주석과 동일 — anon key가 다른 프로젝트와 공유되면 "anon 전체 허용" RLS가
// 구멍이 된다. 인증은 middleware.js가 /api/*까지 이미 Basic Auth로 막는다.
const { upsert, deleteRows } = require("./_supabase");

module.exports = async (req, res) => {
  if (req.method === "POST") {
    const { rows } = req.body || {};
    if (!Array.isArray(rows) || rows.length === 0) {
      return res.status(400).json({ error: "rows(배열) 필요" });
    }
    for (const r of rows) {
      if (!r.base_topic || !r.track) {
        return res.status(400).json({ error: "각 행에 base_topic/track 필요" });
      }
    }
    try {
      await upsert("completed_topics", rows);
      return res.status(200).json({ ok: true });
    } catch (e) {
      return res.status(500).json({ error: String(e) });
    }
  }

  if (req.method === "DELETE") {
    const { base_topic } = req.body || {};
    if (!base_topic) {
      return res.status(400).json({ error: "base_topic 필요" });
    }
    try {
      await deleteRows("completed_topics", `base_topic=eq.${encodeURIComponent(base_topic)}`);
      return res.status(200).json({ ok: true });
    } catch (e) {
      return res.status(500).json({ error: String(e) });
    }
  }

  res.setHeader("Allow", "POST, DELETE");
  return res.status(405).end();
};
