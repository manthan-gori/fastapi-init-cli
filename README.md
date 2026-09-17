# fastapi-init-cli

<div align="center">

<h3>Production-Ready FastAPI Scaffolding in Seconds</h3>

<p>An interactive, highly configurable CLI tool to bootstrap modern, scalable FastAPI applications with SQLAlchemy 2.0, JWT Authentication, OAuth, OTP verification, and Alembic migrations.</p>

[![PyPI version](https://img.shields.io/pypi/v/fastapi-init-cli.svg?style=flat-square&color=007ec6)](https://pypi.org/project/fastapi-init-cli/)
[![Python versions](https://img.shields.io/pypi/pyversions/fastapi-init-cli.svg?style=flat-square&color=3776ab)](https://pypi.org/project/fastapi-init-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688.svg?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0+-red.svg?style=flat-square)](https://www.sqlalchemy.org/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2-e92063.svg?style=flat-square)](https://docs.pydantic.dev/)

[Features](#features) •
[Installation](#installation) •
[Quickstart](#quickstart) •
[Architecture](#project-architecture) •
[API Reference](#api-endpoints-reference) •
[Contributing](#development--contributing) •
[Author](#author)

</div>

---

## Why fastapi-init-cli?

Setting up a robust FastAPI backend for production typically takes hours: setting up async database sessions, configuring JWT authentication with refresh token lifecycle, securing password hashing with `bcrypt`, wiring email OTP verification, setting up Alembic migrations, and structuring files into a clean layered architecture.

**`fastapi-init-cli` automates all of this in under 10 seconds** with an interactive questionnaire, generating 100% clean, standard FastAPI code with **zero vendor lock-in**.

---

## Features

- **Async-First & Sync Flexibility**: Full support for asynchronous SQLAlchemy 2.0 (`asyncpg`, `aiomysql`, `aiosqlite`) or synchronous mode (`psycopg`, `pymysql`, `sqlite`).
- **Multi-Database Support**: Out-of-the-box presets for **PostgreSQL**, **MySQL**, and **SQLite**.
- **Modular Authentication Suite**:
  - **JWT Tokens**: Dual access and refresh token lifecycle with Bearer authentication.
  - **Secure Password Hashing**: Native `bcrypt` hashing with safe password length truncation.
  - **Google OAuth 2.0**: Ready-to-use authorization code flow and user sync.
  - **Email Verification**: 6-digit OTP dispatch and validation.
  - **Forgot & Reset Password**: Secure OTP-based credential recovery.
- **Database Migrations & Auto Table Creation**:
  - Pre-configured async/sync **Alembic** environment with model auto-discovery.
  - Automatic startup table creation fallback when Alembic is disabled.
- **Clean Layered Architecture**:
  - Separation of concerns across `core/`, `models/`, `schemas/`, `services/`, and `routes/v1/`.
- **Pydantic v2 Settings**: Strongly typed environment configurations via `pydantic-settings`.
- **Zero Runtime Overhead**: The generated project has **zero dependency** on `fastapi-init-cli`.

---

## Installation

Install `fastapi-init-cli` from PyPI:

```bash
pip install fastapi-init-cli
```

Or run directly using [pipx](https://pypa.github.io/pipx/):

```bash
pipx run fastapi-init-cli
```

---

## Quickstart

Run the interactive generator:

```bash
fastapi-init
```
*(alias: `fastapi-init-cli`)*

### Interactive CLI Walkthrough

```text
╭───────────────────────────────────────────────────────────────────╮
│                            FastAPI Init                           │
│       Create a production-ready FastAPI backend in seconds.       │
╰───────────────────────────────────────────────────────────────────╯

? Project / Folder name: backend
? Select database engine: PostgreSQL
? Select execution architecture: Async
? Do you want authentication? Yes
? Select authentication method: JWT + Google OAuth
? Do you want email verification? (OTP-based) Yes
? Do you want forgot-password functionality? (OTP-based) Yes
? Do you want database migrations with Alembic? Yes
```

### Run Your New Backend

```bash
# 1. Navigate to your project
cd backend

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run database migrations (if Alembic is enabled)
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# 5. Start the development server
uvicorn app.main:app --reload
```

Your interactive API documentation will be immediately accessible at:
- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## Project Architecture

Every generated project follows modern FastAPI best practices and clean design patterns:

```
my-fastapi-backend/
├── .env.example                # Example environment variables template
├── .gitignore                  # Production Python gitignore
├── README.md                   # Project documentation with endpoints guide
├── requirements.txt            # Pinned dependencies for your configuration
├── alembic.ini                 # Alembic migration configuration (optional)
├── alembic/                    # Migration scripts & environment (optional)
│   ├── env.py
│   └── script.py.mako
└── app/
    ├── main.py                 # FastAPI application factory & lifespan
    ├── core/
    │   ├── config.py           # Pydantic v2 BaseSettings
    │   ├── database.py         # Async/sync engine & session dependency
    │   ├── dependencies.py     # Auth dependencies (get_current_user)
    │   └── security.py         # Password hashing & JWT helpers
    ├── models/
    │   ├── base.py             # SQLAlchemy DeclarativeBase & timestamp mixins
    │   ├── user.py             # User ORM model
    │   └── otp.py              # OTP ORM model (optional)
    ├── schemas/
    │   ├── auth.py             # Token & OAuth payload schemas
    │   ├── user.py             # User create/read/update schemas
    │   └── otp.py              # OTP request/response schemas
    ├── services/
    │   ├── auth_service.py     # Login, registration, token issuance
    │   ├── user_service.py     # User CRUD operations
    │   ├── otp_service.py      # OTP generation & validation logic
    │   └── email_service.py    # SMTP email delivery (optional)
    └── routes/
        ├── router.py           # Master router aggregator
        └── v1/
            ├── health.py       # Service health check
            ├── auth.py         # Authentication & OAuth routes
            └── users.py        # Current user profile routes
```

---

## API Endpoints Reference

Depending on your selected options, your generated backend comes pre-configured with:

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | Service health check | No |
| `POST` | `/api/v1/auth/register` | Register new user account | No |
| `POST` | `/api/v1/auth/login` | Email/password login for JWT access & refresh tokens | No |
| `POST` | `/api/v1/auth/refresh` | Exchange refresh token for new access token | No |
| `POST` | `/api/v1/auth/verify-email` | Verify account via 6-digit OTP | No |
| `POST` | `/api/v1/auth/resend-otp` | Resend verification OTP code | No |
| `POST` | `/api/v1/auth/forgot-password` | Dispatch password reset OTP | No |
| `POST` | `/api/v1/auth/reset-password` | Reset password using verified OTP | No |
| `GET` | `/api/v1/auth/google/url` | Retrieve Google OAuth consent URL | No |
| `GET` | `/api/v1/auth/google/callback`| Handle OAuth redirect & user synchronization | No |
| `GET` | `/api/v1/users/me` | Fetch authenticated user profile | **Yes (Bearer)** |
| `PATCH` | `/api/v1/users/me` | Update authenticated user details | **Yes (Bearer)** |

---

## Development & Contributing

Contributions are always welcome! Follow these steps to set up the project locally:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/manthan-gori/fastapi-init-cli.git
   cd fastapi-init-cli
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Run the test suite:**
   ```bash
   pytest
   ```

---

## Author

**Manthan Gori**

- LinkedIn: [linkedin.com/in/manthan-gori](https://www.linkedin.com/in/manthan-gori/)
- GitHub: [@ManthanGori](https://github.com/manthan-gori)

---

## License

This project is open-source and licensed under the [MIT License](LICENSE).

<div align="center">
  <sub>Built for the FastAPI & Python Community.</sub>
</div>
