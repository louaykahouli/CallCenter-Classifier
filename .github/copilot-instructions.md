## Repository Snapshot

This repository provides a ticket-classification service built around a Hugging Face Transformer model, a fallback SVM, and a small "intelligent agent" router. Key folders:
- `Transformer/` : FastAPI app, model loading, training & deployment scripts, MLflow integration.
- `ia_agent/` : Complexity analyzer and router (decides between SVM, BERT, Transformer, or Grok).
- `tfidf_svm/` : SVM-based model artifacts and training code.

## Big picture (what to know first)
- The production API lives under `Transformer/` and exposes endpoints in `Transformer/api/main.py` (`/classify`, `/classify-batch`, `/classes`, `/stats`).
- Model selection is driven by `ia_agent.IntelligentAgent` (see `ia_agent/intelligent_agent.py`) which uses thresholds from the complexity analyzer (`ia_agent/complexity_analyzer.py`).
- The API can load either a local model (`USE_LOCAL_MODEL=True`) from `Transformer/models/transformer/best_model` or a Hugging Face model identified by `HF_MODEL_NAME` (see `Transformer/api/config.py`).
- MLflow tracking is optional and configured via `MLFLOW_TRACKING_URI` and `MLFLOW_EXPERIMENT_NAME` in `Transformer/api/config.py`.

## Quick developer workflows (concrete commands)
- Create venv and install deps (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r Transformer/requirements.txt
```
- Run the API locally (recommended when editing API code):
```powershell
cd Transformer
# Use Uvicorn directly (works cross-platform)
uvicorn api.main:app --host 0.0.0.0 --port 8000
```
- Full stack (MLflow + API): use the provided shell script `Transformer/start_all.sh` (requires a POSIX shell / WSL or Docker on Windows). If on Windows prefer WSL or Docker.
- Run unit tests for API:
```powershell
cd Transformer
pytest tests/test_api.py -q
```

## Configuration and toggles the AI should use when editing code
- Model source: toggle `USE_LOCAL_MODEL` in `Transformer/api/config.py`. When `True` the app expects `label_mappings.json` and model files under `Transformer/models/transformer/best_model`.
- HF model and token: `HF_MODEL_NAME`, `HF_TOKEN` in the same `config.py`.
- GPU toggle: `USE_GPU` in `config.py`.
- Batch limits and tokenization params are defined in `api/main.py` and `config.py` (`MAX_LENGTH`, `BATCH_SIZE`, max 100 tickets per batch).

## Project-specific conventions and patterns
- Two model loading strategies exist and should be preserved when modifying prediction code:
  - HF pipeline mode (preferred): uses `transformers.pipeline` for inference and reads labels from `model.config.id2label`.
  - Local mode: loads model/tokenizer via `AutoModelForSequenceClassification.from_pretrained()` and reads `label_mappings.json` for id→label mapping.
- The code logs and tries to start an MLflow run at API startup; avoid creating duplicate runs when editing startup logic.
- The `ia_agent` module is used to decide which model to call — change routing thresholds only in `ia_agent/intelligent_agent.py` and document any change in `ia_agent/README.md`.

## Integration points and external dependencies
- Hugging Face model hub: model id in `HF_MODEL_NAME`. Edits that change expected label names must also update `label_mappings.json` for local models.
- MLflow (optional): `MLFLOW_TRACKING_URI` default is `http://localhost:5000` and `start_all.sh` sets up MLflow in the repo scripts.
- Grok AI (optional): `ia_agent/grok_agent.py` expects an API key (`GROK_API_KEY`) — keep this optional and respect fallback to local analysis.
- SVM artifact: `tfidf_svm/models/tfidf_svm.joblib` (used for lightweight routing/tests).

## Examples of things to do safely (and where)
- Add a new API route: modify `Transformer/api/main.py` and add tests in `Transformer/tests/`.
- Change model input preprocessing: update `Transformer/src/data_preprocessing.py` and re-run training scripts in `Transformer/`.
- Change routing thresholds: update `ia_agent/intelligent_agent.py` and add unit tests calling `ia_agent` methods directly.

## Files to reference when performing common edits
- API entry: `Transformer/api/main.py`
- API config: `Transformer/api/config.py`
- Agent router and analyzer: `ia_agent/intelligent_agent.py`, `ia_agent/complexity_analyzer.py`
- Local model artifacts: `Transformer/models/transformer/best_model/` and `tfidf_svm/models/`
- Start scripts & deployment helpers: `Transformer/start_all.sh`, `Transformer/start_project.sh`, root `Dockerfile`, `docker-compose.yml`.

## Safety and non-goals for the assistant
- Do not commit secrets (HF tokens, GROK API keys) — prefer `.env` and `Transformer/api/config.py` reads from environment.
- Avoid changing MLflow run lifecycle semantics — edits that change when runs are started/stopped should include a clear justification and tests.

## If uncertain, ask the maintainer about
- Whether `USE_LOCAL_MODEL` should be the default for CI or HF model should be used.
- Expected label names and whether a change requires updating consumer clients (UI or external integrations).

---
If you'd like, I can merge this into an existing `.github/copilot-instructions.md` (none found) or expand any section with examples and runnable snippets. What should I refine next?
