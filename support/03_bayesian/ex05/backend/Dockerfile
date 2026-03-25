FROM python:3.14-alpine

WORKDIR /app

# Install the required websocket library
RUN pip install websockets

# Copy the server script into the container
COPY server.py .

# Expose the websocket port
EXPOSE 8765

# Run the server
CMD ["python", "server.py"]