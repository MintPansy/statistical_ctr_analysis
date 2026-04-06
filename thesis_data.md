# 프로젝트 파일 정리 — CTR 통계 분석

광고 클릭률(CTR) 예측 관련 논문 개발 + 대회 제출용 코드 정리.

---

## 디렉토리 구조

```
statistical_ctr_analysis/
├── notebooks/
│   ├── static_laboratory2.ipynb        ← 논문 메인 분석 노트북
│   ├── CTR_토스_논문_최종.ipynb         ← 논문 최종본 (합성 데이터 포함)
│   └── ctr_pattern_db.ipynb            ← DB 연동 패턴 분석
├── scripts/
│   ├── generate_submission.py          ← 대회 제출 파일 생성 (핵심)
│   └── upload_parquet_to_db.py         ← Parquet → DB 적재
├── src/
│   ├── ctr_analysis.py                 ← CTR 계산 유틸리티
│   ├── data_loader.py                  ← 데이터 로드 (Parquet / DB)
│   └── db_connector.py                 ← DB 연결 (PostgreSQL / MongoDB)
├── data/
│   ├── train.parquet                   ← 전체 학습 데이터
│   ├── train_sample.parquet            ← 50k 샘플 (빠른 개발용)
│   ├── test.parquet                    ← 테스트 데이터 (1,527,298행)
│   └── sample_submission.csv           ← 제출 포맷 템플릿 (ID, clicked)
├── app_streamlit.py                    ← Streamlit 대시보드
├── download_data.py                    ← 데이터 다운로드 스크립트
└── thesis_data.md                      ← 이 파일
```

---

## 노트북 파일

### `notebooks/static_laboratory2.ipynb` — **논문 메인 노트북**
논문 분석의 핵심. 아래 순서로 실행.

| 셀 범위 | 내용 |
|---------|------|
| Cell 0–4 | 환경 설정, 데이터 로드 (`train_sample.parquet`, 50k rows) |
| Cell 5–9 | CTR 기본 시각화 (분포, 불균형 확인) |
| Cell 13–14 | **RQ1**: 성별·연령대별 CTR 분석 + 통계 검정 (ANOVA, Kruskal-Wallis, Cramér's V) |
| Cell 17–18 | **RQ2**: 시간대·요일별 CTR 분석 + 통계 검정 |
| Cell 24–34 | **피처 엔지니어링**: age_gender_interaction, time_of_day, weekday_weekend, 상관관계 히트맵 |
| Cell 37–43 | 데이터 인코딩 (OHE + StandardScaler), Logistic Regression 학습·평가 |
| Cell 44 | **3-Fold Stratified CV** + PR 곡선 + 최적 임계값 탐색 |
| Cell 45 | **Ablation Study**: User / Env / Combined / Full 피처 서브셋 비교 (RQ4) |
| Cell 46 | SHAP + XGBoost 해석 (xgboost 설치 필요) |
| Cell 57–61 | 테스트 데이터 전처리 → 노트북 내 제출 파일 생성 |
| Cell 65–66 | test.parquet 전체 로드 (배치) → 제출 파일 검증 |

**속도 관련 파라미터** (빠른 개발 ↔ 논문 제출 전환):
- Cell 4: `n_rows=50_000` → 논문 제출 시 `n_rows=None` (전체)
- Cell 44, 45: `n_splits=3` → 논문 제출 시 `n_splits=5`

---

### `notebooks/CTR_토스_논문_최종.ipynb` — **논문 최종본**
- 합성 데이터(`train_sample_2000000.csv`) 생성 코드 포함 → 실제 데이터 없이도 실행 가능
- CTR 기본 통계, 시간 패턴, 사용자 특성 분석, 모델 성능 시각화
- xgboost, shap 포함 → 첫 실행 시 `!pip install` 필요

---

### `notebooks/ctr_pattern_db.ipynb` — **DB 연동 패턴 분석**
- `src/` 모듈 (data_loader, ctr_analysis) 활용
- PostgreSQL 또는 MongoDB에서 클릭 로그 로드 후 CTR 패턴 분석
- Streamlit 대시보드(`app_streamlit.py`)와 연동되는 분석 흐름 확인용

---

## 스크립트 파일

### `scripts/generate_submission.py` — **대회 제출 파일 생성 (핵심)**
`static_laboratory2.ipynb`의 피처 엔지니어링·모델 파이프라인을 독립 스크립트로 분리.

**노트북과 동일한 구성:**
- 피처: `gender`, `age_group`, `inventory_id`, `day_of_week`, `hour` (OHE) + `l_feat_*`, `feat_e_*` 등 수치형 전체
- 파생 변수: `time_of_day`, `weekday_weekend`
- 모델: `LogisticRegression(class_weight='balanced', solver='saga')`
- 출력: `notebooks/submission.csv` (ID, clicked 확률값)

**노트북 대비 개선점:**
- test.parquet을 100k 배치로 나눠 처리 (메모리 효율)
- saga solver + n_jobs=-1 (병렬, 빠름)
- 약 83초 완료 (1.5M 행 예측 포함)

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

## 데이터 파일 요약

| 파일 | 행 수 | 컬럼 수 | 용도 |
|------|-------|---------|------|
| `train.parquet` | ~수백만 | 119 | 전체 학습 데이터 |
| `train_sample.parquet` | 50,000 | 119 | 빠른 개발·실험용 샘플 |
| `test.parquet` | 1,527,298 | 118 | 제출용 예측 대상 (`clicked` 컬럼 없음) |
| `sample_submission.csv` | 1,527,298 | 2 | 제출 포맷 (`ID`, `clicked`) |

**주요 피처 그룹:**
- 사용자: `gender`, `age_group`
- 환경: `inventory_id`, `day_of_week`, `hour`
- 행동 수치: `l_feat_1~27`, `feat_e_1~10`, `feat_d_1~6`, `feat_c_1~8`, `feat_b_1~6`, `feat_a_1~18`
- 히스토리: `history_a_1~7`, `history_b_1~30`
- 타겟: `clicked` (0/1, CTR ≈ 2.0%)
