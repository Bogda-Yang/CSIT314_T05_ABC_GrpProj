# FireflyFund

FireflyFund is a `Python + FastAPI + SQLAlchemy` fundraising platform prototype focused on person-to-person and family support. Local development uses SQLite, while Render deployment can use Supabase Postgres and Supabase Storage.

## Current Features

- FastAPI server with Jinja templates and static assets
- Home page, About Us page, Profile page, and Settings page
- Email + password login
- Username + email + password + verification code registration
- SMTP-based email verification and password reset codes
- Logout with database-backed session invalidation
- Profile editing for:
  - username
  - gender
  - age
  - occupation
  - personal bio
- Profile avatar upload with shared display on:
  - Profile page
  - Home page user menu
  - About Us page user menu
- Campaign image upload with up to 5 images per campaign
- Password change
- Delete account
- SQLite local database for development demo data
- Supabase Postgres storage for shared Render deployment data
- Supabase Storage for user avatars and campaign images on Render

## Backend Stack

- `FastAPI`
- `SQLAlchemy`
- `SQLite` locally
- `Supabase Postgres` on Render
- `Jinja2`
- `python-dotenv`
- `python-multipart`
- `SMTP`

## Main Files

```text
app.py
core/
  config.py
  db.py
  storage.py
models/
  user.py
  campaign.py
  donation.py
  admin.py
routers/
  user.py
  donee.py
  fundraiser.py
  admin.py
services/
  user_service.py
  campaign_service.py
  donation_service.py
  admin_service.py
templates/
  index.html
  about.html
  auth.html
  profile.html
  settings.html
  dashboard.html
static/
  styles.css
  auth.css
  auth.js
  site.js
assets/
  images/
uploads/
  avatars/
  campaigns/
docs/
scripts/
requirements.txt
start.sh
```

## Environment Variables

Create a local `.env` file based on `.env.example`.

Required for local development:

- `SECRET_KEY`

Required for email verification and password reset:

- `SMTP_USER`
- `SMTP_PASS`
- `SMTP_HOST`
- `SMTP_PORT`

Required for local and Render Supabase deployment:

- `DATABASE_URL`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

Optional values:

- `RUN_DB_MIGRATIONS` set to `true` only when you intentionally need to create
  tables, add missing columns, or create indexes on Supabase.
- `VERIFY_STORAGE_BUCKETS` set to `true` only when you intentionally want startup
  to verify or create Supabase Storage buckets.
- `RUN_STARTUP_SEED` set to `true` only when you intentionally need to create the
  default admin account, default categories, or simulated featured campaigns.
- `WARM_DATABASE_POOL` defaults to `true` and opens one Supabase database
  connection in the background after startup, reducing the first page request
  delay without blocking the app from starting.
- `SUPABASE_PUBLISHABLE_KEY`
- `SUPABASE_AVATAR_BUCKET`
- `SUPABASE_CAMPAIGN_BUCKET`

Example Supabase connection string used by both local runs and Render:

```env
DATABASE_URL=postgresql+psycopg2://postgres.your-project-ref:your-password@aws-0-region.pooler.supabase.com:6543/postgres
RUN_DB_MIGRATIONS=false
VERIFY_STORAGE_BUCKETS=false
RUN_STARTUP_SEED=false
WARM_DATABASE_POOL=true
```

## Run Locally

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Start the project:

```bash
cd /Users/apple/Desktop/CSIT314_T05_ABC_GrpProj
./start.sh
```

Open:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/about`
- `http://127.0.0.1:8000/auth?mode=login`
- `http://127.0.0.1:8000/auth?mode=register`
- `http://127.0.0.1:8000/profile`
- `http://127.0.0.1:8000/settings`

## Authentication Notes

- The app loads `.env` automatically.
- Local runs and Render both use the same Supabase PostgreSQL database through
  `DATABASE_URL`; SQLite is only used as a CI compile fallback.
- User login state is backed by `user_sessions` and `authentication_tokens`.
- On project startup, server-side sessions are cleared, so users must log in again after a restart.
- Gmail SMTP should use an app password instead of the mailbox login password.

## Profile Notes

- `Save Profile` updates username and profile information in one BCE-aligned flow.
- Avatar and campaign image uploads use Supabase Storage when `SUPABASE_URL` and
  `SUPABASE_SERVICE_ROLE_KEY` are configured. Use the same credentials locally
  and on Render so uploaded media is shared across both environments.

## Render Notes

- To make uploaded avatars and campaign images visible on Render, configure these
  environment variables in Render:
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_ROLE_KEY`
  - optionally `SUPABASE_AVATAR_BUCKET`
  - optionally `SUPABASE_CAMPAIGN_BUCKET`
- Existing images uploaded before the Supabase Storage migration may need to be
  uploaded again, because old local files are not available on Render instances.

## BCE Mapping

The current BCE mapping files are here:

- [U1-5_BCE_MAPPING.md](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/docs/U1-5_BCE_MAPPING.md)
- [A1-5_BCE_MAPPING.md](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/docs/A1-5_BCE_MAPPING.md)
- [P1-7_BCE_MAPPING.md](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/docs/P1-7_BCE_MAPPING.md)
- [F1-13_BCE_MAPPING.md](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/docs/F1-13_BCE_MAPPING.md)
- [D1-11_BCE_MAPPING.md](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/docs/D1-11_BCE_MAPPING.md)

The CI/CD evidence report is here:

- [CI_CD_EVIDENCE_REPORT.md](/Users/apple/Desktop/CSIT314_T05_ABC_GrpProj/docs/CI_CD_EVIDENCE_REPORT.md)

## Git Notes

- `.env` is ignored by git.
- Uploaded avatars and local generated files should be reviewed before committing.
