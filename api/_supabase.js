// service_role 키로 Supabase REST(PostgREST)를 직접 두드리는 공용 헬퍼.
// WHY SDK 대신 fetch인지: 이 프로젝트는 빌드 스텝이 없는 정적 배포라
// package.json/node_modules가 없다 — @supabase/supabase-js를 쓰려면 그걸
// 새로 들여야 하는데, PostgREST는 그냥 REST라 네이티브 fetch만으로 충분하다.
const SUPABASE_URL = process.env.SUPABASE_URL;
const SERVICE_ROLE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY;

function headers(extra) {
  return {
    apikey: SERVICE_ROLE_KEY,
    Authorization: `Bearer ${SERVICE_ROLE_KEY}`,
    "Content-Type": "application/json",
    ...extra,
  };
}

async function upsert(table, rows) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${table}`, {
    method: "POST",
    headers: headers({ Prefer: "resolution=merge-duplicates,return=minimal" }),
    body: JSON.stringify(rows),
  });
  if (!res.ok) throw new Error(`${table} upsert 실패 ${res.status}: ${await res.text()}`);
}

async function deleteRows(table, query) {
  const res = await fetch(`${SUPABASE_URL}/rest/v1/${table}?${query}`, {
    method: "DELETE",
    headers: headers(),
  });
  if (!res.ok) throw new Error(`${table} delete 실패 ${res.status}: ${await res.text()}`);
}

module.exports = { upsert, deleteRows };
