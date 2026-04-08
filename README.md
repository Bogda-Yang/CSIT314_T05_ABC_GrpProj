# FireflyFund

FireflyFund is now scaffolded as a `Python + FastAPI + Supabase Postgres` project.

## Features

- Home page served by FastAPI with Jinja templates
- Login page with email and password
- Register page with username, email, password, and email verification code
- SMTP-based verification email sending
- Supabase Postgres storage for users and verification codes
- Cloud-friendly `DATABASE_URL` configuration for multi-user deployment

## Project Structure

```text
main.py
templates/
static/
login.jpg
logo0.jpg
requirements.txt
start.sh
```

## Run

1. Create and activate a virtual environment if you want one.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.env` from `.env.example`, then fill in your values.
   Required: `DATABASE_URL`, `SECRET_KEY`, and SMTP settings.

4. Start FastAPI:

```bash
uvicorn main:app --reload
```

5. Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/auth?mode=login`
- `http://127.0.0.1:8000/auth?mode=register`

## Notes

- `.env.example` is included as a reference template.
- `.env` is ignored by git.
- For Gmail SMTP, use an app password rather than your normal mailbox password.
- The app now loads `.env` automatically on startup.
- Example Supabase Postgres URL:

```bash
postgresql+psycopg2://postgres.your-project-ref:your-password@aws-0-region.pooler.supabase.com:6543/postgres
```

- This structure is suitable for cloud deployment where multiple users share the same Supabase database.
