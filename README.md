# Snowboard Pipeline

Quick scaffold for the snowboard pipeline project.

Setup

- Create and activate venv:

  mac/linux:

  ```bash
  python -m venv venv
  source venv/bin/activate
  ```

  windows:

  ```powershell
  python -m venv venv
  venv\Scripts\activate
  ```

- Install dependencies:

```bash
pip install -r requirements.txt
```

VS Code extensions recommended

- Python (Microsoft)
- dbt Power User
- Docker
- SQLTools

Project layout

See the scaffolded folders and initial files in the repository.

Git

Git has been initialized in this folder. The `.env` file is ignored by default.

Next steps

- Add API keys to `.env`
- Create dbt project under `transforms/` when ready
