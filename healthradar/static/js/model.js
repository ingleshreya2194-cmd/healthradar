/* model.js - Model Info page: accuracy, confusion matrix and feature importance. */

(function () {
  const body = document.getElementById("modelBody");

  HR.getJSON("/api/model-info")
    .then(show)
    .catch(function (err) {
      HR.clear(body);
      HR.message(document.getElementById("modelError"),
        err.message + " (Run python train_model.py once, then reload this page.)", "warn");
    });

  function show(m) {
    HR.clear(body);
    const labels = m.labels;

    // Confusion matrix: darker cell = more rows
    const maxCell = Math.max.apply(null, m.confusion_matrix.flat().concat([1]));
    const cmHead = HR.h("tr", {}, HR.h("th", {}, "Real \\ Predicted"), labels.map(function (l) { return HR.h("th", {}, l); }));
    const cmRows = m.confusion_matrix.map(function (row, i) {
      return HR.h("tr", {}, HR.h("th", {}, labels[i]),
        row.map(function (v, j) {
          const strength = v / maxCell;
          const style = "background: rgba(15,157,122," + (0.08 + strength * 0.55).toFixed(2) + ")";
          return HR.h("td", { class: i === j ? "diag" : "", style: style }, HR.fmt(v));
        }));
    });

    // Per-class precision / recall
    const pcHead = HR.h("tr", {}, ["Risk level", "Precision", "Recall", "F1-score"].map(function (t) { return HR.h("th", {}, t); }));
    const pcRows = labels.map(function (l) {
      const c = m.per_class[l] || {};
      return HR.h("tr", {}, HR.h("td", {}, l), HR.h("td", {}, c.precision), HR.h("td", {}, c.recall), HR.h("td", {}, c["f1-score"]));
    });

    // Feature importance bars
    const imp = Object.entries(m.feature_importance).sort(function (a, b) { return b[1] - a[1]; });
    const names = { cases_4w: "Cases (4 weeks)", growth_rate: "Growth rate", population: "Population", cases_per_100k: "Cases per 100k" };

    body.append(
      HR.h("div", { class: "info-grid" },
        HR.h("div", { class: "card" },
          HR.h("div", { class: "muted small" }, "Accuracy on test weeks"),
          HR.h("div", { class: "big-number" }, (m.accuracy * 100).toFixed(1) + "%"),
          HR.h("p", { class: "small muted", style: "margin-top:8px" },
            m.model + ". Trained on " + HR.fmt(m.train_rows) + " rows, tested on " + HR.fmt(m.test_rows) +
            " newer rows (from " + m.test_period_start + "). Forecast method: " + m.forecast_method + ".")),
        HR.h("div", { class: "card" },
          HR.h("h3", {}, "What drives the prediction"),
          imp.map(function (pair) {
            return HR.h("div", { class: "bar-row" },
              HR.h("span", {}, names[pair[0]] || pair[0]),
              HR.h("div", { class: "bar" }, HR.h("i", { style: "width:" + Math.round(pair[1] * 100) + "%" })),
              HR.h("span", {}, Math.round(pair[1] * 100) + "%"));
          }))
      ),
      HR.h("div", { class: "card", style: "margin-top:14px" },
        HR.h("h3", {}, "Confusion matrix"),
        HR.h("p", { class: "small muted" }, "Rows are the real risk level, columns are what the model predicted. Numbers on the diagonal are correct predictions."),
        HR.h("div", { class: "table-wrap" }, HR.h("table", { class: "cm" }, HR.h("thead", {}, cmHead), HR.h("tbody", {}, cmRows)))
      ),
      HR.h("div", { class: "card", style: "margin-top:14px" },
        HR.h("h3", {}, "Results for each risk level"),
        HR.h("div", { class: "table-wrap" }, HR.h("table", { class: "cm" }, HR.h("thead", {}, pcHead), HR.h("tbody", {}, pcRows)))
      ),
      HR.h("div", { class: "status warn", style: "margin-top:14px" }, m.note)
    );
  }
})();
