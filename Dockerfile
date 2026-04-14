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

# Point the system to the virtual environment created by uv
#ENV PATH="/home/app/.venv/bin:$PATH"

EXPOSE 42070

CMD ["uv","run","fastmcp", "run", "main.py:mcp", "--transport", "http", "--host", "0.0.0.0", "--port", "42070"]
