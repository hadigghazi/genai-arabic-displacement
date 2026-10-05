// Chapter 8 (what it means) and the closing page (the paper, downloads, references).
import { h, f, sg, pct, fp, pe, kpis, card, grid, table, flag } from "./ui.js";
import { chapterHead, sec, prose, takeaway, sources, storyNav } from "./story.js";

const BASE = "research/";
function size(n) { return n >= 1e6 ? `${(n / 1e6).toFixed(1)} MB` : `${Math.round(n / 1e3)} kB`; }
function day(iso) { return iso ? new Date(iso).toLocaleDateString("en-GB", { year: "numeric", month: "long", day: "numeric" }) : ""; }
const REF_GROUPS = [
  ["AI and language", ["kubrak2025", "sallam2024", "saarela2026", "bouzayenne2026"]],
  ["Arabic, English and language shift", ["albataineh2021", "masri2019", "mustafawi2022", "mehio2026", "alghamdi2018", "fishman1965", "fishman1972", "ferguson1959", "hargittai2002"]],
  ["First-language attrition", ["chaouch2025", "gallo2025", "aycicegi2015"]],
  ["Measuring perceived change", ["wirtz2025", "schwaba2023"]],
  ["Statistics", ["holm1979", "page1963", "long2000", "davidson2008", "hayes2022", "fritz2007", "firth1993", "dunn2014"]],
  ["Machine learning", ["nadeau2003", "chawla2002", "vandewiele2021", "santos2018", "pedregosa2011", "lemaitre2017"]],
  ["Software", ["seabold2010", "virtanen2020", "spss23"]],
];
const ch = (id, n, text) => h("a", { href: "#" + id }, text || `Chapter ${n}`);

// ------------------------------------------------------------------ chapter 8
export function meaning(main, S) {
  const A = S.hypotheses.family_a, B = S.hypotheses.family_b, r = S.rq1;
  const ws = r.domains.find((d) => d.id === "WorkStudy");
  const formal = S.ml.targets.find((t) => t.id === "AnyFormalLoss");
  const rows = [
    ["H1", "Less Fusha, less Arabic at work or study", `${A.H1a.less} vs ${A.H1a.more}; ${A.H1b.less} vs ${A.H1b.more}`, flag("supported", "good"), ch("where", 3)],
    ["H2a", "Work or study, then personal matters, then family", `Page p ${fp(A.H2a.page_p)}`, flag("supported", "good"), ch("where", 3)],
    ["H2b", "Larger for Fusha than for the dialect", `p ${pe(A.H2b.p_holm)}`, flag("not supported"), ch("where", 3)],
    ["H3", "AI use predicts the decrease", `through English only, b = ${f(B.H3b.b)}`, flag("supported", "good"), ch("language", 4)],
    ["H4", "The decrease goes with difficulty without AI", `p ${pe(B.H4.p)}`, flag("not supported"), ch("language", 4)],
    ["H5", "The decrease is the route to that difficulty", "interval only just excludes zero", flag("borderline", "mid"), ch("language", 4)],
    ["RQ4", "AI-use answers improve prediction", `ΔAUC ${sg(formal.delta_ai.d)}, not significant`, flag("not supported"), ch("prediction", 6)],
  ];
  main.append(
    chapterHead("meaning", "What the 105 answers add up to, how far they reach, and where the next study should go."),
    sec("The answer",
      takeaway("Lebanese bilinguals report that generative AI has reduced their Arabic, mainly at work or study, in writing and in Fusha, "
        + "and those who use AI in English report more of it."),
      h("ol", { class: "findings" },
        h("li", null, h("b", null, "Formal areas first. "), `${pct(ws.less)} report less Arabic in work or study and ${pct(ws.more)} more; family use and religion barely move, the order domain theory predicts. `, ch("where", 3, "Chapter 3")),
        h("li", null, h("b", null, "Language, not amount. "), "Writing to AI in English goes with the decrease in every check; how much people use AI, and the quality gap they perceive, do not. ", ch("language", 4, "Chapter 4")),
        h("li", null, h("b", null, "A shift that began before AI. "), "The same people report losing Arabic to social media; AI carries that shift from everyday communication into work, study and writing. ", ch("wider", 5, "Chapter 5")),
        h("li", null, h("b", null, "Predictable, moderately. "), "Three simple models identify who reports a decrease; answers about AI use add no significant gain over background. ", ch("prediction", 6, "Chapter 6")))),
    sec("The scorecard", card({ title: "Every hypothesis, and where to read about it", span2: true },
      table([
        { label: "", get: (x) => x[0], class: "strong" }, { label: "Prediction", get: (x) => x[1] },
        { label: "Result", get: (x) => x[2] }, { label: "Verdict", get: (x) => x[3] }, { label: "", get: (x) => x[4] },
      ], rows))),
    sec("What it suggests",
      h("div", { class: "evidence" },
        h("div", { class: "evcard accent" }, h("div", { class: "evlabel" }, "For AI tools"), h("div", { class: "evtitle" }, "Better Arabic may keep Arabic in use"),
          h("p", null, "If the language of AI use, rather than its amount, goes with the decrease, then how well AI works in Arabic matters for more than convenience. "
            + "This is a reading of the pattern, not a tested effect.")),
        h("div", { class: "evcard" }, h("div", { class: "evlabel" }, "For study and work"), h("div", { class: "evtitle" }, "Watch the formal, written uses"),
          h("p", null, "The decrease concentrates in work, study and writing, where AI now helps most. In a diglossic language, formal written work is where Fusha lives.")))),
    sec("How far it reaches, and what comes next",
      grid(
        card({ title: "What the study covers" }, prose(
          "The respondents are young, highly educated and often in computing, so the percentages describe this group rather than all Lebanese bilinguals.",
          "The study records the change people attribute to AI, rated looking back over two to four years. It shows what bilinguals experience, not a measured change in their Arabic.")),
        card({ title: "Next steps" }, h("ul", { class: "findings" },
          h("li", null, "Larger and more varied samples across the Arab region."),
          h("li", null, "Asking about AI and social media side by side, in alternating order, to see what each adds."),
          h("li", null, "Following the same people over time, and recording the language they actually use with AI."),
          h("li", null, "Testing the three models on new people."))))),
    storyNav("meaning"));
}

// ------------------------------------------------------------------ the paper and materials
export async function paper(main, S) {
  main.append(h("header", { class: "chapterhead" },
    h("div", { class: "eyebrow" }, "Read more"),
    h("h2", null, "Paper & materials"),
    h("p", { class: "lede" }, "The study in full: a six-page paper in the IEEE conference format, the numbers behind every chart, and the sources.")));
  let pp = null;
  try { const r = await fetch(BASE + "paper.json"); if (r.ok) pp = await r.json(); } catch { /* not published here */ }
  if (pp) {
    const facts = [pp.pages ? `${pp.pages} pages` : null, pp.updated ? `updated ${day(pp.updated)}` : null, pp.commit ? `version ${pp.commit}` : null].filter(Boolean).join(" · ");
    main.append(sec("The paper", card({ title: "Preprint", sub: facts, span2: true },
      h("h4", { class: "papertitle" }, pp.title),
      h("p", { class: "paperby" }, `${pp.author} · ${pp.affiliation}`),
      h("p", { class: "abstract" }, pp.abstract),
      h("p", { class: "keywords" }, h("b", null, "Index terms: "), pp.keywords.join(", ")),
      h("div", { class: "paperactions" },
        h("a", { class: "btn", href: BASE + pp.pdf, target: "_blank", rel: "noopener" }, `Read the paper (PDF, ${size(pp.bytes)})`),
        h("a", { class: "btn ghost", href: BASE + pp.pdf, download: pp.pdf }, "Download"),
        h("a", { class: "btn ghost", href: BASE + pp.bib, download: pp.bib }, "Cite (BibTeX)")))));
  } else {
    main.append(card({ title: "The paper" }, h("div", { class: "cardmsg" }, "The paper hasn’t been published on this server yet.")));
  }
  main.append(
    sec("Downloads and citation", grid(
      card({ title: "Downloads" }, h("ul", { class: "srclist" },
        pp ? h("li", null, h("a", { href: BASE + pp.pdf, download: pp.pdf }, "The paper"), ` (PDF, ${pp.pages || "?"} pages)`) : null,
        pp ? h("li", null, h("a", { href: BASE + pp.bib, download: pp.bib }, "BibTeX entry")) : null,
        h("li", null, h("a", { href: "data/study.json", download: "genai-arabic-study-results.json" }, "Every number on this site"), " (JSON, group-level results only)"),
        h("li", null, h("a", { href: "#study" }, "The questionnaire"), ", in Arabic and English (Chapter 2)")),
        h("p", { class: "muted" }, "Individual responses are not shared: participants were told that answers would be reported only as group results.")),
      card({ title: "Cite this study" },
        h("p", { class: "citebox" }, `${S.study.author}, “${(pp ? pp.title : S.study.title).replace("Arabic-English", "Arabic–English")},” ${S.study.affiliation}, 2026.`)))),
    sec("References", card({ title: `The ${Object.keys(S.references).length} works the paper cites`, sub: "Grouped by what they contribute to the study. Titles link to the source.", span2: true },
      REF_GROUPS.map(([name, keys]) => h("div", { class: "refgroup" }, h("h4", null, name), sources(S, keys))))),
    storyNav("paper"));
}
