const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const status = document.getElementById('status');
const ballPos = document.getElementById('ball-pos');
const paddlePos = document.getElementById('paddle-pos');

// Connect to port 8765
const SOCKET_URL = `ws://${window.location.hostname}:8765/ws`;
let socket;

function connect() {
    socket = new WebSocket(SOCKET_URL);

    socket.onopen = () => {
        status.innerText = "Connected";
        status.className = "connected";
        status.style.color = "green";
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "state") {
            draw(data);
        }
    };

    socket.onclose = () => {
        status.innerText = "Disconnected. Retrying...";
        status.className = "disconnected";
        status.style.color = "red";
        setTimeout(connect, 2000);
    };
}

function draw(data) {
    const { state, reward, done, score } = data;
    const [bx, by, bvx, bvy, px] = state;
    const w = canvas.width;
    const h = canvas.height;

    // Clear
    ctx.clearRect(0, 0, w, h);

    if (done) {
        ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
        ctx.fillRect(0, 0, w, h);
        ctx.fillStyle = "white";
        ctx.font = "30px Arial";
        ctx.textAlign = "center";
        ctx.fillText("GAME OVER", w / 2, h / 2);
        ctx.font = "20px Arial";
        ctx.fillText(`Score: ${score}`, w / 2, h / 2 + 40);
        return;
    }

    // Draw Paddle
    const paddleWidth = 0.2 * w;
    const paddleHeight = 15;
    ctx.fillStyle = "#007bff";
    ctx.fillRect((px * w) - (paddleWidth / 2), h - 25, paddleWidth, paddleHeight);

    // Draw Ball
    ctx.beginPath();
    ctx.arc(bx * w, by * h, 10, 0, Math.PI * 2);
    ctx.fillStyle = "#dc3545";
    ctx.fill();
    ctx.closePath();

    // Update Text
    ballPos.innerText = `(${bx.toFixed(2)}, ${by.toFixed(2)})`;
    paddlePos.innerText = `${px.toFixed(2)}`;
    status.innerText = `Connected - Score: ${score}`;
}

connect();
