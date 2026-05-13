const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const status = document.getElementById('status');
const scoreDisplay = document.getElementById('score');

const SOCKET_URL = `ws://${window.location.hostname}:8765/ws`;
let socket;

function connect() {
    socket = new WebSocket(SOCKET_URL);

    socket.onopen = () => {
        status.innerText = "Connected";
        status.className = "connected";
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "state") {
            drawSnake(data.snake, data.food, data.size);
            scoreDisplay.innerText = data.score;
        } else if (data.type === "activations") {
            // Draw chart for action probabilities (0: Up, 1: Right, 2: Down, 3: Left)
            draw_bar_chart(data.activations[0], "canvas_network", data.chosen_action, ["Up", "Right", "Down", "Left"]);
        }
    };

    socket.onclose = () => {
        status.innerText = "Disconnected. Retrying...";
        status.className = "disconnected";
        setTimeout(connect, 2000);
    };
}

function drawSnake(snake, food, size) {
    const cellSize = canvas.width / size;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Draw Grid (Optional, keep it light)
    ctx.strokeStyle = "#eee";
    for(let i=0; i<=size; i++) {
        ctx.beginPath(); ctx.moveTo(i*cellSize, 0); ctx.lineTo(i*cellSize, canvas.height); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(0, i*cellSize); ctx.lineTo(canvas.width, i*cellSize); ctx.stroke();
    }

    // Draw Body
    ctx.fillStyle = "#28a745";
    snake.slice(1).forEach(seg => {
        ctx.fillRect(seg[1]*cellSize + 1, seg[0]*cellSize + 1, cellSize - 2, cellSize - 2);
    });

    // Draw Head
    ctx.fillStyle = "#1e7e34";
    ctx.fillRect(snake[0][1]*cellSize, snake[0][0]*cellSize, cellSize, cellSize);

    // Draw Food
    ctx.fillStyle = "#dc3545";
    ctx.beginPath();
    ctx.arc(food[1]*cellSize + cellSize/2, food[0]*cellSize + cellSize/2, cellSize/3, 0, Math.PI*2);
    ctx.fill();
}

connect();
