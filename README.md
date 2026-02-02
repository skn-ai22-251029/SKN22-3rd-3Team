# 🐱 ZIPSA (AI Cat Butler) - Execution Guide

본 문서는 프로젝트 가동을 위한 실제 실행 루틴만을 기술합니다.

## 1. 환경 설정 (Setup)
```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정 (.env 파일 생성 및 API 키 입력)
# OPENAI_API_KEY, MONGO_V3_URI, THECATAPI_API_KEY, OPENAPI_API_KEY 필수
```

## 2. 데이터 파이프라인 가동 (Data Pipeline V3)
원천 데이터 수집부터 검색 엔진 적재까지의 전체 공정입니다.

### **[Step 1] 원천 데이터 수집 ([Crawl](./scripts/crawl))**
```bash
python scripts/crawl/crawl_thecatapi.py  # 결과: data/raw/cat_breeds_thecatapi.json
python scripts/crawl/crawl_wiki.py       # 결과: data/raw/cat_breeds_wiki_info.json
python scripts/crawl/crawl_bemypet.py    # 결과: data/raw/bemypet_catlab.json
```

### **[Step 2] 데이터 통합 (Integration)**
```bash
# 묘종 마스터 데이터 통합 및 정규화
python scripts/process/preprocess_integrated_breeds.py  # 결과: data/cat_breeds_integrated.json
```

### **[Step 3] 도메인 사전 빌드**
```bash
python scripts/build_domain_dict.py      # 결과: src/core/tokenizer/domain_dictionary.txt
```

### **[Step 4] 3단계 자동화 공정 실행 (Pipeline V3)**
```bash
# 1. 아티클 데이터 처리 (V3)
python scripts/v3/run_preprocess.py      # 결과: data/v3/processed.json (임베딩 및 로드 포함 가능)

# 2. 묘종 데이터 통합 처리 (V3 + Policy)
python scripts/process_breeds_v3.py      # 결과: MongoDB cat_library.care_guides (이미지 매칭 포함)
```

## 3. 애플리케이션 실행 (Application)
```bash
# Streamlit 기반 AI 집사 인터페이스 기동
streamlit run src/ui/app.py
```

## 4. 에이전트 아키텍처

```
User → Head Butler (라우터) → Matchmaker | Care Team | Liaison → Head Butler → Response
```

- **Head Butler**: 사용자 의도 분류 및 최적 전문가 라우팅. 일반 질문은 직접 응답.
- **Matchmaker**: 품종 추천 전문가. 10건 RAG 검색 후 LLM이 상위 3건을 선별(Agentic Selection).
- **Care Team**: 건강(의료) + 행동(교정) 통합 상담. RAG 기반 응답 생성.
- **Liaison**: 입양/구조 정보 전문가. 국가동물보호정보시스템 API 연동(`search_abandoned_animals` Tool).

## 5. 실험 및 벤치마크 ([Notebooks](./src/notebooks))
`src/notebooks/` 디렉토리의 Jupyter Notebook을 통해 각 모듈의 개별 실험 및 성능 측정이 가능합니다.

- **[`tokenizer_experiment.ipynb`](./src/notebooks/tokenizer_experiment.ipynb)**: Kiwi 형태소 분석기 및 도메인 사전 토큰화 실험.
- **[`retriever_experiment.ipynb`](./src/notebooks/retriever_experiment.ipynb)**: 하이브리드 검색(RRF) 성능 벤치마킹 및 파라미터 튜닝.
- **[`agent_prompt_experiment.ipynb`](./src/notebooks/agent_prompt_experiment.ipynb)**: 각 전문가 에이전트별 프롬프트 최적화 및 페르소나 테스트.
- **[`debug_langgraph.ipynb`](./src/notebooks/debug_langgraph.ipynb)**: LangGraph 전이 로직 및 상태 관리 디버깅.