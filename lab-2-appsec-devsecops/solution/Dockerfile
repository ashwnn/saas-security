FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    FLASK_DEBUG=0 \
    DB_PATH=/tmp/invoiceflow.db

RUN groupadd --system --gid 10001 invoiceflow \
    && useradd --system --uid 10001 --gid invoiceflow --home-dir /nonexistent invoiceflow

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=10001:10001 app.py .

USER 10001:10001
EXPOSE 5000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/health', timeout=2)"
CMD ["flask", "--app", "app", "run", "--host=0.0.0.0", "--port=5000"]

