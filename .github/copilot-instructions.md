# Project Guidelines

## Code Style
- Follow existing Python style in `src/`, `scripts/`, and `app_streamlit.py`: type hints where practical, small focused functions, and minimal comments.
- Preserve current naming conventions for data fields and features (for example `clicked`, `day_of_week`, `l_feat_*`, `history_b_*`).
- Prefer UTF-8 safe handling for Korean text in docs/notebooks, but keep source code changes straightforward and readable.

## Architecture
- Core analytics logic lives in `src/`:
  - `src/data_loader.py`: unified loader for `parquet`, `postgres`, and `mongodb`.
  - `src/ctr_analysis.py`: CTR aggregation/statistics helpers.
  - `src/db_connector.py`: optional DB connectivity and parquet-to-DB helpers.
- UI layer is `app_streamlit.py` and should stay thin: load data via `src.data_loader`, compute metrics via `src.ctr_analysis`.
- Batch prediction pipeline is `scripts/generate_submission.py`.
- Data acquisition/bootstrap is `download_data.py`.
- Notebook outputs in `notebooks/` are artifacts; avoid editing generated outputs unless the task is explicitly about results.

## Build And Run
- Install dependencies:
  - `pip install -r requirements_streamlit.txt`
- Run dashboard:
  - `streamlit run app_streamlit.py`
- Generate submission:
  - `python scripts/generate_submission.py`
  - `python scripts/generate_submission.py --full-train`
- Download/bootstrap data:
  - `python download_data.py`
  - `python download_data.py --sample-only`
- Optional DB upload:
  - `python scripts/upload_parquet_to_db.py postgres`
  - `python scripts/upload_parquet_to_db.py mongodb`

## Conventions
- Default data source is parquet and should remain the safe fallback for local work.
- For routine development, prefer `data/train_sample.parquet` to reduce runtime/memory.
- Click target columns can vary by dataset; shared helpers auto-detect from known names. Reuse that behavior instead of hardcoding new target names.
- Keep feature engineering consistent with current training pipeline (`time_of_day`, `weekday_weekend`) unless a task explicitly changes modeling assumptions.

## Pitfalls
- `download_data.py` ships with placeholder URLs (`YOUR_*`); full data download will be skipped until configured.
- Full datasets (`train.parquet`, `test.parquet`) may be absent; do not assume they exist.
- DB access is optional and environment-driven via `.env` (`POSTGRES_URI`, `MONGODB_URI`); code should keep parquet paths usable without DB setup.
- No automated test suite is currently configured in this repository. If you add logic, validate with focused script runs and document what was executed.

## References
- Project overview and workflow: `README.md`
- Research framing and statistical guidance: `thesis_data.md`
- Evaluation-metric priorities and thesis alignment: `thesis_data_v2.md`
