# Stage 1: Base Image
FROM python:3.11-slim AS base

# --- Environment Configuration ---
WORKDIR /app
ENV PYTHONUNBUFFERED=1
# NOTE: The PATH for /root/.local/bin is no longer needed with system-wide installs.

# Stage 2: Install Dependencies
FROM base AS dependencies

# Install uv, the package installer.
RUN pip install uv

# Copy only the dependency definition files.
COPY pyproject.toml uv.lock ./

# Install project dependencies system-wide.
RUN uv pip install --system -r pyproject.toml

# Stage 3: Build the Runtime Image
FROM base AS runtime

# Copy the installed libraries from the previous stage.
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

COPY --from=dependencies /usr/local/bin /usr/local/bin

# Copy your application's source code.
COPY ./src ./src

# --- Runtime Configuration ---
EXPOSE 8000

# This command works because uvicorn was installed to /usr/local/bin, which is in the default PATH.
CMD ["uvicorn", "server.main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8000"]