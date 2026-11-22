FROM python:3.13-slim
WORKDIR /app
COPY requirements.lock .
RUN pip install --no-cache-dir -r requirements.lock
COPY . .
ENV USE_LAKEHOUSE=false
ENV HOST=0.0.0.0
EXPOSE 8000
CMD ["python", "server.py"]
