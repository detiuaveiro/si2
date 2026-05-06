const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const status = document.getElementById('status');
const scoreDisplay = document.getElementById('score');

const SOCKET_URL = `ws://${window.location.hostname}:8000/ws`;
let socket;
let totalFood = 0;

function connect() {
    socket = new WebSocket(SOCKET_URL);
    socket.onopen = () => { status.innerText = "Connected"; status.className = "connected"; };
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "state") {
            draw(data);
            if (data.reward > 0) {
                totalFood++;
                scoreDisplay.innerText = totalFood;
            }
            if (data.done) {
                totalFood = 0; // Reset for next game session
            }
        }
    };
    socket.onclose = () => { status.innerText = "Disconnected. Retrying..."; status.className = "disconnected"; setTimeout(connect, 2000); };
}

function draw(data) {
    const s = canvas.width;
    const size = data.size || 10;
    const cw = s / size;

    ctx.clearRect(0, 0, s, s);

    // Grid
    ctx.strokeStyle = "#ddd";
    ctx.lineWidth = 1;
    for(let i=0; i<=size; i++) {
        ctx.beginPath(); ctx.moveTo(i*cw, 0); ctx.lineTo(i*cw, s); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(0, i*cw); ctx.lineTo(s, i*cw); ctx.stroke();
    }

    // Food
    const [fr, fc] = data.food;
    ctx.fillStyle = "#e74c3c";
    ctx.fillRect(fc * cw + 4, fr * cw + 4, cw - 8, cw - 8);

    // Snake
    data.snake.forEach((pos, i) => {
        const [r, c] = pos;
        ctx.fillStyle = (i === 0) ? "#27ae60" : "#2ecc71";
        ctx.fillRect(c * cw + 2, r * cw + 2, cw - 4, cw - 4);
    });
}

connect();
