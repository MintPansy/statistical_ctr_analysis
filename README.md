# Statistical CTR Analysis

CTR(클릭률) 데이터에 대한 통계적 분석 프로젝트입니다.

## 프로젝트 구조

```
├── data/              # 샘플 데이터 (train_sample.parquet ~10MB)
├── notebooks/         # 분석 Jupyter 노트북
├── src/               # 공통 코드
├── download_data.py   # 전체 데이터 다운 스크립트
└── README.md
```

## 데이터

### 샘플 데이터 (저장소 포함)
- `data/train_sample.parquet` : 학습용 샘플 (~10MB, 20만 행)
- 분석/실험용으로 충분한 크기입니다.

### 전체 데이터 (다운로드 필요)
```bash
# 1. download_data.py 에서 데이터 URL 설정
# 2. 다운로드 실행
python download_data.py

# 기존 train.parquet에서 샘플만 생성
python download_data.py --sample-only
```

## 데이터 로드 가이드

### Python / Pandas
```python
import pandas as pd

# 샘플 데이터 로드 (권장)
train = pd.read_parquet("data/train_sample.parquet")

# 전체 데이터 로드 (download_data.py 실행 후)
# train = pd.read_parquet("data/train.parquet")
# test = pd.read_parquet("data/test.parquet")
```

### 노트북에서
`notebooks/` 내 노트북에서는 프로젝트 루트 기준 경로 사용:
```python
train = pd.read_parquet("../data/train_sample.parquet")
```

## 환경 설정

```bash
pip install pandas numpy pyarrow
```

## 분석

`notebooks/static_laboratory.ipynb` 에서 CTR 분석을 수행합니다.
