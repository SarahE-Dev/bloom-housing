# Bloom Affordable Housing Platform

Bloom is [Exygy](https://www.exygy.com/)’s affordable housing platform. Bloom's goal is to be a single entry point for affordable housing seekers and application management for developers. You can read more about the platform on [bloomhousing.com](https://bloomhousing.com/).

## Overview

![TypeScript](https://img.shields.io/badge/typescript-%23007ACC.svg?style=for-the-badge&logo=typescript&logoColor=white)
![Next.js](https://img.shields.io/badge/Next-black?style-for-the-badge&logo=next.js&logoColor=white)
![NestJS](https://img.shields.io/badge/nestjs-%23E0234E.svg?style-for-the-badge&logo=nestjs&logoColor=white)
![Prisma](https://img.shields.io/badge/Prisma-3982CE?style-for-the-badge&logo=Prisma&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style-for-the-badge&logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style-for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style-for-the-badge&logo=flask&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-%23d6f0fa.svg?style-for-the-badge&logo=xgboost&logoColor=black)
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style-for-the-badge&logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/kubernetes-%23326ce5.svg?style-for-the-badge&logo=kubernetes&logoColor=white)
![SASS](https://img.shields.io/badge/SASS-hotpink.svg?style-for-the-badge&logo=SASS&logoColor=white)
![Jest](https://img.shields.io/badge/-jest-%23C21325?style-for-the-badge&logo=jest&logoColor=white)
![Cypress](https://img.shields.io/badge/-cypress-%23E5E5E5?style-for-the-badge&logo=cypress&logoColor=058a5e)
![Testing-Library](https://img.shields.io/badge/-TestingLibrary-%23E33332?style-for-the-badge&logo=testing-library&logoColor=white)

Bloom consists of a client/server architecture using [Next.js](https://nextjs.org) for the frontend applications and [NestJS](https://nestjs.com), [Prisma](https://www.prisma.io/), and [Postgres](https://www.postgresql.org/) on the backend.

### Structure

Bloom uses a monorepo-style repository containing multiple user-facing applications and backend services. The main high-level packages are `api`, `sites`, `model`, and `shared-helpers`. Additionally, Bloom's UI leverages the in-house packages `@bloom-housing/ui-seeds` and `@bloom-housing/ui-components`.

```
bloom/
├── api/                    # Backend services (NestJS, Prisma, Postgres)
├── model/                  # Risk prediction microservice (Python, Flask, XGBoost)
├── sites/                  # Frontend applications
│   ├── public/             # Applicant-facing portal (Next.js)
│   └── partners/           # Developer and admin portal (Next.js)
├── shared-helpers/         # Shared types, functions, and components
├── @bloom-housing/ui-seeds # Design system and React component library
├── @bloom-housing/ui-components # Legacy component library (being phased out)
```

- **`sites/public`**: Applicant-facing site for browsing and applying to listings using Bloom’s Common Application or third-party applications. See [sites/public/README](https://github.com/bloom-housing/bloom/blob/main/sites/public/README.md).
- **`sites/partners`**: Secure portal for housing developers, property managers, and city/county employees to manage applications and listings. Requires login. See [sites/partners/README](https://github.com/bloom-housing/bloom/blob/main/sites/partners/README.md).
- **`api`**: Backend services (e.g., listings, applications, users) stored in a Postgres database and served via a REST API over HTTPS. See [api/README](https://github.com/bloom-housing/bloom/blob/main/api/README.md).
- **`model`**: Flask-based microservice using XGBoost to predict housing instability risk based on features like income and household size. Exposes a `/predict` endpoint. See [model/README](https://github.com/bloom-housing/bloom/blob/main/model/README.md).
- **`shared-helpers`**: Shared types, functions, and components for public and partners sites. See [shared-helpers/README](https://github.com/bloom-housing/bloom/blob/main/shared-helpers/README.md).
- **`@bloom-housing/ui-seeds`**: Component library with React components and design system tokens. Explore the [Storybook](https://storybook-ui-seeds.netlify.app/?path=/story/tokens-introduction--page) and [design documentation](https://zeroheight.com/5e69dd4e1/p/938cb5-seeds-design-system).
- **`@bloom-housing/ui-components`**: Legacy component library, being replaced by `ui-seeds`. View the [Storybook](https://storybook.bloom.exygy.dev/).

## Getting Started for Developers

If this is your first time working with Bloom, check the `sites/public`, `sites/partners`, `api`, and `model` README files for specific configuration details before proceeding with the setup instructions below.

## Starting Locally

### Dependencies

Run `yarn install` at the root and from within the `api` directory.

If you don’t have Yarn installed, install [Homebrew](https://brew.sh/) and run `brew install yarn`.

### Local Environment Variables

Configuration is read from environment variables. Copy `.env.template` to `.env` in `sites/public`, `sites/partners`, `api`, and `model`. Some keys are secret and available internally. Template files include default values and variable descriptions.

### VSCode Extensions

Recommended extensions for VSCode:

- [Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode): Enable `Format on Save` (⌘⇧P > Open User Settings > search `Format on Save` > enable, then Reload Window).
- [Postgres Explorer](https://marketplace.visualstudio.com/items?itemName=ckolkman.vscode-postgres): Inspect local database (see [api/README](https://github.com/bloom-housing/bloom/blob/main/api/README.md)).
- [Code Spell Checker](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker): Flags spelling errors.
- [CSS Variable Autocomplete](https://marketplace.visualstudio.com/items?itemName=vunguyentuan.vscode-css-variables): Autocompletes `ui-seeds` CSS variables (see [public/README](https://github.com/bloom-housing/bloom/blob/main/sites/public/README.md)).
- [CSS Module Autocomplete](https://marketplace.visualstudio.com/items?itemName=clinyong.vscode-css-modules): Autocompletes CSS module files.
- [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python): Supports model development.

### Running a Local Test Server

Run `yarn dev:all` from the root to start three processes on different ports:

- Public app: `http://localhost:3000`
- Partners app: `http://localhost:3001`
- API: `http://localhost:3100`

Alternatively, run each process individually from separate terminals in `api`, `sites/public`, or `sites/partners` with `yarn dev`.

### Risk Prediction Model

The `model/app/` directory contains a Flask-based microservice powered by an XGBoost model to predict housing instability risk based on features like income, household size, housing status, income vouchers, household expecting changes, and household student status. It exposes a `/predict` endpoint and can be run standalone for local development or testing without requiring the full Bloom platform.

#### Setup and Run Locally (Standalone)

1. **Prerequisites**:

   - Python 3.10+ ([python.org](https://www.python.org/downloads/)).
   - pip (Python package manager).
   - Git.
   - Optional: Docker for containerized runs, Minikube and kubectl for Kubernetes.

2. **Set Up Virtual Environment**:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   Install required Python libraries (e.g., flask, xgboost, pandas, numpy):

   ```bash
   pip install -r requirements.txt
   ```

4. **Train the Model**:
   Generate synthetic training data and save the trained model to `app/mock-model.pkl`:

   ```bash
   python utils/train_model.py
   ```

5. **Run the Flask Microservice**:
   Start the Flask API server:

   ```bash
   cd app
   python main.py
   ```

   The service will be available at `http://localhost:5000/predict`.

6. **Test the API**:
   In another terminal from the `model/` directory, send a test request to the `/predict` endpoint:

   ```bash
   python utils/test_prediction.py
   ```

   Alternatively, use `curl` or Postman:

   ```bash
   curl -X POST http://localhost:5000/predict \
     -H "Content-Type: application/json" \
     -d '{"features": {"income": 1800, "household_size": 3, "housing_status": 1, "income_vouchers": true, "household_expecting_changes": false, "household_student": true}}'
   ```

   Expected response:

   ```json
   {
     "risk_score": 0.82,
     "message": "Risk score represents likelihood of becoming unhoused (0 to 1, higher is riskier)"
   }
   ```

7. **Folder Structure**:

   ```
    model/
    ├── app/
    │   ├── Dockerfile           # Model container setup
    │   ├── main.py              # Flask app with /predict endpoint
    │   ├── mock-model.pkl       # Mock XGBoost model (generated by utils/train_model.py)
    │   └── requirements.txt     # Specific requirements for prediction container
    │
    ├── images/
    │   ├── browser-console.png       # Return of Risk Score after Form Submission in console
    │   ├── microservice-flow.png     # Data flow diagram of form submission to prediction endpoint
    │   └── test-console.png          # Output of running test_prediction.py for prediction endpoint
    │
    ├── notebooks/
    │   ├── 1-ahs_dataset_formatting.ipynb      # Initial data cleaning and feature engineering on AHS'23 Dataset
    │   └── 2-model_selection.ipynb             # Model selection, experimentation, and explainability using AHS'23 Dataset
    |
    ├── utils/
    │   ├── test_prediction.py        # Sends test POST request to /predict endpoint
    │   └── train_model.py            # Script to generate training data and save mock-model.pkl
    │
    ├── docker-compose.yaml      # Builds and sets up container environment
    ├── requirements.txt         # Python dependencies (All container dependencies)
    └── README.md                # You’re here!
   ```

8. **Troubleshooting**:
   - **Module Not Found**: Run `pip install -r requirements.txt`.
   - **Port Conflict**: If port 5000 is in use, update the port in `app/main.py`.
   - **Model File Missing**: Run `python utils/train_model.py` to generate `app/mock-model.pkl`.
   - **API Errors**: Check server logs or see model/README.

## 🐳 Running with Docker

1. **Build and Run the container**:

   ```bash
   docker compose up --build
   ```

   **NOTE:** You can drop the `--build` flag after the initial build to run the containers. If any changes are made, include it to rebuild the containers with the additions included.

2. **Test the endpoint**:

   ```bash
   python utils/test_prediction.py
   ```

#### Prediction API

- **Endpoint**: `POST /predict`
- **Purpose**: Returns a risk score (0 to 1, higher is riskier) based on housing-related features.
- **Example Request**:
  ```json
  {
    "features": {
      "income": 1800,
      "household_size": 3,
      "housing_status": 1,
      "income_vouchers": true,
      "household_expecting_changes": false,
      "household_student": true
    }
  }
  ```
  Note: `housing_status` is numeric (e.g., 0: homeless, 1: renting, 2: stable).
- **Example Response**:
  ```json
  {
    "risk_score": 0.82,
    "message": "Risk score represents likelihood of becoming unhoused (0 to 1, higher is riskier)"
  }
  ```

For integration with Bloom’s NestJS backend, configure the `application-service` in `api/` to call `http://localhost:5000/predict`. See [model/README](https://github.com/bloom-housing/bloom/blob/main/model/README.md) for further details.

## Bloom UIC Development

Because Bloom’s `ui-components` package is a separate open-source repository, developing in Bloom while iterating in `ui-components` requires linking the folders:

### Directory Setup

1. Clone both Bloom and the [ui-components repository](https://github.com/bloom-housing/ui-components) at the same directory level.

### Symlinking UIC

1. In the Bloom directory, run `yarn link:uic`.
2. Open the `next.config.js` file in the `public` and `partners` directories.
3. Uncomment the `experimental` property at the bottom of each file.
4. Run Bloom locally with `yarn dev:all`.
   This allows local `ui-components` changes to reflect in Bloom’s `node_modules`.

### Unlinking UIC

1. In the Bloom directory, run `yarn unlink:uic`.
2. Open the `next.config.js` file in the `public` and `partners` directories.
3. Comment out the `experimental` property.
4. Run Bloom locally with `yarn dev:all`.
   Bloom will use the published `@bloom-housing/ui-components` version specified in `package.json`.

## Contributing

Contributions to Bloom’s applications and services are welcomed. To meet quality and maintainability goals, contributors must follow these guidelines:

### Issue Tracking

Development tasks are managed via [GitHub Issues](https://github.com/bloom-housing/bloom/issues). Submit issues even if you don’t plan to implement them. Check for existing issues before creating new ones, and provide detailed descriptions with screenshots. Contact the Bloom team (@ludtkemorgan, @emilyjablonski, @yazeedloonat) before starting work to avoid duplication.

### Committing

Bloom uses [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) for commit messages. On commit, linting and conventional commit verification run automatically. Use one of these methods:

- Install [Commitizen](https://commitizen.github.io/cz-cli/) (`npm install -g commitizen`) and run `git cz` for a CLI to build commit messages.
- Run `git commit` with a message following the conventional standard; the linter will fail if it doesn’t comply.

### Pull Requests

Open pull requests to the `main` branch. Complete the PR template, including issue links, PR description, reviewer testing instructions, and a testing checklist. Label PRs as `needs review(s)` when ready or `wip` if in progress. Reviewers should provide clear next steps: mark “Requested Changes” for further work or “Approved” for minor changes not requiring re-review, with comments on remaining tasks.
