// global_product_links 쓰기 전용 엔드포인트. WHY 서버 경유인지: api/posting-log.js
// 상단 주석과 동일. 인증은 middleware.js가 /api/*까지 이미 Basic Auth로 막는다.
const { upsert } = require("./_supabase");

module.exports = async (req, res) => {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).end();
  }

  const { market, product, url } = req.body || {};
  if (!market || !product || !url) {
    return res.status(400).json({ error: "market/product/url 필요" });
  }
  try {
    await upsert("global_product_links", [{ market, product, url }]);
    return res.status(200).json({ ok: true });
  } catch (e) {
    return res.status(500).json({ error: String(e) });
  }
};
