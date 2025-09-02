# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:$PATH"

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install Python dependencies
RUN uv sync --frozen

# Copy application code
COPY weather.py ./
COPY sse_server.py ./

# Expose port (Code Engine will use this)
EXPOSE 8000

# Create a startup script that can handle both HTTP and stdio modes
COPY start.py ./

# Use the startup script as the entry point
CMD ["uv", "run", "start.py"]
