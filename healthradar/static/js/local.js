/* local.js - Local Mode: find the user's state with the browser location,
   or let them choose it from a drop-down if location is blocked or unavailable. */

(function () {
  const statusBox = document.getElementById("locStatus");
  const select = document.getElementById("stateSelect");
  const result = document.getElementById("localResult");
  const locBtn = document.getElementById("useLocation");

  function setStatus(text, type) {
    statusBox.className = "status " + (type || "");
    statusBox.textContent = text;
  }

  // 1) Fill the state drop-down (this is also the fallback)
  HR.getJSON("/api/states")
    .then(function (data) {
      HR.clear(select);
      select.append(HR.h("option", { value: "" }, "Choose a state"));
      data.states.forEach(function (s) {
        select.append(HR.h("option", { value: s.state }, s.state));
      });
    })
    .catch(function (err) {
      HR.clear(select);
      select.append(HR.h("option", { value: "" }, "Could not load states"));
      setStatus("Could not load the list of states. " + err.message, "bad");
    });

  select.addEventListener("change", function () {
    if (select.value) loadState({ state: select.value }, false);
  });
  locBtn.addEventListener("click", askLocation);

  // 2) Ask the browser for the location
  function askLocation() {
    if (!("geolocation" in navigator)) {
      setStatus("Your browser cannot share location. Please choose your state below.", "warn");
      return;
    }
    setStatus("Asking your browser for your location...");
    navigator.geolocation.getCurrentPosition(
      function (pos) {
        loadState({ lat: pos.coords.latitude.toFixed(3), lon: pos.coords.longitude.toFixed(3) }, true);
      },
      function (err) {
        // Permission denied, timeout, or no signal: use the drop-down instead
        const reason = err.code === 1 ? "Location permission was denied."
          : err.code === 3 ? "Finding your location took too long."
          : "Your location is not available.";
        setStatus(reason + " Please choose your state from the list.", "warn");
      },
      { timeout: 10000, maximumAge: 600000 }
    );
  }

  // 3) Load data for a state
  function loadState(params, fromLocation) {
    setStatus("Loading local data...");
    HR.clear(result);
    const query = new URLSearchParams(params).toString();
    HR.getJSON("/api/local?" + query)
      .then(function (data) {
        setStatus(fromLocation
          ? "Nearest state found: " + data.state + " (approximate). Not right? Choose another state below."
          : "Showing data for " + data.state + ".");
        if (select.value !== data.state) select.value = data.state;
        show(data);
      })
      .catch(function (err) {
        // For example: the user is outside the supported area
        setStatus(err.message, "warn");
      });
  }

  // 4) Draw the results
  function show(data) {
    HR.clear(result);
    const top = data.diseases[0]; // the API sorts by most cases first
    let chartHolder = HR.h("div", { class: "loading" }, "Loading forecast...");
    const forecastSelect = HR.h("select", { "aria-label": "Disease for the forecast" },
      data.diseases.map(function (d) { return HR.h("option", { value: d.disease }, d.disease); }));

    result.append(
      HR.h("div", { class: "card", style: "margin-top:16px" },
        HR.h("h2", {}, data.state, " ", HR.badge(data.risk, data.risk + " overall risk")),
        HR.h("p", { class: "muted small" },
          "Latest data week: " + data.data_date + (data.sample_data ? " (SAMPLE data)" : "")),
        top ? HR.h("p", {}, "Most cases in the last 4 weeks: ", HR.h("strong", {}, top.disease), " (" + HR.fmt(top.cases_4w) + " cases).") : null
      ),
      HR.h("h3", { style: "margin-top:18px" }, "Diseases ranked by cases"),
      HR.h("div", { class: "result-grid" }, data.diseases.map(function (d, i) {
        const card = HR.diseaseCard(d);
        card.prepend(HR.h("div", { class: "small muted" }, "#" + (i + 1)));
        return card;
      })),
      HR.h("div", { class: "card", style: "margin-top:14px" },
        HR.h("h3", {}, "Recent weekly records"),
        HR.h("div", { class: "table-wrap" }, buildTable(data))
      ),
      HR.h("div", { class: "card", style: "margin-top:14px" },
        HR.h("div", { class: "row", style: "display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;align-items:center" },
          HR.h("h3", { style: "margin:0" }, "Forecast"), forecastSelect),
        chartHolder
      )
    );

    function drawForecast() {
      const holder = HR.h("div", { class: "loading" }, "Loading forecast...");
      chartHolder.replaceWith(holder);
      HR.getJSON("/api/forecast/" + encodeURIComponent(data.state) + "?disease=" + encodeURIComponent(forecastSelect.value))
        .then(function (f) {
          HR.drawChart(holder, f.history, f.forecast);
          holder.classList.remove("loading");
        })
        .catch(function (err) { HR.message(holder, "Could not load the forecast. " + err.message, "warn"); });
      // keep a reference so the next redraw replaces this holder
      chartHolder = holder;
    }
    forecastSelect.addEventListener("change", drawForecast);
    drawForecast();
  }

  function buildTable(data) {
    const names = ["Dengue", "Influenza", "COVID-19"];
    const head = HR.h("tr", {}, HR.h("th", {}, "Week ending"), names.map(function (n) { return HR.h("th", {}, n); }));
    const rows = data.recent_records.map(function (r) {
      return HR.h("tr", {}, HR.h("td", {}, r.date),
        names.map(function (n) { return HR.h("td", {}, r[n] === null ? "-" : HR.fmt(r[n])); }));
    });
    return HR.h("table", {}, HR.h("thead", {}, head), HR.h("tbody", {}, rows));
  }

  // Start by trying the location automatically
  askLocation();
})();
