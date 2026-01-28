import streamlit as st

def show_onboarding():
    st.markdown("""
        <div class='animate-fade'>
            <h1 style='text-align: center; font-size: 3rem;'>🎩 집사 등록 (Onboarding)</h1>
            <p style='text-align: center; color: var(--text-secondary); font-size: 1.2rem; max-width: 800px; margin: 0 auto 2rem;'>
                수석 집사가 지휘하는 AI 팀이 집사님과 주인님(고양이)의 완벽한 매칭을 위해 몇 가지 질문을 준비했습니다.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Removed invalid glass-card div injection

    
    with st.form("onboarding_form", clear_on_submit=False):
        st.subheader("🏠 거주 및 활동 환경")
        col1, col2 = st.columns(2)
        
        with col1:
            housing = st.selectbox(
                "거주 형태",
                ["원룸/오피스텔", "빌라/아파트", "단독주택", "기타"],
                index=1
            )
            work_style = st.select_slider(
                "집을 비우는 시간 (일일 평균)",
                options=["재택/주로 있음", "4-6시간", "8-10시간", "그 이상"],
                value="4-6시간"
            )
        
        with col2:
            companion = st.multiselect(
                "함께 사는 가족/구성원",
                ["혼자 살아요", "배우자/파트너", "어린 아이", "연로하신 부모님", "다른 고양이", "강아지"],
                default=["혼자 살아요"]
            )
            activity = st.radio(
                "집사님의 생활 활동량",
                ["정적 (독서, 영화)", "활동적 (산책, 운동)", "매우 활동적"],
                horizontal=True
            )

        st.divider()
        st.subheader("😺 기대하는 주인님의 성향")
        
        traits = st.multiselect(
            "원하는 고양이 성격 (중복 선택)",
            ["개냥이 (애교)", "독립적 (차분함)", "에너자이저 (활동성)", "수다쟁이 (매력)", "무릎 냥이"],
            default=["개냥이 (애교)"]
        )
        
        experience = st.radio(
            "양육 경험",
            ["초보 집사 (처음이에요)", "경력 집사 (1~2번)", "베테랑 (전문가 수준)"],
            horizontal=True
        )

        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("🛡️ 수석 집사에게 정보 전달")
        
        if submit:
            profile = {
                "housing": housing,
                "work_style": work_style,
                "companion": companion,
                "activity": activity,
                "traits": traits,
                "experience": experience
            }
            st.session_state.user_profile = profile
            st.session_state.page = "chat"
            st.success("✅ 정보가 성공적으로 전달되었습니다. 수석 집사가 상담을 준비합니다.")
            st.rerun()

        # Removed invalid glass-card div closure

