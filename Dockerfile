FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

#(선택) 빌드 안정성용
RUN pip install --no-cache-dir --upgrade pip

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app/app

#Cloud Run / 컨테이너 표준 포트
ENV PORT=8000
EXPOSE 8000

CMD ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:${PORT} --workers 2 --timeout 60"]