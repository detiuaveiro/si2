const arrow = [
  [2, 0],
  [-10, -4],
  [-10, 4],
];

/**
 * Draws a visualization of a Neural Network on a canvas with semantic coloring.
 * @param {Array<number>} networkLayer - Array containing the number of neurons in each layer (e.g., [4, 5, 1]).
 * @param {Array<Array<number>>} activations - Array of arrays containing the activation values for each neuron.
 * @param {boolean} [bias=false] - If true, adds a bias label (+1) to the first neuron of hidden layers.
 * @param {string} [canvas_id='canvas_network'] - The ID of the HTML canvas element.
 */
function draw_network(
  networkLayer,
  activations,
  bias = false,
  canvas_id = "canvas_network",
) {
  const canvas = document.getElementById(canvas_id);
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  const width = canvas.width * 0.9;
  const height = canvas.height * 0.9;

  // Reset Canvas state
  ctx.save();
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "rgba(255, 255, 255, 1.0)";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.font = "12px Arial";

  // 1. Calculate Geometry
  const maxNeuronNumInLayer = Math.max(...networkLayer);
  const maxRadiusY = height / maxNeuronNumInLayer / 2.2;
  const maxRadiusX = width / (3 * networkLayer.length);
  const radius = Math.min(maxRadiusY, maxRadiusX, 15); // Cap radius for small networks

  const intervalVertical = (height - maxNeuronNumInLayer * radius * 2) / maxNeuronNumInLayer;
  const intervalHorizontal = (width - networkLayer.length * radius * 2) / (networkLayer.length - 1);

  let x = radius + canvas.width * 0.05;
  const neuronLocationPerLayer = [];

  for (let layerIdx = 0; layerIdx < networkLayer.length; layerIdx++) {
    const thisLayerNeuronLocation = [];
    const neuronCount = networkLayer[layerIdx];
    let y = (height - neuronCount * (radius * 2 + intervalVertical)) / 2 + radius + canvas.height * 0.05 + intervalVertical / 2;

    for (let i = 0; i < neuronCount; ++i) {
      thisLayerNeuronLocation.push({ x: x, y: y });
      y += radius * 2 + intervalVertical;
    }
    neuronLocationPerLayer.push(thisLayerNeuronLocation);
    x += intervalHorizontal + radius * 2;
  }

  // 2. Draw Connections
  ctx.lineWidth = 1;
  ctx.strokeStyle = "rgba(200, 200, 200, 0.5)";
  for (let i = 0; i < networkLayer.length - 1; i++) {
    const sourceLayer = neuronLocationPerLayer[i];
    const destLayer = neuronLocationPerLayer[i + 1];
    for (let srcIdx = 0; srcIdx < sourceLayer.length; srcIdx++) {
      for (let destIdx = 0; destIdx < destLayer.length; destIdx++) {
        if (bias && destIdx === 0 && i + 1 !== networkLayer.length - 1) continue;
        
        // Draw connection only if source is somewhat active (optional optimization)
        const sourceVal = activations[i] ? activations[i][srcIdx] : 0;
        if (Math.abs(sourceVal) > 0.01) {
            ctx.beginPath();
            ctx.moveTo(sourceLayer[srcIdx].x + radius, sourceLayer[srcIdx].y);
            ctx.lineTo(destLayer[destIdx].x - radius, destLayer[destIdx].y);
            ctx.stroke();
        }
      }
    }
  }

  // 3. Draw Neurons
  for (let layerIdx = 0; layerIdx < neuronLocationPerLayer.length; layerIdx++) {
    const locations = neuronLocationPerLayer[layerIdx];
    const isInput = (layerIdx === 0);
    const isOutput = (layerIdx === networkLayer.length - 1);
    
    for (let i = 0; i < locations.length; i++) {
      const loc = locations[i];
      const val = activations[layerIdx] ? activations[layerIdx][i] : 0;
      
      let color = "yellow"; // Default for zero
      
      if (isInput) {
          // Tic-Tac-Toe Input Logic: 1 (Green), 0 (Yellow), -1 (Red)
          if (val > 0.5) color = "#28a745"; // Green
          else if (val < -0.5) color = "#dc3545"; // Red
          else color = "#ffc107"; // Yellow
      } else if (isOutput) {
          // Output Logic: Probability Gradient Red (0) to Green (1)
          const r = Math.floor((1 - val) * 255);
          const g = Math.floor(val * 255);
          color = `rgb(${r}, ${g}, 0)`;
      } else {
          // Hidden Layers: Active (Green), Inactive (Yellow)
          // Since it's ReLU, it's usually 0 or positive
          if (val > 0.01) color = "#28a745";
          else color = "#ffc107";
      }

      drawCircle(ctx, loc.x, loc.y, radius, color);

      if (bias && i === 0 && layerIdx !== networkLayer.length - 1) {
        ctx.save();
        ctx.fillStyle = "black";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("+1", loc.x, loc.y);
        ctx.restore();
      }
    }
  }
  ctx.restore();
}

/**
 * Draws a bar chart on a canvas to visualize confidence/Q-values.
 * @param {Array<number>} values - Array of values to plot.
 * @param {string} [canvas_id='canvas_network'] - The ID of the HTML canvas element.
 */
/**
 * Draws a bar chart on a canvas to visualize confidence/Q-values.
 * @param {Array<number>} values - Array of values to plot.
 * @param {string} [canvas_id='canvas_network'] - The ID of the HTML canvas element.
 * @param {number} [chosen_index=-1] - The index of the action selected by the agent.
 */
function draw_bar_chart(values, canvas_id = "canvas_network", chosen_index = -1) {
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
  // Ensure we have a decent range for small values
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
  ctx.fillStyle = "#666";
  ctx.font = "12px Arial";
  ctx.fillText("0.0", padding_left - 10, zeroY + 5);

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

    // Semantic coloring
    let color;
    if (isIllegal) {
        color = "#e0e0e0"; // Light grey
    } else {
        const ratio = (normVal + 1) / 2; // 0 to 1
        const r = Math.floor((1 - ratio) * 200) + 55;
        const g = Math.floor(ratio * 200) + 55;
        color = `rgb(${r}, ${g}, 50)`;
    }
    
    ctx.fillStyle = color;

    // Highlight chosen action
    if (i === chosen_index) {
        ctx.shadowBlur = 10;
        ctx.shadowColor = "rgba(0,0,0,0.5)";
        ctx.strokeStyle = "#007bff";
        ctx.lineWidth = 4;
        ctx.strokeRect(x - 2, y - 2, w + 4, h + 4);
        ctx.shadowBlur = 0;
    }

    ctx.fillRect(x, y, w, h);
    
    // Label index (X-axis)
    ctx.fillStyle = i === chosen_index ? "#007bff" : "#333";
    ctx.textAlign = "center";
    ctx.font = i === chosen_index ? "bold 16px Arial" : "14px Arial";
    ctx.fillText(i.toString(), x + w/2, canvas.height - padding_bottom + 30);
    
    // Value label
    if (!isIllegal) {
        ctx.save();
        ctx.fillStyle = "#000";
        ctx.font = "bold 13px Arial";
        const labelY = val >= 0 ? y - 10 : y + h + 20;
        ctx.fillText(val.toFixed(2), x + w/2, labelY);
        ctx.restore();
    } else {
        ctx.save();
        ctx.fillStyle = "#999";
        ctx.font = "italic 11px Arial";
        ctx.fillText("N/A", x + w/2, zeroY + 15);
        ctx.restore();
    }

    // "BEST" tag
    if (i === chosen_index && !isIllegal) {
        ctx.fillStyle = "#007bff";
        ctx.font = "bold 12px Arial";
        ctx.fillText("BEST", x + w/2, padding_top - 5);
    }
  });

  ctx.restore();
}

function drawCircle(context, centerX, centerY, radius, color) {
  context.beginPath();
  context.arc(centerX, centerY, radius, 0, 2 * Math.PI, false);
  context.fillStyle = color;
  context.fill();
  context.lineWidth = 1;
  context.strokeStyle = "#444";
  context.stroke();
}
