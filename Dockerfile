# IndiaCryptoAlpha - Production Dockerfile
# 
# Build: docker build -t indiacryptoalpha:latest .
# Run:   docker run -it -p 8501:8501 indiacryptoalpha:latest
#
# This Dockerfile ensures 100% reproducible builds across all systems

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app/

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip, setuptools, wheel
RUN pip install --upgrade pip setuptools wheel

# Install dependencies
RUN pip install -r requirements.txt

# Create data and logs directories
RUN mkdir -p data logs

# Initialize database
RUN python -c "from logger import TradeDatabase; db = TradeDatabase(); db.close()"

# Initialize Excel log
RUN python -c "from logger import ExcelLogger; excel = ExcelLogger(); excel.close()"

# Expose Streamlit port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Default command: start trading system and dashboard
CMD ["sh", "-c", "python main.py & streamlit run dashboard/app.py"]
