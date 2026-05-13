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
    const grid = data.grid;
    const pos = data.agent_pos;
    const target = data.target;
    const path = data.path;
    const s = canvas.width;
    const cells = grid.length;
    const cw = s / cells;

    ctx.clearRect(0, 0, s, s);

    for (let r = 0; r < cells; r++) {
        for (let c = 0; c < cells; c++) {
            if (grid[r][c] === 1) {
                ctx.fillStyle = "#333";
                ctx.fillRect(c * cw, r * cw, cw, cw);
            } else {
                ctx.strokeStyle = "#eee";
                ctx.strokeRect(c * cw, r * cw, cw, cw);
            }
        }
    }

    // Path taken
    if (path) {
        ctx.strokeStyle = "rgba(0, 123, 255, 0.3)";
        ctx.lineWidth = 2;
        ctx.beginPath();
        path.forEach((p, i) => {
            if (i === 0) ctx.moveTo(p[1] * cw + cw / 2, p[0] * cw + cw / 2);
            else ctx.lineTo(p[1] * cw + cw / 2, p[0] * cw + cw / 2);
        });
        ctx.stroke();
    }

    // Goal
    ctx.fillStyle = "#dc3545";
    ctx.fillRect(target[1] * cw + 2, target[0] * cw + 2, cw - 4, cw - 4);

    // Agent
    ctx.beginPath();
    ctx.arc(pos[1] * cw + cw/2, pos[0] * cw + cw/2, cw/3, 0, Math.PI * 2);
    ctx.fillStyle = "#007bff";
    ctx.fill();
    ctx.strokeStyle = "white";
    ctx.lineWidth = 2;
    ctx.stroke();
}

connect();
