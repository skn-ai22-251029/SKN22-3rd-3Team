# VERSION: 2.2 - TRANSPARENCY PATCH
import streamlit as st
import asyncio
from utils import get_zipsa_response

def show_chat():
    st.markdown("""
        <div class='animate-fade'>
            <h1 style='font-size: 2.5rem;'>🎩 AI 수석 집사 상담소 (v2.2)</h1>
            <p style='color: var(--text-secondary);'>투명한 AI 상담: <b>전문가 팀</b>의 분석 근거를 확인할 수 있습니다.</p>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar: System Status
    with st.sidebar:
        st.markdown("### 🖥️ 시스템 상태")
        st.success("데이터베이스 연결됨 (v2 Policy)")
        st.info("검색 모드: Hybrid (Vector + Keyword)")
        
        with st.expander("🩺 협업 전문가 가이드", expanded=False):
            st.markdown("""
            - 🧩 **Matchmaker**: 품종 추천 RAG
            - 🩺 **Physician**: 관리 가이드 RAG
            - ⚖️ **Peacekeeper**: 관계 교정 RAG
            - 🔭 **Liaison**: 실시간 매칭
            """)

    st.divider()

    # Display History
    for i, msg in enumerate(st.session_state.messages):
        role_class = "chat-user" if msg["role"] == "user" else "chat-assistant"
        role_label = "집사님" if msg["role"] == "user" else "🎩 Zipsa"
        
        st.markdown(f"<div class='{role_class}'><b>{role_label}:</b><br>{msg['content']}</div>", unsafe_allow_html=True)
        
        # Display Debug Info if available
        if msg.get("debug_info") and msg["role"] == "assistant":
            with st.expander("📁 [Debug] 전문가 분석 근거 (Expert Reasoning)", expanded=False):
                debug = msg["debug_info"]
                st.markdown(f"**활성화된 전문가:** `{debug.get('specialist', 'General')}`")
                st.markdown(f"**DB 검색 쿼리:** `{debug.get('search_query', 'N/A')}`")
                
                if debug.get("retrieved_docs"):
                    st.markdown("**참조된 데이터 (Top Matches):**")
                    for d in debug["retrieved_docs"]:
                        st.markdown(f"- `{d['title']}` (신뢰도: {d['score']:.2f})")

    # Chat Input
    if prompt := st.chat_input("수석 집사에게 질문하거나 지시를 내려주세요..."):
        # 1. UI Feedback
        st.markdown(f"<div class='chat-user'><b>집사님:</b><br>{prompt}</div>", unsafe_allow_html=True)
        
        # 2. Call Agent
        with st.status("🔍 전문가 팀이 데이터를 분석 중입니다...", expanded=True) as status:
            # Prepare internal message for session
            user_msg = {"role": "user", "content": prompt}
            
            st.write("📂 지식 베이스(RAG) 검색 및 전문가 소환 중...")
            
            # RUN AGENT
            content, debug_info = asyncio.run(get_zipsa_response(
                prompt,
                st.session_state.user_profile,
                st.session_state.messages,
                st.session_state.thread_id
            ))
            
            # 🛡️ Safety Filter
            for token in ["__end__", "__start__", "Command("]:
                if token in content:
                    content = content.split(token)[0].strip()
            
            st.write("✨ 답변을 정리하고 근거를 생성하고 있습니다...")
            status.update(label="분석 완료!", state="complete")

        # 3. Store and Refresh
        st.session_state.messages.append(user_msg)
        st.session_state.messages.append({
            "role": "assistant", 
            "content": content,
            "debug_info": debug_info
        })
        st.rerun()
