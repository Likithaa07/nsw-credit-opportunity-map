# Runs the whole pipeline in a clean container (downloads about 1 GB of spatial data):
#   docker build -t credit-map .
#   docker run --rm -v "$PWD/data:/app/data" -v "$PWD/outputs:/app/outputs" credit-map
# Just the ranking and tests, from the committed tables:
#   docker run --rm credit-map python -m pytest -v
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ src/
COPY tests/ tests/
COPY data/ data/

CMD ["python", "src/run_all.py"]
