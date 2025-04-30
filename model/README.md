# 🏠 Housing Risk Prediction Microservice

This is a Flask-based microservice within the [`bloom-housing`](https://github.com/SarahE-Dev/bloom-housing) monorepo. It powers housing instability screening by providing a `/predict` endpoint that returns a risk score based on anonymized housing application data.

This service is intended to be consumed by the main NestJS backend via `http://localhost:5000/predict`.

> 📢 **Note**: If you're running this via Docker, update the `application-service` endpoint in NestJS accordingly.

---

## 🧰 Technologies Used

- **Python 3.10**
- **Flask** – Micro web framework for the API
- **XGBoost** – Machine Learning Library
- **Docker** – Containerization
- **Postman or curl** – API testing
- **VS Code + Python extensions** – Suggested for development

---

## 📸 Features & Screenshots

### ✅ Application submits and receives prediction in browser console

<img src="./assets/browser-console.png" alt="Browser console with prediction response" width="600"/>

### 🧪 Local test request via `utils/test_prediction.py`

<img src="./assets/test-console.png" alt="Python script testing endpoint" width="600"/>

---

## 📁 Folder Structure

```
model/
├── app/
│   ├── Dockerfile           # Model container setup
│   ├── main.py              # Flask app with /predict endpoint
│   ├── xgboost_model.pkl    # Trained XGBoost model artifact
│   ├── scaler.pkl           # Scaler artifact
│   └── requirements.txt     # Specific requirements for prediction container
│
├── data/                    # Raw AHS CSV files (place data here)
│
├── pipeline/                # Data processing and model training scripts
│   ├── data_processing.py   # Download/clean raw data and write features
│   └── model_training.py    # Train the XGBoost model and save artifacts to app/
│
├── tests/                   # Automated tests
│   └── test_prediction.py   # pytest suite for the /predict endpoint
│
├── assets/                  # Screenshots and diagrams
│
├── docs/
│   └── developer_guide.md   # Guide for developers working on this service
│
├── notebooks/               # Data exploration and modeling notebooks
│
├── docker-compose.yaml      # Builds and sets up container environment
├── requirements.txt         # Python dependencies
└── README.md                # You’re here!
```

---

## 📋 Prerequisites

Before starting, make sure you have the following installed:

- Python 3.10+
- pip (Python package manager)
- Git
- Docker (optional for containerized runs)
- Your preferred environment manager

---

## 💻 Installation & Pipeline

1. **Clone the repo and navigate to `model/`:**

   ```bash
   git clone https://github.com/SarahE-Dev/bloom-housing.git
   cd bloom-housing/model
   ```

2. **Set up your virtual environment**:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare data**:
   - Download and extract the **"AHS 2023 National PUF v1.1 CSV"** zip from:
     https://www.census.gov/programs-surveys/ahs/data/2023/ahs-2023-public-use-file--puf-/ahs-2023-national-public-use-file--puf-.html
   - Place the extracted `.csv` into the `model/data/` folder. You do **NOT** need to rename any of the files`.

5. **Run the data processing and training pipeline**:

   ```bash
   python pipeline/data_processing.py
   python pipeline/model_training.py
   ```

   - This will generate `model/app/xgboost_model.pkl` and `model/app/scaler.pkl`.

6. **Start the Flask app**:

   ```bash
   python app/main.py
   ```

---

## 🐳 Running with Docker

1. **Build and run the container**:

   ```bash
   docker compose up --build
   ```

2. **Test the endpoint locally**:

   ```bash
   pytest tests/test_prediction.py  
   ```

---

## 📡 Prediction API

### `POST /predict`

Send anonymized housing-related features and receive a risk score.

#### Example Request Body:

```json
{
  "age": 30,
  "income": 50000,
  "veteran": false,
  "benefits": true,
  "threshold": 0.5
}
```

#### Example Response:

```json
{
  "prediction": 1,
  "probability": 0.8234,
  "label": "At risk"
}
```

---

## 🧪 Testing

Run the pytest suite:

```bash
pytest tests/test_prediction.py
```

---

## 🙌 Acknowledgements

- Created as part of the [Bloom Housing](https://github.com/bloom-housing/bloom) initiative
- Thanks to the open-source communities behind Flask, XGBoost
- Inspired by real-world housing application risk screening needs

---

## 📄 License

MIT License — see the root `LICENSE` file for details.


