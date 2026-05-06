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

Required for Render/Supabase deployment:

- `DATABASE_URL`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`

Optional values:

- `SUPABASE_PUBLISHABLE_KEY`
- `SUPABASE_AVATAR_BUCKET`
- `SUPABASE_CAMPAIGN_BUCKET`

Example local database value:

```env
DATABASE_URL=sqlite:///./fireflyfund_local.db
```

Example Supabase connection string for Render:

```env
DATABASE_URL=postgresql+psycopg2://postgres.your-project-ref:your-password@aws-0-region.pooler.supabase.com:6543/postgres
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
- User login state is backed by `user_sessions` and `authentication_tokens`.
- On project startup, server-side sessions are cleared, so users must log in again after a restart.
- Gmail SMTP should use an app password instead of the mailbox login password.

## Profile Notes

- `Save Profile` updates username and profile information in one BCE-aligned flow.
- Avatar and campaign image uploads use Supabase Storage when `SUPABASE_URL` and
  `SUPABASE_SERVICE_ROLE_KEY` are configured.
- Local `uploads/` directories remain as a development fallback when Supabase
  Storage credentials are not configured.

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
