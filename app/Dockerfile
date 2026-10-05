# The model app: FastAPI serves the page (web/), the model card and predictions from model/model.json.
#   docker build --target test -t arabic-ai:test app && docker run --rm arabic-ai:test
#   docker build --target runtime -t arabic-ai app && docker run --rm -p 8082:8000 arabic-ai
FROM python:3.12-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server ./server
COPY web ./web
COPY model ./model

FROM base AS test
COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt
COPY tests ./tests
CMD ["python", "-m", "pytest", "-q", "tests"]

FROM base AS runtime
RUN useradd --system --uid 10001 app
USER app
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=2)"
# no access log: answers travel in POST bodies and are never written anywhere
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--no-access-log"]
