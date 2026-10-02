# Student Directory

A small full stack student database project built as an internship portfolio demo. It pairs a responsive browser dashboard with a REST API and a local SQLite database. The demo works without a cloud account or API key.

## Project overview

The project demonstrates how a browser interface, API routes, validation schemas, and a relational database work together. Student records are created and updated through the API, stored in SQLite, and then displayed in the dashboard. The optional chatbot demonstrates connecting a backend service to a language model using database context.

## What it does

- Add, view, edit, and delete student records.
- Search by student name, email, course, phone, or status.
- Store contact and academic details: phone, date of birth, enrollment date, GPA, and enrollment status.
- View directory totals, distinct courses, and average study year.
- Validate email addresses, required fields, year range, and duplicate emails.
- Browse and try the API through interactive Swagger documentation.
- Optionally ask questions about the directory using Gemini.

The first run creates a local SQLite database and inserts three fictional sample students. Existing databases are preserved; sample records are not reinserted after a user deletes them.

## Built with

- **Frontend:** HTML, CSS, vanilla JavaScript
- **Backend:** Python, FastAPI, Pydantic
- **Database:** SQLite and SQLAlchemy
- **Optional AI:** LangGraph and Google Gemini

## Run locally

Use Python 3.10–3.13. From the project folder:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

On macOS or Linux, create and activate the virtual environment with `python3 -m venv .venv` and `source .venv/bin/activate`, then install the same requirements and run Uvicorn.

Open these pages after the server starts:

- Dashboard: <http://127.0.0.1:8000>
- Swagger API docs: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/health>

Stop the server with **Ctrl+C**. The `students.db` file is created in the project folder and is excluded from Git.

## Optional Gemini chatbot

The app runs without Gemini. To enable AI answers, install the optional packages and add a Google AI Studio key to `.env`:

```powershell
python -m pip install -r requirements-ai.txt
```

Set `GEMINI_API_KEY` in `.env`, then restart the server. When enabled, the chatbot sends student record fields to the Gemini API to answer questions. Use fictional demo records only; do not put real student personal data in this demo.

## API overview

All student endpoints use the `/api/v1/students` path.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/students` | List students; accepts `q`, `limit`, and `offset` |
| `POST` | `/api/v1/students` | Create a student |
| `GET` | `/api/v1/students/{id}` | Read one student |
| `PATCH` | `/api/v1/students/{id}` | Update selected fields |
| `DELETE` | `/api/v1/students/{id}` | Delete a student |
| `POST` | `/api/v1/chat` | Ask the optional directory chatbot a question |

Example request to create a record:

```http
POST /api/v1/students
Content-Type: application/json

{
  "name": "Asha Kumar",
  "email": "asha@example.com",
  "course": "Computer Science",
  "year": 3
}
```

Names and courses are trimmed and cannot be blank. Email addresses are validated and normalized to lowercase. Study year must be between 1 and 10, GPA must be between 0 and 4, and status must be Active, Graduated, or On leave. Phone, birth date, and enrollment date are optional. Duplicate email addresses return HTTP `409`; missing student IDs return HTTP `404`.

## Project structure

```text
app/
  api/
    chat.py          Optional Gemini chatbot endpoint
    students.py      Student CRUD and search endpoints
  static/
    index.html       Responsive dashboard
  config.py          Environment-based settings
  database.py        SQLAlchemy engine and sessions
  main.py            FastAPI app and first-run database setup
  models.py          Student database model
  schemas.py         Request validation and response schemas
requirements.txt     Core dependencies
requirements-ai.txt  Optional chatbot dependencies
Dockerfile           Container setup
render.yaml          Render deployment blueprint
.github/workflows/
  deploy-render.yml   Deploy to Render on pushes to main
```

## Run in Docker

```sh
docker build -t student-directory .
docker run --rm -p 8000:8000 -v student-directory-data:/app student-directory
```

The named volume keeps the SQLite database when the container is recreated. For a hosted deployment, configure persistent storage or use a managed database; container filesystems may be temporary.

## Deploy from GitHub with Render

The included GitHub Actions workflow triggers a Render deploy when code is pushed to `main`. It also supports a manual run from the Actions tab. The Render blueprint uses the included Dockerfile and selects Render's free web service plan.

### One-time setup

1. Open the [student-directory-demo repository](https://github.com/kompellysagar/student-directory-demo) in Render by creating a new **Blueprint** and connecting your GitHub account. Render reads `render.yaml` and creates the web service. Wait for its first deploy to finish.
2. In that Render service, open **Settings** and create a **Deploy Hook**.
3. In the GitHub repository, open **Settings → Secrets and variables → Actions → New repository secret**. Name it `RENDER_DEPLOY_HOOK_URL` and paste the hook URL as the secret value.
4. Push a new commit to `main`, or open **Actions → Deploy to Render → Run workflow** to deploy manually.

Keep the deploy hook URL private. The workflow sends it to Render without printing it in the job log. See [Render's deploy hook guide](https://render.com/docs/deploy-hooks) for details.

The workflow safely skips deployment until the repository secret is configured, so the initial push can happen before the Render service and hook exist.

The starter blueprint uses SQLite. Render's default service filesystem is ephemeral, so student records added after launch can be lost when the service restarts or redeploys. The fictional sample data is re-created when the database is first initialized. For durable hosted records, switch to a managed database such as PostgreSQL before using real data. See [Render's filesystem and disk documentation](https://render.com/docs/disks).

### Push future changes

The project is already published at [github.com/kompellysagar/student-directory-demo](https://github.com/kompellysagar/student-directory-demo). To publish later changes from this checkout:

```sh
git add .
git commit -m "Describe your change"
git push origin main
```

The `.gitignore` excludes `.env`, virtual environments, Python caches, and local database files. Keep API keys and real student data out of the repository.

## Demo walkthrough

1. Open the dashboard and review the sample directory and summary cards.
2. Search for a name, email, or course.
3. Add a student, then edit the record and confirm the summary updates.
4. Try creating a duplicate email to see validation in action.
5. Open `/docs` and call the list or create endpoints directly.

## Scope

This is an educational demo, not a production student information system. It does not include user authentication, role permissions, audit history, or production privacy controls. Use fictional data and add those controls before adapting it for real records. The app adds newly introduced student columns to an existing SQLite database at startup.
