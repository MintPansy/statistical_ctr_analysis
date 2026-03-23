"""
광고 클릭 로그 데이터 로더 - DB(PostgreSQL/MongoDB) 또는 Parquet

사용 예:
    df = load_click_logs(source="parquet", path="data/train_sample.parquet")
    df = load_click_logs(source="postgres", table="ad_click_logs", limit=100_000)
    df = load_click_logs(source="mongodb", collection="ad_click_logs", limit=100_000)
"""
from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional, Union

import pandas as pd


def load_click_logs(
    source: Literal["parquet", "postgres", "mongodb"] = "parquet",
    path: Optional[str] = None,
    n_rows: Optional[int] = None,
    # DB options
    table: str = "ad_click_logs",
    database: str = "ctr_analysis",
    collection: str = "ad_click_logs",
    query: Optional[Union[str, dict]] = None,
) -> pd.DataFrame:
    """
    광고 클릭 로그를 로드합니다.

    Args:
        source: 'parquet' | 'postgres' | 'mongodb'
        path: Parquet 파일 경로 (source=parquet일 때)
        n_rows: 최대 행 수 (대용량 시 샘플링)
        table: PostgreSQL 테이블명
        database: MongoDB DB명
        collection: MongoDB 컬렉션명
        query: PostgreSQL SQL 문자열 또는 MongoDB 필터 dict

    Returns:
        pandas DataFrame
    """
    if source == "parquet":
        return _load_parquet(path or "data/train_sample.parquet", n_rows)
    if source == "postgres":
        from .db_connector import load_from_postgres
        return load_from_postgres(
            table=table,
            query=query if isinstance(query, str) else None,
            limit=n_rows,
        )
    if source == "mongodb":
        from .db_connector import load_from_mongodb
        return load_from_mongodb(
            database=database,
            collection=collection,
            query=query if isinstance(query, dict) else None,
            limit=n_rows,
        )
    raise ValueError(f"Unknown source: {source}")


def _load_parquet(path: str, n_rows: Optional[int] = 200_000) -> pd.DataFrame:
    """Parquet에서 메모리 효율적으로 로드."""
    p = Path(path)
    if not p.exists():
        # 프로젝트 루트 기준
        p = Path(__file__).resolve().parent.parent / path
    if not p.exists():
        raise FileNotFoundError(f"Parquet not found: {path}")

    if n_rows is None:
        return pd.read_parquet(p, engine="pyarrow")

    try:
        import pyarrow.parquet as pq
        pf = pq.ParquetFile(p)
        batches = []
        loaded = 0
        for batch in pf.iter_batches(batch_size=50_000):
            df_batch = batch.to_pandas()
            batches.append(df_batch)
            loaded += len(df_batch)
            if loaded >= n_rows:
                break
        if not batches:
            return pd.DataFrame()
        result = pd.concat(batches, ignore_index=True)
        return result.iloc[:n_rows].copy()
    except Exception:
        df = pd.read_parquet(p, engine="pyarrow")
        return df.head(n_rows) if n_rows else df
