# 📜 Scripts (`scripts/`)

데이터 수집(Crawl)부터 정제(Process), 검증(Validate), 그리고 검색 엔진 적재(Load)까지 이어지는 전체 데이터 파이프라인 운영을 전담하는 도구 모음입니다.

---

## 🏗️ Data Pipeline (3-Stage Workflow)

본 프로젝트는 데이터의 원천 수집부터 최종 검색 인덱스 서비스까지 **3단계(3-Stage)** 자동화 파이프라인을 구축하여 관리합니다. 각 단계는 `./v1/`, `./v2/`, `./v3/`와 같이 세대별로 구분된 세 개의 실행 스크립트 팩을 통해 동작합니다.

### **[현재 활성 파이프라인: V3]**
V3 파이프라인은 고수준의 의미론적 검색을 위해 **LLM 기반 구조화**와 **비동기 병렬 임베딩** 공정을 포함합니다.

1.  **Stage 1: Preprocess (`run_preprocess.py`)**
    - **입력**: `data/raw/bemypet_catlab.json` (Raw Data)
    - **핵심 로직**: `src/pipelines/v3/preprocessor.py`
    - **기술**: **GPT-4o-mini**를 이용한 배치(Batch 5) 분류 및 요약 추출 + **Kiwi** 기반 한국어 토큰화.
    - **결과**: `data/v3/processed.json` 생성.
2.  **Stage 2: Embed (`run_embed.py`)**
    - **입력**: `data/v3/processed.json`
    - **핵심 로직**: `src/pipelines/v3/embedder.py`
    - **기술**: **OpenAI text-embedding-3-small** 사용. `asyncio.Semaphore`를 이용한 5개 병렬 세션 처리 (Batch 100).
    - **결과**: `data/v3/embedded.pkl` (Pickle format) 생성.
3.  **Stage 3: Load (`run_load.py`)**
    - **입력**: `data/v3/embedded.pkl`
    - **핵심 로직**: `src/pipelines/v3/loader.py`
    - **기술**: MongoDB Atlas의 `cat_library` 데이터베이스에 비동기 Upsert 연동.
    - **결과**: 벡터 검색(Vector Search) 및 키워드 검색 인덱스 즉각 반영.

---

## 📂 디렉토리 및 개별 스크립트 명세

### 1. [crawl/](./crawl) - 데이터 수집 엔진
- `crawl_wiki.py`: Wikipedia 고양이 품종 정보를 가공하기 쉬운 JSON 형태로 수합합니다.
- `crawl_catapi.py`: TheCatAPI를 호출하여 67종 묘종의 기본 스펙 및 이미지 정보를 수집합니다.
- `crawl_bemypet.py`: BemyPet Catlab 아티클을 동적으로 크롤링하여 지식 베이스의 원천을 확보합니다.

### 2. [process/](./process) - 도메인 가공 및 지능화
- `build_domain_dict.py`: 원천 데이터와 사전을 분석하여 서비스 특화 형태소 분석 사전(`domain_dictionary.txt`)을 빌드합니다.
- `process_breeds_v3.py`: 수집된 67종 묘종의 통계치와 특징을 V3 스키마에 맞춰 고도화 가공합니다.
- `preprocess_integrated_breeds.py`: 중복된 묘종 정보를 제거하고 명칭을 정규화합니다.

### 3. [validate/](./validate) - 품질 및 성능 검증
- `validate_bemypet.py` / `validate_wiki.py`: 전처리 전후 데이터의 스키마 정확도 및 필수 필드 누락 여부를 검사합니다.
- `generate_testset.py`: 검색 엔진의 성능(Hit@3, MRR 등)을 정량적으로 측정하기 위한 **Golden Dataset**을 생성합니다.

---

## 🛠️ 실행 가이드 (V3 Pipeline 예시)
```bash
# 1. 전처리 및 LLM 기반 메타데이터 추출
python scripts/v3/run_preprocess.py

# 2. 비동기 병렬 임베딩 생성 (OpenAI)
python scripts/v3/run_embed.py

# 3. MongoDB Atlas 'cat_library' 적재
python scripts/v3/run_load.py
```
