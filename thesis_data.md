# 프로젝트 파일 정리 — CTR 통계 분석

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
│   ├── static_laboratory2.ipynb        ← 논문 메인 분석 노트북
│   ├── CTR_toss_thesis_final.ipynb         ← 논문 최종본 (합성 데이터 포함)
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
│   ├── train_sample.parquet            ← 200k 랜덤 샘플 (random_state=42)
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
| Cell 0–4 | 환경 설정, 데이터 로드 (`train_sample.parquet`, 샘플 데이터) |
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

## 노트북 3종 비교 분석

비교 대상:
- `static_laboratory2.ipynb`
- `CTR_토스_논문_최종 (1).ipynb`
- `stat_CTR_p1.ipynb`

---

### 1) 한눈에 보는 역할 구분

| 항목 | static_laboratory2.ipynb | CTR_토스_논문_최종 (1).ipynb | stat_CTR_p1.ipynb |
|------|---------------------------|-------------------------------|-------------------|
| 목적 | 논문 메인(통계 검정 + 해석 + LR) | 통합 최종 실행/시각화 중심 | DCN 딥러닝 실험(심화 모델) |
| 연구 포지션 | **핵심 본문** | 본문 보완/부록성 결과 | 비교 실험(보조) |
| 권장 사용 | RQ 검정, 해석 서술의 기준본 | 재현 실행, 그림/표 보강 | "통계 결과 재검증" 용 모델 실험 |

---

### 2) 방법론 비교 (통계 vs 모델)

| 구분 | static_laboratory2.ipynb | CTR_토스_논문_최종 (1).ipynb | stat_CTR_p1.ipynb |
|------|---------------------------|-------------------------------|-------------------|
| EDA | 체계적 (RQ 흐름에 맞춤) | 통합 시각화 중심 | 포함 (모델 실험 전 탐색) |
| 통계 검정 | ANOVA/Kruskal/카이제곱 계열 중심 | 일부 통합/요약 중심 | 상대적으로 약함 |
| 상호작용 해석 | 명시적 (age×gender, time 파생) | 통합 서술 가능 | 모델 내부 학습에 흡수 |
| 머신러닝 | Logistic Regression (해석 용이) | LR + 확장 실험 혼합 가능 | WideDeepCTR (DCN, Bi-LSTM) |
| 해석 가능성 | 높음 | 중간 | 낮음(블랙박스 성향) |

---

### 3) 논문 반영 관점에서의 장단점

#### static_laboratory2.ipynb
- 장점: 통계 검정 -> 해석 -> 모델 검증 흐름이 논문 구조와 가장 일치
- 장점: 변수별 효과를 본문 문장으로 옮기기 쉬움
- 한계: 성능 최적화보다는 설명 중심이라 대회 점수 극대화에는 불리할 수 있음

#### CTR_토스_논문_최종 (1).ipynb
- 장점: 통합 실행본으로 그림/표 산출과 결과 확인이 편함
- 장점: 최종 정리 단계에서 재현성 점검에 유리
- 한계: 분석 목적과 실험 목적이 섞이면 본문 논리(가설-검정-해석)가 흐려질 수 있음

#### stat_CTR_p1.ipynb
- 장점: 고급 모델(DCN)로 "예측 관점 보조 검증"에 적합
- 장점: 시퀀스 피처 활용 근거를 제시하기 좋음
- 한계: 해석 난도가 높아 본문 메인으로 쓰기에는 부담
- 한계: 환경 의존/학습 복잡도로 재현성 관리가 필요

---

### 4) 최종 권장 구성 (논문형)

1. **메인 분석 노트북**: `static_laboratory2.ipynb`
2. **최종 통합 실행/정리**: `CTR_토스_논문_최종 (1).ipynb`
3. **보조 성능 검증 실험**: `stat_CTR_p1.ipynb`

권장 서술 문장:

> "본 연구는 통계 검정을 통해 CTR 차이의 원인을 우선 규명하고, 추가적으로 예측 모델을 통해 해당 변수들의 설명력과 실무 활용 가능성을 재검증하였다."

---

### 5) 본문에 바로 넣을 비교 요약

> "세 노트북 중 `static_laboratory2.ipynb`를 본 연구의 핵심 분석 프레임으로 사용하였다. `CTR_토스_논문_최종 (1).ipynb`는 통합 실행과 결과 정리 용도로 활용했으며, `stat_CTR_p1.ipynb`는 DCN 기반 보조 실험으로 통계적으로 도출된 패턴의 예측적 일관성을 확인하는 데 사용하였다. 따라서 본 연구의 중심은 통계적 설명에 두고, 머신러닝은 검증 도구로 제한하였다."

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
