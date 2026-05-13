/**
 * Draws a bar chart on a canvas to visualize confidence/Q-values.
 * @param {Array<number>} values - Array of values to plot.
 * @param {string} [canvas_id='canvas_network'] - The ID of the HTML canvas element.
 * @param {number} [chosen_index=-1] - The index of the action selected by the agent.
 * @param {Array<string>} [labels=[]] - Optional labels for the bars.
 */
function draw_bar_chart(values, canvas_id = "canvas_network", chosen_index = -1, labels = []) {
  const canvas = document.getElementById(canvas_id);
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  const padding_left = 70;
  const padding_right = 30;
  const padding_top = 60;
  const padding_bottom = 70;
  
  const width = canvas.width - padding_left - padding_right;
  const height = canvas.height - padding_top - padding_bottom;

  // Reset Canvas state
  ctx.save();
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "#ffffff";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Calculate scales
  const barWidth = width / values.length;
  const cleanValues = values.map(v => isFinite(v) ? v : 0);
  const maxAbs = Math.max(...cleanValues.map(Math.abs), 0.1);
  const extreme = maxAbs < 1.0 ? 1.0 : maxAbs * 1.1;
  
  const zeroY = padding_top + height / 2;

  // Draw Title
  ctx.fillStyle = "#222";
  ctx.font = "bold 20px Arial";
  ctx.textAlign = "center";
  ctx.fillText("Agent's Strategy (Action Values)", canvas.width / 2, 35);

  // Draw axes
  ctx.strokeStyle = "#000";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.moveTo(padding_left, padding_top);
  ctx.lineTo(padding_left, canvas.height - padding_bottom);
  ctx.stroke();

  // Draw Zero Line
  ctx.setLineDash([8, 4]);
  ctx.strokeStyle = "#aaa";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(padding_left, zeroY);
  ctx.lineTo(canvas.width - padding_right, zeroY);
  ctx.stroke();
  ctx.setLineDash([]);

  // Y-Axis Labels
  ctx.font = "bold 14px Arial";
  ctx.fillStyle = "#28a745";
  ctx.textAlign = "right";
  ctx.fillText("WIN", padding_left - 10, padding_top + 15);
  ctx.fillStyle = "#dc3545";
  ctx.fillText("LOSS", padding_left - 10, canvas.height - padding_bottom);

  // Draw bars
  values.forEach((val, i) => {
    const isIllegal = !isFinite(val);
    const displayVal = isIllegal ? -extreme * 0.8 : val;
    const normVal = displayVal / extreme;
    const barHeight = normVal * (height / 2);
    const x = padding_left + i * barWidth + barWidth * 0.15;
    const w = barWidth * 0.7;
    
    let y, h;
    if (displayVal >= 0) {
        y = zeroY - barHeight;
        h = barHeight;
    } else {
        y = zeroY;
        h = -barHeight;
    }

    let color;
    if (isIllegal) color = "#e0e0e0";
    else {
        const ratio = (normVal + 1) / 2;
        const r = Math.floor((1 - ratio) * 200) + 55;
        const g = Math.floor(ratio * 200) + 55;
        color = `rgb(${r}, ${g}, 50)`;
    }
    ctx.fillStyle = color;

    if (i === chosen_index) {
        ctx.shadowBlur = 10;
        ctx.shadowColor = "rgba(0,0,0,0.5)";
        ctx.strokeStyle = "#007bff";
        ctx.lineWidth = 4;
        ctx.strokeRect(x - 2, y - 2, w + 4, h + 4);
        ctx.shadowBlur = 0;
    }

    ctx.fillRect(x, y, w, h);
    
    const label = labels[i] || i.toString();
    ctx.fillStyle = i === chosen_index ? "#007bff" : "#333";
    ctx.textAlign = "center";
    ctx.font = i === chosen_index ? "bold 16px Arial" : "14px Arial";
    ctx.fillText(label, x + w/2, canvas.height - padding_bottom + 30);
    
    if (!isIllegal) {
        ctx.save();
        ctx.fillStyle = "#000";
        ctx.font = "bold 13px Arial";
        const labelY = val >= 0 ? y - 10 : y + h + 20;
        ctx.fillText(val.toFixed(2), x + w/2, labelY);
        ctx.restore();
    }

    if (i === chosen_index && !isIllegal) {
        ctx.fillStyle = "#007bff";
        ctx.font = "bold 12px Arial";
        ctx.fillText("BEST", x + w/2, padding_top - 5);
    }
  });

  ctx.restore();
}
