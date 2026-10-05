// Home, Chapter 1 (the question) and Chapter 2 (how we asked).
import { h, f, pct, fp, kpis, card, grid, table } from "./ui.js";
import { chart, hbar } from "./charts.js";
import { CHAPTERS, chapterHead, sec, prose, takeaway, howWeKnow, cite, sources, storyNav } from "./story.js";

// ------------------------------------------------------------------ home
export function home(main, S) {
  const r = S.rq1, ws = r.domains.find((d) => d.id === "WorkStudy"), B = S.hypotheses.family_b;
  const usable = S.ml.targets.filter((t) => t.usability.usable);
  main.append(
    h("header", { class: "hero" },
      h("div", { class: "eyebrow" }, `A survey of ${S.sample.n} Lebanese Arabic–English bilinguals`),
      h("h1", null, "Is generative AI displacing Arabic?"),
      h("p", { class: "lede" }, "AI tools work better in English than in Arabic. We asked bilinguals who use them every day whether, because of AI, "
        + "they now use Arabic less, and in which parts of their lives."),
      h("div", { class: "herobtns" },
        h("a", { class: "btn", href: "#question" }, "Read the story"),
        h("a", { class: "btn ghost", href: "#model" }, "Try the model"),
        h("a", { class: "btn ghost", href: "#paper" }, "Read the paper"))),
    card({ title: "The short answer", span2: true },
      h("p", { class: "answer" }, "About two thirds say yes, in at least one part of their lives: mostly at work or study and in writing, "
        + "hardly with family or in religion. What goes with it is not how much people use AI, but the language they use it in."),
      kpis([
        { n: pct(r.any_decrease / S.sample.n), l: `report less Arabic somewhere because of AI (${r.any_decrease} of ${S.sample.n})` },
        { n: `${pct(ws.less)} vs ${pct(ws.more)}`, l: "less vs more Arabic in work or study" },
        { n: `b = ${f(B.H3b.b)}`, l: `writing to AI in English goes with the decrease (Holm p ${fp(B.H3b.p_holm)})` },
        { n: usable.length, l: "usable prediction models, judged by rules fixed in advance" },
      ])),
    h("section", { class: "storysec" }, h("h3", null, "The story in eight chapters"),
      h("div", { class: "storymap" }, CHAPTERS.map((c, i) => h("a", { href: "#" + c.id },
        h("span", { class: "chno" }, String(i + 1)), h("b", null, c.title), h("span", null, c.teaser))))),
    storyNav("home"));
}

// ------------------------------------------------------------------ chapter 1
export function question(main, S) {
  const c = (...k) => cite(S, ...k);
  const links = [["H1", "Arabic is used less for Fusha and for work or study.", "where"],
    ["H2", "The decrease follows the order work or study, then personal matters, then family, and is larger for Fusha than for the dialect.", "where"],
    ["H3", "How much people use AI, the share they use in English and the quality gap they perceive predict the decrease.", "language"],
    ["H4", "The decrease goes with finding it harder to use Arabic without AI.", "language"],
    ["H5", "The decrease is the route from AI use to that difficulty.", "language"],
    ["RQ4", "Knowing how someone uses AI helps predict whether they report a decrease.", "prediction"]];
  main.append(
    chapterHead("question", "AI tools speak better English than Arabic. People who live in both languages may be quietly moving their AI-assisted work into English. "
      + "This chapter sets out why that matters and what we expected to find."),
    sec("AI works better in English",
      prose(["Generative AI tools perform less well in Arabic than in English. Tool-calling accuracy drops when the same tasks are prompted in Arabic ",
        c("kubrak2025"), ", and chatbots answered the same infectious-disease questions less well in Arabic than in English ", c("sallam2024"),
        ". Bilinguals who use these tools daily may therefore do more of their AI-assisted tasks in English."])),
    sec("A shift already under way",
      prose(["English was moving into Arabic speakers’ formal lives well before generative AI. It dominates higher education in the UAE ", c("albataineh2021"),
        ", where students at English-medium universities report weaker academic Arabic ", c("masri2019"),
        "; Qatar University students rate English more useful than Arabic for scientific and professional communication ", c("mustafawi2022"),
        "; and in Lebanon, English runs across education and professional life ", c("mehio2026"), "."],
        ["Social networking sites then moved young Arabs’ informal writing toward English and Latin script, giving rise to Arabizi ", c("alghamdi2018"),
          ". Generative AI may be the next step of the same shift."]),
      takeaway("Research on AI and language has looked at people learning a second language ", c("saarela2026"),
        ". The closest work on Arabic records which language people choose with ChatGPT ", c("bouzayenne2026"),
        ", but no study had asked Arabic speakers whether AI has changed their own Arabic.")),
    sec("Two ideas from linguistics",
      grid(
        card({ title: "Domains" }, prose(["Language use is organised by domains: family, friendship, religion, education, work. "
          + "When a stronger language spreads, it takes over one domain at a time, starting with the public and formal ones ", c("fishman1965", "fishman1972"), "."])),
        card({ title: "Diglossia" }, prose(["Arabic has two varieties: Fusha (Modern Standard Arabic) for formal and written uses, and the spoken dialect for everyday life ",
          c("ferguson1959"), ". If AI moves formal work into English, Fusha should be affected first."]))),
      h("div", { class: "domainline", "aria-label": "From formal to intimate domains" },
        h("span", { class: "end" }, "formal"),
        ["Work or study", "Writing", "Personal matters", "Family", "Religion"].map((d, i) => [i ? h("span", { class: "arrow" }, "→") : null, h("span", { class: "chip static" }, d)]),
        h("span", { class: "end" }, "intimate")),
      h("p", { class: "muted" }, "The order theory predicts: a stronger language reaches the formal end first.")),
    sec("What we expected",
      h("div", { class: "hyplist" }, links.map(([k, t, ch]) => h("a", { href: "#" + ch, class: "hyp" }, h("span", { class: "hk" }, k), h("span", null, t),
        h("span", { class: "hto" }, "Chapter " + (CHAPTERS.findIndex((x) => x.id === ch) + 1) + " →"))))),
    sec("What a survey like this can tell us",
      prose(["We asked people about the change they attribute to AI, comparing now with before they started using it regularly. "
        + "That is a perception, not a measurement of how their Arabic changed. People can rate how a major life event changed their language use ",
        c("wirtz2025"), ", and such ratings track real change only partly ", c("schwaba2023"), ". So the findings describe what bilinguals experience, "
        + "which is where any longer study of AI and Arabic would start."])),
    sec("Sources for this chapter", sources(S, ["kubrak2025", "sallam2024", "albataineh2021", "masri2019", "mustafawi2022", "mehio2026", "alghamdi2018",
      "saarela2026", "bouzayenne2026", "fishman1965", "fishman1972", "ferguson1959", "wirtz2025", "schwaba2023"])),
    storyNav("question"));
}

// ------------------------------------------------------------------ chapter 2
const SAMPLE_MAIN = ["Age", "Field", "AI_Freq", "AI_Lang"];
const SAMPLE_MORE = ["Gender", "Education", "Role", "Eng_Prof", "Country_GrewUp", "Country_Now", "AI_Start", "AI_TaskShare", "AI_Breadth",
  "AI_Content", "AI_ContentLang", "FushaPreAI"];

export function study(main, S) {
  const s = S.sample, it = (c) => s.items.find((x) => x.code === c);
  const sampleCard = (code) => {
    const x = it(code);
    const c = card({ title: x.q.replace(/\s*\(tick all that apply\)/, ""), sub: x.type === "check" ? "More than one answer allowed." : null });
    c.draw = () => chart(c.body, (p) => hbar(p, { labels: x.options.map((o) => o.label), values: x.options.map((o) => o.n), color: p.s1 }),
      26 * x.options.length + 16, x.q);
    return c;
  };
  const main4 = SAMPLE_MAIN.map(sampleCard);
  const more = SAMPLE_MORE.map(sampleCard);
  const moreGrid = h("div", null, ...Array.from({ length: Math.ceil(more.length / 2) }, (_, i) => grid(more[2 * i], more[2 * i + 1] || h("div"))));
  const q = S.instrument;
  main.append(
    chapterHead("study", "An anonymous survey in Arabic, built around one question asked about eight areas of daily life."),
    sec("The survey",
      prose(`The survey was an anonymous Google Form in Arabic, open from ${S.study.collected}. It was shared through university WhatsApp groups, `
        + "friends and their contacts, Instagram stories and LinkedIn posts. Before launch, a speech-language pathologist reviewed the form.",
        "To take part, people had to have Arabic as their first language, use English for study or work, and have used AI tools at least weekly for six months. "
        + `All ${s.n} who answered met these conditions.`)),
    sec("The core question",
      card({ title: `“${q.question.en}”`, sub: "Compared with before regular AI use. Each area was answered on five steps; an area that did not apply could be marked as such and is left out." },
        table([
          { label: "Area (English source wording)", get: (r) => r.en, class: "strong" },
          { label: "Arabic, as fielded", get: (r) => h("span", { class: "ar", lang: "ar", dir: "rtl" }, r.ar) },
        ], q.rows),
        h("div", { class: "qopts" }, h("span", { class: "muted" }, "Answers: "),
          ["Much less", "Less", "No change", "More", "Much more"].map((o) => h("span", { class: "chip static" }, o))),
        h("p", { class: "muted ar", lang: "ar", dir: "rtl", style: { marginTop: "10px" } }, q.question.ar)),
      prose("Around it, the survey asked how people use AI, the language they write to it in, how hard Arabic feels without AI, the same change question "
        + "for social media, what else changed in their lives, and their background.")),
    sec("Who took part",
      kpis([
        { n: s.grew_up_lebanon, l: `grew up in Lebanon; ${s.live_lebanon} live there` },
        { n: it("Age").options[0].n, l: "were under 25" },
        { n: it("Education").options[2].n, l: "held or were studying for a master’s degree or higher" },
        { n: it("AI_Freq").options[3].n, l: "used AI several times a day" },
        { n: it("AI_Lang").options[4].n, l: "always wrote to AI in English" },
      ]),
      grid(main4[0], main4[1]), grid(main4[2], main4[3]),
      howWeKnow("Every other background and AI-use answer", moreGrid, () => more.forEach((c) => c.draw())),
      h("p", { class: "muted" }, "Only totals for single questions are shown, never combinations, so no respondent can be singled out.")),
    sec("The full questionnaire", questionnaireCard(S.questionnaire)),
    sec("How we analysed it",
      prose("Every test follows an analysis plan written before data collection. Two families of hypotheses were tested with corrections for multiple testing, "
        + `every analysis choice was rerun the other way to check it, and the results describe all ${s.n} respondents, with the plan’s narrower core sample `
        + `(n = ${s.core_n}) as a check.`),
      howWeKnow("The tests, in brief", h("div", { class: "prose" },
        h("ul", null,
          h("li", null, h("b", null, "Direction (H1): "), "Wilcoxon signed-rank tests against zero, with exact sign tests alongside."),
          h("li", null, h("b", null, "Order (H2): "), "Page’s one-sided test of the predicted order, with Friedman’s test and Kendall’s W."),
          h("li", null, h("b", null, "Predictors (H3, H4): "), "regression with HC3 robust standard errors, adjusted for age and an English-medium start; a wild bootstrap checked every p-value."),
          h("li", null, h("b", null, "Mediation (H5): "), "PROCESS model 4 logic with a 5,000-resample percentile bootstrap."),
          h("li", null, h("b", null, "Multiple testing: "), "Holm’s correction within each family of hypotheses."),
          h("li", null, h("b", null, "Machine learning: "), "repeated 10×5-fold cross-validation, permutation tests, and four usability criteria fixed in advance (Chapter 6)."),
          h("li", null, h("b", null, "Software: "), "SPSS 23 and Python; 34 statistics computed in both agree.")),
        h("p", null, "Responses were collected in two waves; every analysis choice was fixed before the second was analysed.")))),
    storyNav("study"));
  main4.forEach((c) => c.draw());
}

function questionnaireCard(Q) {
  let n = 0;
  const sections = Q.map((sec_) => h("details", { class: "qsec" },
    h("summary", null, h("span", null, sec_.title.en), h("span", { class: "ar", lang: "ar", dir: "rtl" }, sec_.title.ar)),
    sec_.items.map((it) => {
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
  return card({ title: "Every question, in Arabic and English", span2: true,
    sub: "As fielded: the Arabic wording is the instrument, the English is the source wording. Open a section to read it." },
    h("div", { class: "qsecs" }, sections));
}
