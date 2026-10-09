/* home.js - the first page: risk cards for every country and the side panel. */

(function () {
  const grid = document.getElementById("countryGrid");
  const chips = document.getElementById("diseaseChips");
  const search = document.getElementById("search");
  const riskFilter = document.getElementById("riskFilter");
  const errorBox = document.getElementById("countryError");
  const panel = document.getElementById("sidePanel");
  const backdrop = document.getElementById("panelBackdrop");

  let countries = [];         // data from /api/countries
  let selectedDisease = "All"; // current chip
  let lastFocused = null;

  // ---- Load data ----
  HR.getJSON("/api/countries")
    .then(function (data) {
      countries = data.countries;
      document.getElementById("dataDate").textContent =
        "Latest data week: " + data.data_date + (data.sample_data ? " (sample data)" : "");
      buildChips();
      renderStats();
      renderCards();
    })
    .catch(function (err) {
      HR.clear(grid);
      HR.message(errorBox, "Could not load the country data. " + err.message, "bad");
    });

  // ---- Disease filter chips ----
  function buildChips() {
    ["All", "Dengue", "Influenza", "COVID-19"].forEach(function (name) {
      const b = HR.h("button", { class: "chip" + (name === "All" ? " active" : ""), type: "button" },
        name === "All" ? "All diseases" : name);
      b.addEventListener("click", function () {
        selectedDisease = name;
        chips.querySelectorAll(".chip").forEach(function (c) { c.classList.remove("active"); });
        b.classList.add("active");
        renderCards();
      });
      chips.append(b);
    });
  }

  // Risk of a country for the chosen disease (or overall if "All")
  function riskFor(c) {
    if (selectedDisease === "All") return c.risk;
    const d = c.diseases.find(function (x) { return x.disease === selectedDisease; });
    return d ? d.risk : "Low";
  }

  // ---- Hero numbers: how many countries are High / Medium / Low overall ----
  function renderStats() {
    const box = document.getElementById("heroStats");
    HR.clear(box);
    ["High", "Medium", "Low"].forEach(function (level) {
      const n = countries.filter(function (c) { return c.risk === level; }).length;
      box.append(HR.h("div", { class: "stat" }, HR.h("b", {}, n), HR.h("span", {}, level + " risk countries")));
    });
  }

  // ---- Cards ----
  function renderCards() {
    const text = search.value.trim().toLowerCase();
    const wanted = riskFilter.value;
    const list = countries.filter(function (c) {
      return (!text || c.country.toLowerCase().includes(text)) && (!wanted || riskFor(c) === wanted);
    });
    HR.clear(grid);
    if (!list.length) {
      grid.append(HR.h("p", { class: "muted" }, "No countries match your filters."));
      return;
    }
    // Show the highest risk first, then alphabetical
    const order = { High: 0, Medium: 1, Low: 2 };
    list.sort(function (a, b) { return order[riskFor(a)] - order[riskFor(b)] || a.country.localeCompare(b.country); });

    list.forEach(function (c) {
      const risk = riskFor(c);
      const minis = c.diseases.map(function (d) { return HR.badge(d.risk, d.disease); });
      const card = HR.h("button", { class: "country-card " + risk, type: "button", "aria-label": c.country + ", " + risk + " risk" },
        HR.h("div", { class: "top" },
          HR.h("span", { class: "name" }, c.country),
          HR.h("span", {}, HR.h("i", { class: "dot " + risk }), " ", HR.badge(risk))),
        HR.h("div", { class: "sub" }, c.continent + " - population " + HR.short(c.population)),
        HR.h("div", { class: "mini-diseases" }, minis));
      card.addEventListener("click", function () { openPanel(c.country, selectedDisease); });
      grid.append(card);
    });
  }
  search.addEventListener("input", renderCards);
  riskFilter.addEventListener("change", renderCards);

  // ---- Side panel ----
  function openPanel(name, preferDisease) {
    lastFocused = document.activeElement;
    document.getElementById("panelTitle").textContent = name;
    HR.clear(document.getElementById("panelRisk"));
    HR.clear(document.getElementById("panelTabs"));
    const body = document.getElementById("panelBody");
    HR.clear(body);
    body.append(HR.h("p", { class: "loading" }, "Loading..."));
    panel.classList.add("open");
    backdrop.classList.add("show");
    panel.setAttribute("aria-hidden", "false");
    document.getElementById("panelClose").focus();

    HR.getJSON("/api/country/" + encodeURIComponent(name))
      .then(function (data) { showCountry(data, preferDisease); })
      .catch(function (err) { HR.message(body, "Could not load details. " + err.message, "bad"); });
  }

  function closePanel() {
    panel.classList.remove("open");
    backdrop.classList.remove("show");
    panel.setAttribute("aria-hidden", "true");
    if (lastFocused) lastFocused.focus();
  }
  document.getElementById("panelClose").addEventListener("click", closePanel);
  backdrop.addEventListener("click", closePanel);
  document.addEventListener("keydown", function (e) { if (e.key === "Escape") closePanel(); });

  function showCountry(data, preferDisease) {
    const tabs = document.getElementById("panelTabs");
    const riskBox = document.getElementById("panelRisk");
    HR.clear(riskBox);
    riskBox.append(HR.badge(data.risk, "Overall: " + data.risk + " risk"),
      HR.h("span", { class: "muted small" }, "  Data week " + data.data_date + (data.sample_data ? " (sample)" : "")));

    // Show the disease with the most cases first, unless the user chose a disease chip
    let current = data.diseases.find(function (d) { return d.disease === preferDisease; }) || data.diseases[0];

    function drawTabs() {
      HR.clear(tabs);
      data.diseases.forEach(function (d) {
        const t = HR.h("button", { class: "tab" + (d === current ? " active" : ""), type: "button", role: "tab" }, d.disease);
        t.addEventListener("click", function () { current = d; drawTabs(); drawBody(); });
        tabs.append(t);
      });
    }

    function drawBody() {
      const body = document.getElementById("panelBody");
      HR.clear(body);
      const chartBox = HR.h("div", { class: "loading" }, "Loading forecast...");
      body.append(
        HR.h("h3", {}, current.disease, " ", HR.badge(current.risk)),
        HR.h("div", { class: "facts" },
          fact(HR.fmt(current.cases_4w), "cases, last 4 weeks"),
          fact((current.growth_pct > 0 ? "+" : "") + current.growth_pct + "%", "2-week change"),
          fact(current.cases_per_100k, "per 100,000 people")),
        HR.h("h3", {}, "Case trend and forecast"),
        chartBox,
        HR.h("div", { class: "advisory" }, HR.h("strong", {}, "Travel advisory: "), current.advisory),
        HR.h("p", { class: "small muted", style: "margin-top:12px" },
          "Learn more: ", HR.h("a", { href: "/disease/" + (current.disease === "COVID-19" ? "covid-19" : current.disease.toLowerCase()) }, current.disease + " information page")));

      // The forecast comes from a separate API call
      HR.getJSON("/api/forecast/" + encodeURIComponent(data.country) + "?disease=" + encodeURIComponent(current.disease))
        .then(function (f) {
          const holder = HR.h("div", {});
          chartBox.replaceWith(holder);
          HR.drawChart(holder, f.history, f.forecast);
        })
        .catch(function () {
          // Fall back to the trend we already have, without forecast
          const holder = HR.h("div", {});
          chartBox.replaceWith(holder);
          HR.drawChart(holder, current.trend, []);
        });
    }

    function fact(value, label) {
      return HR.h("div", { class: "fact" }, HR.h("b", {}, value), HR.h("span", {}, label));
    }

    drawTabs();
    drawBody();
  }
})();
