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
![Testing Library](https://img.shields.io/badge/-TestingLibrary-%23E33332?style-for-the-badge&logo=testing-library&logoColor=white)


Bloom consists of a client/server architecture using [Next.js](https://nextjs.org) for the frontend applications and [NestJS](https://nestjs.com), [Prisma](https://www.prisma.io/), and [Postgres](https://www.postgresql.org/) on the backend.

### Structure

Bloom uses a monorepo-style repository containing multiple user-facing applications and backend services. The main high-level packages are `api`, `sites`, `model`, and `shared-helpers`. Additionally, Bloom's UI leverages the in-house packages `@bloom-housing/ui-seeds` and `@bloom-housing/ui-components`.

```
bloom/
├── api/                    # NestJS backend services
├── model/                  # Risk prediction microservice (Flask, XGBoost)
├── sites/
│   ├── public/             # Next.js applicant-facing portal
│   └── partners/           # Next.js developer/admin portal
├── shared-helpers/         # Shared types and utilities
├── @bloom-housing/ui-seeds # Design system and React components
└── @bloom-housing/ui-components # Legacy React component library
```

- **`sites/public`**: Applicant-facing site for browsing and applying to listings using Bloom’s Common Application or third-party applications. See [sites/public/README](https://github.com/bloom-housing/bloom/blob/main/sites/public/README.md).
- **`sites/partners`**: Secure portal for housing developers, property managers, and city/county employees to manage applications and listings. Requires login. See [sites/partners/README](https://github.com/bloom-housing/bloom/blob/main/sites/partners/README.md).
- **`api`**: Backend services (e.g., listings, applications, users) stored in a Postgres database and served via a REST API over HTTPS. See [api/README](https://github.com/bloom-housing/bloom/blob/main/api/README.md).
- **`model`**: Flask-based microservice using XGBoost to predict housing instability risk based on features like income and household size. Exposes a `/predict` endpoint. See [model/README](https://github.com/bloom-housing/bloom/blob/main/model/README.md).
- **`shared-helpers`**: Shared types, functions, and components for public and partners sites. See [shared-helpers/README](https://github.com/bloom-housing/bloom/blob/main/shared-helpers/README.md).
- **`@bloom-housing/ui-seeds`**: Component library with React components and design system tokens. Explore the [Storybook](https://storybook-ui-seeds.netlify.app/?path=/story/tokens-introduction--page) and [design documentation](https://zeroheight.com/5e69dd4e1/p/938cb5-seeds-design-system).
- **`@bloom-housing/ui-components`**: Legacy component library, being replaced by `ui-seeds`. View the [Storybook](https://storybook.bloom.exygy.dev/).

## Getting Started

If you're new to Bloom, follow the individual README files in each package first:

- **api/**: [api/README.md](api/README.md)
- **sites/public/**: [sites/public/README.md](sites/public/README.md)
- **sites/partners/**: [sites/partners/README.md](sites/partners/README.md)
- **model/**: [model/README.md](model/README.md)

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

## Local Development Setup

1. **Install Dependencies**
   ```bash
   yarn install
   cd api && yarn install
   ```
   If you don’t have Yarn installed, install [Homebrew](https://brew.sh/) and run `brew install yarn`.

2. **Environment Variables**
   Copy `.env.template` to `.env` in each of `sites/public`, `sites/partners`, `api`, and `model`, then fill in any required secrets.

3. **Run Everything**
   ```bash
   yarn dev:all
   ```
   This starts:
   - Public: http://localhost:3000
   - Partners: http://localhost:3001
   - API: http://localhost:3100

Alternatively, run each process individually from separate terminals in `api`, `sites/public`, or `sites/partners` with `yarn dev`.

## Risk Prediction Model (model/)

The `model/app/` directory contains a Flask-based microservice powered by an XGBoost model to predict housing instability risk. It exposes a `/predict` endpoint and can be run standalone for local development or testing without requiring the full Bloom platform.

### New Data & Training Workflow

1. **Download AHS 2023 Data**
   - Go to: https://www.census.gov/.../ahs-2023-national-public-use-file--puf-.html
   - Download the **AHS 2023 National PUF v1.1 CSV** zip and extract the CSV into `model/data/`.

2. **Install Python Dependencies**
   ```bash
   cd model
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Run Pipeline**
   ```bash
   python pipeline/data_processing.py
   python pipeline/model_training.py
   ```
   - Outputs `model/app/xgboost_model.pkl` and `model/app/scaler.pkl`.

4. **Start Flask Service**
   ```bash
   python app/main.py
   ```

5. **Testing**
   ```bash
   # Local Flask tests
   pytest tests/test_prediction.py
   ```

### Docker Usage

```bash
cd model
docker-compose up --build
# Local tests
pytest tests/test_prediction.py
```

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

##Contributing

Contributions to Bloom’s applications and services are welcomed. To meet quality and maintainability goals, contributors must follow these guidelines:

### Issue Tracking

- Development tasks are managed via [GitHub Issues](https://github.com/bloom-housing/bloom/issues).
- Submit issues even if you don’t plan to implement them.
- Check for existing issues before creating new ones, and provide detailed descriptions with screenshots.
- Contact the Bloom team (@ludtkemorgan, @emilyjablonski, @yazeedloonat) before starting work to avoid duplication.

### Committing

We adhere to **Conventional Commits**: https://www.conventionalcommits.org/en/v1.0.0/

- Install [Commitizen](https://commitizen.github.io/cz-cli/) globally:
  ```bash
  npm install -g commitizen
  ```
- Run `git cz` to generate well-formed commit messages, or write your own following the format:
  ```text
  <type>(<scope>): <short summary>

  <detailed description>
  ```
- Types include: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`.

### Pull Requests

- Target the `main` branch.
- Include the PR template with:
  - Issue reference (e.g., `Closes #123`).
  - Description of changes.
  - Testing instructions for reviewers.
  - A checklist of completed tasks.
- Label PRs appropriately:
  - `needs review(s)` when ready for review.
  - `wip` for work in progress.
- Reviewers:
  - Mark “Requested Changes” if further work is needed, or “Approved” when ready to merge.

## License

MIT License


