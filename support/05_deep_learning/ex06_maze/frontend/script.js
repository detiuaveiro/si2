const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const status = document.getElementById('status');
const agentPosDisplay = document.getElementById('agent-pos');

const SOCKET_URL = `ws://${window.location.hostname}:8003/ws`;
let socket;

function connect() {
    socket = new WebSocket(SOCKET_URL);
    socket.onopen = () => { status.innerText = "Connected"; status.className = "connected"; };
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "state") {
            draw(data);
            agentPosDisplay.innerText = `(${data.agent_pos[0]}, ${data.agent_pos[1]})`;
        }
    };
    socket.onclose = () => { status.innerText = "Disconnected. Retrying..."; status.className = "disconnected"; setTimeout(connect, 2000); };
}

function draw(data) {
    const maze = data.maze;
    const pos = data.agent_pos;
    const goal = data.goal;
    const s = canvas.width;
    const cells = maze.length;
    const cw = s / cells;

    ctx.clearRect(0, 0, s, s);

    for (let r = 0; r < cells; r++) {
        for (let c = 0; c < cells; c++) {
            if (maze[r][c] === 1) {
                ctx.fillStyle = "#333";
                ctx.fillRect(c * cw, r * cw, cw, cw);
            } else {
                ctx.strokeStyle = "#ddd";
                ctx.strokeRect(c * cw, r * cw, cw, cw);
            }
        }
    }

    // Start
    ctx.fillStyle = "rgba(40, 167, 69, 0.3)";
    ctx.fillRect(0, 0, cw, cw);

    // Goal
    ctx.fillStyle = "rgba(220, 53, 69, 0.6)";
    ctx.fillRect(goal[1] * cw, goal[0] * cw, cw, cw);
    ctx.fillStyle = "white";
    ctx.font = "12px Arial";
    ctx.textAlign = "center";
    ctx.fillText("GOAL", goal[1] * cw + cw/2, goal[0] * cw + cw/2 + 5);

    // Agent
    ctx.beginPath();
    ctx.arc(pos[1] * cw + cw/2, pos[0] * cw + cw/2, cw/3, 0, Math.PI * 2);
    ctx.fillStyle = "#007bff";
    ctx.fill();
    ctx.strokeStyle = "white";
    ctx.lineWidth = 2;
    ctx.stroke();
    ctx.closePath();
}

connect();
