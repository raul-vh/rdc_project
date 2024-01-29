FROM python:3.11-slim-bookworm

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
#    git \
    && rm -rf /var/lib/apt/lists/*

# RUN git clone https://github.com/raul-vh/rdc_project .

COPY requirements.txt requirements.txt

COPY .env .env

# RUN pip install --upgrade pip

RUN pip install -r requirements.txt

COPY app.py app.py

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]

