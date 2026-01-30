# 📂 Data Assets (`data/`)

본 프로젝트에서 사용되는 데이터셋을 원천(Raw)과 가공(v1, v2, v3) 단계로 구분하여 관리합니다.

## 📂 디렉토리 구조 및 데이터 명세

### 0. [raw/](./raw) (원천 데이터)
수집 엔진을 통해 확보한 정제 전 원시 데이터셋입니다.
- **`bemypet_catlab.json`**: BemyPet Catlab 아티클 원본.
- **`cat_breeds_thecatapi.json`**: TheCatAPI 기반 묘종 기본 데이터.
- **`cat_breeds_wiki_info.json`**: Wikipedia 추가 정보 수집본.
- **`cat_breeds.csv`**: 품종 마스터 리스트.
- **`cat_cafes.json`**: 고양이 카페 위치 정보.
- **`동물병원.csv`**: 전국 동물병원 위치 정보.
- **`youtube_extract_info.md`**: 전문가 유튜브 콘텐츠 추출 텍스트.

### 1. [v1/](./v1) (프로토타입 단계)
- **`cat_breeds_integrated.json`**: 초기 통합 묘종 정보.
- **`bemypet_catlab_preprocessed.json`**: 초기 가공 아티클.
- **`processed.json`**: V1 파이프라인 결과물.

### 2. [v2/](./v2) (구조화 단계)
- **`cat_breeds_integrated.json`**: 다중 라벨링 및 전문가 페르소나 매핑이 적용된 고도화 묘종 데이터.
- **`bemypet_catlab_v2_preprocessed.json`**: V2 공정 분류 완료 데이터.

### 3. [v3/](./v3) (운영 최적화 단계)
- **`golden_dataset.json`**: 검색 품질 측정을 위한 쿼리-정답지 성능 평가셋.
- **`embedded.pkl`**: OpenAI `3-small` 임베딩이 적용된 최종 서비스용 벡터 자산.
- **`processed.json`**: V3 파이프라인 정제 결과 데이터.
