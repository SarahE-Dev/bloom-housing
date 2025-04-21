# 🧑‍💻 Developer Guide — Housing Risk Prediction Microservice

This guide provides key information for developers contributing to the `bloom-housing` risk prediction microservice. Whether you're fixing a bug, tweaking the model, or deploying with Kubernetes — this document has you covered.

---

## 📁 Project Structure

```
model/
├── app/
│   ├── main.py              # Flask app
│   └── model.pkl            # Trained model
├── assets/                  # Visual assets for documentation
│   ├── browser-console.png
│   ├── microservice-flow.png
│   └── test-console.png
├── docs/                    # Developer documentation
│   └── developer_guide.md
├── utils/                   # Scripts for training and testing
│   ├── test_prediction.py
│   └── train_model.py
├── .gitignore               # Git exclusions
├── deployment.yaml          # K8s deployment config
├── Dockerfile               # Docker container setup
├── README.md                # Project overview & usage
├── requirements.txt         # Python dependencies
└── service.yaml             # K8s service config
```

---

## ⚙️ Environment Setup

### Required Tools

- Python 3.10+
- Docker (optional, for containerized runs)
- Minikube & kubectl (optional, for local K8s testing)
- Git
- VS Code or preferred IDE

### Setup Steps

```bash
git clone https://github.com/SarahE-Dev/bloom-housing.git
cd bloom-housing/model
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python utils/train_model.py
cd app && python main.py
```

Test prediction:
```bash
python utils/test_prediction.py
```

---

## 🧠 Model Overview

- **Algorithm**: XGBoost Classifier
- **Inputs**: JSON-encoded application data
- **Output**: Categorical risk score (0–1)
- **Training**: Synthetic data via `utils/train_model.py`
- **Serving**: Flask microservice

To re-train:
```bash
python utils/train_model.py
```

---

## 🧪 Testing & Debugging

Run test request:

```bash
python utils/test_prediction.py
```

Add your own payload in the script to simulate real applications.

### Logging

All key actions and prediction steps are logged to console. Consider using Python’s built-in `logging` module for enhanced logging to file or external service (e.g., Sentry, Datadog).

---

## 🐛 Troubleshooting Common Issues

| Error Message | Likely Cause | Fix |
|---------------|--------------|-----|
| `ModuleNotFoundError` | Missing dependency | Re-run `pip install -r requirements.txt` |
| `model.pkl not found` | Model not trained | Run `python utils/train_model.py` |
| `unhandledRejection: TypeError` | Issue with frontend/backend setup | Check API response formatting and Tailwind config |
| CORS or network issues | Wrong endpoint or port | Ensure Flask is running on `localhost:5000` |

---

## 📡 API Reference

### POST `/predict`

Accepts a JSON payload with housing-related features. Returns a `risk_score`.

See the [README.md](../README.md#prediction-api) for request/response examples.

---

## 🔀 Branching & Workflow

### 🏷️ Conventional Commits

Use the [Conventional Commits](https://www.conventionalcommits.org/) format:

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring (no feature change)
- `test:` Adding or updating tests
- `chore:` Maintenance (build config, etc.)

### 📦 Branch Strategy

- `main` – Stable, production-ready
- `develop` – Active sprint work
- `feature/*` – New features
- `bugfix/*` – Fixes
- `docs/*` – Documentation updates

---

## 📄 Contribution Guidelines

1. Fork and clone the repo
2. Create a feature branch:  
   `git checkout -b feature/improve-validation`
3. Code your change
4. Write/update tests
5. Commit with a [conventional commit](https://www.conventionalcommits.org/)
6. Push and open a Pull Request to `develop`
7. Tag maintainers for review

---

## 📈 Model Lifecycle Management

### When to Retrain

- Input schema changes
- Model logic or features change
- You integrate real-world data

### Steps

```bash
python utils/train_model.py
# Replace model.pkl in /app/
```

Version models in `model_vX.pkl` format if needed.

---

## 🔒 Security & Privacy

This project avoids PII — inputs are limited to anonymized, synthetic features. If you intend to integrate real data, ensure compliance with local privacy laws (e.g., GDPR, HIPAA).

---

## ☁️ Deployment Notes

### Docker

```bash
docker build -t housing-service .
docker run -p 5000:5000 housing-service
```

### Kubernetes (Minikube)

```bash
minikube start
eval $(minikube docker-env)
docker build -t housing-service .
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl port-forward housing-service-loadbalancer 5000:5000
```

---

## 🚧 Roadmap Highlights

- Integrate with real housing application data
- Enable feature logging and monitoring
- Add automated CI/CD
- Improve model explainability (e.g., SHAP)

---

## 🧵 Suggested Enhancements

- Add endpoint for feature introspection
- Add schema validation (e.g., `pydantic`)
- Model versioning support

---

## 🤝 Maintainers & Contacts

This repo is maintained by the JTC Team 4 Bloom Housing project team.  
Ping us via GitHub Issues for questions!

