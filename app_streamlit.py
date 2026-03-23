"""
CTR 패턴 분석 - Streamlit 대시보드

실행: streamlit run app_streamlit.py
"""
import sys
from pathlib import Path

# 프로젝트 루트를 path에 추가
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

import streamlit as st
import pandas as pd

from src.data_loader import load_click_logs
from src.ctr_analysis import compute_ctr_patterns, get_overall_stats

st.set_page_config(page_title="CTR 패턴 분석", page_icon="📊", layout="wide")

st.title("📊 CTR 패턴 분석 대시보드")
st.caption("광고 클릭 로그 기반 CTR 패턴 분석")

# ----- 사이드바: 데이터 소스 설정 -----
st.sidebar.header("데이터 소스")
source = st.sidebar.radio(
    "소스 선택",
    ["parquet", "postgres", "mongodb"],
    index=0,
)
n_rows = st.sidebar.slider("최대 행 수 (0=전체)", 0, 500_000, 100_000, step=10_000)
if n_rows == 0:
    n_rows = None

# ----- 데이터 로드 -----
@st.cache_data(ttl=300)
def load_data(_source: str, _n_rows: int | None):
    try:
        path = str(ROOT / "data" / "train_sample.parquet") if _source == "parquet" else None
        df = load_click_logs(
            source=_source,
            path=path,
            n_rows=_n_rows,
        )
        return df
    except Exception as e:
        st.error(f"데이터 로드 실패: {e}")
        return pd.DataFrame()

df = load_data(source, n_rows)
if df.empty:
    st.warning("데이터가 없습니다. Parquet 파일 경로 또는 DB 연결을 확인해 주세요.")
    st.stop()

# ----- 전체 통계 -----
stats = get_overall_stats(df)
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("총 노출 수", f"{stats['total_impressions']:,}")
with col2:
    st.metric("총 클릭 수", f"{stats['total_clicks']:,}")
with col3:
    st.metric("CTR", f"{stats['click_rate_pct']:.2f}%")
with col4:
    st.metric("데이터 소스", source)

st.divider()

# ----- 차원별 CTR 패턴 -----
st.subheader("차원별 CTR 패턴")
patterns = compute_ctr_patterns(df)
dimensions = list(patterns.keys())

if dimensions:
    tab_names = dimensions[:4]  # 최대 4개 탭
    tabs = st.tabs(tab_names)
    for tab, dim in zip(tabs, tab_names):
        with tab:
            ctr_df = patterns[dim].copy()
            ctr_df["ctr_pct"] = (ctr_df["ctr"] * 100).round(2)
            cols = [dim, "ctr_pct", "clicks", "impressions"]
            st.dataframe(ctr_df[cols], use_container_width=True)
            chart_df = ctr_df[[dim, "ctr_pct"]].set_index(dim)
            st.bar_chart(chart_df)
else:
    st.info("분석 가능한 차원(gender, age_group, hour, day_of_week)이 데이터에 없습니다.")

st.divider()

# ----- raw 데이터 미리보기 -----
with st.expander("📋 원본 데이터 미리보기"):
    st.dataframe(df.head(100), use_container_width=True)
