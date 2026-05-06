FROM python:3.11-slim
WORKDIR /app
RUN pip install fastapi "uvicorn[standard]" numpy
COPY . .
CMD ["python", "server.py"]
