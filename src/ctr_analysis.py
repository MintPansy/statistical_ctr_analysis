"""
CTR 패턴 분석 - pandas 기반

사용 예:
    from src.ctr_analysis import compute_ctr_patterns, get_ctr_by_dimension
"""
from __future__ import annotations

from typing import Optional, Union

import pandas as pd


# 클릭 컬럼 후보 (데이터에 따라 매핑)
CLICK_COLS = ["clicked", "click", "label", "target", "is_click"]


def _get_click_col(df: pd.DataFrame) -> str:
    for c in CLICK_COLS:
        if c in df.columns:
            return c
    raise KeyError(f"클릭 컬럼을 찾을 수 없습니다. 후보: {CLICK_COLS}")


def compute_ctr_patterns(
    df: pd.DataFrame,
    dimensions: Optional[list[str]] = None,
    click_col: Optional[str] = None,
) -> dict[str, pd.DataFrame]:
    """
    여러 차원별 CTR 패턴 계산.

    Args:
        df: 광고 클릭 로그 DataFrame
        dimensions: 분석 차원 (예: ['gender', 'age_group', 'hour', 'day_of_week'])
        click_col: 클릭 여부 컬럼명 (None이면 자동 탐지)

    Returns:
        {차원명: CTR DataFrame}
    """
    click_col = click_col or _get_click_col(df)
    dims = dimensions or [
        c for c in ["gender", "age_group", "hour", "day_of_week"]
        if c in df.columns
    ]
    if not dims:
        dims = df.select_dtypes(include=["int64", "int32", "object"]).columns[:4].tolist()

    result = {}
    for dim in dims:
        if dim not in df.columns:
            continue
        ctr = df.groupby(dim)[click_col].agg(["mean", "sum", "count"])
        ctr.columns = ["ctr", "clicks", "impressions"]
        ctr = ctr.reset_index()
        result[dim] = ctr
    return result


def get_ctr_by_dimension(
    df: pd.DataFrame,
    dimension: str,
    click_col: Optional[str] = None,
) -> pd.DataFrame:
    """단일 차원별 CTR."""
    patterns = compute_ctr_patterns(df, dimensions=[dimension], click_col=click_col)
    return patterns.get(dimension, pd.DataFrame())


def get_overall_stats(df: pd.DataFrame, click_col: Optional[str] = None) -> dict:
    """전체 CTR 및 기본 통계."""
    click_col = click_col or _get_click_col(df)
    return {
        "total_impressions": len(df),
        "total_clicks": int(df[click_col].sum()),
        "ctr": float(df[click_col].mean()),
        "click_rate_pct": float(df[click_col].mean() * 100),
    }


def get_time_patterns(
    df: pd.DataFrame,
    hour_col: str = "hour",
    day_col: str = "day_of_week",
    click_col: Optional[str] = None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """시간대·요일별 CTR 패턴."""
    click_col = click_col or _get_click_col(df)
    hour_ctr = get_ctr_by_dimension(df, hour_col, click_col) if hour_col in df.columns else pd.DataFrame()
    day_ctr = get_ctr_by_dimension(df, day_col, click_col) if day_col in df.columns else pd.DataFrame()
    return hour_ctr, day_ctr
