FROM python:3.10-slim-bullseye

# System dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ffmpeg \
        git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy project
COPY . /app/
WORKDIR /app/

# Install Python dependencies
RUN python3 -m pip install --upgrade pip setuptools
RUN pip3 install --no-cache-dir --upgrade --requirement requirements.txt

# Render ke liye port expose karo
ENV PORT=8080
EXPOSE 8080

# Bot start karo
CMD ["python3", "main.py"]
