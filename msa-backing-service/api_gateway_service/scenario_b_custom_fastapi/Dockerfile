FROM python:3.9-slim

WORKDIR /gateway_app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app ./app
COPY ./certs ./certs # SSL 인증서 복사 (Uvicorn에서 직접 SSL 사용 시)
ENV API_GW_CONFIG_PATH=app/routes.yml
ENV PYTHONPATH=/gateway_app
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--ssl-keyfile", "/gateway_app/certs/selfsigned.key", "--ssl-certfile", "/gateway_app/certs/selfsigned.crt"]