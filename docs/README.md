# 📄 Documentation (`docs/`)

본 디렉토리는 프로젝트의 비전 기획부터 기술적 설계 규격, 파이프라인 전략 및 실무 가이드를 관리하는 통합 문서 보관소입니다.

---

## 📂 디렉토리 및 핵심 파일 명세

### 1. [01_project](./01_project) (비전 및 구조)
- **`overview.md`**: 전담 전문가 에이전트 시스템(ZIPSA)의 기획 의도와 핵심 가치 제언.
- **`personas.md`**: `Head Butler`, `Matchmaker`, `Physician` 등 4대 전문가 페르소나의 행동 강령 및 역할 정의.
- **`architecture_graph.md`**: LangGraph의 계층적 토폴로지 및 데이터 흐름 다이어그램.

### 2. [02_convention](./02_convention) (개발 표준)
- **`workflow_rules.md`**: Git 브랜치 전략(Git Flow), 커밋 메시지 규격 및 협업 워크플로우.
- **`naming_guide.md`**: 변수, 함수, 클래스 및 파일 시스템 명명 규칙 가이드라인.

### 3. [03_api](./03_api) (외부 연동 규격)
- **`thecatapi_spec.md` / `thecatapi-oas.yaml`**: TheCatAPI 기반 묘종 데이터 수집 인터페이스 정의.
- **`openapi_spec.md`**: OpenAI 임베딩 및 Chat Completion API 활용 프로토콜.
- **`hospital_search_v2-3.md`**: 지역 기반 동물병원 검색 기능 설계 문서.

### 4. [04_data](./04_data) (데이터 전략)
- **`v3_pipeline_strategy_report.md`**: 검샘 품질을 위한 **구조적 임베딩(Structured Embedding)** 전략 보고서.
- **`v3_pipeline_flow.md`**: V3 파이프라인의 3단계 자동화 공정 시각화 문서.
- **`data_preprocessing_report_v1~v3.md`**: 각 세대별 데이터 정제 및 메타데이터 추출 결과 데이터.

### 5. [05_feature](./05_feature) (기능 명세)
- **`auth_profile_spec.md`**: 사용자 인증 및 반려묘 프로필 관리 로딕 상세.
- **`cat_card_spec.md`**: 묘종 검색 결과 시각화(Cat Identity Card) 컴포넌트 규격.

### 6. [05_guides](./05_guides) (매뉴얼)
- **`mongodb_setup_guide.md`**: MongoDB Atlas 벡터 검색 인덱스 및 키워드 검색 설정 가이드.

### 7. [report](./report) (성과 관리)
- **`checklist.md`**: 프로젝트 완성도 자가 점검 및 11개 영역별 피드백 리스트.

### 8. [dev_logs](./dev_logs) (기록)
- 일자별 기술적 의사결정(ADR) 및 트러블슈팅 내역 보관 (`YYYY-MM-DD.md`).
