// The study's findings: overview, domain profile, hypotheses, predictors, context, sample.
import { h, f, sg, pct, fp, pe, ci, pageHead, kpis, card, grid, table, callout, flag, link } from "./ui.js";
import { chart, diverging, hbar, vbar, groupedHbar, forest } from "./charts.js";

const verdict = (ok, text) => flag(text || (ok ? "supported" : "not supported"), ok ? "good" : null);

// ------------------------------------------------------------------ overview
export function overview(main, S) {
  const r = S.rq1, fb = S.hypotheses.family_b, ws = r.domains.find((d) => d.id === "WorkStudy");
  const usable = S.ml.targets.filter((t) => t.usability.usable);
  const aucs = usable.map((t) => t.blocks.with_ai.score);
  main.append(
    pageHead("Study overview", "Is generative AI displacing Arabic?",
      `An anonymous Arabic survey asked ${S.sample.n} Lebanese Arabic–English bilinguals who use AI regularly whether, because of AI, `
      + "they now use Arabic less or more in eight areas of daily life. These pages show what they reported, what goes with it, "
      + "and a live model built from their answers."),
    kpis([
      { n: S.sample.n, l: "respondents, 30 September to 4 October 2026" },
      { n: pct(r.any_decrease / S.sample.n), l: `report less Arabic in at least one area because of AI (${r.any_decrease} of ${S.sample.n})` },
      { n: `${pct(ws.less)} vs ${pct(ws.more)}`, l: "less vs more Arabic in work or study" },
      { n: `b = ${f(fb.H3b.b)}`, l: `writing to AI in English predicts the decrease (Holm p ${fp(fb.H3b.p_holm)})` },
      { n: usable.length, l: `usable prediction models (AUC ${Math.min(...aucs).toFixed(2)}–${Math.max(...aucs).toFixed(2)})` },
    ]));
  const findings = card({ title: "What the study found", span2: true },
    h("ol", { class: "findings" },
      h("li", null, h("b", null, "The decrease follows the formal domains. "),
        `Work or study (${pct(ws.less)} less), writing messages (${pct(r.domains.find((d) => d.id === "Writing").less)}) and following content `
        + `(${pct(r.domains.find((d) => d.id === "Consume").less)}) lead; family use and religious texts are hardly affected. `
        + "The order predicted by domain theory, work/study > personal matters > family, holds. ", link("profile", "See the profile")),
      h("li", null, h("b", null, "The language of AI use matters, not the amount. "),
        "The more often respondents write to AI in English, the larger the decrease they report, in every specification. "
        + "How much they use AI, and how large they judge the Arabic–English quality gap, do not predict it. ", link("predictors", "See the predictors")),
      h("li", null, h("b", null, "AI continues a shift that social media began. "),
        `Respondents who report losing Arabic to AI also report losing it to social media (ρ = ${f(S.context.ai_vs_social.rho)}). `,
        link("context", "See social media and life changes")),
      h("li", null, h("b", null, "Three usable prediction models. "),
        "Answers about background and AI use identify who reports a decrease in formal areas, in work or study and in self-talk; "
        + "AI-use answers add no significant gain over background alone. ", link("model", "Try the model")),
      h("li", null, h("b", null, "These are perceptions. "),
        "The study measures the change people attribute to AI. Tracking actual language use over time is the next step.")));
  const profile = card({ title: "Where Arabic is used less", sub: "Share of respondents answering less, the same or more, by area. Hover for details." });
  const explore = card({ title: "Explore the study" },
    h("div", { class: "linkcards" },
      [["profile", "Where Arabic is used less", "The eight areas of daily life"],
       ["hypotheses", "Hypotheses", "Five hypotheses and how they fared"],
       ["predictors", "What goes with the decrease", "AI use, English and difficulty"],
       ["context", "Social media and life changes", "The wider picture"],
       ["sample", "Who took part", "The 105 respondents"],
       ["ml", "Prediction models", "Cross-validated machine learning"],
       ["model", "Try the model", "Answer 12 questions"],
       ["research", "The paper", "Read, download or cite it"],
       ["method", "How the study was done", "Design, instrument, analysis"]]
        .map(([id, t, s]) => h("a", { class: "linkcard", href: "#" + id }, h("b", null, t), h("span", null, s)))));
  main.append(findings, grid(profile, explore));
  chart(profile.body, (p, w) => diverging(p, r.domains, w), 330, "AI-attributed change in Arabic use by area");
}

// ------------------------------------------------------------------ RQ1 profile
export function profile(main, S) {
  const r = S.rq1;
  const sub = r.substitution;
  main.append(
    pageHead("Finding 01 · RQ1", "Where respondents use Arabic less",
      "The core question: ", h("i", null, `“${S.instrument.question.en}”`),
      " Each area was rated from much less to much more, compared with before regular AI use. Areas a respondent marked as not applicable are left out."),
    kpis([
      { n: r.any_decrease, l: `of ${S.sample.n} report less Arabic in at least one area` },
      { n: r.domains_lost_mean.toFixed(1), l: "areas with a decrease per person, on average" },
      { n: pct(sub.k / sub.n), l: `did something in English they could have done in Arabic, because AI works better in English (95% CI ${pct(sub.ci[0])}–${pct(sub.ci[1])})` },
      { n: "8", l: "areas of daily life rated" },
    ]));
  const chartCard = card({ title: "AI-attributed change by area", span2: true,
    sub: "Bars are centred on “no change”: less Arabic to the left, more to the right. n excludes respondents who marked the area not applicable." });
  const dist = card({ title: "How many areas each person reported less Arabic in", sub: `${r.domains_lost[0]} respondents reported no decrease anywhere.` });
  const tab = card({ title: "The numbers", sub: "Wilcoxon signed-rank test of the net change against zero; Holm-adjusted across the eight areas as a strict check." },
    table([
      { label: "Area", get: (d) => d.label, class: "strong" },
      { label: "n", num: true, get: (d) => d.n },
      { label: "Less [95% CI]", num: true, get: (d) => `${pct(d.less)} [${pct(d.less_ci[0])}, ${pct(d.less_ci[1])}]` },
      { label: "More", num: true, get: (d) => pct(d.more) },
      { label: "z", num: true, get: (d) => f(d.z) },
      { label: "Holm p", num: true, get: (d) => fp(d.p_holm8) },
    ], [...r.domains].sort((a, b) => b.less - a.less)));
  main.append(chartCard, grid(dist, tab),
    callout(h("b", null, "Reading this. "), "These are the changes respondents attribute to AI, not measured changes in their Arabic. "
      + "The pattern is what domain theory predicts: formal and work-related uses shift first, intimate and religious uses last."));
  chart(chartCard.body, (p, w) => diverging(p, r.domains, w), 380, "AI-attributed change by area");
  chart(dist.body, (p) => vbar(p, { labels: r.domains_lost.map((_, i) => String(i)), values: r.domains_lost, color: p.s1,
    tip: (i) => `${r.domains_lost[i]} respondents reported less Arabic in ${i} area${i === 1 ? "" : "s"}` }), 250,
    "Number of areas with a decrease per respondent");
}

// ------------------------------------------------------------------ hypotheses
export function hypotheses(main, S) {
  const A = S.hypotheses.family_a, B = S.hypotheses.family_b, h5 = S.hypotheses.h5.primary, C = S.hypotheses.family_a_core;
  const rows = [
    { group: "Family A: direction and order of the change (within each person)" },
    { h: "H1a  Less Fusha", n: A.H1a.n, res: `${A.H1a.less} less, ${A.H1a.more} more`, test: `z = ${f(A.H1a.z)}, r = ${f(A.H1a.r)}`, p: A.H1a.p_holm, ok: A.H1a.p_holm < .05 },
    { h: "H1b  Less Arabic in work or study", n: A.H1b.n, res: `${A.H1b.less} less, ${A.H1b.more} more`, test: `z = ${f(A.H1b.z)}, r = ${f(A.H1b.r)}`, p: A.H1b.p_holm, ok: A.H1b.p_holm < .05 },
    { h: "H2a  Work/study > personal > family", n: A.H2a.n, res: `means ${f(A.H2a.means.WorkStudy)}, ${f(A.H2a.means.Personal)}, ${f(A.H2a.means.Family)}`,
      test: `Page; χ²(2) = ${f(A.H2a.chi2)}, W = ${f(A.H2a.W)}`, p: A.H2a.p_holm, ok: A.H2a.p_holm < .05 },
    { h: "H2b  Fusha > dialect areas", n: A.H2b.n, res: `difference ${sg(A.H2b.mean_diff)}`, test: `z = ${f(A.H2b.z)}`, p: A.H2b.p_holm, ok: A.H2b.p_holm < .05 },
    { group: `Family B: what predicts the decrease (regression, n = ${B.n}, robust errors)` },
    { h: "H3  AI use predicts the decrease (joint)", n: B.n, res: "three predictors", test: `F(${B.joint.df.join(", ")}) = ${f(B.joint.F)}, p ${fp(B.joint.p)}`, p: null, ok: B.joint.p < .05 },
    { h: "H3a  AI-use intensity", n: "", res: `b = ${f(B.H3a.b, 3)} ${ci(B.H3a.ci[0], B.H3a.ci[1])}`, test: `p ${pe(B.H3a.p)}`, p: B.H3a.p_holm, ok: B.H3a.p_holm < .05 },
    { h: "H3b  English share of AI use", n: "", res: `b = ${f(B.H3b.b)} ${ci(B.H3b.ci[0], B.H3b.ci[1])}`, test: `p ${fp(B.H3b.p)}`, p: B.H3b.p_holm, ok: B.H3b.p_holm < .05 },
    { h: "H3c  Perceived quality gap", n: "", res: `b = ${f(B.H3c.b)} ${ci(B.H3c.ci[0], B.H3c.ci[1])}`, test: `p ${pe(B.H3c.p)}`, p: B.H3c.p_holm, ok: B.H3c.p_holm < .05 },
    { h: "H4  Decrease goes with difficulty without AI", n: B.n, res: `b = ${f(B.H4.b)} ${ci(B.H4.ci[0], B.H4.ci[1])}`, test: `p ${pe(B.H4.p)}`, p: B.H4.p_holm, ok: B.H4.p_holm < .05 },
    { h: "H5  The decrease mediates AI use → difficulty", n: B.n, res: `indirect ${f(h5.indirect)} [${h5.ci[0].toFixed(4)}, ${f(h5.ci[1])}]`, test: "percentile bootstrap", p: null, ok: null },
  ];
  const tab = card({ title: "Confirmatory tests", span2: true,
    sub: "Holm’s correction within each family. Family B adjusts for age 25 or over and an English-medium start; brackets are 95% CIs." },
    table([
      { label: "Hypothesis", get: (x) => x.h, class: "strong" },
      { label: "n", num: true, get: (x) => x.n },
      { label: "Result", get: (x) => x.res },
      { label: "Test", get: (x) => x.test },
      { label: "Holm p", num: true, get: (x) => (x.p === null ? "" : fp(x.p)) },
      { label: "Verdict", get: (x) => (x.ok === null ? flag("borderline", "mid") : verdict(x.ok)) },
    ], rows));
  const order = card({ title: "H2a: the predicted order", sub: `Mean decrease (higher = more decrease), complete cases, n = ${A.H2a.n}. Page’s test p ${fp(A.H2a.page_p)} (one-sided).` });
  const h1 = card({ title: "H1: decreases against increases", sub: "Respondents reporting less vs more, among those who reported a change." });
  const core = card({ title: "Same tests in the core sample", sub: `The analysis plan’s narrower sample (grew up and live in the Arab region, no move since 2022; n = ${S.sample.core_n}).` },
    table([
      { label: "Hypothesis", get: (x) => x[0], class: "strong" },
      { label: "All respondents", num: true, get: (x) => fp(x[1]) },
      { label: "Core sample", num: true, get: (x) => fp(x[2]) },
    ], [["H1a", A.H1a.p_holm, C.H1a.p_holm], ["H1b", A.H1b.p_holm, C.H1b.p_holm], ["H2a", A.H2a.p_holm, C.H2a.p_holm], ["H2b", A.H2b.p_holm, C.H2b.p_holm]]),
    h("p", { class: "muted" }, "Holm-adjusted p-values. Family B in the core sample is shown on the next page."));
  const notes = card({ title: "Reading the verdicts" },
    h("div", { class: "prose" },
      h("p", null, h("b", null, "H3 "), "is supported through the English share alone: intensity and the quality gap add nothing."),
      h("p", null, h("b", null, "H4 "), `falls just short in the main analysis (p ${pe(B.H4.p)}). It is positive in every specification and strong in the core sample; one respondent whose answers run against the trend holds it down.`),
      h("p", null, h("b", null, "H5 "), `is borderline: the indirect effect’s interval only just excludes zero, and the path from the decrease to difficulty is not significant (p ${pe(h5.b_p)}).`)));
  main.append(
    pageHead("Finding 02 · H1–H5", "How the hypotheses fared",
      "Two families of confirmatory tests, fixed in the analysis plan: the direction and order of the change (H1–H2), and what predicts it (H3–H5)."),
    tab, grid(order, h1), grid(core, notes));
  chart(order.body, (p) => vbar(p, { labels: ["Work or study", "Personal matters", "Family"],
    values: [A.H2a.means.WorkStudy, A.H2a.means.Personal, A.H2a.means.Family], color: p.s1, fmt: (v) => f(v) }), 230, "Mean decrease by area");
  chart(h1.body, (p) => groupedHbar(p, { labels: ["Fusha (H1a)", "Work or study (H1b)"],
    series: [{ name: "Less", values: [A.H1a.less, A.H1b.less], color: p.s2 }, { name: "More", values: [A.H1a.more, A.H1b.more], color: p.s1 }] }), 200, "Less vs more counts");
}

// ------------------------------------------------------------------ predictors
export function predictors(main, S) {
  const B = S.hypotheses.family_b, H = S.hypotheses, h5 = H.h5;
  const coef = [
    { label: "AI-use intensity (H3a)", ...B.H3a }, { label: "English share of AI use (H3b)", ...B.H3b },
    { label: "Perceived quality gap (H3c)", ...B.H3c }, { label: "Age 25 or over", ...B.covariates.Age25 },
    { label: "Started English-medium study or work", ...B.covariates.EventMove },
  ].map((x) => ({ label: x.label, b: x.b, lo: x.ci[0], hi: x.ci[1], on: x.p < .05,
                  tip: `${x.label}<br>b = <b>${f(x.b)}</b> ${ci(x.ci[0], x.ci[1])}, p ${fp(x.p)}` }));
  const spec = (key) => H.specs.map((s) => ({ label: s.label, b: s[key].b, lo: s[key].ci[0], hi: s[key].ci[1], on: s[key].p_holm < .05,
    tip: `${s.label} (n = ${s.n})<br>b = <b>${f(s[key].b)}</b> ${ci(s[key].ci[0], s[key].ci[1])}<br>Holm p ${fp(s[key].p_holm)}` }));
  const rel = H.reliability;
  main.append(
    pageHead("Finding 03 · H3–H5", "What goes with the decrease",
      "The displacement score averages a respondent’s AI-attributed change over the areas that apply to them (higher = more decrease). "
      + "It is regressed on three measures of AI use, with age and an English-medium start held constant."),
    kpis([
      { n: `b = ${f(B.H3b.b)}`, l: `English share of AI use, 95% CI ${ci(B.H3b.ci[0], B.H3b.ci[1])}, Holm p ${fp(B.H3b.p_holm)}` },
      { n: `F = ${f(B.joint.F)}`, l: `the three AI-use measures jointly, p ${fp(B.joint.p)}` },
      { n: `b = ${f(B.H3a.b, 3)}`, l: `AI-use intensity: no relation (p ${pe(B.H3a.p)})` },
      { n: `ρ = ${f(H.english_share_vs_proficiency_rho)}`, l: "English share and English level go together, yet the share predicts with level controlled" },
    ]));
  const c1 = card({ title: "The regression", span2: true, sub: `Coefficients with 95% CIs (n = ${B.n}, HC3 robust errors). Blue: p < 0.05. Units differ by measure (scales of 1–5, standardised intensity, 0/1 indicators).` });
  const c2 = card({ title: "English share under every specification", sub: "Blue: Holm-significant. The effect holds in all ten." });
  const c3 = card({ title: "H4: decrease and difficulty without AI", sub: "Blue: Holm-significant. Positive throughout; significant in four of ten." });
  const c4 = card({ title: "H5: mediation", sub: "AI-use intensity → displacement → difficulty without AI, percentile bootstrap (5,000 resamples)." },
    table([
      { label: "Path", get: (x) => x[0], class: "strong" },
      { label: "All respondents", num: true, get: (x) => x[1] },
      { label: "Core sample", num: true, get: (x) => x[2] },
    ], [
      ["a: intensity → decrease", `${f(h5.primary.a, 3)} (p ${pe(h5.primary.a_p)})`, `${f(h5.core.a, 3)} (p ${pe(h5.core.a_p)})`],
      ["b: decrease → difficulty", `${f(h5.primary.b, 3)} (p ${pe(h5.primary.b_p)})`, `${f(h5.core.b, 3)} (p ${pe(h5.core.b_p)})`],
      ["c′: direct effect", f(h5.primary.c_direct, 3), f(h5.core.c_direct, 3)],
      ["indirect a × b [95% CI]", `${f(h5.primary.indirect, 3)} [${h5.primary.ci[0].toFixed(4)}, ${f(h5.primary.ci[1], 3)}]`, `${f(h5.core.indirect, 3)} [${f(h5.core.ci[0], 3)}, ${f(h5.core.ci[1], 3)}]`],
    ]));
  const c5 = card({ title: "Reliability of the scores", sub: "McDonald’s ω with a bootstrap 95% CI, and Cronbach’s α." },
    table([
      { label: "Score", get: (x) => x[0], class: "strong" },
      { label: "Items", num: true, get: (x) => x[1] },
      { label: h("span", { style: { textTransform: "none" } }, "ω [95% CI]"), num: true, get: (x) => x[2] },
      { label: h("span", { style: { textTransform: "none" } }, "α"), num: true, get: (x) => x[3] },
    ], [["Displacement", "8 areas", rel.Displacement], ["Difficulty without AI", "3", rel.AbilityDecline], ["Perceived quality gap", "4", rel.QualityGap]]
      .map(([n, it, r]) => [n, it, `${f(r.omega)} ${ci(r.omega_ci[0], r.omega_ci[1])}`, f(r.alpha)])));
  main.append(c1, grid(c2, c3), grid(c4, c5),
    callout(h("b", null, "Reading this. "), `The amount of AI use does not go with the decrease; the language of AI use does. `
      + `The 23 respondents aged 25 or over reported little change (15 none), which is why age carries a large coefficient. `
      + `H4 depends on one respondent (Cook’s distance ${f(H.h4_influence.cooks_d)}); without that person b = ${f(H.specs.find((s) => s.label.startsWith("Without the most")).H4.b)}.`));
  chart(c1.body, (p) => forest(p, { rows: coef, xName: "change in the displacement score per unit" }), 250, "Regression coefficients");
  chart(c2.body, (p) => forest(p, { rows: spec("H3b") }), 360, "English share across specifications");
  chart(c3.body, (p) => forest(p, { rows: spec("H4") }), 360, "H4 across specifications");
}

// ------------------------------------------------------------------ social media and life changes
export function context(main, S) {
  const C = S.context, sm = C.ai_vs_social, st = C.stable, u = C.started_university;
  main.append(
    pageHead("Finding 04", "Social media and life changes",
      "Generative AI is not the first technology to move young Arabs’ everyday language toward English: social networking sites did so before it, "
      + "and the AI years also brought new universities, jobs and English-medium study. Both were asked about alongside AI."),
    kpis([
      { n: `ρ = ${f(sm.rho)}`, l: "between the decrease people attribute to AI and to social media" },
      { n: `${sg(sm.social)} vs ${sg(sm.ai)}`, l: `social media vs AI, decrease averaged over the areas (p ${fp(sm.p)})` },
      { n: `${C.under25_transition} of ${C.under25_n}`, l: "respondents under 25 started university, graduated, began a new job or started studying or working in English" },
      { n: `${f(u.mean)} vs ${f(u.rest_mean)}`, l: `change in work/study Arabic: started university vs the rest (p ${fp(u.p)})` },
    ]));
  const a = card({ title: "AI and social media", sub: "Decrease attributed to each (higher = more decrease). Social media was one overall question, so it is compared with AI averaged over the areas and over the two formal areas." });
  const b = card({ title: "Who attributes the decrease to AI", sub: "Displacement score by whether the respondent also reported a decrease because of social media (exploratory)." });
  const c = card({ title: "Life events since regular AI use began", sub: "Respondents ticking each event (more than one allowed)." });
  const d = card({ title: "Work or study: a change of setting", sub: "Mean AI-attributed change in work/study Arabic (negative = less Arabic)." });
  main.append(grid(a, b), grid(c, d),
    callout(h("b", null, "Reading this. "), "The two technologies read as successive stages of one shift: social media moved informal communication toward English, "
      + "and AI carries it into work, study and writing. The English share of AI use still predicts the decrease with social media held constant. "
      + `Among the ${st.n} whose setting did not change, decreases in work or study still outnumbered increases (${st.less} against ${st.more}, sign test p ${pe(st.sign_p)}).`));
  chart(a.body, (p) => groupedHbar(p, { labels: ["Averaged over the areas", "Formal areas"], fmt: (v) => sg(v),
    series: [{ name: "Because of AI", values: [sm.ai, sm.formal_ai], color: p.s1 }, { name: "Because of social media", values: [sm.social, sm.formal_social], color: p.s2 }] }), 200, "AI vs social media");
  chart(b.body, (p) => hbar(p, { labels: [`Also blame social media (${C.blamers.n})`, `Do not (${C.non_blamers.n})`],
    values: [C.blamers.mean, C.non_blamers.mean], color: p.s1, fmt: (v) => sg(v) }), 160, "Displacement by social-media attribution");
  chart(c.body, (p) => hbar(p, { labels: C.events.map((e) => e.label), values: C.events.map((e) => e.n), color: p.s3 }), 230, "Life events");
  chart(d.body, (p) => hbar(p, { labels: [`Started university (${u.n})`, `Everyone else (${u.rest_n})`, `Setting changed (${st.changed_n})`, `Setting unchanged (${st.n})`],
    values: [-u.mean, -u.rest_mean, -st.changed_mean, -st.mean], color: p.s2, fmt: (v) => f(-v),
    tip: (i) => ["Started university", "Everyone else", "Setting changed", "Setting unchanged"][i] + `: mean change <b>${f([u.mean, u.rest_mean, st.changed_mean, st.mean][i])}</b>` }), 230,
    "Work/study change by setting");
}

// ------------------------------------------------------------------ sample
export function sample(main, S) {
  const s = S.sample;
  const find = (c) => s.items.find((x) => x.code === c);
  const n = (c, i) => find(c).options[i].n;
  main.append(
    pageHead("Sample", "Who took part",
      `${s.n} Arabic–English bilinguals answered an anonymous Arabic online survey between 30 September and 4 October 2026, `
      + "recruited through university WhatsApp groups, friends and their contacts, Instagram stories and LinkedIn posts. "
      + "All had Arabic as their first language, used English for study or work and had used AI tools at least weekly for six months."),
    kpis([
      { n: s.grew_up_lebanon, l: `grew up in Lebanon; ${s.live_lebanon} live there; all but ${s.n - s.lebanon_either} did one or the other` },
      { n: n("Age", 0), l: "were under 25" },
      { n: n("Education", 2), l: "held or were studying for a master’s degree or higher" },
      { n: n("AI_Freq", 3), l: "used AI several times a day" },
      { n: n("AI_Lang", 4), l: "always wrote to AI in English" },
    ]));
  const order = ["Age", "Gender", "Education", "Role", "Field", "Eng_Prof", "Country_GrewUp", "Country_Now", "AI_Start", "AI_Freq",
    "AI_TaskShare", "AI_Breadth", "AI_Lang", "AI_Content", "AI_ContentLang", "FushaPreAI"];
  const cards = order.map((code) => {
    const it = find(code);
    const c = card({ title: it.q.replace(/\s*\(tick all that apply\)/, ""), sub: it.type === "check" ? "More than one answer allowed." : null });
    c.draw = () => chart(c.body, (p) => hbar(p, { labels: it.options.map((o) => o.label), values: it.options.map((o) => o.n), color: p.s1 }),
      26 * it.options.length + 16, it.q);
    return c;
  });
  for (let i = 0; i < cards.length; i += 2) main.append(grid(cards[i], cards[i + 1] || h("div")));
  cards.forEach((c) => c.draw());
  main.append(callout("Only totals for single questions are shown, never combinations, so no respondent can be singled out."));
}
