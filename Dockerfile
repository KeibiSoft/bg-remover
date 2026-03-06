# Stage 1: Build
FROM python:3.12-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src/ ./src/
COPY scripts/ ./scripts/

# Install dependencies into a virtual environment
RUN uv sync --frozen --no-dev --extra cpu --extra server

# Pre-download AI model
RUN uv run scripts/download_model.py

# Stage 2: Runtime
FROM python:3.12-slim

# Create a non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup -m appuser

WORKDIR /app

# Copy the virtual environment and installed packages from builder
COPY --from=builder /app /app
# Copy the AI model from the builder's home directory to the appuser's home
COPY --from=builder /root/.u2net /home/appuser/.u2net

# Set ownership to appuser
RUN chown -R appuser:appgroup /app /home/appuser/.u2net

# Switch to non-root user
USER appuser

# Expose port (informational)
EXPOSE 8000

# Environment variables
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV BG_REMOVER_MODE=server

# Use the python module as the entrypoint
CMD ["python", "-m", "bg_remover.main"]
