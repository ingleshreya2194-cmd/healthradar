/* travel.js - Travel Check page: choose a country, see active diseases, risk and precautions. */

(function () {
  const select = document.getElementById("destination");
  const result = document.getElementById("travelResult");
  const button = document.getElementById("checkBtn");

  // General tips shown for every destination
  const GENERAL_TIPS = [
    "Check the latest travel health advice from WHO, CDC or your own health ministry before you go.",
    "Ask your doctor or a travel clinic about vaccines that suit your trip, ideally 4-6 weeks before travel.",
    "Carry any regular medicines, hand sanitiser and mosquito repellent.",
    "If you feel unwell during or after your trip, especially with fever, see a doctor and mention where you travelled.",
  ];

  // Fill the drop-down with countries
  HR.getJSON("/api/countries")
    .then(function (data) {
      HR.clear(select);
      select.append(HR.h("option", { value: "" }, "Choose a country"));
      data.countries
        .map(function (c) { return c.country; })
        .sort()
        .forEach(function (name) { select.append(HR.h("option", { value: name }, name)); });
      // Allow links like /travel?country=India
      const wanted = new URLSearchParams(window.location.search).get("country");
      if (wanted) { select.value = wanted; if (select.value) check(); }
    })
    .catch(function (err) {
      HR.clear(select);
      select.append(HR.h("option", { value: "" }, "Could not load countries"));
      HR.message(result, err.message, "bad");
    });

  button.addEventListener("click", check);
  select.addEventListener("change", function () { if (select.value) check(); });

  function check() {
    if (!select.value) {
      HR.message(result, "Please choose a destination country first.", "warn");
      return;
    }
    HR.message(result, "Checking " + select.value + "...");
    HR.getJSON("/api/country/" + encodeURIComponent(select.value))
      .then(show)
      .catch(function (err) { HR.message(result, "Could not check this country. " + err.message, "bad"); });
  }

  function show(data) {
    HR.clear(result);
    // Diseases with Medium or High risk are "active concerns"; show all, highest risk first
    const order = { High: 0, Medium: 1, Low: 2 };
    const diseases = data.diseases.slice().sort(function (a, b) {
      return order[a.risk] - order[b.risk] || b.cases_4w - a.cases_4w;
    });
    const active = diseases.filter(function (d) { return d.risk !== "Low"; });

    result.append(
      HR.h("div", { class: "card", style: "margin-top:16px" },
        HR.h("h2", {}, data.country, " ", HR.badge(data.risk, data.risk + " overall risk")),
        HR.h("p", { class: "muted small" },
          "Data week " + data.data_date + (data.sample_data ? " (SAMPLE data)" : "") + ". Risk levels come from our risk model."),
        HR.h("p", {}, active.length
          ? "Diseases to be careful about: " + active.map(function (d) { return d.disease + " (" + d.risk + ")"; }).join(", ") + "."
          : "No disease is at medium or high risk right now. Basic precautions still help.")
      ),
      HR.h("div", { class: "result-grid" }, diseases.map(function (d) { return HR.diseaseCard(d); })),
      HR.h("div", { class: "card", style: "margin-top:14px" },
        HR.h("h3", {}, "Before you travel"),
        HR.h("ul", {}, GENERAL_TIPS.map(function (t) { return HR.h("li", {}, t); }))
      )
    );
  }
})();
