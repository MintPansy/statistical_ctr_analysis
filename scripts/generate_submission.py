"""
generate_submission.py
======================
빠른 CTR 예측 제출 파일 생성 스크립트.

학습: train_sample.parquet (50k rows) 또는 train.parquet (full)
예측: test.parquet → submission.csv (sample_submission 형식)

Usage:
    python scripts/generate_submission.py [--full-train]

Options:
    --full-train   train.parquet 전체 데이터로 학습 (느리지만 성능 향상)
"""

import sys
import argparse
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import roc_auc_score

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"


# ── 피처 정의 ──────────────────────────────────────────────────────────────

CAT_FEATS = ["gender", "age_group", "inventory_id", "day_of_week", "hour"]

NUM_FEATS = (
    [f"l_feat_{i}" for i in range(1, 28)]
    + [f"feat_e_{i}" for i in range(1, 11)]
    + [f"feat_d_{i}" for i in range(1, 7)]
    + [f"feat_c_{i}" for i in range(1, 9)]
    + [f"feat_b_{i}" for i in range(1, 7)]
    + [f"feat_a_{i}" for i in range(1, 19)]
    + [f"history_a_{i}" for i in range(1, 8)]
    + [f"history_b_{i}" for i in range(1, 31)]
)


def add_engineered_features(df: pd.DataFrame) -> pd.DataFrame:
    """시간대·요일 파생 피처 추가."""
    hour = df["hour"].astype(int)
    day = df["day_of_week"].astype(int)

    def time_of_day(h):
        if 5 <= h < 12:
            return "morning"
        elif 12 <= h < 17:
            return "afternoon"
        elif 17 <= h < 21:
            return "evening"
        else:
            return "night"

    df = df.copy()
    df["time_of_day"] = hour.map(time_of_day)
    df["weekday_weekend"] = day.map(lambda d: "weekend" if d in (6, 7) else "weekday")
    return df


def load_train(full: bool = False, n_rows: int = 200_000) -> pd.DataFrame:
    if full:
        print("Loading full train.parquet ...")
        return pd.read_parquet(DATA / "train.parquet", engine="pyarrow")
    else:
        # train_sample.parquet (50k) 사용
        sample_path = DATA / "train_sample.parquet"
        if sample_path.exists():
            print("Loading train_sample.parquet (50k rows) ...")
            return pd.read_parquet(sample_path, engine="pyarrow")
        else:
            print(f"Loading {n_rows:,} rows from train.parquet ...")
            pf = pq.ParquetFile(DATA / "train.parquet")
            batches = []
            loaded = 0
            for batch in pf.iter_batches(batch_size=50_000):
                batches.append(batch.to_pandas())
                loaded += len(batches[-1])
                if loaded >= n_rows:
                    break
            df = pd.concat(batches, ignore_index=True).head(n_rows)
            return df


def load_test_batched(batch_size: int = 100_000):
    """test.parquet을 배치로 읽는 제너레이터."""
    pf = pq.ParquetFile(DATA / "test.parquet")
    for batch in pf.iter_batches(batch_size=batch_size):
        yield batch.to_pandas()


def build_pipeline(cat_feats, num_feats):
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), cat_feats),
            ("num", StandardScaler(), num_feats),
        ]
    )
    model = LogisticRegression(
        solver="saga",
        max_iter=300,
        C=0.1,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    return Pipeline([("prep", preprocessor), ("clf", model)])


def main(full_train: bool = False):
    t0 = time.time()

    # ── 1. 학습 데이터 로드 ─────────────────────────────────────────────────
    train = load_train(full=full_train)
    train = add_engineered_features(train)
    print(f"  Train shape: {train.shape}, CTR: {train['clicked'].mean():.4f}")

    # 사용 피처 (engineered 포함)
    cat_feats = CAT_FEATS + ["time_of_day", "weekday_weekend"]
    num_feats = [f for f in NUM_FEATS if f in train.columns]

    # 결측값 처리
    train[cat_feats] = train[cat_feats].fillna("unknown").astype(str)
    train[num_feats] = train[num_feats].apply(pd.to_numeric, errors="coerce").fillna(0)

    X_train = train[cat_feats + num_feats]
    y_train = train["clicked"].astype(int)

    # ── 2. 모델 학습 ────────────────────────────────────────────────────────
    print("Training LogisticRegression (saga solver) ...")
    pipe = build_pipeline(cat_feats, num_feats)
    pipe.fit(X_train, y_train)

    # train AUC 확인
    y_prob_train = pipe.predict_proba(X_train)[:, 1]
    train_auc = roc_auc_score(y_train, y_prob_train)
    print(f"  Train AUC: {train_auc:.4f}  (elapsed: {time.time()-t0:.1f}s)")

    # ── 3. 테스트 예측 (배치) ───────────────────────────────────────────────
    print("Predicting on test.parquet (1.5M rows, batched) ...")
    ids = []
    preds = []

    for i, batch in enumerate(load_test_batched(batch_size=100_000)):
        batch = add_engineered_features(batch)
        batch[cat_feats] = batch[cat_feats].fillna("unknown").astype(str)
        batch[num_feats] = batch[num_feats].apply(pd.to_numeric, errors="coerce").fillna(0)

        prob = pipe.predict_proba(batch[cat_feats + num_feats])[:, 1]
        ids.append(batch["ID"].values)
        preds.append(prob)

        if (i + 1) % 5 == 0:
            done = (i + 1) * 100_000
            print(f"  {done:,} rows done ... ({time.time()-t0:.1f}s)")

    # ── 4. 제출 파일 저장 ───────────────────────────────────────────────────
    submission = pd.DataFrame({
        "ID": np.concatenate(ids),
        "clicked": np.concatenate(preds),
    })

    out_path = ROOT / "notebooks" / "submission.csv"
    submission.to_csv(out_path, index=False)

    print(f"\nDone! submission.csv saved → {out_path}")
    print(f"  Rows: {len(submission):,} | clicked mean: {submission['clicked'].mean():.4f}")
    print(f"  Total elapsed: {time.time()-t0:.1f}s")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-train", action="store_true",
                        help="train.parquet 전체 데이터 사용 (느림)")
    args = parser.parse_args()
    main(full_train=args.full_train)
