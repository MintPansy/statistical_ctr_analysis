"""
DB 연결 유틸리티 - PostgreSQL / MongoDB

환경 변수 또는 .env 사용:
  POSTGRES_URI = postgresql://user:pass@host:5432/dbname
  MONGODB_URI = mongodb://user:pass@host:27017/dbname
"""
from __future__ import annotations

import os
from typing import Optional

# Optional: python-dotenv for .env loading
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# ---------------------------------------------------------------------------
# PostgreSQL
# ---------------------------------------------------------------------------

def get_postgres_uri() -> str:
    """PostgreSQL 연결 URI. 환경변수 POSTGRES_URI 사용."""
    return os.getenv(
        "POSTGRES_URI",
        "postgresql://localhost:5432/ctr_analysis"
    )


def load_from_postgres(
    table: str = "ad_click_logs",
    query: Optional[str] = None,
    limit: Optional[int] = None,
) -> "pd.DataFrame":
    """
    PostgreSQL에서 광고 클릭 로그 로드.

    Args:
        table: 테이블명
        query: 커스텀 SQL (None이면 SELECT * FROM table)
        limit: 최대 행 수 (None이면 전체)

    Returns:
        pandas DataFrame
    """
    import pandas as pd

    try:
        from sqlalchemy import create_engine
        engine = create_engine(get_postgres_uri())
    except ImportError:
        import psycopg2
        conn = psycopg2.connect(get_postgres_uri())
        sql = query or f"SELECT * FROM {table}"
        if limit:
            sql = f"{sql} LIMIT {limit}" if "LIMIT" not in sql.upper() else sql
        return pd.read_sql(sql, conn)

    sql = query or f"SELECT * FROM {table}"
    if limit:
        sql = f"{sql} LIMIT {limit}" if "LIMIT" not in sql.upper() else sql
    return pd.read_sql(sql, engine)


# ---------------------------------------------------------------------------
# MongoDB
# ---------------------------------------------------------------------------

def get_mongodb_uri() -> str:
    """MongoDB 연결 URI. 환경변수 MONGODB_URI 사용."""
    return os.getenv(
        "MONGODB_URI",
        "mongodb://localhost:27017/"
    )


def load_from_mongodb(
    database: str = "ctr_analysis",
    collection: str = "ad_click_logs",
    query: Optional[dict] = None,
    limit: Optional[int] = None,
    projection: Optional[dict] = None,
) -> "pd.DataFrame":
    """
    MongoDB에서 광고 클릭 로그 로드.

    Args:
        database: DB명
        collection: 컬렉션명
        query: 필터 쿼리 (예: {"clicked": 1})
        limit: 최대 행 수 (None이면 전체)
        projection: 반환 필드 지정 (None이면 전체)

    Returns:
        pandas DataFrame
    """
    import pandas as pd
    from pymongo import MongoClient

    client = MongoClient(get_mongodb_uri())
    coll = client[database][collection]

    cursor = coll.find(
        query or {},
        projection=projection,
        limit=limit or 0
    )
    return pd.DataFrame(list(cursor))


# ---------------------------------------------------------------------------
# 파라quet → DB 적재 (선택)
# ---------------------------------------------------------------------------

def parquet_to_postgres(
    parquet_path: str,
    table: str = "ad_click_logs",
    if_exists: str = "replace",
) -> int:
    """
    Parquet 파일을 PostgreSQL 테이블로 적재.

    Args:
        parquet_path: parquet 파일 경로
        table: 대상 테이블명
        if_exists: 'replace' | 'append' | 'fail'

    Returns:
        적재된 행 수
    """
    import pandas as pd
    from sqlalchemy import create_engine

    df = pd.read_parquet(parquet_path)
    engine = create_engine(get_postgres_uri())
    df.to_sql(table, engine, if_exists=if_exists, index=False)
    return len(df)


def parquet_to_mongodb(
    parquet_path: str,
    database: str = "ctr_analysis",
    collection: str = "ad_click_logs",
) -> int:
    """
    Parquet 파일을 MongoDB 컬렉션에 적재.

    Args:
        parquet_path: parquet 파일 경로
        database: DB명
        collection: 컬렉션명

    Returns:
        적재된 문서 수
    """
    import pandas as pd
    from pymongo import MongoClient

    df = pd.read_parquet(parquet_path)
    # NaN → None, ObjectId 등 호환
    records = df.replace({float("nan"): None}).to_dict("records")
    client = MongoClient(get_mongodb_uri())
    coll = client[database][collection]
    coll.delete_many({})  # 기존 삭제 후 적재 (선택적)
    result = coll.insert_many(records)
    return len(result.inserted_ids)
