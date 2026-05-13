const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const status = document.getElementById('status');

const SOCKET_URL = `ws://${window.location.hostname}:8765/ws`;
let socket;

function connect() {
    socket = new WebSocket(SOCKET_URL);
    socket.onopen = () => { status.innerText = "Connected"; status.className = "connected"; };
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "state") {
            draw(data);
        }
    };
    socket.onclose = () => { status.innerText = "Disconnected. Retrying..."; status.className = "disconnected"; setTimeout(connect, 2000); };
}

function draw(data) {
    const { snake, food, size, score, done } = data;
    const s = canvas.width;
    const cw = s / size;

    ctx.clearRect(0, 0, s, s);

    // Grid
    ctx.strokeStyle = "#eee";
    for(let i=0; i<=size; i++) {
        ctx.beginPath(); ctx.moveTo(i*cw, 0); ctx.lineTo(i*cw, s); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(0, i*cw); ctx.lineTo(s, i*cw); ctx.stroke();
    }

    // Food
    ctx.fillStyle = "#dc3545";
    ctx.fillRect(food[1] * cw + 2, food[0] * cw + 2, cw - 4, cw - 4);

    // Snake
    snake.forEach((p, i) => {
        ctx.fillStyle = i === 0 ? "#28a745" : "#66bb6a";
        ctx.fillRect(p[1] * cw + 1, p[0] * cw + 1, cw - 2, cw - 2);
    });

    if (done) {
        ctx.fillStyle = "rgba(0, 0, 0, 0.5)";
        ctx.fillRect(0, 0, s, s);
        ctx.fillStyle = "white";
        ctx.font = "30px Arial";
        ctx.textAlign = "center";
        ctx.fillText("GAME OVER", s / 2, s / 2);
        ctx.font = "20px Arial";
        ctx.fillText(`Score: ${score}`, s / 2, s / 2 + 40);
    } else {
        status.innerText = `Connected - Score: ${score}`;
    }
}

connect();
