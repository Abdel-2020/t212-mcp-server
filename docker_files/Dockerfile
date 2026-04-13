FROM python:3.12-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:0.9.26 /uv /uvx /bin/

RUN mkdir -p /home/app

ADD  ../ /home/app

WORKDIR /home/app

RUN uv sync --locked # Similar to pip install -r requirements.txt

EXPOSE 6767

CMD ["uv","run","fastmcp", "run", "main.py:mcp", "--transport", "http", "--host", "0.0.0.0", "--port", "6767"]
