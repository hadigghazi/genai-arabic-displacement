// How the study was done: design, instrument, analysis, machine learning, limits, citation.
import { h, pageHead, card, grid, table } from "./ui.js";

export function method(main, S) {
  const st = S.study;
  main.append(
    pageHead("About", "How the study was done",
      "A cross-sectional survey of perceived, AI-attributed change in Arabic use, analysed with tests fixed in an analysis plan written before data collection."),
    grid(
      card({ title: "Design and sample" },
        h("div", { class: "prose" },
          h("p", null, `An anonymous Google Form in Arabic was open from ${st.collected}. Respondents were recruited through university WhatsApp groups, `
            + "friends and their contacts, Instagram stories and LinkedIn posts. A screening question required Arabic as first language, use of English for "
            + "study or work, and weekly AI use for six months or more. Before launch, a speech-language pathologist reviewed the form."),
          h("p", null, `All ${S.sample.n} respondents form the primary sample. The analysis plan’s core sample, which holds migration constant `
            + `(grew up and live in the Arab region, no move since 2022; n = ${S.sample.core_n}), is analysed as a sensitivity check.`))),
      card({ title: "What was measured" },
        h("div", { class: "prose" },
          h("p", null, h("b", null, "Displacement score: "), "minus the mean AI-attributed change over the areas that apply (at least six), so higher means more decrease."),
          h("p", null, h("b", null, "Difficulty without AI: "), "three items on finding the everyday word, speaking one’s dialect fluently and saying what one means fully in Arabic."),
          h("p", null, h("b", null, "AI use: "), "frequency, share of work or study done with AI, number of uses, start year, the language used to write to AI, and exposure to AI-generated content."),
          h("p", null, h("b", null, "Also: "), "the perceived Arabic–English quality gap, the same change question for social media, life events, expected change, and English level.")))),
    card({ title: "The core question, as fielded", span2: true, sub: S.instrument.question.en },
      table([
        { label: "Area (English source wording)", get: (r) => r.en, class: "strong" },
        { label: "Arabic, as fielded", get: (r) => h("span", { class: "ar", lang: "ar", dir: "rtl" }, r.ar) },
      ], S.instrument.rows),
      h("p", { class: "muted ar", lang: "ar", dir: "rtl", style: { marginTop: "10px" } }, S.instrument.question.ar)),
    grid(
      card({ title: "Statistical analysis" },
        h("div", { class: "prose" },
          h("ul", null,
            h("li", null, h("b", null, "Direction (H1): "), "Wilcoxon signed-rank tests against zero, with exact sign tests alongside."),
            h("li", null, h("b", null, "Order (H2a): "), "Page’s one-sided test of the predicted order, with Friedman’s test and Kendall’s W."),
            h("li", null, h("b", null, "Predictors (H3, H4): "), "OLS regression with HC3 robust standard errors and t-based inference, adjusted for age and an English-medium start; a wild bootstrap checked every p-value."),
            h("li", null, h("b", null, "Mediation (H5): "), "PROCESS model 4 logic with a 5,000-resample percentile bootstrap."),
            h("li", null, h("b", null, "Multiple testing: "), "Holm’s correction within each family of hypotheses."),
            h("li", null, h("b", null, "Robustness: "), "every analysis choice rerun the other way, Firth logistic regression, influence diagnostics, and McDonald’s ω for reliability.")),
          h("p", null, "Analyses ran in SPSS 23 and Python; 34 statistics computed in both agree."))),
      card({ title: "Machine learning" },
        h("div", { class: "prose" },
          h("ul", null,
            h("li", null, h("b", null, "Question: "), "does information about AI use improve prediction of who reports a decrease, beyond background characteristics?"),
            h("li", null, h("b", null, "Models: "), "L2 logistic or ridge regression with fixed settings; random forest and gradient boosting as checks."),
            h("li", null, h("b", null, "Validation: "), "repeated stratified 10×5-fold cross-validation, SMOTENC oversampling inside the training folds only."),
            h("li", null, h("b", null, "Inference: "), "Nadeau–Bengio corrected t-tests for comparisons, permutation tests (500, whole pipeline refit) for chance, Holm’s correction."),
            h("li", null, h("b", null, "Usable: "), "four criteria fixed in advance (above chance, stable across splits, not carried by age, balanced accuracy ≥ 0.65)."))))),
    grid(
      card({ title: "Limits" },
        h("div", { class: "prose" },
          h("p", null, "The sample is young, highly educated and computing-heavy, so the percentages describe this group rather than all Lebanese bilinguals. "
            + "Change was rated retrospectively, over two to four years for most respondents, and the outcome is the change people attribute to AI. "
            + "Apart from the expert review, the instrument was not back-translated or formally pretested."),
          h("p", null, "Longitudinal designs and behavioural records of the language people use with AI are the next step."))),
      card({ title: "Cite" },
        h("div", { class: "prose" },
          h("p", null, `${st.author}, “${st.title.replace("Arabic-English", "Arabic–English")},” ${st.affiliation}, 2026.`),
          h("p", { class: "muted" }, "Every number on these pages is a group-level result; no individual response is published.")))));
}
