// Chapters 3-5: where Arabic is used less, the language of AI use, and the shift that began before AI.
import { h, f, sg, pct, fp, pe, ci, kpis, card, grid, table, flag } from "./ui.js";
import { chart, diverging, hbar, vbar, groupedHbar, forest } from "./charts.js";
import { chapterHead, sec, prose, takeaway, howWeKnow, storyNav } from "./story.js";

const ok = (b) => flag(b ? "supported" : "not supported", b ? "good" : null);

// ------------------------------------------------------------------ chapter 3
export function where(main, S) {
  const r = S.rq1, A = S.hypotheses.family_a, C = S.hypotheses.family_a_core, sub = r.substitution;
  const dom = (id) => r.domains.find((d) => d.id === id);
  const ws = dom("WorkStudy"), fu = dom("Fusha");
  const prof = card({ title: "AI-attributed change, area by area", span2: true,
    sub: "Bars are centred on “no change”: less Arabic to the left, more to the right. n excludes respondents who marked the area not applicable. Hover for details." });
  const order = card({ title: "The predicted order", sub: `Mean decrease (higher = more), n = ${A.H2a.n}.` });
  const h1 = card({ title: "Decreases against increases", sub: "Among respondents who reported a change." });
  const dist = card({ title: "Areas with a decrease, per person", sub: `${r.domains_lost[0]} respondents reported none.` });
  main.append(
    chapterHead("where", `About two thirds of respondents (${r.any_decrease} of ${S.sample.n}) said AI has reduced their Arabic in at least one area. `
      + "The decrease sits where theory expects it."),
    kpis([
      { n: `${pct(ws.less)} vs ${pct(ws.more)}`, l: "less vs more Arabic in work or study" },
      { n: pct(dom("Writing").less), l: "write messages and posts in Arabic less often" },
      { n: `${fu.counts[0] + fu.counts[1]} vs ${fu.counts[3] + fu.counts[4]}`, l: "read or write less vs more Fusha" },
      { n: pct(sub.k / sub.n), l: "did something in English they could have done in Arabic, because AI works better in English" },
    ]),
    sec("Eight areas of daily life", prof,
      takeaway("Work and study, writing and following content shift first; family and religion barely move.")),
    sec("Formal first",
      prose(`Respondents reported less Fusha than more (${A.H1a.less} against ${A.H1a.more}) and far more often less than more Arabic in work or study (${A.H1b.less} against ${A.H1b.more}). `
        + "The size of the decrease falls from work or study to personal matters to family, the order domain theory predicts."),
      grid(order, h1),
      prose(`One prediction did not hold: the decrease is no larger for Fusha than for the dialect (difference ${sg(A.H2b.mean_diff)}, p ${pe(A.H2b.p_holm)}). `
        + "The change follows tasks, the things people now do with AI, more than it follows the two varieties of Arabic.")),
    sec("How widespread",
      grid(dist, card({ title: "Doing it in English instead", sub: "“Has it happened that you did something in English, although you could have done it in Arabic, because AI helps you better in English?”" },
        h("div", { class: "bignum" }, pct(sub.k / sub.n)),
        h("p", { class: "muted" }, `${sub.k} of ${sub.n} said sometimes or more often (95% CI ${pct(sub.ci[0])}–${pct(sub.ci[1])}).`)))),
    howWeKnow("Tests of direction and order, area by area", h("div", null,
      table([
        { label: "Hypothesis", get: (x) => x.h, class: "strong" }, { label: "n", num: true, get: (x) => x.n },
        { label: "Result", get: (x) => x.res }, { label: "Test", get: (x) => x.test },
        { label: "Holm p", num: true, get: (x) => fp(x.p) }, { label: "Core sample", num: true, get: (x) => fp(x.pc) },
        { label: "Verdict", get: (x) => ok(x.p < .05) },
      ], [
        { h: "H1a  Less Fusha", n: A.H1a.n, res: `${A.H1a.less} less, ${A.H1a.more} more`, test: `Wilcoxon z = ${f(A.H1a.z)}, r = ${f(A.H1a.r)}`, p: A.H1a.p_holm, pc: C.H1a.p_holm },
        { h: "H1b  Less Arabic in work or study", n: A.H1b.n, res: `${A.H1b.less} less, ${A.H1b.more} more`, test: `Wilcoxon z = ${f(A.H1b.z)}, r = ${f(A.H1b.r)}`, p: A.H1b.p_holm, pc: C.H1b.p_holm },
        { h: "H2a  Work/study > personal > family", n: A.H2a.n, res: `means ${f(A.H2a.means.WorkStudy)}, ${f(A.H2a.means.Personal)}, ${f(A.H2a.means.Family)}`, test: `Page; χ²(2) = ${f(A.H2a.chi2)}, W = ${f(A.H2a.W)}`, p: A.H2a.p_holm, pc: C.H2a.p_holm },
        { h: "H2b  Fusha > dialect", n: A.H2b.n, res: `difference ${sg(A.H2b.mean_diff)}`, test: `Wilcoxon z = ${f(A.H2b.z)}`, p: A.H2b.p_holm, pc: C.H2b.p_holm },
      ]),
      h("p", { class: "muted" }, `Wilcoxon signed-rank tests against zero (exact sign tests agree); Page’s one-sided test of the predicted order; Holm’s correction across the four. The core sample is a narrower sample: grew up and live in the Arab region, no move since 2022 (n = ${S.sample.core_n}).`),
      table([
        { label: "Area", get: (d) => d.label, class: "strong" }, { label: "n", num: true, get: (d) => d.n },
        { label: "Less [95% CI]", num: true, get: (d) => `${pct(d.less)} [${pct(d.less_ci[0])}, ${pct(d.less_ci[1])}]` },
        { label: "More", num: true, get: (d) => pct(d.more) }, { label: "z", num: true, get: (d) => f(d.z) },
        { label: "Holm p (8 areas)", num: true, get: (d) => fp(d.p_holm8) },
      ], [...r.domains].sort((a, b) => b.less - a.less)))),
    storyNav("where"));
  chart(prof.body, (p, w) => diverging(p, r.domains, w), 380, "AI-attributed change by area");
  chart(order.body, (p) => vbar(p, { labels: ["Work or study", "Personal matters", "Family"],
    values: [A.H2a.means.WorkStudy, A.H2a.means.Personal, A.H2a.means.Family], color: p.s1, fmt: (v) => f(v) }), 220, "Mean decrease by area");
  chart(h1.body, (p) => groupedHbar(p, { labels: ["Fusha", "Work or study"],
    series: [{ name: "Less", values: [A.H1a.less, A.H1b.less], color: p.s2 }, { name: "More", values: [A.H1a.more, A.H1b.more], color: p.s1 }] }), 190, "Less vs more");
  chart(dist.body, (p) => vbar(p, { labels: r.domains_lost.map((_, i) => String(i)), values: r.domains_lost, color: p.s1,
    tip: (i) => `${r.domains_lost[i]} respondents reported less Arabic in ${i} area${i === 1 ? "" : "s"}` }), 220, "Areas with a decrease per person");
}

// ------------------------------------------------------------------ chapter 4
export function language(main, S) {
  const B = S.hypotheses.family_b, H = S.hypotheses, h5 = H.h5;
  const coef = [
    { label: "How much AI is used (H3a)", ...B.H3a }, { label: "Writing to AI in English (H3b)", ...B.H3b },
    { label: "Perceived quality gap (H3c)", ...B.H3c }, { label: "Age 25 or over", ...B.covariates.Age25 },
    { label: "Started English-medium study or work", ...B.covariates.EventMove },
  ].map((x) => ({ label: x.label, b: x.b, lo: x.ci[0], hi: x.ci[1], on: x.p < .05,
                  tip: `${x.label}<br>b = <b>${f(x.b)}</b> ${ci(x.ci[0], x.ci[1])}, p ${fp(x.p)}` }));
  const spec = (key) => H.specs.map((s) => ({ label: s.label, b: s[key].b, lo: s[key].ci[0], hi: s[key].ci[1], on: s[key].p_holm < .05,
    tip: `${s.label} (n = ${s.n})<br>b = <b>${f(s[key].b)}</b> ${ci(s[key].ci[0], s[key].ci[1])}<br>Holm p ${fp(s[key].p_holm)}` }));
  const reg = card({ title: "What goes with the decrease", span2: true,
    sub: `Regression estimates with 95% CIs (n = ${B.n}); blue = p < 0.05. Units differ by measure (1–5 scales, standardised intensity, 0/1 indicators).` });
  const rob = card({ title: "Writing to AI in English, ten ways", sub: "Blue: significant after Holm’s correction. It holds in all ten." });
  const h4c = card({ title: "Decrease and difficulty, ten ways", sub: "Blue: significant after Holm’s correction. Positive in all ten; significant in four." });
  const rel = H.reliability;
  main.append(
    chapterHead("language", "Three measures of AI use were tested against the decrease. One of them matters: the language people write to AI in."),
    kpis([
      { n: `b = ${f(B.H3b.b)}`, l: `writing to AI in English, 95% CI ${ci(B.H3b.ci[0], B.H3b.ci[1])}, Holm p ${fp(B.H3b.p_holm)}` },
      { n: `b = ${f(B.H3a.b, 3)}`, l: `how much AI is used: no relation (p ${pe(B.H3a.p)})` },
      { n: `b = ${f(B.H3c.b)}`, l: `the quality gap people perceive: no relation (p ${pe(B.H3c.p)})` },
      { n: "10 of 10", l: "ways of checking in which the English effect holds" },
    ]),
    sec("Not how much, but in which language", reg,
      takeaway("The more often people write to AI in English, the more decrease they report. How much they use AI does not matter."),
      prose(`The model holds age and a move to English-medium study or work constant. The ${H.age25.n} respondents aged 25 or over reported little change `
        + `(${H.age25.no_change} reported none), which is why age carries a large estimate of its own.`)),
    sec("It holds every way we looked", rob,
      prose("Each row reruns the analysis with one choice made differently: another way of scoring the decrease, other covariates, without unusual respondents, "
        + `or in a narrower core sample. Writing to AI in English stays significant every time, even with English level held constant `
        + `(the two go together, ρ = ${f(H.english_share_vs_proficiency_rho)}) and with the blame people give social media held constant (Chapter 5).`)),
    sec("Is Arabic harder without AI?", grid(h4c, card({ title: "What respondents said", sub: "“Because of AI, has each of these become harder or easier for you, when you use Arabic on your own without AI?”" },
      prose("Finding the everyday word, speaking one’s dialect fluently, and saying what one means fully in Arabic. "
        + `Most respondents reported no change in difficulty; those who reported more decrease also tended to find Arabic harder (ρ = ${f(H.h4_spearman)}).`,
        `In the main analysis this falls just short of significance (p ${pe(B.H4.p)}). It is positive in every version and strong in the narrower sample; `
        + "one respondent whose answers run against the trend holds it down. Whether the decrease is the route from AI use to difficulty (H5) is borderline.")))),
    howWeKnow("Regression, robustness, mediation and reliability", h("div", null,
      h("div", { class: "prose" }, h("p", null, `Ordinary least squares with HC3 robust standard errors and t-based inference; the three AI-use measures were also tested jointly `
        + `(F(${B.joint.df.join(", ")}) = ${f(B.joint.F)}, p ${fp(B.joint.p)}). A wild bootstrap (9,999 resamples) confirmed the p-values `
        + `(writing to AI in English, Holm p ${fp(H.wild_holm.H3b)}), and a Firth logistic regression of any net decrease agreed (p ${pe(H.firth_english_p)}). `
        + `The influential respondent for H4 has a Cook’s distance of ${f(H.h4_influence.cooks_d)}.`)),
      table([{ label: "Mediation (H5)", get: (x) => x[0], class: "strong" }, { label: "All respondents", num: true, get: (x) => x[1] }, { label: "Core sample", num: true, get: (x) => x[2] }], [
        ["a: AI use → decrease", `${f(h5.primary.a, 3)} (p ${pe(h5.primary.a_p)})`, `${f(h5.core.a, 3)} (p ${pe(h5.core.a_p)})`],
        ["b: decrease → difficulty", `${f(h5.primary.b, 3)} (p ${pe(h5.primary.b_p)})`, `${f(h5.core.b, 3)} (p ${pe(h5.core.b_p)})`],
        ["indirect a × b [95% CI]", `${f(h5.primary.indirect, 3)} [${h5.primary.ci[0].toFixed(4)}, ${f(h5.primary.ci[1], 3)}]`, `${f(h5.core.indirect, 3)} [${f(h5.core.ci[0], 3)}, ${f(h5.core.ci[1], 3)}]`],
      ]),
      table([{ label: "Score", get: (x) => x[0], class: "strong" }, { label: "Items", num: true, get: (x) => x[1] },
             { label: h("span", { style: { textTransform: "none" } }, "McDonald’s ω [95% CI]"), num: true, get: (x) => x[2] },
             { label: h("span", { style: { textTransform: "none" } }, "Cronbach’s α"), num: true, get: (x) => x[3] }],
        [["Decrease (displacement)", "8 areas", rel.Displacement], ["Difficulty without AI", "3", rel.AbilityDecline], ["Perceived quality gap", "4", rel.QualityGap]]
          .map(([n, it, x]) => [n, it, `${f(x.omega)} ${ci(x.omega_ci[0], x.omega_ci[1])}`, f(x.alpha)])))),
    storyNav("language"));
  chart(reg.body, (p) => forest(p, { rows: coef, xName: "change in the decrease score per unit" }), 250, "Regression estimates");
  chart(rob.body, (p) => forest(p, { rows: spec("H3b") }), 360, "English share across specifications");
  chart(h4c.body, (p) => forest(p, { rows: spec("H4") }), 360, "H4 across specifications");
}

// ------------------------------------------------------------------ chapter 5
export function wider(main, S) {
  const C = S.context, sm = C.ai_vs_social, st = C.stable, u = C.started_university;
  const a = card({ title: "Because of AI, because of social media", sub: "Decrease attributed to each (higher = more). Social media was one overall question, so it is compared with AI averaged over the areas and over the formal areas." });
  const b = card({ title: "Who feels it", sub: "The decrease people attribute to AI, by whether they also attribute a decrease to social media." });
  const c = card({ title: "What else changed", sub: "Life events since regular AI use began (more than one allowed)." });
  const d = card({ title: "Work or study, by setting", sub: "Mean AI-attributed change in work/study Arabic (negative = less Arabic)." });
  main.append(
    chapterHead("wider", "Generative AI arrived in the middle of two other changes: a decade of social media, and, for most respondents, the move from school to university or work."),
    kpis([
      { n: `ρ = ${f(sm.rho)}`, l: "between the decrease people attribute to AI and to social media" },
      { n: `${sg(sm.social)} vs ${sg(sm.ai)}`, l: "social media vs AI, decrease averaged over the areas" },
      { n: `${C.under25_transition} of ${C.under25_n}`, l: "respondents under 25 who started university, graduated, began a job or started studying or working in English" },
    ]),
    sec("Social media came first", grid(a, b),
      takeaway("The same people feel both: social media moved everyday communication toward English, and AI carries the shift into work, study and writing."),
      prose(`Respondents who did not report a decrease from social media reported almost none from AI (${sg(C.non_blamers.mean)}), while those who did reported `
        + `${sg(C.blamers.mean)}. Writing to AI in English still predicts the decrease with social media held constant, so AI adds something of its own.`)),
    sec("A time of change", grid(c, d),
      prose(`Those who started university reported larger work/study decreases than the rest (${f(u.mean)} against ${f(u.rest_mean)}, p ${pe(u.p)}). `
        + `Yet among the ${st.n} whose study or work setting did not change, decreases still outnumbered increases (${st.less} against ${st.more}, p ${pe(st.sign_p)}): `
        + "a new setting adds to the change, but the decrease appears without one too.")),
    howWeKnow("How these comparisons were made", prose(
      `AI against social media: paired Wilcoxon test (p ${pe(sm.p)}; for the formal areas p ${pe(sm.formal_p)}); Spearman correlation ρ = ${f(sm.rho)}. `
      + `Those who also blame social media against those who do not: Mann–Whitney test (p ${pe(C.blamers_mw_p)}), exploratory. `
      + `Started university against the rest: Mann–Whitney test. Unchanged against changed setting: Mann–Whitney p ${pe(st.mw_p)}; the unchanged group includes `
      + `more people aged 25 or over, and adjusted for age the difference is not significant (p ${pe(st.age_adjusted_p)}).`)),
    storyNav("wider"));
  chart(a.body, (p) => groupedHbar(p, { labels: ["Averaged over the areas", "Formal areas"], fmt: (v) => sg(v),
    series: [{ name: "Because of AI", values: [sm.ai, sm.formal_ai], color: p.s1 }, { name: "Because of social media", values: [sm.social, sm.formal_social], color: p.s2 }] }), 200, "AI vs social media");
  chart(b.body, (p) => hbar(p, { labels: [`Also blame social media (${C.blamers.n})`, `Do not (${C.non_blamers.n})`],
    values: [C.blamers.mean, C.non_blamers.mean], color: p.s1, fmt: (v) => sg(v) }), 150, "Decrease by social-media attribution");
  chart(c.body, (p) => hbar(p, { labels: C.events.map((e) => e.label), values: C.events.map((e) => e.n), color: p.s3 }), 230, "Life events");
  chart(d.body, (p) => hbar(p, { labels: [`Started university (${u.n})`, `Everyone else (${u.rest_n})`, `Setting changed (${st.changed_n})`, `Setting unchanged (${st.n})`],
    values: [-u.mean, -u.rest_mean, -st.changed_mean, -st.mean], color: p.s2, fmt: (v) => f(-v),
    tip: (i) => ["Started university", "Everyone else", "Setting changed", "Setting unchanged"][i] + `: mean change <b>${f([u.mean, u.rest_mean, st.changed_mean, st.mean][i])}</b>` }), 230,
    "Work/study change by setting");
}
