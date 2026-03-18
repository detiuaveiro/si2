const arrow = [
  [2, 0],
  [-10, -4],
  [-10, 4],
];

/**
 * Draws a visualization of a Neural Network on a canvas.
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
  ctx.save(); // Save initial state
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = "rgba(255, 255, 255, 1.0)";
  ctx.fillRect(0, 0, canvas.width, canvas.height); // Actually fill the background
  ctx.font = "15px Arial";

  // 1. Calculate Geometry
  const maxNeuronNumInLayer = Math.max(...networkLayer);

  // Calculate max radius allowed by vertical space (original logic)
  const maxRadiusY = height / maxNeuronNumInLayer / 2.5;

  // Calculate max radius allowed by horizontal space (width / (layers * 3 to allow for spacing))
  const maxRadiusX = width / (3 * networkLayer.length);
  // Use the smaller radius to ensure fit in both dimensions
  const radius = Math.min(maxRadiusY, maxRadiusX);

  // Calculate vertical spacing (gap between neurons)
  const intervalVertical =
    (height - maxNeuronNumInLayer * radius * 2) / maxNeuronNumInLayer;

  // Calculate horizontal spacing (gap between layers)
  const intervalHorizontal =
    (width - networkLayer.length * radius * 2) / (networkLayer.length - 1);

  let x = radius + canvas.width * 0.05; // Add padding
  const neuronLocationPerLayer = [];

  // 2. Calculate Positions (Do not draw yet)
  for (let layerIdx = 0; layerIdx < networkLayer.length; layerIdx++) {
    const thisLayerNeuronLocation = [];
    const neuronCount = networkLayer[layerIdx];

    // Center the layer vertically
    // Formula: (TotalHeight - (Neurons * TotalNeuronHeight)) / 2 + Radius + Padding
    let y =
      (height - neuronCount * (radius * 2 + intervalVertical)) / 2 +
      radius +
      canvas.height * 0.05;

    // Adjust y to remove the trailing intervalVertical for perfect centering
    y += intervalVertical / 2;

    for (let i = 0; i < neuronCount; ++i) {
      thisLayerNeuronLocation.push({ x: x, y: y });
      y += radius * 2 + intervalVertical;
    }

    neuronLocationPerLayer.push(thisLayerNeuronLocation);
    x += intervalHorizontal + radius * 2;
  }

  // 3. Draw Connections (First, so they go behind nodes)
  for (let i = 0; i < networkLayer.length - 1; i++) {
    const sourceLayer = neuronLocationPerLayer[i];
    const destLayer = neuronLocationPerLayer[i + 1];

    for (let srcIdx = 0; srcIdx < sourceLayer.length; srcIdx++) {
      for (let destIdx = 0; destIdx < destLayer.length; destIdx++) {
        const source = sourceLayer[srcIdx];
        const dest = destLayer[destIdx];

        // Logic to skip drawing INPUT connections TO a Bias node.
        // If bias is ON, we assume the first node (index 0) of every layer
        // EXCEPT the last one is a Bias node.
        // However, connections go FROM bias nodes, they usually don't receive them.
        // The original logic seemed to stop connections GOING TO index 0.
        if (bias && destIdx === 0 && i + 1 !== networkLayer.length - 1) {
          continue;
        }

        drawLineArrow(
          ctx,
          source.x + radius,
          source.y,
          dest.x - radius,
          dest.y,
        );
      }
    }
  }

  // 4. Draw Neurons (Second, so they sit on top of lines)
  for (let layerIdx = 0; layerIdx < neuronLocationPerLayer.length; layerIdx++) {
    const locations = neuronLocationPerLayer[layerIdx];
    for (let i = 0; i < locations.length; i++) {
      const loc = locations[i];

      // Safety check for activations
      const isActive = activations[layerIdx] && activations[layerIdx][i] > 0;
      const color = isActive ? "green" : "red";

      drawCircle(ctx, loc.x, loc.y, radius, color);

      // Draw Bias Label
      // If bias is on, and this is the 0th node, and it's not the output layer
      if (bias && i === 0 && layerIdx !== networkLayer.length - 1) {
        ctx.save(); // Save state before changing text props
        ctx.fillStyle = "black";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText("+1", loc.x, loc.y);
        ctx.restore(); // Restore state
      }
    }
  }

  ctx.restore(); // Restore original canvas state
}

function drawCircle(context, centerX, centerY, radius, color) {
  context.beginPath();
  context.arc(centerX, centerY, radius, 0, 2 * Math.PI, false);
  context.fillStyle = color;
  context.fill();
  context.lineWidth = radius / 20;
  context.strokeStyle = "#000000";
  context.stroke();
}

function getRadiusSize(neuronSize) {
  return neuronSize / 2.5;
}

function drawFilledPolygon(ctx, shape) {
  ctx.beginPath();
  ctx.moveTo(shape[0][0], shape[0][1]);

  for (let p = 1; p < shape.length; p++) {
    ctx.lineTo(shape[p][0], shape[p][1]);
  }

  ctx.lineTo(shape[0][0], shape[0][1]);
  ctx.fillStyle = "#000000";
  ctx.fill();
}

function translateShape(shape, x, y) {
  const rv = [];
  for (let p = 0; p < shape.length; p++) {
    rv.push([shape[p][0] + x, shape[p][1] + y]);
  }
  return rv;
}

function rotateShape(shape, ang) {
  const rv = [];
  for (let p = 0; p < shape.length; p++) {
    rv.push(rotatePoint(ang, shape[p][0], shape[p][1]));
  }
  return rv;
}

function rotatePoint(ang, x, y) {
  return [
    x * Math.cos(ang) - y * Math.sin(ang),
    x * Math.sin(ang) + y * Math.cos(ang),
  ];
}

function drawLineArrow(ctx, x1, y1, x2, y2) {
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.lineTo(x2, y2);
  ctx.strokeStyle = "#000000";
  ctx.stroke();

  // Draw Arrowhead
  const ang = Math.atan2(y2 - y1, x2 - x1);
  drawFilledPolygon(ctx, translateShape(rotateShape(arrow, ang), x2, y2));
}
