"""PKNU Finder 홈 화면."""

import streamlit as st


def render_home() -> None:
    """로그인한 사용자가 보는 간단한 홈 화면을 표시합니다."""
    st.title("🔎 PKNU Finder")
    st.subheader("부경대학교 분실물·습득물 찾기")
    st.write(
        "학교에서 잃어버린 물건을 찾거나, 습득한 물건을 공유할 수 있는 서비스입니다."
    )

    st.divider()

    left, right = st.columns(2)
    with left:
        st.markdown("### 🔍 분실물 찾기")
        st.write("분실한 물건의 정보를 검색해 보세요.")
    with right:
        st.markdown("### 📦 습득물 등록하기")
        st.write("물건을 발견했다면 정보를 등록해 다른 학생이 찾을 수 있도록 도와주세요.")

    st.info("왼쪽 메뉴에서 **분실물/습득물 검색** 또는 **분실물/습득물 등록**을 선택하세요.")
    st.caption("※ 검색 및 등록 기능은 현재 개발 중입니다.")