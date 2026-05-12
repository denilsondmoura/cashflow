FROM ubuntu:24.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Update and install dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    libpq-dev \
    gcc \
    curl \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install python dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt --break-system-packages

# Expose port
EXPOSE 8000

# Start command
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
