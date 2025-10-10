# Stage 1: Base Image
# Use a slim, modern Python version for a smaller final image size.
FROM python:3.11-slim as base

# --- Environment Configuration ---
# Set the working directory inside the container.
WORKDIR /app
# Prevents Python from buffering stdout and stderr, which is useful for logging.
ENV PYTHONUNBUFFERED=1
# Add the local bin to the path to make installed CLIs available.
ENV PATH="/root/.local/bin:${PATH}"


# Stage 2: Install Dependencies
# This stage is dedicated to installing dependencies. It's a separate stage
# to leverage Docker's layer caching. Dependencies are only re-installed
# when your pyproject.toml or uv.lock file changes.
FROM base as dependencies

# Install uv, the package installer.
RUN pip install uv

# Copy only the dependency definition files.
COPY pyproject.toml uv.lock ./

# Install project dependencies using uv.
# The --system flag installs packages into the global site-packages,
# which is standard practice for containers.
RUN uv pip install --system -r pyproject.toml


# Stage 3: Build the Runtime Image
# This is the final image that will run your application.
FROM base as runtime

# Copy the installed dependencies from the previous stage.
COPY --from=dependencies /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=dependencies /root/.local/bin /root/.local/bin

# Copy your application's source code.
COPY ./src ./src

# --- Runtime Configuration ---
# Expose the port your FastAPI application will run on.
EXPOSE 8000

# Define the command to start your FastAPI application using Uvicorn.
# This command tells Uvicorn where to find your FastAPI app instance.
# 'src.server.main' corresponds to the file path src/server/main.py
# 'app' is the variable name of your FastAPI instance inside that file.
CMD ["uvicorn", "src.server.main:app", "--host", "0.0.0.0", "--port", "8000"]