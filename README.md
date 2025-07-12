# VPN Admin Panel

## Project Overview

This project is a comprehensive, modern, responsive, RTL, and Persian-language VPN admin panel designed to be compatible with the Marzban VPN panel. It provides a Super Admin interface to manage Admins, and an Admin interface for managing VPN users, plans, and payments.

## Key Features (High-Level)

*   **Super Admin Panel:**
    *   Manage Admin accounts (create, view, update, delete).
    *   Define and manage VPN plans (duration, data limit, price).
*   **Admin Panel:**
    *   View available plans.
    *   Create VPN users (integrated with Marzban and Abresani API).
    *   View QR codes and access links for VPN users.
    *   Reset or delete VPN users.
    *   Recharge account balance (via Zarinpal payment gateway).
*   **Technical Features:**
    *   Modern UI/UX, fully responsive and RTL (Persian).
    *   RESTful APIs for frontend-backend communication.
    *   JWT-based authentication.

## Technology Stack

*   **Backend:** Python, FastAPI, SQLAlchemy (with PostgreSQL)
*   **Frontend:** Vue.js (Vue 3), Vuex, Vue Router, Axios
*   **Database:** PostgreSQL
*   **Key Python Libraries:** Uvicorn, Pydantic, Passlib, Python-JOSE
*   **Key Frontend Libraries:** Vue, Vuex, Vue-Router, Axios

## Prerequisites

Before you begin, ensure you have the following installed:

*   **Python:** Version 3.8+
*   **Pip:** Python package installer (usually comes with Python)
*   **Virtualenv (recommended):** For creating isolated Python environments (`pip install virtualenv`)
*   **Node.js:** Version 16.x or higher (which includes npm)
*   **PostgreSQL:** A running PostgreSQL server instance (Version 12+ recommended)
*   **Git:** For cloning the repository

## Project Structure

```
.
├── backend/        # FastAPI backend application
│   ├── app/        # Core application logic, models, schemas, API endpoints
│   ├── .env.example # Example environment variables for backend
│   └── requirements.txt # Python dependencies
├── frontend/       # Vue.js frontend application
│   ├── public/
│   ├── src/        # Vue components, store, router, assets
│   ├── .env.example # Example environment variables for frontend (if needed for VUE_APP_ variables)
│   └── package.json # Node.js dependencies
└── README.md
```

## Backend Setup

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Navigate to Backend Directory:**
    ```bash
    cd backend
    ```

3.  **Create and Activate Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    # On Windows
    # .\venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

4.  **Install Python Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Setup PostgreSQL Database:**
    *   Ensure PostgreSQL is installed and running.
    *   Create a new database, for example, `vpnadmin_db`.
        ```sql
        -- Example PSQL commands:
        CREATE DATABASE vpnadmin_db;
        ```
    *   Create a new user (role) with a password that has privileges on this database.
        ```sql
        CREATE USER vpnadmin_user WITH PASSWORD 'your_strong_password_here';
        ALTER DATABASE vpnadmin_db OWNER TO vpnadmin_user;
        -- Grant privileges (might need more specific grants depending on setup)
        GRANT ALL PRIVILEGES ON DATABASE vpnadmin_db TO vpnadmin_user;
        ```
        *Note: For security, grant only necessary privileges in a production environment.*

6.  **Configure Backend Environment Variables:**
    *   Copy the example environment file:
        ```bash
        cp .env.example .env
        ```
    *   Edit the `.env` file with your actual settings:
        *   `DATABASE_URL`: Set this to your PostgreSQL connection string.
            *   Format: `postgresql://vpnadmin_user:your_strong_password_here@localhost:5432/vpnadmin_db`
            *   Adjust `localhost`, `5432` (port), username, password, and database name as per your setup.
        *   `SECRET_KEY`: **Important!** Generate a strong secret key for JWT. You can use `openssl rand -hex 32` to generate one.
        *   `ALGORITHM`: Default is `HS256`.
        *   `ACCESS_TOKEN_EXPIRE_MINUTES`: Default is `30`.
        *   `INITIAL_SUPER_ADMIN_USERNAME`, `INITIAL_SUPER_ADMIN_EMAIL`, `INITIAL_SUPER_ADMIN_PASSWORD`:
            Set these to create the first Super Admin user on application startup if it doesn't exist.
            **Change the default password immediately!**

7.  **Database Migrations/Table Creation:**
    *   Currently, the application creates tables based on SQLAlchemy models when the FastAPI app starts (`Base.metadata.create_all(bind=engine)` in `backend/app/main.py`). This is suitable for development.
    *   **For Production:** It is highly recommended to use a database migration tool like Alembic. (Alembic setup is not yet included in this phase).

8.  **Run the Backend Development Server:**
    ```bash
    # Ensure your virtual environment is activated and you are in the 'backend' directory
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ```
    *   `--reload`: Enables auto-reload on code changes (for development).
    *   `--host 0.0.0.0`: Makes the server accessible from your network (not just localhost).
    *   `--port 8000`: Runs on port 8000.

## Frontend Setup

1.  **Navigate to Frontend Directory:**
    ```bash
    # From the project root directory
    cd frontend
    ```

2.  **Install Node.js Dependencies:**
    ```bash
    npm install
    # Or if you prefer yarn:
    # yarn install
    ```

3.  **Configure Frontend Environment Variables (Optional for this phase):**
    *   The frontend uses `VUE_APP_API_BASE_URL` in `frontend/src/store/modules/auth.js` which defaults to `http://localhost:8000/api/v1`.
    *   If your backend is running on a different URL or port, create a `.env` file in the `frontend` directory:
        ```bash
        # frontend/.env
        VUE_APP_API_BASE_URL=http://your_backend_host:your_backend_port/api/v1
        ```

4.  **Run the Frontend Development Server:**
    ```bash
    npm run serve
    # Or if you prefer yarn:
    # yarn serve
    ```
    *   This will typically start the frontend on `http://localhost:8080` (check your console output for the exact URL).

## Accessing the Application

*   **Frontend (Admin Panel UI):** Open your browser and navigate to the URL provided by the frontend development server (e.g., `http://localhost:8080`).
*   **Backend API Documentation (Swagger UI):** `http://localhost:8000/docs`
*   **Backend API Documentation (ReDoc):** `http://localhost:8000/redoc`

## Initial Super Admin User

*   The initial Super Admin user is created on the first startup of the backend application if one with the specified username doesn't already exist.
*   Credentials for this user are taken from the backend `.env` file:
    *   `INITIAL_SUPER_ADMIN_USERNAME`
    *   `INITIAL_SUPER_ADMIN_EMAIL`
    *   `INITIAL_SUPER_ADMIN_PASSWORD`
*   **It is crucial to set a strong, unique password for `INITIAL_SUPER_ADMIN_PASSWORD` in your `.env` file and not use the default placeholder.**
*   Login with these credentials on the Super Admin login page of the frontend.

## Environment Variables Summary

### Backend (`backend/.env`)

*   `DATABASE_URL`: (Required) PostgreSQL connection string.
*   `SECRET_KEY`: (Required) Strong secret key for JWT.
*   `ALGORITHM`: (Optional) JWT algorithm (default: `HS256`).
*   `ACCESS_TOKEN_EXPIRE_MINUTES`: (Optional) JWT expiry time (default: `30`).
*   `INITIAL_SUPER_ADMIN_USERNAME`: (Optional) Username for the first super admin (default: `superadmin`).
*   `INITIAL_SUPER_ADMIN_EMAIL`: (Optional) Email for the first super admin (default: `superadmin@example.com`).
*   `INITIAL_SUPER_ADMIN_PASSWORD`: (Optional) Password for the first super admin (default: `ChangeMeSuperSecure!123` - **CHANGE THIS!**).
*   `MARZBAN_API_BASE_URL`, `MARZBAN_ADMIN_USERNAME`, `MARZBAN_ADMIN_PASSWORD`: (For future Marzban integration)
*   `ABRESANI_API_KEY`, `ABRESANI_API_BASE_URL`: (For future Abresani integration)
*   `ZARINPAL_MERCHANT_ID`, `ZARINPAL_CALLBACK_URL`, etc.: (For future Zarinpal integration)

### Frontend (`frontend/.env`)

*   `VUE_APP_API_BASE_URL`: (Optional) Overrides the default backend API URL if it's not `http://localhost:8000/api/v1`.

## Basic Troubleshooting

*   **Port Conflicts:** If port `8000` (backend) or `8080` (frontend) is in use, Uvicorn or Vue CLI will usually indicate this. You can change the port in the run commands (e.g., `uvicorn ... --port 8001`, `npm run serve -- --port 8081`).
*   **Database Connection Issues:**
    *   Ensure your PostgreSQL server is running.
    *   Double-check the `DATABASE_URL` in `backend/.env` for typos, correct credentials, host, port, and database name.
    *   Verify that the database user has the necessary permissions.
    *   Check PostgreSQL logs for any connection errors.
*   **`ModuleNotFoundError` (Python):** Ensure your virtual environment is activated and you've run `pip install -r requirements.txt`.
*   **`npm ERR!` (Frontend):** Ensure Node.js and npm are correctly installed. Try deleting `node_modules` and `package-lock.json` (or `yarn.lock`) and run `npm install` (or `yarn install`) again.
*   **CORS Issues:** If the frontend has trouble communicating with the backend, it might be a CORS (Cross-Origin Resource Sharing) issue. FastAPI is configured with basic CORS middleware in Phase 1 for development (allowing all origins, methods, headers). For production, this needs to be configured more restrictively.

## Further Development (Next Phases Outline)

*   **Phase 2: Admin Panel - Core Features & SuperAdmin UI Completion**
    *   Full CRUD UI for Admins and Plans in SuperAdmin dashboard.
    *   Admin authentication and dashboard shell.
    *   Marzban API integration for user creation and management.
    *   Admin-facing UI for VPN user management.
*   **Phase 3: Payment Integration (Zarinpal) & Abresani Integration**
*   **Phase 4: UI Polish, Testing & Deployment Prep**

---

This `README.md` provides a starting point. It will be updated as the project progresses with more features, deployment instructions for production, and detailed API usage examples if needed beyond the auto-generated docs.