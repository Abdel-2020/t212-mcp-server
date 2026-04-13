# Base OS
FROM python:3.12-slim-trixie

# Install UV
COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

# Setup our app directory
WORKDIR /home/app

# Copy files into container 
ADD  . .

# Install deps
RUN uv sync --locked # Similar to pip install -r requirements.txt

EXPOSE 6767

CMD ["uv","run","fastmcp", "run", "main.py:mcp", "--transport", "http", "--host", "0.0.0.0", "--port", "6767"]
