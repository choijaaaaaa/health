// product_links(topic별) 쓰기 전용 엔드포인트 — lib/dashboard.py가 생성하는
// 각 topic dashboard.html이 호출한다. WHY 서버 경유인지: api/posting-log.js
// 상단 주석과 동일. 인증은 middleware.js가 /api/*까지 이미 Basic Auth로 막는다.
const { upsert, deleteRows } = require("./_supabase");

module.exports = async (req, res) => {
  if (req.method === "POST") {
    const { topic, market, product, url } = req.body || {};
    if (!topic || !market || !product || !url) {
      return res.status(400).json({ error: "topic/market/product/url 필요" });
    }
    try {
      await upsert("product_links", [{ topic, market, product, url }]);
      return res.status(200).json({ ok: true });
    } catch (e) {
      return res.status(500).json({ error: String(e) });
    }
  }

  if (req.method === "DELETE") {
    const { topic, market, product } = req.body || {};
    if (!topic || !market || !product) {
      return res.status(400).json({ error: "topic/market/product 필요" });
    }
    try {
      await deleteRows(
        "product_links",
        `topic=eq.${encodeURIComponent(topic)}&market=eq.${encodeURIComponent(market)}&product=eq.${encodeURIComponent(product)}`
      );
      return res.status(200).json({ ok: true });
    } catch (e) {
      return res.status(500).json({ error: String(e) });
    }
  }

  res.setHeader("Allow", "POST, DELETE");
  return res.status(405).end();
};
