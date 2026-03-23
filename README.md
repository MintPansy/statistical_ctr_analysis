# Statistical CTR Analysis

CTR(클릭률) 데이터에 대한 통계적 분석 및 예측 모델링 프로젝트입니다.  
사용자 특성·시간 요인에 따른 클릭률 분석, 피처 엔지니어링, 로지스틱 회귀 베이스라인 모델까지의 전체 파이프라인을 제공합니다.

## 주요 내용

- **탐색적 데이터 분석(EDA)**: 클릭 분포 시각화(막대/파이/도넛/Seaborn)
- **사용자 특성별 CTR**: 성별(gender), 연령대(age_group)에 따른 클릭률 분석
- **시간·요일별 CTR**: hour, day_of_week에 따른 트렌드 분석
- **피처 엔지니어링**: 연령×성별 상호작용, 시간대(time_of_day), 평일/주말(weekday_weekend)
- **상관관계 분석**: 숫자형 피처와 clicked 타겟 간 히트맵 시각화
- **모델링**: 로지스틱 회귀 (`class_weight='balanced'`)로 불균형 데이터 처리
- **평가**: ROC AUC, 정밀도, 재현율, F1, 혼동 행렬
- **예측 및 제출**: test 데이터 전처리 후 `submission.csv` 생성

## 분석 파이프라인 (static_laboratory2.ipynb)

```
데이터 로드 → 기본 CTR 시각화 → 사용자 특성별 CTR → 시간/요일별 CTR
    → 피처 엔지니어링 (상호작용, 시간대, 주중여부)
    → 상관관계 히트맵 → 데이터 준비 (원-핫 인코딩, 분할)
    → 로지스틱 회귀 학습 → 모델 평가 → 테스트 예측 → 제출 파일 생성
```

## 주요 인사이트 (샘플 기준)

| 항목 | 결과 |
|------|------|
| **전체 CTR** | ~1.98% (불균형 데이터) |
| **성별** | 남녀 차이 거의 없음 |
| **연령대** | 연령 1.0대 CTR 4.63%로 최고 |
| **시간대** | 새벽 3시, 오후 2–4시 클릭률 상승 |
| **요일** | 금요일(5요일) CTR 최고 |
| **모델 AUC** | 베이스라인 로지스틱 ~0.70 |

## 프로젝트 구조

```
├── data/                      # 데이터
│   ├── train_sample.parquet   # 학습 샘플 (~10MB, 20만 행)
│   ├── train.parquet          # 전체 학습 (다운로드 필요)
│   └── test.parquet           # 테스트 (다운로드 필요)
├── notebooks/
│   ├── static_laboratory2.ipynb   # CTR 분석·모델링·제출 파이프라인
│   └── ctr_pattern_db.ipynb       # DB/Parquet 기반 CTR 패턴 분석
├── src/
│   ├── db_connector.py        # PostgreSQL / MongoDB 연결
│   ├── data_loader.py         # 통합 데이터 로더 (DB + Parquet)
│   └── ctr_analysis.py        # CTR 패턴 분석 (pandas)
├── scripts/
│   └── upload_parquet_to_db.py    # Parquet → DB 적재
├── app_streamlit.py           # Streamlit 대시보드
├── download_data.py           # 데이터 다운로드 스크립트
├── .env.example               # DB 연결 설정 예시
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

## 환경 설정

### 기본 (노트북 분석)
```bash
pip install pandas numpy pyarrow matplotlib seaborn scikit-learn
```

### DB + Streamlit (전체 파이프라인)
```bash
pip install -r requirements_streamlit.txt
```

## 데이터 소스: Parquet / PostgreSQL / MongoDB

광고 클릭 로그를 Parquet, PostgreSQL, MongoDB 중에서 선택해 로드할 수 있습니다.

| 소스 | 설명 |
|------|------|
| **Parquet** | `data/train_sample.parquet` (기본, DB 불필요) |
| **PostgreSQL** | `ad_click_logs` 테이블 (`POSTGRES_URI` 환경변수) |
| **MongoDB** | `ctr_analysis.ad_click_logs` 컬렉션 (`MONGODB_URI` 환경변수) |

### Parquet → DB 적재
```bash
# .env에 POSTGRES_URI 또는 MONGODB_URI 설정 후
python scripts/upload_parquet_to_db.py postgres
python scripts/upload_parquet_to_db.py mongodb
```

### Python에서 사용
```python
from src.data_loader import load_click_logs

# Parquet (기본)
df = load_click_logs(source="parquet", path="data/train_sample.parquet", n_rows=100_000)

# PostgreSQL
df = load_click_logs(source="postgres", n_rows=100_000)

# MongoDB
df = load_click_logs(source="mongodb", n_rows=100_000)
```

## Streamlit 대시보드

```bash
streamlit run app_streamlit.py
```

데이터 소스(Parquet/PostgreSQL/MongoDB)를 사이드바에서 선택하고, 차원별 CTR 패턴을 확인할 수 있습니다.

## 노트북 실행

### 로컬 / Jupyter
```bash
jupyter notebook notebooks/static_laboratory2.ipynb
jupyter notebook notebooks/ctr_pattern_db.ipynb   # DB/Parquet CTR 패턴
```

### Google Colab
1. Drive 마운트 후 `static_document_dataset.zip` 경로 확인
2. `ZIP_FILE_PATH` 변수를 해당 경로로 수정
3. 셀을 순서대로 실행

노트북 내 데이터 경로는 `../data/` 기준으로 설정되어 있습니다. Colab에서는 `static_document_dataset/` 등 실제 경로로 변경이 필요할 수 있습니다.

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

### 메모리 효율적 로드 (대용량)
```python
import pyarrow.parquet as pq
import pandas as pd

def load_parquet_safely(path, n_rows=200_000, batch_size=50_000):
    if n_rows is None:
        return pd.read_parquet(path, engine="pyarrow")
    pf = pq.ParquetFile(path)
    batches = [b.to_pandas() for b in pf.iter_batches(batch_size=batch_size)]
    result = pd.concat(batches, ignore_index=True)
    return result.iloc[:n_rows]
```

## 라이선스

이 프로젝트는 통계·데이터 분석 학습 및 연구 목적으로 사용됩니다.
