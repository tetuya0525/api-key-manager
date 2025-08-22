FROM python:3.12-slim
ENV PYTHONUNBUFFERED True
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PORT 8080
# タイムアウトを延長し、ワーカー数を1にすることで、起動時の安定性を確保
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "300", "main:app"]
