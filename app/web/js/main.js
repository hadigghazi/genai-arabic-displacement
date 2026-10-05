// The site shell: sidebar navigation, hash routing, theme switch, and the study data every page reads.
import { h } from "./ui.js";
import { disposeCharts, rerenderCharts } from "./charts.js";
import { overview, profile, hypotheses, predictors, context, sample } from "./findings.js";
import { results, oversampling } from "./mlpages.js";
import { model } from "./model.js";
import { method } from "./about.js";
import { research } from "./research.js";

const PAGES = [
  { id: "overview", no: "–", label: "Overview", render: overview },
  { id: "profile", no: "01", label: "Where Arabic is used less", group: "Findings", render: profile },
  { id: "hypotheses", no: "02", label: "Hypotheses", group: "Findings", render: hypotheses },
  { id: "predictors", no: "03", label: "What goes with it", group: "Findings", render: predictors },
  { id: "context", no: "04", label: "Social media & life changes", group: "Findings", render: context },
  { id: "sample", no: "05", label: "Who took part", group: "Findings", render: sample },
  { id: "ml", no: "M1", label: "Prediction models", group: "Machine learning", render: results },
  { id: "oversampling", no: "M2", label: "Oversampling check", group: "Machine learning", render: oversampling },
  { id: "model", no: "★", label: "Try the model", group: "Machine learning", render: model, cta: true, noData: true },
  { id: "research", no: "R1", label: "The paper", group: "Research", render: research },
  { id: "method", no: "A", label: "How the study was done", group: "About", render: method },
];

const mainEl = document.getElementById("main");
const nav = document.getElementById("nav");
const sidebar = document.getElementById("sidebar");
const menubtn = document.getElementById("menubtn");
let data = null;

function loadData() {
  data = data || fetch("data/study.json").then((r) => { if (!r.ok) throw new Error(r.status); return r.json(); });
  return data;
}

function current() {
  const id = location.hash.replace(/^#/, "").split("?")[0];
  return PAGES.find((p) => p.id === id) || PAGES[0];
}

function buildNav() {
  let group = null;
  nav.replaceChildren(...PAGES.flatMap((p) => {
    const out = [];
    if (p.group && p.group !== group) out.push(h("div", { class: "navsec" }, p.group));
    group = p.group;
    out.push(h("a", { class: "navbtn" + (p.cta ? " cta" : ""), href: "#" + p.id, "data-id": p.id },
      h("span", { class: "no" }, p.no), p.label));
    return out;
  }));
}

async function show() {
  const page = current();
  for (const a of nav.querySelectorAll(".navbtn")) {
    const on = a.dataset.id === page.id;
    a.classList.toggle("active", on);
    if (on) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
  }
  sidebar.classList.remove("open");
  menubtn.setAttribute("aria-expanded", "false");
  disposeCharts();
  mainEl.replaceChildren(h("div", { class: "skel", style: { height: "120px", marginBottom: "18px" } }), h("div", { class: "skel", style: { height: "320px" } }));
  document.title = (page.id === "overview" ? "" : page.label + " · ") + "Generative AI and Arabic";
  try {
    const S = page.noData ? null : await loadData();
    if (current() !== page) return;                       // the reader moved on while this loaded
    mainEl.replaceChildren();
    await page.render(mainEl, S);
  } catch (e) {
    mainEl.replaceChildren(h("div", { class: "cardmsg error", role: "alert" }, "This page could not be loaded. Please refresh."));
    console.error(e);
  }
}

// ------------------------------------------------------------------ theme: system -> light -> dark
const themebtn = document.getElementById("themebtn");
function getTheme() { try { return localStorage.getItem("arabic-ai-theme") || "system"; } catch { return "system"; } }
function applyTheme(t) {
  if (t === "system") document.documentElement.removeAttribute("data-theme");
  else document.documentElement.setAttribute("data-theme", t);
  themebtn.textContent = t;
  try { localStorage.setItem("arabic-ai-theme", t); } catch { /* private mode */ }
  rerenderCharts();
}
themebtn.addEventListener("click", () => applyTheme({ system: "light", light: "dark", dark: "system" }[getTheme()]));
window.matchMedia("(prefers-color-scheme: dark)").addEventListener("change", rerenderCharts);
applyTheme(getTheme());

menubtn.addEventListener("click", () => {
  const open = !sidebar.classList.contains("open");
  sidebar.classList.toggle("open", open);
  menubtn.setAttribute("aria-expanded", String(open));
});
window.addEventListener("hashchange", () => { window.scrollTo(0, 0); show(); });

buildNav();
show();
