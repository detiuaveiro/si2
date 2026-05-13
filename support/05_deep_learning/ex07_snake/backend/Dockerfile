FROM python:3.14-alpine
WORKDIR /app
RUN pip install fastapi "uvicorn[standard]" numpy
COPY . .
EXPOSE 8765
CMD ["python", "server.py"]
