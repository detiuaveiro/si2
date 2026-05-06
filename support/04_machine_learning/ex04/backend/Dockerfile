FROM python:3.14-alpine

WORKDIR /app

RUN pip install websockets

COPY server.py .

EXPOSE 8765

CMD ["python", "server.py"]
