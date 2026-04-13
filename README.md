# Statistical CTR Analysis

광고 클릭률(CTR)의 변동 요인을 통계적으로 분석하고, 머신러닝으로 재검증하는 논문형 연구 프로젝트입니다.  
단순 예측 성능 최적화가 아닌, **CTR이 왜 달라지는지**를 설명하는 데 초점을 맞춥니다.

---

## 연구 질문 (Research Questions)

| RQ | 질문 | 주요 검정 |
|----|------|----------|
| **RQ1** | 사용자 특성(연령·성별)이 CTR에 유의한 영향을 미치는가? | One-way ANOVA, 카이제곱, Tukey HSD |
| **RQ2** | 시간대(hour)에 따라 CTR이 유의하게 달라지는가? | One-way ANOVA, eta² |
| **RQ3** | 요일(day_of_week)에 따른 CTR 차이가 존재하는가? | One-way ANOVA, eta² |
| **RQ4** | 통계적으로 유의한 패턴이 예측 모델에서도 재현되는가? | XGBoost + SHAP |

---

## 주요 결과 요약

### 통계 검정

| 변수 | 검정 | 결과 | 효과 크기 | 유의성 |
|------|------|------|----------|--------|
| 연령대 | One-way ANOVA | F=37.12, p<0.001 | eta²=0.0013 (small) | 유의 |
| 성별 | 카이제곱 | chi²=1.24, p=0.266 | Cramer's V=0.0025 | 비유의 |
| 시간(hour) | One-way ANOVA | F=2.51, p<0.001 | eta²=0.0003 (small) | 유의 |
| 요일 | One-way ANOVA | F=3.59, p=0.001 | eta²=0.0001 (small) | 유의 |

> 통계적 유의성은 확인되었으나 효과 크기는 모두 매우 작음. 인구통계 단독 변수보다 행동 이력 피처가 CTR 설명에 핵심임을 시사.

### 모델 검증 (XGBoost)

| 설정 | Val AUC | Val AP | Val LogLoss |
|------|---------|--------|-------------|
| top 50 features | 0.6437 | 0.0428 | 0.5258 |
| top 75 features | 0.6668 | 0.0455 | 0.5026 |
| **top 100 features** | **0.6707** | **0.0492** | **0.4959** |
| top 112 features | 0.6666 | 0.0499 | 0.4967 |

> 메인 지표: LogLoss / 보조 지표: AUC / AP·WLL은 대회 기준 참고 지표

### SHAP 상위 설명 변수

| 순위 | 피처 | 방향 |
|------|------|------|
| 1 | `history_a_1` | 값 클수록 CTR 상승 |
| 2 | `feat_d_4` | 값 클수록 CTR 상승 |
| 3 | `feat_e_3` | 값 클수록 CTR 하락 |

---

## 데이터

| 파일 | 설명 |
|------|------|
| `data/train_sample.parquet` | 학습 샘플 (20만 행, random_state=42) |
| `data/train.parquet` | 전체 학습 데이터 |
| `data/test.parquet` | 예측 대상 |
| `data/sample_submission.csv` | 제출 포맷 |

- 분석 타겟: `clicked` (이진 변수)
- 전체 CTR: **~1.90%** (강한 클래스 불균형)

---

## 프로젝트 구조

```
├── data/
│   ├── train_sample.parquet       # 학습 샘플 (20만 행)
│   ├── train.parquet              # 전체 학습 데이터
│   ├── test.parquet               # 테스트 데이터
│   └── sample_submission.csv      # 제출 포맷
├── notebooks/
│   ├── CTR_통합_최종.ipynb         # 메인 분석 노트북 (EDA → 통계 → 모델 → SHAP)
│   ├── paper_xgb_performance_table.csv  # 모델 성능표 (논문용)
│   ├── paper_xgb_shap_top10.csv         # SHAP 상위 10개 피처 (논문용)
│   ├── paper_xgb_summary.txt            # 본문 서술 자동 생성 텍스트
│   └── *.png                            # 분석 시각화 산출물
├── src/
│   ├── data_loader.py             # 통합 데이터 로더 (Parquet / DB)
│   ├── db_connector.py            # PostgreSQL / MongoDB 연결
│   └── ctr_analysis.py            # CTR 패턴 분석
├── scripts/
│   ├── generate_submission.py     # 제출 파일 생성
│   └── upload_parquet_to_db.py    # Parquet → DB 적재
├── thesis_data_v2.md              # 논문 작성 가이드 (결과 서술 기준)
├── app_streamlit.py               # Streamlit 대시보드
├── download_data.py               # 데이터 다운로드
└── README.md
```

---

## 노트북 구성 (CTR_통합_최종.ipynb)

```
1. 데이터 로드 및 기본 통계
2. EDA — CTR 분포, 클래스 불균형 확인
3. RQ1 — 사용자 특성(연령·성별)별 CTR 분석
4. RQ2 — 시간대별 CTR 분석
5. RQ3 — 요일별 CTR 분석
6. RQ4 — XGBoost 모델 학습 및 피처 수 실험
7. SHAP 해석 — 상위 설명 변수 및 방향성 도출
8. 논문용 결과물 자동 저장 (표·그림·서술문)
```

---

## 환경 설정

```bash
# 기본 (노트북 분석)
pip install pandas numpy pyarrow matplotlib seaborn scikit-learn xgboost shap

# Streamlit 대시보드 포함
pip install -r requirements_streamlit.txt
```

---

## 데이터 로드

```python
import pandas as pd

# 샘플 (권장)
train = pd.read_parquet("data/train_sample.parquet")

# 전체
train = pd.read_parquet("data/train.parquet")
```

---

## 라이선스

통계·데이터 분석 학습 및 연구 목적으로 사용됩니다.
