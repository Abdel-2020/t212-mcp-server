# Base OS
FROM python:3.12-slim-trixie

# Install UV
COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

# Copy project into image
COPY src/ /app

# Sync the project into a new environment. 
WORKDIR /app

# Install deps
RUN uv sync --locked

# Initialize db
RUN python setup_db.py

EXPOSE 42070


CMD ["uv", "run", "main.py"]
