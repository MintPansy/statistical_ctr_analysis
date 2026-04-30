# Statistical CTR Analysis

광고 클릭 로그 데이터를 바탕으로 CTR 변동 요인을 통계적으로 검증하고, 같은 패턴이 머신러닝 모델에서도 재현되는지 확인한 연구 프로젝트입니다.  
단순 예측 성능보다도 **"어떤 요인이 CTR 차이를 만드는가"** 를 해석하는 데 초점을 두었습니다.

---

## Overview

광고 클릭률(CTR)은 마케팅 효과를 측정하는 핵심 지표이지만, 어떤 요인이 CTR 차이를 유발하는지는 예측 모델만으로는 설명하기 어렵습니다.  
이 프로젝트는 통계 검정(ANOVA, 카이제곱)으로 변수별 유의성을 먼저 확인한 뒤, XGBoost + SHAP으로 동일 패턴이 모델에서도 재현되는지 검증합니다.  
전체 CTR이 약 1.9%인 강한 클래스 불균형 환경에서, 통계적 유의성과 실질적 효과 크기를 함께 보고하는 것이 핵심 방법론입니다.

---

## Key Findings

- 연령, 시간대, 요일 일부 변수는 통계적으로 유의했지만 **효과 크기는 매우 작았습니다** (eta² ≤ 0.0013).
- **인구통계 변수보다 행동 이력 기반 피처**(`history_*`)가 CTR 예측에 더 큰 영향을 미쳤습니다.
- XGBoost + SHAP 분석에서도 행동 이력 기반 피처 중요도가 상위를 차지하며, 통계 검정 결과와 일관된 방향을 보였습니다.
- 결론적으로 CTR 분석에서는 통계적 유의성 자체보다 **데이터 품질과 피처 해석 가능성**이 더 중요했습니다.

---

## Research Questions

| RQ | 질문 | 주요 검정 |
|----|------|----------|
| **RQ1** | 사용자 특성(연령·성별)이 CTR에 유의한 영향을 미치는가? | One-way ANOVA, 카이제곱, Tukey HSD |
| **RQ2** | 시간대(hour)에 따라 CTR이 유의하게 달라지는가? | One-way ANOVA, eta² |
| **RQ3** | 요일(day_of_week)에 따른 CTR 차이가 존재하는가? | One-way ANOVA, eta² |
| **RQ4** | 통계적으로 유의한 패턴이 예측 모델에서도 재현되는가? | XGBoost + SHAP |

---

## Dataset

| 파일 | 설명 |
|------|------|
| `data/train_sample.parquet` | 학습 샘플 (20만 행, random_state=42) |
| `data/train.parquet` | 전체 학습 데이터 |
| `data/test.parquet` | 예측 대상 |
| `data/sample_submission.csv` | 제출 포맷 |

- 분석 타겟: `clicked` (이진 변수)
- 전체 CTR: **~1.90%** (강한 클래스 불균형)
- 주요 피처 그룹: 인구통계(`age`, `gender`), 시간(`hour`, `day_of_week`), 행동 이력(`history_*`), 광고 속성(`feat_*`)

---

## Method

1. **탐색적 데이터 분석 (EDA)** — CTR 분포, 클래스 불균형, 변수별 기초 통계 확인
2. **통계 검정** — 집단 간 CTR 차이를 ANOVA·카이제곱으로 검증, eta²·Cramer's V로 효과 크기 측정
3. **머신러닝 검증** — XGBoost로 CTR 예측, 피처 수 실험(top 50 → 112)을 통해 최적 구성 탐색
4. **SHAP 해석** — 모델 예측에 기여한 상위 변수와 방향성을 통계 결과와 대조

> 평가 지표 우선순위: **LogLoss** (메인) → AUC (보조)

---

## Model Performance

### 통계 검정 결과

| 변수 | 검정 | 결과 | 효과 크기 | 유의성 |
|------|------|------|----------|--------|
| 연령대 | One-way ANOVA | F=37.12, p<0.001 | eta²=0.0013 (small) | 유의 |
| 성별 | 카이제곱 | chi²=1.24, p=0.266 | Cramer's V=0.0025 | 비유의 |
| 시간(hour) | One-way ANOVA | F=2.51, p<0.001 | eta²=0.0003 (small) | 유의 |
| 요일 | One-way ANOVA | F=3.59, p=0.001 | eta²=0.0001 (small) | 유의 |

> 모든 유의 변수의 효과 크기가 매우 작음 — 통계적 유의성이 실질적 중요도를 보장하지 않음.

### XGBoost 모델 성능

| 설정 | Val AUC | Val AP | Val LogLoss |
|------|---------|--------|-------------|
| top 50 features | 0.6437 | 0.0428 | 0.5258 |
| top 75 features | 0.6668 | 0.0455 | 0.5026 |
| **top 100 features** | **0.6707** | **0.0492** | **0.4959** |
| top 112 features | 0.6666 | 0.0499 | 0.4967 |

### SHAP 상위 설명 변수

| 순위 | 피처 | 방향 |
|------|------|------|
| 1 | `history_a_1` | 값 클수록 CTR 상승 |
| 2 | `feat_d_4` | 값 클수록 CTR 상승 |
| 3 | `feat_e_3` | 값 클수록 CTR 하락 |

---

## Repository Structure

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
│   └── paper_xgb_summary.txt            # 본문 서술 자동 생성 텍스트
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

**메인 노트북 흐름 (`CTR_통합_최종.ipynb`)**

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

## How to Run

```bash
# 의존성 설치
pip install -r requirements_streamlit.txt

# Streamlit 대시보드 실행
streamlit run app_streamlit.py

# 제출 파일 생성 (샘플 데이터 기준)
python scripts/generate_submission.py

# 전체 데이터로 학습 후 제출 파일 생성
python scripts/generate_submission.py --full-train

# 데이터 다운로드 (URL 설정 필요)
python download_data.py
```

```python
# 노트북에서 직접 데이터 로드
import pandas as pd

train = pd.read_parquet("data/train_sample.parquet")  # 샘플 (권장)
train = pd.read_parquet("data/train.parquet")          # 전체
```

---

## Limitations

- **효과 크기 한계**: 통계적으로 유의한 변수들도 eta² ≤ 0.0013으로, 실무적 의사결정에 직접 활용하기엔 설명력이 제한적입니다.
- **클래스 불균형**: CTR ~1.9%로 모델 평가 지표 해석 시 주의가 필요합니다. AP·WLL은 대회 기준 참고 지표로만 사용합니다.
- **피처 익명화**: `feat_*`, `history_*` 피처는 원본 의미를 알 수 없어 도메인 해석에 제약이 있습니다.
- **데이터 접근**: `download_data.py`의 URL이 미설정(`YOUR_*`) 상태이므로 전체 데이터 다운로드는 별도 설정이 필요합니다.
- **DB 연동 선택적**: PostgreSQL·MongoDB 연결은 `.env` 설정 시에만 동작하며, 기본 실행은 parquet 파일로도 완전히 가능합니다.

---

## License

통계·데이터 분석 학습 및 연구 목적으로 사용됩니다.
