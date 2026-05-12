# 프로젝트 파일 정리 — CTR 통계 분석

> **참고**: 본 문서는 초기 연구 가이드(v1)입니다. 최신 논문 작성 기준은 `thesis_data_v2.md`를 우선 참조하십시오.

광고 클릭률(CTR) 예측 관련 논문 개발 + 대회 제출용 코드 정리.

---

## 논문 반영 가이드 (통계 중심, 모델 보조)

### 1) 논문 메인 흐름

아래 순서로 서술하면 논문형 구조가 깔끔하게 잡힙니다.

1. EDA (기초 분포 확인)
2. 통계 검정 (핵심)
3. 결과 해석 (핵심)
4. 머신러닝 검증 (보조)
5. 실무적 시사점

핵심 메시지는 다음과 같이 고정:

> "CTR 예측 정확도 자체보다, CTR 차이의 원인을 통계적으로 설명하고 모델로 재확인하는 데 연구의 초점을 둔다."

---

### 2) 머신러닝 역할 정의 (논문 문장 템플릿)

모델을 주연으로 쓰지 말고, 통계 결과의 재검증 도구로 배치합니다.

권장 문장:

> "CTR 예측 모델을 통해 변수의 설명력 및 실무적 활용 가능성을 추가적으로 검증하였다."

보강 문장:

> "통계 검정에서 유의하게 확인된 변수(및 상호작용)가 예측 모델의 주요 설명 변수로도 일관되게 나타나는지 확인하였다."

---

### 3) 평가 지표 정리 (논문용)

지표를 과도하게 늘리지 않고, 아래처럼 계층을 나눕니다.

- 메인 지표: LogLoss (확률 예측 품질)
- 보조 지표: AUC (분류 순위 성능)
- 참고 지표: AP/WLL (대회 기준 비교용)

논문 본문에는 LogLoss와 AUC 중심으로 제시하고, AP/WLL은 "대회 기준 참고 지표"로 축약 기술하는 것을 권장.

---

### 4) 결과 작성 원칙 (성능 중심 -> 해석 중심)

피해야 할 문장:

> "XGBoost가 AP 0.01 더 높다."

권장 문장:

> "20대는 저녁 시간대 CTR이 유의하게 높았으며 (p < 0.05), 해당 패턴은 모델 중요 변수에서도 일관되게 확인되었다."

즉, "더 잘 맞췄다"보다 "왜 달라지는지 설명했다"를 우선합니다.

---

### 5) 제출 전 체크리스트

- [ ] 각 RQ별 통계 검정 결과(p-value)와 효과 크기를 함께 제시했는가?
- [ ] 통계 결과와 모델 중요 변수(또는 계수 방향)를 1:1로 연결했는가?
- [ ] 결론이 "성능 향상"이 아니라 "해석/원인 설명" 중심인가?
- [ ] 실무적 시사점(타겟팅/예산/노출 시간 최적화)으로 마무리했는가?

---

## 디렉토리 구조

```
statistical_ctr_analysis/
├── notebooks/
│   ├── CTR_논문제출용.ipynb             ← 논문 제출용 실행 노트북 (권장)
│   ├── CTR_통합_최종.ipynb              ← 통합 분석 원본 노트북
│   ├── CTR_최종점검.ipynb               ← 규모 일반화 검증 (200k vs 500k 통제 비교)
│   ├── paper_xgb_performance_table.csv ← 모델 성능표 (논문용 산출물)
│   ├── paper_xgb_shap_top10.csv        ← SHAP 상위 10개 피처 (논문용 산출물)
│   └── paper_xgb_summary.txt           ← 본문 서술 자동 생성 텍스트
├── scripts/
│   ├── generate_submission.py          ← 대회 제출 파일 생성 (XGBoost 기반)
│   └── upload_parquet_to_db.py         ← Parquet → DB 적재
├── src/
│   ├── ctr_analysis.py                 ← CTR 계산 유틸리티
│   ├── data_loader.py                  ← 데이터 로드 (Parquet / DB)
│   └── db_connector.py                 ← DB 연결 (PostgreSQL / MongoDB)
├── data/
│   ├── train.parquet                   ← 전체 학습 데이터
│   ├── train_sample.parquet            ← 200k 랜덤 샘플 (random_state=42)
│   ├── test.parquet                    ← 테스트 데이터 (1,527,298행)
│   └── sample_submission.csv           ← 제출 포맷 템플릿 (ID, clicked)
├── app_streamlit.py                    ← Streamlit 대시보드
├── download_data.py                    ← 데이터 다운로드 스크립트
├── thesis_data.md                      ← 이 파일 (v1 참고용)
└── thesis_data_v2.md                   ← 최신 논문 작성 기준 문서
```

---

## 노트북 파일

### `notebooks/CTR_논문제출용.ipynb` — **논문 제출용 실행 노트북 (권장)**
논문 제출을 위해 셀 흐름을 정리한 독립 노트북. 본문 재현 실행은 이 파일 기준을 권장.

| 단계 | 내용 |
|------|------|
| 1 | 데이터 로드 및 기본 통계 |
| 2 | EDA — CTR 분포, 클래스 불균형 확인 |
| 3 | **RQ1** — 사용자 특성(연령·성별)별 CTR + ANOVA, 카이제곱, Tukey HSD |
| 4 | **RQ2** — 시간대별 CTR + ANOVA, eta² |
| 5 | **RQ3** — 요일별 CTR + ANOVA, eta² |
| 6 | **RQ4** — XGBoost 학습 및 피처 수 실험 |
| 7 | SHAP 해석 — 상위 설명 변수 및 방향성 도출 |
| 8 | 논문용 결과물 자동 저장 (표·그림·서술문) |

---

### `notebooks/CTR_통합_최종.ipynb` — **통합 분석 원본 노트북**
- 개발/탐색 과정이 포함된 통합 버전
- 제출본 수정 시 원본 추적 및 비교 기준으로 활용

---

### `notebooks/CTR_최종점검.ipynb` — **규모 일반화 검증 노트북**
- **핵심 설계**: 동일 파이프라인·동일 하이퍼파라미터로 200k Baseline 재학습 후 500k 결과와 통제 비교
- 샘플 크기 외 모든 조건 통제 → 규모 일반화 가능성 직접 검증
- 논문 방법론의 재현성 근거로 활용 (→ `thesis_data_v2.md` 섹션 3.4 참조)

---

## 스크립트 파일

### `scripts/generate_submission.py` — **대회 제출 파일 생성 (핵심)**
`CTR_통합_최종.ipynb`의 피처 엔지니어링·모델 파이프라인을 독립 스크립트로 분리.

**구성:**
- 피처: `gender`, `age_group`, `inventory_id`, `day_of_week`, `hour` + `l_feat_*`, `feat_e_*` 등 수치형 전체
- 파생 변수: `time_of_day`, `weekday_weekend`
- 모델: **XGBoost** (top 100 features 기준, LogLoss 0.4959)
- 출력: `notebooks/submission_xgb_best.csv` (ID, clicked 확률값)

```bash
# 기본 (train_sample 50k, ~83초)
python scripts/generate_submission.py

# 전체 train 데이터 사용 (성능 향상, 느림)
python scripts/generate_submission.py --full-train
```

---

### `scripts/upload_parquet_to_db.py` — **DB 적재**
```bash
python scripts/upload_parquet_to_db.py postgres   # PostgreSQL
python scripts/upload_parquet_to_db.py mongodb    # MongoDB
```

---

## `src/` 모듈

| 파일 | 역할 |
|------|------|
| `src/data_loader.py` | Parquet / PostgreSQL / MongoDB에서 클릭 로그 로드 |
| `src/ctr_analysis.py` | 차원별 CTR 계산 (`compute_ctr_patterns`), 전체 통계 (`get_overall_stats`) |
| `src/db_connector.py` | PostgreSQL (psycopg2) / MongoDB (pymongo) 연결 유틸리티 |

---

## 기타

### `app_streamlit.py` — Streamlit 대시보드
```bash
streamlit run app_streamlit.py
```
`src/data_loader` + `src/ctr_analysis` 를 사용해 CTR 패턴을 웹 UI로 시각화.

### `download_data.py` — 데이터 다운로드
`data/` 폴더에 train.parquet, test.parquet, sample_submission.csv 다운로드 + train_sample.parquet 생성. URL은 파일 내 `get_data_urls()` 에 직접 입력 필요.

---

## 노트북 역할 요약 (현재 기준)

| 노트북 | 역할 | 논문 포지션 |
|--------|------|------------|
| `CTR_논문제출용.ipynb` | 제출용 실행 흐름(EDA + 통계 + XGBoost + SHAP) | **핵심 본문(실행 기준)** |
| `CTR_통합_최종.ipynb` | 통합 분석 원본/개발 히스토리 | 본문 근거 보강 |
| `CTR_최종점검.ipynb` | 200k vs 500k 통제 비교, 재현성 점검 | 방법론 보강 / 부록 |


권장 서술 문장:

> "본 연구는 통계 검정을 통해 CTR 차이의 원인을 우선 규명하고, 예측 모델(XGBoost + SHAP)을 통해 동일 패턴이 모델에서도 재현되는지 추가 검증하였다. 규모 일반화 가능성은 동일 조건 통제 비교(re-trained baseline, 200k vs 500k)를 통해 실증하였다."

---

## 데이터 파일 요약

| 파일 | 행 수 | 컬럼 수 | 용도 |
|------|-------|---------|------|
| `train.parquet` | ~수백만 | 119 | 전체 학습 데이터 |
| `train_sample.parquet` | 200,000 | 119 | 랜덤 샘플 (random_state=42) |
| `test.parquet` | 1,527,298 | 118 | 제출용 예측 대상 (`clicked` 컬럼 없음) |
| `sample_submission.csv` | 1,527,298 | 2 | 제출 포맷 (`ID`, `clicked`) |

**주요 피처 그룹:**
- 사용자: `gender`, `age_group`
- 환경: `inventory_id`, `day_of_week`, `hour`
- 행동 수치: `l_feat_1~27`, `feat_e_1~10`, `feat_d_1~6`, `feat_c_1~8`, `feat_b_1~6`, `feat_a_1~18`
- 히스토리: `history_a_1~7`, `history_b_1~30`
- 타겟: `clicked` (0/1, CTR ≈ 2.0%)
