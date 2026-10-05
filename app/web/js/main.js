// The site shell: sidebar navigation, hash routing, theme switch, and the study data every page reads.
// The site tells one story: Home, eight chapters (story.js), then the paper and materials.
import { h } from "./ui.js";
import { disposeCharts, rerenderCharts } from "./charts.js";
import { CHAPTERS } from "./story.js";
import { home, question, study } from "./opening.js";
import { where, language, wider } from "./findings.js";
import { prediction } from "./prediction.js";
import { model } from "./model.js";
import { meaning, paper } from "./closing.js";

const RENDER = { home, question, study, where, language, wider, prediction, model, meaning, paper };
const PAGES = [
  { id: "home", no: "⌂", label: "Home" },
  ...CHAPTERS.map((c, i) => ({ id: c.id, no: String(i + 1), label: c.title, group: "The story", cta: c.id === "model" })),
  { id: "paper", no: "¶", label: "Paper & materials", group: "Read more" },
].map((p) => ({ ...p, render: RENDER[p.id], noData: p.id === "model" }));

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
  document.title = (page.id === "home" ? "" : page.label + " · ") + "Is Generative AI Displacing Arabic?";
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
// old addresses from before the site was a story
const MOVED = { overview: "home", profile: "where", hypotheses: "meaning", predictors: "language", context: "wider", sample: "study",
  ml: "prediction", oversampling: "prediction", research: "paper", method: "study" };
window.addEventListener("hashchange", () => {
  const id = location.hash.replace(/^#/, "");
  if (MOVED[id]) { history.replaceState(null, "", "#" + MOVED[id]); }
  window.scrollTo(0, 0);
  show();
});
{ const id = location.hash.replace(/^#/, ""); if (MOVED[id]) history.replaceState(null, "", "#" + MOVED[id]); }

buildNav();
show();
