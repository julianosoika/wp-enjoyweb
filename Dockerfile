FROM python:3.10-slim

WORKDIR /app

RUN pip install --no-cache-dir fastapi==0.110.0 uvicorn==0.28.0 python-multipart==0.0.9

COPY main.py app.py

EXPOSE 80

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]