const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const status = document.getElementById('status');
const winnerDisplay = document.getElementById('winner-display');

const SOCKET_URL = `ws://${window.location.hostname}:8002/ws`;
let socket;

function connect() {
    socket = new WebSocket(SOCKET_URL);
    socket.onopen = () => { status.innerText = "Connected"; status.className = "connected"; };
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "state") {
            draw(data.board);
            updateWinner(data.winner);
        }
    };
    socket.onclose = () => { status.innerText = "Disconnected. Retrying..."; status.className = "disconnected"; setTimeout(connect, 2000); };
}

function draw(board) {
    const s = canvas.width;
    const cell = s / 3;
    ctx.clearRect(0, 0, s, s);

    // Draw Grid
    ctx.strokeStyle = "#444";
    ctx.lineWidth = 2;
    for(let i=1; i<3; i++) {
        ctx.beginPath(); ctx.moveTo(i*cell, 0); ctx.lineTo(i*cell, s); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(0, i*cell); ctx.lineTo(s, i*cell); ctx.stroke();
    }

    // Draw X and O
    ctx.font = "bold 60px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    board.forEach((val, i) => {
        const x = (i % 3) * cell + cell/2;
        const y = Math.floor(i / 3) * cell + cell/2;
        if (val === 1) {
            ctx.fillStyle = "#e44";
            ctx.fillText("X", x, y);
        } else if (val === -1) {
            ctx.fillStyle = "#44e";
            ctx.fillText("O", x, y);
        }
    });
}

function updateWinner(winner) {
    if (winner === 1) winnerDisplay.innerText = "Winner: Agent (X)";
    else if (winner === -1) winnerDisplay.innerText = "Winner: Opponent (O)";
    else if (winner === 0) winnerDisplay.innerText = "Draw!";
    else winnerDisplay.innerText = "Game in progress";
}

connect();
