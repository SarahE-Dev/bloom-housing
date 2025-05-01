# 👩‍💻 Developer Guide: Housing Risk Prediction Microservice

Welcome to the developer guide for the **Housing Risk Prediction Microservice**, a Flask-based API that provides housing instability risk scores. This service is part of the [`bloom-housing`](https://github.com/SarahE-Dev/bloom-housing) monorepo.

---

## 📦 Overview

This microservice exposes a `/predict` endpoint powered by an XGBoost model trained on U.S. Census housing data. It is designed to be consumed by the main NestJS backend and can run independently for testing and development.

---

## 🧭 Key Components

| Location | Purpose |
|---------|---------|
| `app/` | Contains the Flask app, Dockerfile, and model artifacts |
| `pipeline/` | Scripts for data cleaning, processing, and model training |
| `tests/` | pytest suite for validating the `/predict` endpoint |
| `data/` | Place raw CSVs from the AHS dataset here |
| `notebooks/` | Jupyter notebooks for EDA and experimentation |
| `assets/` | Screenshots and visuals for documentation |
| `docs/` | This guide and future documentation lives here |

---

## 🔧 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/SarahE-Dev/bloom-housing.git
cd bloom-housing/model
```

### 2. Set up your Python environment

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## 📊 Data Processing & Model Training

### 1. Get the data

Download the **AHS 2023 National PUF v1.1 CSV** dataset:

- 📎 [Download Link](https://www.census.gov/programs-surveys/ahs/data/2023/ahs-2023-public-use-file--puf-/ahs-2023-national-public-use-file--puf-.html)
- Place the `.csv` file(s) in the `model/data/` folder without renaming.

### 2. Run the pipeline

```bash
python pipeline/data_processing.py
python pipeline/model_training.py
```

- Artifacts will be saved to `app/` as:
  - `xgboost_model.pkl`
  - `scaler.pkl`

---

## 🚀 Run the API

### Option 1: Locally with Flask

```bash
python app/main.py
```

This starts the server at `http://localhost:5000/predict`.

### Option 2: With Docker

```bash
docker compose up --build
```

If consumed by NestJS, be sure the service URL matches (`http://localhost:5000/predict` or internal Docker network name).

---

## 📡 API Reference

### `POST /predict`

#### Payload Format:

```json
{
  "age": 30,
  "income": 50000,
  "veteran": false,
  "benefits": true,
  "threshold": 0.5
}
```

#### Sample Response:

```json
{
  "prediction": 1,
  "probability": 0.8234,
  "label": "At risk"
}
```

- `threshold` is optional; default is `0.5`.

---

## 🧪 Testing

### Manual test:

```bash
python tests/test_prediction.py
```

### With pytest:

```bash
pytest tests/test_prediction.py
```

---

## 🧩 Common Issues

- **Model file not found (`xgboost_model.pkl` or `scaler.pkl`)**  
  Make sure you've run the full data pipeline:
  ```bash
  python pipeline/data_processing.py
  python pipeline/model_training.py
  ```

- **Docker errors related to ports**  
  Ensure port `5000` is not already in use, or change the exposed port in `docker-compose.yaml`.

- **Prediction returns 500 error**  
  Check the request body format. All expected fields must be present and correctly typed.

- **App won't start on Windows**  
  Try running with:
  ```bash
  set FLASK_APP=app/main.py
  python -m flask run
  ```
---

## 🔍 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | Ensure you're in the virtual environment and installed dependencies |
| Model not found | Ensure you've run both pipeline scripts to generate the artifacts |
| Flask doesn't restart on change | Install and run with `flask run --reload` or use a dev watcher |

---

## 🤝 Contributing

Contributions are welcome and appreciated! To get started:

1. Fork the repository and create a new branch.
2. Make your changes with clear, concise commits.
3. Ensure all tests pass:
   ```bash
   pytest
   ```
4. Open a pull request with a detailed description.

Please follow the existing code style and folder conventions. Check out `docs/developer_guide.md` if you’re working on the data pipeline or API logic.

---

## 🙌 Contributing Tips

- Keep data transformation logic inside `pipeline/`—keep `main.py` minimal.
- Make sure model outputs stay in sync with expected schema.
- Document any assumptions in `/docs/` as needed.
- Test often—changes to preprocessing or model structure may require retraining.

---

## 📬 Questions or Support

If you have questions or need help getting set up:

- Open an [Issue](https://github.com/SarahE-Dev/bloom-housing/issues)
- Reach out to us on GitHub

## 📜 Licensing

This project is released under the MIT License.






