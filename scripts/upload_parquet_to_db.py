"""
Parquet → DB 적재 스크립트

사용:
    python scripts/upload_parquet_to_db.py postgres
    python scripts/upload_parquet_to_db.py mongodb
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("db", choices=["postgres", "mongodb"], help="대상 DB")
    parser.add_argument(
        "--path",
        default=str(ROOT / "data" / "train_sample.parquet"),
        help="Parquet 파일 경로",
    )
    parser.add_argument("--table", default="ad_click_logs", help="PostgreSQL 테이블명")
    parser.add_argument("--database", default="ctr_analysis", help="MongoDB DB명")
    parser.add_argument("--collection", default="ad_click_logs", help="MongoDB 컬렉션명")
    args = parser.parse_args()

    from src.db_connector import parquet_to_postgres, parquet_to_mongodb

    if args.db == "postgres":
        n = parquet_to_postgres(args.path, table=args.table)
        print(f"PostgreSQL 적재 완료: {n}행")
    else:
        n = parquet_to_mongodb(args.path, database=args.database, collection=args.collection)
        print(f"MongoDB 적재 완료: {n}문서")


if __name__ == "__main__":
    main()
