# Study Guide: Machine Maintenance Tracker (Accenture ATE interview)

## Learn the project in this order (about 7 days)
1. Day 1: Run it. Open /docs, click every endpoint. Read `schemas.py` and `models.py`.
2. Day 2: Read `main.py` line by line. Draw the request flow on paper.
3. Day 3: Read `tests/test_api.py`. Break a route on purpose, watch a test fail, fix it.
4. Day 4: Read the JS in `index.html`. Understand `api()`, `el()`, `refresh()`.
5. Day 5: Put it on GitHub, watch the CI workflow run green. Build the Docker image.
6. Day 6: Add ONE feature yourself (ideas below). This is what makes it yours.
7. Day 7: Practise the 2-minute explanation and the questions below out loud.

## Features to add yourself (pick one or two)
- Search tasks by title (`?q=`) plus a test
- `completed_at` timestamp set when status becomes done
- A "high priority and overdue" badge
- Edit a task's title in the UI
- Deploy on Render and put the live link on your resume

## 2-minute explanation (put it in your own words)
"I built a maintenance tracker because I'm a mechanical engineering student and wanted a
problem from my own field. It's a FastAPI backend with SQLAlchemy and SQLite, a plain
JavaScript frontend, and Pydantic validation. I wrote 10 automated pytest tests, containerised
it with Docker and set up GitHub Actions to run the tests on every push. I used AI assistants
to speed up boilerplate and explain concepts, but I ran and verified everything, for example
[a real example of an AI suggestion you corrected]."

## Likely interview questions
- Why FastAPI? (fast, type hints, automatic validation and docs)
- What is REST? What do GET / POST / PATCH / DELETE mean? PUT vs PATCH?
- What do status codes 200, 201, 204, 404, 409, 422 mean, and where did you use each?
- Why keep Pydantic schemas separate from DB models?
- What is an ORM? What is a foreign key? What does cascade delete do?
- What is dependency injection (`Depends(get_db)`)?
- How do you prevent XSS and SQL injection here? (textContent, ORM parameterised queries)
- Why write tests? What is a fixture? Why an in-memory DB for tests?
- What does your CI pipeline do? CI vs CD?
- What does the Dockerfile do, line by line? Image vs container?
- How would you scale this? (PostgreSQL, auth, caching, cloud deploy)
- Where did AI help, where was it wrong, and how did you verify it?
