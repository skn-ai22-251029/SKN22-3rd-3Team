# 📊 ZIPSA KPI & Evaluation Metrics

프로젝트의 성과 및 AI 모델의 품질을 정량적으로 측정하기 위한 핵심 지표(KPI) 정의서입니다.
LangSmith 등의 도구를 통해 자동 측정되며, 지속적인 모니터링 대상입니다.

---

## 1. Performance Metrics (성능 지표)
시스템의 응답성과 안정성을 측정합니다.

| Metric | Definition | Target Goal | Measurement |
| :--- | :--- | :--- | :--- |
| **E2E Latency** | 사용자 질문 후 첫 번째 토큰이 생성되기까지 걸리는 시간 (TTFT) 및 전체 완료 시간. | TTFT < 1.5s<br>Total < 5s | Streamlit `st.session_state` 타임스탬프 기록 |
| **Error Rate** | 전체 요청 중 예외(Exception)나 타임아웃이 발생한 비율. | < 1% | Log Error Count / Total Requests |
| **Routing Accuracy** | 사용자의 의도(Intent)에 맞게 올바른 에이전트(`Liaison`/`Matchmaker`)로 라우팅된 비율. | > 95% | LangSmith Tracer (Actual vs Expected) |

---

## 2. Cost & Efficiency Metrics (비용/효율)
운영 비용을 최적화하기 위한 지표입니다.

| Metric | Definition | Target Goal | Measurement |
| :--- | :--- | :--- | :--- |
| **Token Usage** | 요청(Turn) 당 소비되는 평균 Input/Output 토큰 수. | Avg < 1k tokens | OpenAI Usage API Response |
| **Cost per Turn** | 대화 한 턴당 발생하는 비용 (USD). | < $0.01 | Token Count * Model Unit Price |
| **Cache Hit Rate** | 동일/유사 질문에 대해 Redis 캐시가 응답한 비율. | > 30% | Redis Hits / Total Queries |

---

## 3. Quality Validation Metrics (품질 지표)
LLM의 답변 품질을 평가합니다. (LLM-as-a-Judge 활용)

| Metric | Definition | Evaluation Method |
| :--- | :--- | :--- |
| **Faithfulness** | 답변이 검색된 문서(Context/RAG)의 내용에 **충실한가?** (환각 여부) | Ragas / LangSmith Evaluator |
| **Answer Relevance** | 답변이 사용자의 질문(Query)에 **적절하게 대답했는가?** | Ragas / LangSmith Evaluator |
| **Context Precsion** | 검색된 문서들이 질문과 **얼마나 관련성이 높은가?** (Retriever 성능) | Ragas / LangSmith Evaluator |

---

## 4. User Experience Metrics (사용자 경험)
실제 사용자의 만족도를 측정합니다.

| Metric | Definition | Measurement |
| :--- | :--- | :--- |
| **Feedback Score** | 답변에 대한 좋아요(👍)/싫어요(👎) 비율. | UI Feedback Widget Data |
| **Session Length** | 사용자가 이탈하지 않고 대화를 이어가는 평균 턴 수. | Avg Turns per SessionID |

---

## 5. Implementation Strategy (구현 시나리오)

지표를 측정하기 위해 별도의 대시보드를 직접 개발하는 것은 **비효율적(Over-engineering)** 입니다.
초기에는 **LangSmith**의 내장 기능을 100% 활용하는 것을 권장합니다.

### 5.1 Feedback Collection Flow (좋아요/싫어요)
1.  **UI (Next.js/Streamlit)**: 답변 하단에 👍/👎 버튼 배치.
2.  **Action**: 사용자가 버튼 클릭 시, 해당 답변의 `run_id`와 `score` (1 or 0)를 API로 전송.
3.  **Backend**: LangSmith Client를 통해 피드백 등록.
    ```python
    langsmith.client.create_feedback(
        run_id=answer_run_id,
        key="user_score",
        score=1.0  # or 0.0
    )
    ```
4.  **Dashboard**: LangSmith 대시보드에서 자동으로 User Score 통계 시각화됨. (직접 개발 X)

### 5.2 Session Metrics (턴 수 측정)
1.  **Trace Grouping**: 모든 에이전트 호출 시 `session_id`를 LangSmith Tracer에 태깅.
2.  **Analytics**: LangSmith가 `session_id` 기준으로 자동으로 그룹핑하여 **평균 세션 길이(Token/Wards)** 를 계산해줌.

### 5.3 Custom Dashboard 필요성?
*   **Phase 1~3**: **불필요 (Not Essential)**. LangSmith 기본 대시보드로 충분함.
*   **Phase 4**: 비즈니스 팀이 SaaS 형태로 보고 싶어할 때, 그때 가서 Retool이나 Grafana로 연동 고려.
