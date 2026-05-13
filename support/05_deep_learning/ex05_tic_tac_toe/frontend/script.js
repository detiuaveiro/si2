const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const status = document.getElementById('status');
const winnerDisplay = document.getElementById('winner-display');
const resetBtn = document.getElementById('reset-btn');

const SOCKET_URL = `ws://${window.location.hostname}:8765/ws`;
let socket;
let currentBoard = [0, 0, 0, 0, 0, 0, 0, 0, 0];
let gameWinner = null;

function connect() {
    socket = new WebSocket(SOCKET_URL);
    socket.onopen = () => {
        status.innerText = "Connected";
        status.className = "connected";
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "state") {
            currentBoard = data.board;
            gameWinner = data.winner;
            drawGame(currentBoard);
            updateWinner(gameWinner);
        } else if (data.type === "activations") {
            // Use draw_network from draw_tools.js
            draw_network(data.layers, data.activations, false, "canvas_network");
        }
    };

    socket.onclose = () => {
        status.innerText = "Disconnected. Retrying...";
        status.className = "disconnected";
        setTimeout(connect, 2000);
    };
}

function drawGame(board) {
    const s = canvas.width;
    const cell = s / 3;
    ctx.clearRect(0, 0, s, s);

    // Draw Grid
    ctx.strokeStyle = "#444";
    ctx.lineWidth = 2;
    for (let i = 1; i < 3; i++) {
        ctx.beginPath(); ctx.moveTo(i * cell, 0); ctx.lineTo(i * cell, s); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(0, i * cell); ctx.lineTo(s, i * cell); ctx.stroke();
    }

    // Draw X and O
    ctx.font = "bold 60px Arial";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    board.forEach((val, i) => {
        const x = (i % 3) * cell + cell / 2;
        const y = Math.floor(i / 3) * cell + cell / 2;
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
    if (winner === 1) winnerDisplay.innerText = "Winner: Player (X)";
    else if (winner === -1) winnerDisplay.innerText = "Winner: Agent (O)";
    else if (winner === 0) winnerDisplay.innerText = "Draw!";
    else winnerDisplay.innerText = "Game in progress";
}

canvas.addEventListener('click', (e) => {
    if (gameWinner !== null) return;

    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const col = Math.floor(x / (canvas.width / 3));
    const row = Math.floor(y / (canvas.height / 3));
    const index = row * 3 + col;

    if (currentBoard[index] === 0) {
        socket.send(json_message("move", { index: index, player: 1 }));
    }
});

resetBtn.addEventListener('click', () => {
    socket.send(json_message("reset", {}));
});

function json_message(type, payload) {
    return JSON.stringify({ type: type, ...payload });
}

connect();
