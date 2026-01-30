# 🐱 ZIPSA (AI Cat Butler) - Execution Guide

본 문서는 프로젝트 가동을 위한 실제 실행 루틴만을 기술합니다.

## 1. 환경 설정 (Setup)
```bash
# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정 (.env 파일 생성 및 API 키 입력)
# OPENAI_API_KEY, MONGODB_URI 등 필수
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
python scripts/build_domain_dict.py      # 결과: src/core/domain_dictionary.txt
```

### **[Step 4] 3단계 자동화 공정 실행 ([Pipeline V3](./scripts/v3))**
```bash
# 1. 전처리 및 LLM 메타데이터 추출
python scripts/v3/run_preprocess.py      # 결과: data/v3/processed.json

# 2. 비동기 병렬 임베딩 생성
python scripts/v3/run_embed.py           # 결과: data/v3/embedded.pkl

# 3. MongoDB Atlas 최종 적재
python scripts/v3/run_load.py            # 결과: MongoDB Atlas (Vector Search 적용)
```

## 3. 애플리케이션 실행 (Application)
```bash
# Streamlit 기반 AI 집사 인터페이스 기동
streamlit run src/ui/app.py
```

## 4. 실험 및 벤치마크 ([Notebooks](./src/notebooks))
`src/notebooks/` 디렉토리의 Jupyter Notebook을 통해 각 모듈의 개별 실험 및 성능 측정이 가능합니다.

- **[`tokenizer_experiment.ipynb`](./src/notebooks/tokenizer_experiment.ipynb)**: Kiwi 형태소 분석기 및 도메인 사전 토큰화 실험.
- **[`retriever_experiment.ipynb`](./src/notebooks/retriever_experiment.ipynb)**: 하이브리드 검색(RRF) 성능 벤치마킹 및 파라미터 튜닝.
- **[`agent_prompt_experiment.ipynb`](./src/notebooks/agent_prompt_experiment.ipynb)**: 각 전문가 에이전트별 프롬프트 최적화 및 페르소나 테스트.
- **[`debug_langgraph.ipynb`](./src/notebooks/debug_langgraph.ipynb)**: LangGraph 전이 로직 및 상태 관리 디버깅.