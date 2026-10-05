// The paper: read, download, cite; what it contributes; results at a glance; the questionnaire.
// paper.json is written by paper/publish.py when the site is deployed, so this page follows the committed paper.
import { h, f, sg, pct, fp, pe, pageHead, kpis, card, grid, table, flag, link } from "./ui.js";

const BASE = "research/";

function size(n) { return n >= 1e6 ? `${(n / 1e6).toFixed(1)} MB` : `${Math.round(n / 1e3)} kB`; }
function day(iso) { return iso ? new Date(iso).toLocaleDateString("en-GB", { year: "numeric", month: "long", day: "numeric" }) : ""; }

export async function research(main, S) {
  main.append(pageHead("R1 · Research", "The paper",
    "The study is reported in a six-page paper in the IEEE conference format. Read it, download it or cite it here; the questionnaire is at the bottom of the page."));
  let paper;
  try {
    const r = await fetch(BASE + "paper.json");
    if (!r.ok) throw new Error(r.status);
    paper = await r.json();
  } catch {
    main.append(h("section", { class: "card" }, h("div", { class: "cardmsg" }, "The paper hasn’t been published on this server yet.")));
    return;
  }
  const A = S.hypotheses.family_a, B = S.hypotheses.family_b, usable = S.ml.targets.filter((t) => t.usability.usable);
  const ws = S.rq1.domains.find((d) => d.id === "WorkStudy");
  main.append(kpis([
    { n: S.sample.n, l: "Lebanese Arabic–English bilinguals surveyed" },
    { n: "8", l: "areas of daily life rated" },
    { n: "9", l: "confirmatory tests in two families" },
    { n: S.ml.targets.length, l: "outcomes modelled with cross-validated machine learning" },
    { n: usable.length, l: "usable prediction models" },
  ]));

  const facts = [paper.pages ? `${paper.pages} pages` : null, paper.updated ? `updated ${day(paper.updated)}` : null,
                 paper.commit ? `version ${paper.commit}` : null].filter(Boolean).join(" · ");
  const paperCard = card({ title: "The paper", sub: facts, span2: true },
    h("h4", { class: "papertitle" }, paper.title),
    h("p", { class: "paperby" }, `${paper.author} · ${paper.affiliation}`),
    h("p", { class: "abstract" }, paper.abstract),
    h("p", { class: "keywords" }, h("b", null, "Index terms: "), paper.keywords.join(", ")),
    h("div", { class: "paperactions" },
      h("a", { class: "btn", href: BASE + paper.pdf, target: "_blank", rel: "noopener" }, `Read the paper (PDF, ${size(paper.bytes)})`),
      h("a", { class: "btn ghost", href: BASE + paper.pdf, download: paper.pdf }, "Download"),
      h("a", { class: "btn ghost", href: BASE + paper.bib, download: paper.bib }, "Cite (BibTeX)")));

  const contrib = card({ title: "What the paper contributes", span2: true },
    h("ol", { class: "findings" },
      h("li", null, h("b", null, "A first look at AI and Arabic use. "),
        "To our knowledge, the first study to ask Arabic speakers whether they attribute changes in their own Arabic use to generative AI, area by area."),
      h("li", null, h("b", null, "A domain profile that follows theory. "),
        `The reported decrease is largest in work or study (${pct(ws.less)} less, ${pct(ws.more)} more) and smallest with family and in religion, in the order domain theory predicts.`),
      h("li", null, h("b", null, "Language, not amount. "),
        `Writing to AI in English predicts the reported decrease in every specification (b = ${f(B.H3b.b)}, Holm p ${fp(B.H3b.p_holm)}); how much people use AI does not.`),
      h("li", null, h("b", null, "Prediction judged by criteria fixed in advance. "),
        "Three linear models identify who reports a decrease in formal areas, work or study and self-talk; AI-use answers add no significant gain over background."),
      h("li", null, h("b", null, "A worked warning about oversampling. "),
        "Applied before the train–test split, oversampling produces spurious accuracy that grows with the amount of synthetic data; applied correctly, it adds nothing.")));

  const glance = card({ title: "Results at a glance", sub: "From the paper’s confirmatory tests and machine learning. Details on the findings pages." },
    table([
      { label: "Question", get: (x) => x[0], class: "strong" },
      { label: "Result", get: (x) => x[1] },
      { label: "Verdict", get: (x) => x[2] },
    ], [
      ["H1  Less Fusha, less Arabic at work/study", `${A.H1a.less} vs ${A.H1a.more}; ${A.H1b.less} vs ${A.H1b.more}`, flag("supported", "good")],
      ["H2a  Work/study > personal > family", `Page p ${fp(A.H2a.page_p)}`, flag("supported", "good")],
      ["H2b  Fusha > dialect areas", `p ${pe(A.H2b.p_holm)}`, flag("not supported")],
      ["H3  AI use predicts the decrease", `English share b = ${f(B.H3b.b)}`, flag("supported", "good")],
      ["H4  Decrease and difficulty", `p ${pe(B.H4.p)}`, flag("not supported")],
      ["H5  Mediation", "interval only just excludes 0", flag("borderline", "mid")],
      ["RQ4  AI use improves prediction", `ΔAUC ${sg(S.ml.targets.find((t) => t.id === "AnyFormalLoss").delta_ai.d)}`, flag("not supported")],
    ]));
  const downloads = card({ title: "Downloads and sources" },
    h("ul", { class: "srclist" },
      h("li", null, h("a", { href: BASE + paper.pdf, download: paper.pdf }, "The paper"), ` (PDF, ${paper.pages || "?"} pages)`),
      h("li", null, h("a", { href: BASE + paper.bib, download: paper.bib }, "BibTeX entry")),
      h("li", null, h("a", { href: "data/study.json", download: "genai-arabic-study-results.json" }, "Every number on this site"),
        " (JSON, group-level results only)"),
      h("li", null, link("method", "How the study was done"), ": design, measures, tests"),
      h("li", null, link("model", "Try the model"), ": the three usable models, live")),
    h("p", { class: "muted" }, "Individual responses are not shared: participants were told that answers would be reported only as group results."));

  main.append(paperCard, contrib, grid(glance, downloads), questionnaire(S.questionnaire));
}

function questionnaire(Q) {
  let n = 0;
  const sections = Q.map((sec) => h("details", { class: "qsec" },
    h("summary", null, h("span", null, sec.title.en), h("span", { class: "ar", lang: "ar", dir: "rtl" }, sec.title.ar)),
    sec.items.map((it) => {
      if (it.type === "text") {
        return h("div", { class: "qitem note" }, h("p", null, it.text.en), h("p", { class: "ar", lang: "ar", dir: "rtl" }, it.text.ar));
      }
      n += 1;
      return h("div", { class: "qitem" },
        h("div", { class: "qpair" },
          h("div", null, h("span", { class: "no" }, String(n).padStart(2, "0")), h("b", null, it.q.en)),
          h("div", { class: "ar", lang: "ar", dir: "rtl" }, h("b", null, it.q.ar))),
        it.note ? h("div", { class: "qpair muted" }, h("div", null, it.note.en), h("div", { class: "ar", lang: "ar", dir: "rtl" }, it.note.ar)) : null,
        it.rows ? h("ul", { class: "qrows" }, it.rows.map((r) => h("li", { class: "qpair" }, h("span", null, r.en), h("span", { class: "ar", lang: "ar", dir: "rtl" }, r.ar)))) : null,
        it.options ? h("div", { class: "qopts" },
          it.rows ? h("span", { class: "muted" }, "Each row: ") : null,
          it.options.map((o) => h("span", { class: "chip static" }, o.en, h("span", { class: "ar-inline", lang: "ar" }, " · " + o.ar)))) : null);
    })));
  return card({ title: "The questionnaire", span2: true,
    sub: "Every question and option as fielded: the Arabic wording is the instrument, the English is the source wording. Open a section to read it." },
    h("div", { class: "qsecs" }, sections));
}
