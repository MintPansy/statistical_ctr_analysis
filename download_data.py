"""
전체 데이터 다운로드 스크립트

사용법:
    python download_data.py              # 전체 데이터 다운로드 + train_sample.parquet 생성
    python download_data.py --sample-only  # 기존 train.parquet에서 샘플만 생성
"""
import argparse
from pathlib import Path

# 데이터 저장 경로
DATA_DIR = Path(__file__).resolve().parent / "data"
SAMPLE_SIZE_MB = 10


def get_data_urls():
    """데이터 다운로드 URL (실제 링크로 수정 필요)"""
    return {
        "train": "YOUR_TRAIN_DATA_URL",  # e.g., https://example.com/train.parquet
        "test": "YOUR_TEST_DATA_URL",
        "sample_submission": "YOUR_SAMPLE_SUBMISSION_URL",
    }


def download_full_data():
    """전체 데이터 다운로드"""
    try:
        import urllib.request
    except ImportError:
        print("urllib 사용 (표준 라이브러리)")
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    urls = get_data_urls()
    
    for name, url in urls.items():
        if url.startswith("YOUR_"):
            print(f"[건너뜀] {name}: URL을 설정해주세요. (download_data.py 수정)")
            continue
        out_path = DATA_DIR / f"{name}.parquet" if name != "sample_submission" else DATA_DIR / "sample_submission.csv"
        print(f"다운로드 중: {url} -> {out_path}")
        urllib.request.urlretrieve(url, out_path)
        print(f"  완료: {out_path}")


def create_train_sample(n_rows: int = 200_000, max_size_mb: float = SAMPLE_SIZE_MB):
    """
    train.parquet에서 train_sample.parquet 생성 (~10MB)
    n_rows 또는 max_size_mb 중 먼저 도달하는 기준 적용
    """
    try:
        import pyarrow.parquet as pq
        import pandas as pd
    except ImportError:
        print("pyarrow 설치 필요: pip install pyarrow")
        return
    
    train_path = DATA_DIR / "train.parquet"
    out_path = DATA_DIR / "train_sample.parquet"
    
    if not train_path.exists():
        print(f"[오류] {train_path} 없음. 먼저 전체 데이터를 다운로드하세요.")
        return
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    print(f"샘플 생성 중: {train_path} -> {out_path} (~{max_size_mb}MB)")
    parquet_file = pq.ParquetFile(train_path)
    batches = []
    loaded = 0
    batch_size = 50_000
    
    for batch in parquet_file.iter_batches(batch_size=batch_size):
        batch_df = batch.to_pandas()
        batches.append(batch_df)
        loaded += len(batch_df)
        
        # 대략적인 크기 체크 (MB)
        temp = pd.concat(batches, ignore_index=True)
        approx_mb = temp.memory_usage(deep=True).sum() / (1024 * 1024)
        if loaded >= n_rows or approx_mb >= max_size_mb:
            break
    
    if not batches:
        print("샘플 생성 실패")
        return
    
    result = pd.concat(batches, ignore_index=True)
    result = result.iloc[:min(loaded, n_rows)]
    result.to_parquet(out_path, index=False, engine="pyarrow")
    size_mb = out_path.stat().st_size / (1024 * 1024)
    print(f"  완료: {out_path} ({result.shape[0]:,} rows, {size_mb:.1f} MB)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample-only", action="store_true", help="기존 train.parquet에서 샘플만 생성")
    args = parser.parse_args()
    
    if args.sample_only:
        create_train_sample()
    else:
        download_full_data()
        create_train_sample()


if __name__ == "__main__":
    main()
