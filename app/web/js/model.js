// The live model: the survey's 12 questions in English or Arabic, scored by POST api/predict.
// State lives at module level, so answers survive switching pages or language.
import { h, f, pct, card, grid, table } from "./ui.js";
import { chapterHead, storyNav } from "./story.js";

const T = {
  en: {
    formTitle: "Your answers", formSub: "The same questions, with the same options, as the survey.",
    multi: "tick all that apply", submit: "See the results", reset: "Clear",
    missing: "Please answer every question marked in red.", failed: "The model could not be reached. Please try again.",
    resultsTitle: "Results", resultsSub: "Each bar places you between people who did not report the decrease and people who did. The score orders people; it is not a percentage chance.",
    likely: "Likely to report this", unlikely: "Unlikely to report this", lower: "did not report it", higher: "reported it",
    moved: "What moved your score most", raises: "raises", lowers: "lowers",
    tested: (m) => `On people it was not trained on, it ranked someone who reported this above someone who did not ${pct(m.cv.auc)} of the time and classified ${pct(m.cv.balanced_accuracy)} correctly (balanced). ${m.n_yes} of ${m.n_yes + m.n_no} respondents reported it.`,
  },
  ar: {
    formTitle: "إجاباتك", formSub: "الأسئلة نفسها والخيارات نفسها كما في الاستبيان.",
    multi: "اختر كل ما ينطبق", submit: "اعرض النتائج", reset: "مسح",
    missing: "يرجى الإجابة عن كل سؤال مظلَّل بالأحمر.", failed: "تعذّر الوصول إلى النموذج. يرجى المحاولة مرة أخرى.",
    resultsTitle: "النتائج", resultsSub: "يضعك كل شريط بين من لم يُفيدوا بهذا التراجع ومن أفادوا به. النتيجة ترتّب الأشخاص، وليست نسبة احتمال.",
    likely: "يُرجَّح أن تُفيد بهذا", unlikely: "لا يُرجَّح أن تُفيد بهذا", lower: "لم يُفيدوا به", higher: "أفادوا به",
    moved: "أكثر ما أثّر في نتيجتك", raises: "يرفع", lowers: "يخفض",
    tested: (m) => `عند اختباره على أشخاص لم يُدرَّب عليهم، رتّب من أفاد بهذا فوق من لم يُفد به في ${pct(m.cv.auc)} من الحالات، وصنّف ${pct(m.cv.balanced_accuracy)} تصنيفاً صحيحاً (دقة متوازنة). أفاد به ${m.n_yes} من أصل ${m.n_yes + m.n_no} مشاركاً.`,
  },
};
const NONE_OF_THESE = { Events: 6 };   // ticking "None of these" clears the other events, and vice versa
const state = { lang: "en", answers: {}, result: null, error: "", card: null };

function initialLang() {
  try { const s = localStorage.getItem("arabic-ai-model-lang"); if (s === "en" || s === "ar") return s; } catch { /* storage blocked */ }
  return (navigator.language || "").toLowerCase().startsWith("ar") ? "ar" : "en";
}
state.lang = initialLang();

export async function model(main) {
  main.append(
    chapterHead("model", "Answer the survey’s 12 questions about yourself and your AI use, and see whether people with answers like yours reported using less Arabic because of AI. "
      + "The three usable models from Chapter 6 score you. Your answers are scored on the spot and never stored."));
  const holder = h("div");
  main.append(holder, storyNav("model"));
  if (!state.card) {
    holder.append(h("div", { class: "skel", style: { height: "420px" } }));
    try {
      const r = await fetch("api/model");
      if (!r.ok) throw new Error(r.status);
      state.card = await r.json();
    } catch {
      holder.replaceChildren(h("div", { class: "cardmsg error" }, T.en.failed));
      return;
    }
  }
  render(holder);
}

function render(holder) {
  const t = T[state.lang];
  const c = state.card;
  const seg = h("div", { class: "segtoggle", role: "radiogroup", "aria-label": "Language" },
    [["en", "English"], ["ar", "العربية"]].map(([k, l]) => h("button", { type: "button", role: "radio", "aria-checked": String(state.lang === k),
      class: state.lang === k ? "on" : "", onclick: () => { state.lang = k; try { localStorage.setItem("arabic-ai-model-lang", k); } catch { /* blocked */ } render(holder); } }, l)));
  const qlist = h("div", { class: "qlist" }, c.questions.map((q, i) => question(q, i, holder)));
  const err = h("span", { class: "formerror", role: "alert" }, state.error ? t[state.error] : "");
  const form = h("form", { novalidate: true, onsubmit: (e) => { e.preventDefault(); submit(holder); } },
    qlist,
    h("div", { class: "formfoot" },
      h("button", { type: "submit", class: "btn" }, t.submit),
      h("button", { type: "button", class: "btn ghost", onclick: () => { state.answers = {}; state.result = null; state.error = ""; render(holder); } }, t.reset),
      err));
  const formCard = card({ title: t.formTitle, sub: t.formSub, span2: true });
  formCard.querySelector(".cardhead").append(seg);
  const wrap = h("div", { class: "modelwrap", dir: state.lang === "ar" ? "rtl" : "ltr", lang: state.lang }, form);
  formCard.body.append(wrap);
  formCard.querySelector("h3").setAttribute("lang", state.lang);
  const parts = [formCard];
  if (state.result) parts.push(resultsCard());
  parts.push(aboutCard());
  holder.replaceChildren(...parts);
  if (state.scrollToResults) {
    state.scrollToResults = false;
    document.getElementById("model-results")?.scrollIntoView({ behavior: "smooth", block: "start" });
  }
}

function question(q, i, holder) {
  const t = T[state.lang];
  const missing = state.missing && state.missing.has(q.code);
  return h("div", { class: "qblock" + (missing ? " missing" : ""), id: "q-" + q.code },
    h("div", { class: "qhead" }, h("span", { class: "no" }, String(i + 1).padStart(2, "0")),
      h("span", null, q.q[state.lang].replace(/\s*[(（]tick all that apply[)）]|\s*\(اختر كل ما ينطبق\)/, ""),
        q.type === "check" ? h("span", { class: "multi" }, " · " + t.multi) : null)),
    h("div", { class: "chipgroup" }, q.options.map((o) => {
      const id = `${q.code}-${o.code}`;
      const checked = q.type === "check" ? (state.answers[q.code] || []).includes(o.code) : state.answers[q.code] === o.code;
      return h("label", { class: "opt", for: id },
        h("input", { type: q.type === "check" ? "checkbox" : "radio", name: q.code, id, value: o.code, checked,
          onchange: (e) => onChange(q, o.code, e.target.checked, holder) }),
        h("span", { class: "chip" }, o[state.lang]));
    })));
}

function onChange(q, code, checked, holder) {
  if (q.type === "single") {
    state.answers[q.code] = code;
  } else {
    let list = (state.answers[q.code] || []).filter((c) => c !== code);
    if (checked) {
      const none = NONE_OF_THESE[q.code];
      if (none !== undefined) list = code === none ? [] : list.filter((c) => c !== none);
      list.push(code);
    }
    state.answers[q.code] = list;
  }
  if (state.missing) state.missing.delete(q.code);
  if (q.type === "check" && NONE_OF_THESE[q.code] !== undefined) render(holder);
  else document.getElementById("q-" + q.code)?.classList.remove("missing");
}

async function submit(holder) {
  const c = state.card;
  state.missing = new Set(c.questions.filter((q) => q.type === "single" && state.answers[q.code] === undefined).map((q) => q.code));
  if (state.missing.size) {
    state.error = "missing";
    render(holder);
    document.getElementById("q-" + [...state.missing][0])?.scrollIntoView({ behavior: "smooth", block: "center" });
    return;
  }
  const body = Object.fromEntries(c.questions.map((q) => [q.code, q.type === "check" ? (state.answers[q.code] || []) : state.answers[q.code]]));
  try {
    const r = await fetch("api/predict", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
    if (!r.ok) throw new Error(r.status);
    state.result = await r.json();
    state.error = "";
    state.scrollToResults = true;
  } catch {
    state.error = "failed";
  }
  render(holder);
}

function resultsCard() {
  const t = T[state.lang];
  const byId = Object.fromEntries(state.card.models.map((m) => [m.id, m]));
  const box = card({ title: t.resultsTitle, sub: t.resultsSub, span2: true, id: "model-results" });
  box.querySelector("h3").setAttribute("lang", state.lang);
  box.body.append(h("div", { class: "modelwrap", dir: state.lang === "ar" ? "rtl" : "ltr", lang: state.lang },
    h("div", { class: "results" }, state.result.results.map((r) => {
      const m = byId[r.id];
      const mark = h("div", { class: "mark" });
      mark.style.insetInlineStart = (100 * r.score).toFixed(1) + "%";
      return h("article", { class: "result" + (r.likely ? " likely" : "") },
        h("h4", null, r.label[state.lang]),
        h("span", { class: "verdict" }, r.likely ? t.likely : t.unlikely),
        h("div", null, h("div", { class: "meter" }, h("div", { class: "mid" }), mark),
          h("div", { class: "ends", style: { marginTop: "8px" } }, h("span", null, t.lower), h("span", null, t.higher))),
        h("div", null, h("div", { class: "muted", style: { fontWeight: 600, marginBottom: "4px" } }, t.moved),
          h("ul", { class: "moves" }, r.contributions.slice(0, 3).map((x) => h("li", { class: x.contribution >= 0 ? "up" : "down" },
            h("span", { class: "arrow" }, x.contribution >= 0 ? "▲" : "▼"),
            h("span", null, state.card.feature_text[x.feature][state.lang]),
            h("span", { class: "dir" }, x.contribution >= 0 ? t.raises : t.lowers))))),
        h("p", { class: "fine" }, t.tested(m)));
    }))));
  return box;
}

function aboutCard() {
  const ms = state.card.models;
  return grid(
    card({ title: "How the models were tested", sub: "Cross-validated on the 105 respondents (repeated 10×5-fold), then fitted once on everyone." },
      table([
        { label: "Outcome", get: (m) => m.label.en, class: "strong" },
        { label: "AUC", num: true, get: (m) => f(m.cv.auc) },
        { label: "Over 10 splits", num: true, get: (m) => `${f(m.cv.auc_splits.mean)} (${f(m.cv.auc_splits.min)}–${f(m.cv.auc_splits.max)})` },
        { label: "Balanced acc.", num: true, get: (m) => f(m.cv.balanced_accuracy) },
        { label: "Holm p", num: true, get: (m) => f(m.cv.perm_p_holm, 3) },
      ], ms)),
    card({ title: "What the score means" },
      h("div", { class: "prose" },
        h("p", null, "Each model is a logistic regression on the 12 answers. The score places you among the survey’s respondents; at 0.5 or above, people with answers like yours mostly reported the decrease."),
        h("p", null, "It predicts what people ", h("b", null, "report"), ", not how their Arabic actually changed, and it was validated within this sample only."),
        h("p", null, "Answers about AI use did not make the models significantly more accurate than background answers alone."))));
}
