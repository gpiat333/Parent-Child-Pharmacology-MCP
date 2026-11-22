FROM python:3.13-slim
WORKDIR /app
COPY server/requirements.lock /app/requirements.lock
RUN pip install --no-cache-dir -r requirements.lock
COPY src /app/src
COPY main.py /app/main.py
ENV PYTHONPATH=/app/src
ENV USE_LAKEHOUSE=false
ENV MCP_TRANSPORT=streamable-http
ENV MCP_HOST=0.0.0.0
EXPOSE 8000
CMD ["python", "main.py"]
