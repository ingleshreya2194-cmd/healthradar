/* charts.js - a tiny line chart drawn with SVG (no chart library needed, so it is fast on phones).
   HR.drawChart(container, history, forecast)
     history  = [{date, cases}, ...]               real (sample) weekly cases
     forecast = [{date, predicted, lower, upper}]  next weeks predicted by the model
*/

HR.drawChart = function (container, history, forecast) {
  HR.clear(container);
  if (!history || history.length < 2) {
    container.append(HR.h("p", { class: "muted" }, "Not enough data to draw a chart."));
    return;
  }
  forecast = forecast || [];

  const W = 480, H = 230;
  const pad = { left: 52, right: 12, top: 12, bottom: 28 };
  const innerW = W - pad.left - pad.right;
  const innerH = H - pad.top - pad.bottom;

  // All points on one time line: history first, then forecast
  const total = history.length + forecast.length;
  const maxY = Math.max(
    ...history.map(function (p) { return p.cases; }),
    ...forecast.map(function (p) { return p.upper; }),
    1
  ) * 1.08;

  const x = function (i) { return pad.left + (i / (total - 1)) * innerW; };
  const y = function (v) { return pad.top + innerH - (v / maxY) * innerH; };

  // Build the SVG as a string (only numbers and fixed text go in, so this is safe)
  let svg = '<svg viewBox="0 0 ' + W + " " + H + '" role="img" aria-label="Weekly cases and forecast chart">';

  // Grid lines and y-axis labels
  svg += '<g class="grid axis">';
  for (let t = 0; t <= 4; t++) {
    const v = (maxY / 4) * t;
    const yy = y(v);
    svg += '<line x1="' + pad.left + '" x2="' + (W - pad.right) + '" y1="' + yy + '" y2="' + yy + '"/>';
    svg += '<text x="' + (pad.left - 6) + '" y="' + (yy + 3) + '" text-anchor="end">' + HR.short(v) + "</text>";
  }
  svg += "</g>";

  // X-axis date labels (about 5 of them)
  const all = history.map(function (p) { return p.date; }).concat(forecast.map(function (p) { return p.date; }));
  svg += '<g class="axis">';
  const labelCount = 5;
  for (let k = 0; k < labelCount; k++) {
    const i = Math.round((k / (labelCount - 1)) * (total - 1));
    svg += '<text x="' + x(i) + '" y="' + (H - 8) + '" text-anchor="middle">' + all[i].slice(5) + "</text>";
  }
  svg += "</g>";

  // Line for history
  let d = "";
  history.forEach(function (p, i) { d += (i ? "L" : "M") + x(i).toFixed(1) + " " + y(p.cases).toFixed(1); });
  svg += '<path d="' + d + '" fill="none" stroke="#1e6fd9" stroke-width="2.4" stroke-linejoin="round"/>';

  // Forecast: shaded band + dashed line, starting from the last real point
  if (forecast.length) {
    const lastI = history.length - 1;
    let upper = "M" + x(lastI).toFixed(1) + " " + y(history[lastI].cases).toFixed(1);
    let lower = "";
    let line = "M" + x(lastI).toFixed(1) + " " + y(history[lastI].cases).toFixed(1);
    forecast.forEach(function (p, j) {
      const i = history.length + j;
      upper += "L" + x(i).toFixed(1) + " " + y(p.upper).toFixed(1);
      line += "L" + x(i).toFixed(1) + " " + y(p.predicted).toFixed(1);
    });
    for (let j = forecast.length - 1; j >= 0; j--) {
      const i = history.length + j;
      lower += "L" + x(i).toFixed(1) + " " + y(forecast[j].lower).toFixed(1);
    }
    lower += "L" + x(lastI).toFixed(1) + " " + y(history[lastI].cases).toFixed(1) + "Z";
    svg += '<path d="' + upper + lower + '" fill="#f59e0b" opacity="0.18"/>';
    svg += '<path d="' + line + '" fill="none" stroke="#d97706" stroke-width="2.4" stroke-dasharray="6 4" stroke-linejoin="round"/>';
    forecast.forEach(function (p, j) {
      svg += '<circle cx="' + x(history.length + j).toFixed(1) + '" cy="' + y(p.predicted).toFixed(1) +
        '" r="3.5" fill="#d97706"><title>' + p.date + ": about " + HR.fmt(p.predicted) + " cases</title></circle>";
    });
  }
  svg += "</svg>";

  const box = HR.h("div", { class: "chart" });
  box.innerHTML = svg;
  container.append(box);
  container.append(HR.h("div", { class: "chart-key" },
    HR.h("span", {}, HR.h("i", { style: "background:#1e6fd9" }), "Weekly cases (sample)"),
    forecast.length ? HR.h("span", {}, HR.h("i", { style: "background:#d97706" }), "Forecast (next " + forecast.length + " weeks)") : null,
    forecast.length ? HR.h("span", {}, HR.h("i", { style: "background:#f5c46b" }), "Likely range") : null
  ));
};

// 1250000 -> "1.3M", 5400 -> "5.4k"
HR.short = function (v) {
  if (v >= 1e6) return (v / 1e6).toFixed(1) + "M";
  if (v >= 1e3) return (v / 1e3).toFixed(v >= 1e4 ? 0 : 1) + "k";
  return Math.round(v).toString();
};
