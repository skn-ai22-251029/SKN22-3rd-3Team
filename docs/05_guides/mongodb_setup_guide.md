# MongoDB Atlas 인덱스 설정 가이드

하이브리드 검색(Hybrid Search)을 정상적으로 작동시키기 위해 MongoDB Atlas UI에서 다음 두 종류의 인덱스를 생성해야 합니다.

## 1. Vector Search 인덱스 설정
`breeds`와 `care_guides` 컬럼 각각에 대해 다음 설정을 적용하세요.

- **Index Name:** `vector_index`
- **Configuration (JSON):**
```json
{
  "fields": [
    {
      "numDimensions": 1536,
      "path": "embedding",
      "similarity": "cosine",
      "type": "vector"
    },
    {
      "path": "category",
      "type": "filter"
    }
  ]
}
```

## 2. Atlas Search (BM25) 인덱스 설정
키워드 검색을 위해 `breeds`와 `care_guides` 컬럼 각각에 대해 다음 설정을 적용하세요.

- **Index Name:** `keyword_index`
- **Configuration (Visual/JSON):**
```json
{
  "mappings": {
    "dynamic": false,
    "fields": {
      "tokenized_text": {
        "type": "string",
        "analyzer": "lucene.standard"
      }
    }
  }
}
```

---

### ✅ 확인 사항
1. `.env` 파일에 `MONGO_URI`가 올바르게 설정되어 있는지 확인하세요.
2. `scripts/ingest_to_mongodb.py`를 실행하여 데이터를 업로드하세요.
3. 인덱스 생성이 완료(Active 상태)된 후 `src/retrieval/hybrid_search.py`를 통해 검색을 테스트할 수 있습니다.
