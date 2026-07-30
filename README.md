# health

건강 정보 카드뉴스 자동 생성기. 뉴스/자료를 정리한 JSON 스펙을 입력하면 PIL로 카드 이미지를 합성해 출력한다.

## 구조

```
health-shorts/
├── health/<주제>/       캐릭터 원본 이미지(카드에 들어갈 인물/사물 일러스트)
├── data/<주제>/          card_news_spec.json (제목·항목별 텍스트·마무리 문구)
├── lib/card_news.py      카드 이미지 생성 스크립트
└── output/<주제>/card_news/  생성된 카드 이미지(.jpg)
```

## 실행

```bash
pip install -r requirements.txt
python3 lib/card_news.py data/<주제>/card_news_spec.json health/<주제> output/<주제>/card_news
```

## card_news_spec.json 형식

```json
{
  "title": ["표지 제목 줄1", "줄2"],
  "items": [
    { "name": "항목명", "char_file": "캐릭터파일명.jpg", "body": ["본문 줄1", "줄2"] }
  ],
  "closing": {
    "headline": [["마무리 줄1", "줄2"]],
    "tip": ["팁 줄1", "줄2"],
    "cta": "행동유도 문구"
  }
}
```

`lib/card_news.py`의 `generate()`가 표지 → 항목별 카드 → 마무리 카드 순으로 이미지를 만든다.
