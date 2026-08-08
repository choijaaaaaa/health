// health-shorts 관리 데이터(topics/completed_topics/posting_log/product_links/
// youtube_uploaded) 공용 Supabase 클라이언트. index.html과 lib/dashboard.py가
// 생성하는 모든 topic dashboard.html이 이 파일을 루트 절대경로(/supabase_client.js)로
// 불러와 공유한다 — anon key는 RLS로 접근 제어되는 공개 키라 여기 그대로 둬도 된다.
window.HS_SUPABASE_URL = "https://feqjksocdkjqwbeugaiw.supabase.co";
window.HS_SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZlcWprc29jZGtqcXdiZXVnYWl3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODYxNzgwOTYsImV4cCI6MjEwMTc1NDA5Nn0.f0ZacCpKcjr3weFCLX4QZfU9ejB5tbjEXJs6hZzZrTA";
