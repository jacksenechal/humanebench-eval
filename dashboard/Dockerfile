FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml ./
COPY humanebench/ ./humanebench/
COPY dashboard/ ./dashboard/
COPY rubrics/ ./rubrics/
COPY scripts/ ./scripts/
COPY entrypoint.sh ./
RUN pip install --no-cache-dir -e . && chmod +x entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
