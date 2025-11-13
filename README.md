# gym_gpt

## Logs API

### Persistent Logging

Logs are stored in `data/gymgpt.db` using SQLite for persistence between server restarts.

### POST /logs
Add a new set entry:
```json
{
  "name": "Bench Press",
  "reps": 8,
  "weight_kg": 70,
  "rir": 2,
  "focus": "upper"  // optional: upper/lower/full
}
```
Response:
```json
{
  "added": {
    "id": 1,
    "name": "Bench Press",
    "reps": 8,
    "weight_kg": 70,
    "rir": 2,
    # gym_gpt

    Lightweight FastAPI backend for generating gym plans and persisting exercise logs.

    ## Contents

    - `apps/backend` - FastAPI backend (APIs: /health, /plans/*, /logs)
    - `apps/frontend` - simple static frontend (HTML) to call the API
    - `data/gymgpt.db` - SQLite DB created at runtime to persist logs

    ## Quick start (backend)

    1) Create and activate virtualenv, install deps:

    ```bash
    cd apps/backend
    python3 -m venv .venv
    source .venv/bin/activate   # zsh / bash. On Windows: .venv\Scripts\activate
    GymGPT — AI-Powered Workout Planning API

    GymGPT is a FastAPI-based backend that generates personalized workouts using:

    - LLM explanations powered by OpenAI
    - Soreness-aware logic
    - Equipment adaptation (gym/home)
    - Progressive overload using logged training data
    - SQLite exercise database
    - Test suite using pytest

    This backend is stable and ready for integrating into a frontend (e.g., Nuxt).

    🚀 Features
    ✔️ Generate custom workouts

    POST /plans/workout automatically builds a workout based on:

    - focus (upper/lower/full)
    - equipment (gym/home)
    - soreness text
    - DB logs for progression

    ✔️ LLM explanations

    Each workout includes a friendly AI-generated explanation that covers:

    - the workout focus
    - why each lift is included
    - how weight progression works

    Uses gpt-4.1-mini (cheap & fast).

    ✔️ Exercise logging

    POST /logs/ saves:

    - exercise name
    - sets/reps
    - weight (kg)
    - RIR
    - focus
    - timestamp

    The plan generator uses these logs when use_db_logs = true.

    ✔️ Health check

    GET /health → returns { "ok": true }.

    ✔️ Fully tested

    Includes pytest suite:

    - /health
    - workout generation
    - logging + progression flow

    🛠️ Technologies

    Python + FastAPI

    SQLite3

    OpenAI (gpt-4.1-mini)

    Uvicorn

    pytest

    Pydantic models

    dotenv for config

    📦 Project Structure
    gym_gpt/
    └── apps/
        ├── backend/
        │   ├── main.py             # FastAPI app entrypoint
        │   ├── routes/
        │   │   ├── plans.py        # /plans/workout route
        │   │   └── logs.py         # /logs/ route
        │   ├── services/
        │   │   └── llm.py          # LLM explanations + coach chat
        │   ├── data/
        │   │   └── gymgpt.db       # SQLite database
        │   ├── tests/
        │   │   └── test_api.py     # pytest test suite
        │   └── .env                # contains OPENAI_API_KEY
        └── frontend/ (future)

    🔧 Setup
    1. Clone repo
    ```bash
    git clone https://github.com/neeilgupta/gym_gpt.git
    cd gym_gpt/apps/backend
    ```

    2. Create venv
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

    3. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```

    4. Add .env

    Create apps/backend/.env:

    ```
    OPENAI_API_KEY=sk-xxx
    ```

    ▶️ Run the server

    From apps/backend:

    ```bash
    source .venv/bin/activate
    uvicorn main:app --reload --port 8000
    ```


    Server starts at:

    http://127.0.0.1:8000


    Docs available at:

    http://127.0.0.1:8000/docs

    🧪 Running Tests

    Inside backend folder:

    ```bash
    pytest
    ```

    You should see:

    3 passed

    📬 API Usage (curl examples)
    1. Health check
    ```bash
    curl http://127.0.0.1:8000/health
    ```

    2. Generate a workout
    ```bash
    curl -X POST http://127.0.0.1:8000/plans/workout \
      -H "Content-Type: application/json" \
      -d '{
        "focus": "upper",
        "equipment": "gym",
        "soreness_text": "my quads are super sore but chest and back feel good",
        "use_db_logs": false
      }'
    ```

    Sample Output
    ```json
    {
      "date": "2025-11-13",
      "focus": "upper",
      "equipment": "gym",
      "exercises": [
        { "name": "Barbell Bench Press", "sets": 3, "reps": 6, "weight_delta": 1.0 },
        ...
      ],
      "explanation": "This upper workout focuses on..."
    }
    ```

    3. Log a set
    ```bash
    curl -X POST http://127.0.0.1:8000/logs/ \
      -H "Content-Type: application/json" \
      -d '{
        "name": "Barbell Bench Press",
        "reps": 8,
        "weight_kg": 70,
        "rir": 1,
        "focus": "upper"
      }'
    ```


    Logs are stored in apps/data/gymgpt.db.

    🧠 Future Development Ideas

    Frontend with Nuxt 3

    Weekly plan generator (/plans/week)

    Coach chat endpoint (/coach)

    Graphs of workout progression

    User accounts + OAuth

    Exportable PDF programs

    🎉 Status

    Backend is fully functional, tested, and stable.
    Ready for frontend integration and deployment.
