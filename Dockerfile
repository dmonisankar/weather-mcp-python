# Use Python 3.11 slim image
FROM --platform=linux/amd64 python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install uv package manager and Python dependencies
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    export PATH="/root/.local/bin:$PATH" && \
    /root/.local/bin/uv sync --frozen

# Set PATH for uv to be available in subsequent commands
ENV PATH="/root/.local/bin:$PATH"

# Copy application code
COPY weather.py ./

# Expose port (Code Engine will use this)
EXPOSE 8000


# Use the startup script as the entry point
CMD ["uv", "run", "weather.py"]
