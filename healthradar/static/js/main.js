/* main.js - small helpers shared by all pages. */

const HR = {};

// Get JSON from the server. Throws an Error with a readable message if something goes wrong.
HR.getJSON = async function (url) {
  let response;
  try {
    response = await fetch(url);
  } catch (err) {
    throw new Error("Could not reach the server. Check your connection and try again.");
  }
  let data = null;
  try {
    data = await response.json();
  } catch (err) {
    throw new Error("The server sent an unexpected reply.");
  }
  if (!response.ok) {
    throw new Error((data && data.error) || "Request failed.");
  }
  return data;
};

// Create an element safely: HR.h("div", {class: "x"}, "text", otherElement)
// Text is added as plain text (never as HTML), which keeps the page safe.
HR.h = function (tag, attrs, ...children) {
  const node = document.createElement(tag);
  for (const [key, value] of Object.entries(attrs || {})) {
    if (key === "class") node.className = value;
    else if (key.startsWith("on") && typeof value === "function") node.addEventListener(key.slice(2), value);
    else if (value !== false && value !== null && value !== undefined) node.setAttribute(key, value);
  }
  for (const child of children.flat()) {
    if (child === null || child === undefined || child === false) continue;
    node.append(child.nodeType ? child : document.createTextNode(String(child)));
  }
  return node;
};

// Remove everything inside an element
HR.clear = function (node) {
  while (node.firstChild) node.removeChild(node.firstChild);
};

// 12345 -> "12,345"
HR.fmt = function (n) {
  return Number(n).toLocaleString("en-US");
};

// Small coloured badge, e.g. HR.badge("High")
HR.badge = function (risk, text) {
  return HR.h("span", { class: "badge " + risk }, text || risk);
};

// Show a message box inside a container. type: "" | "warn" | "bad"
HR.message = function (container, text, type) {
  HR.clear(container);
  container.append(HR.h("div", { class: "status " + (type || "") }, text));
};

// Mobile menu button + highlight the current page link
document.addEventListener("DOMContentLoaded", function () {
  const toggle = document.getElementById("navToggle");
  const nav = document.getElementById("mainNav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      const open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }
  document.querySelectorAll("#mainNav a").forEach(function (a) {
    if (a.getAttribute("href") === window.location.pathname) a.classList.add("active");
  });
});

// A result card for one disease (used by Travel Check and Local Mode).
// d = {disease, risk, cases_4w, growth_pct, cases_per_100k, advisory?}
HR.diseaseCard = function (d) {
  const slug = d.disease === "COVID-19" ? "covid-19" : d.disease.toLowerCase();
  return HR.h("div", { class: "card disease-result " + d.risk },
    HR.h("div", { class: "row" }, HR.h("h3", {}, d.disease), HR.badge(d.risk, d.risk + " risk")),
    HR.h("div", { class: "facts" },
      HR.h("div", { class: "fact" }, HR.h("b", {}, HR.fmt(d.cases_4w)), HR.h("span", {}, "cases, last 4 weeks")),
      HR.h("div", { class: "fact" }, HR.h("b", {}, (d.growth_pct > 0 ? "+" : "") + d.growth_pct + "%"), HR.h("span", {}, "2-week change")),
      HR.h("div", { class: "fact" }, HR.h("b", {}, d.cases_per_100k), HR.h("span", {}, "per 100,000"))),
    d.advisory ? HR.h("div", { class: "advisory" }, d.advisory) : null,
    HR.h("p", { class: "small", style: "margin:10px 0 0" },
      HR.h("a", { href: "/disease/" + slug }, "About " + d.disease + " and prevention")));
};
