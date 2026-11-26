
FROM python:3.12-slim

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency definitions first for better layer caching
COPY pyproject.toml .

# Install project dependencies
# RUN uv sync --no-dev --no-install-project
RUN uv sync

# Copy application code
COPY . .

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"


CMD ["fastmcp", "run", "main.py:app", "--transport", "streamable-http", "--host", "0.0.0.0", "--port", "8000"]
