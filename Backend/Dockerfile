# 1. Use the official lightweight Python 3.13 image
FROM python:3.13-slim

# 2. Set the working directory inside the container
WORKDIR /app

# 3. Copy uv for fast dependency installation
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# 4. Copy dependency definition first (enables Docker layer caching)
COPY pyproject.toml ./

# 5. Install all production dependencies using uv
RUN uv pip install --system -r pyproject.toml

# 6. Copy application source code
COPY . .

# 7. Expose HTTP port
EXPOSE 8000

# 8. Start FastAPI with Uvicorn (honoring Render's dynamic $PORT variable)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]
