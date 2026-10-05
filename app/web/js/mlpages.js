// Machine learning: cross-validated results, the usability criteria, the oversampling check.
import { h, f, sg, fp, pe, ci, pageHead, kpis, card, grid, table, callout, flag, link } from "./ui.js";
import { chart, dots, forest, groupedHbar, hbar } from "./charts.js";

const CRIT = ["Beats chance", "Stable across splits", "Not carried by age", "Classifies"];

export function results(main, S) {
  const T = S.ml.targets, clf = T.filter((t) => t.kind === "clf"), usable = T.filter((t) => t.usability.usable);
  const formal = T.find((t) => t.id === "AnyFormalLoss");
  main.append(
    pageHead("Machine learning · RQ4", "Predicting who reports a decrease",
      "Linear models (L2 logistic or ridge regression) predict each outcome from background answers, from AI-use answers, or from both, "
      + "and are tested on people they were not trained on: repeated 10×5-fold cross-validation, with oversampling (SMOTENC) inside the training folds only. "
      + "Random forests and gradient boosting were run too and never beat the linear models."),
    kpis([
      { n: usable.length, l: `usable models, meeting all four criteria fixed in advance (${usable.map((t) => t.label.toLowerCase()).join("; ")})` },
      { n: formal.blocks.with_ai.score.toFixed(2), l: "AUC for any formal-domain decrease (0.50 = chance)" },
      { n: sg(formal.delta_ai.d), l: `AUC gained by adding AI-use answers to background, 95% CI ${ci(formal.delta_ai.ci[0], formal.delta_ai.ci[1])}` },
      { n: S.ml.min_detectable_gain.auc.toFixed(2), l: "smallest AUC gain the comparison could detect with 80% power" },
    ]));
  const c1 = card({ title: "How well each outcome is predicted", span2: true,
    sub: "Cross-validated AUC: the chance that the model ranks a person who reported the decrease above one who did not. Dashed lines: chance (0.50) and the usability threshold (0.70)." });
  const rows = T.map((t) => ({ t, ...t.usability }));
  const c2 = card({ title: "The four usability criteria", span2: true,
    sub: "Fixed before the models were run on the full sample: 1 better than chance after Holm’s correction; 2 mean AUC ≥ 0.70 over ten other random splits, none below 0.65 (for a count, Q² > 0 throughout and a significant gain over the mean); 3 still above chance without the age question; 4 balanced accuracy ≥ 0.65." },
    table([
      { label: "Outcome", get: (r) => r.t.label, class: "strong" },
      { label: "Score", num: true, get: (r) => `${r.t.metric} ${f(r.t.blocks.with_ai.score)}` },
      ...CRIT.map((name, i) => ({ label: `${i + 1} ${name}`, get: (r) => {
        const c = r.criteria[i];
        return c.result === "n/a" ? h("span", { class: "muted" }, "n/a") : flag(c.result === "PASS" ? "pass" : "fail", c.result === "PASS" ? "good" : "bad");
      } })),
      { label: "Usable", get: (r) => (r.usable ? flag("usable", "good") : h("span", { class: "muted" }, "no")) },
    ], [{ group: "Outcomes listed in the proposal" }, ...rows.filter((r) => r.t.set === "main"),
        { group: "Further outcomes named before data collection" }, ...rows.filter((r) => r.t.set === "further")]));
  const c3 = card({ title: "What AI-use answers add", sub: "Change in AUC from background alone to background plus AI use, with 95% CIs (Nadeau–Bengio corrected). None is significant after correction." });
  const imp = S.ml.importance.AnyFormalLoss;
  const c4 = card({ title: "What the background model relies on", sub: "Any formal-domain decrease: drop in AUC when one input is shuffled on held-out people." });
  main.append(c1, c2, grid(c3, c4),
    callout(h("b", null, "Reading this. "), "AI-use answers alone predict about as well as background alone, so the two carry overlapping information: "
      + "English level (background) goes with writing to AI in English (AI use). The models are validated within this sample only. ",
      link("model", "Try them with your own answers"), "."));
  const dotsRows = clf;
  chart(c1.body, (p) => dots(p, { labels: dotsRows.map((t) => t.label), min: 0.4, max: 0.85,
    refs: [{ x: 0.5, label: "chance" }, { x: 0.7, label: "usable" }],
    series: [
      { name: "Background", values: dotsRows.map((t) => t.blocks.background.score), color: p.muted },
      { name: "Background + AI use", values: dotsRows.map((t) => t.blocks.with_ai.score), color: p.s1, symbol: "diamond" },
      { name: "AI use only", values: dotsRows.map((t) => t.blocks.ai_only.score), color: p.s2, symbol: "triangle" },
    ] }), 34 * dotsRows.length + 50, "AUC by outcome and feature set");
  chart(c3.body, (p) => forest(p, { rows: clf.map((t) => ({ label: t.label, b: t.delta_ai.d, lo: t.delta_ai.ci[0], hi: t.delta_ai.ci[1], on: false,
    tip: `${t.label}<br>ΔAUC <b>${sg(t.delta_ai.d)}</b> ${ci(t.delta_ai.ci[0], t.delta_ai.ci[1])}, p ${pe(t.delta_ai.p)}` })), xName: "change in AUC" }),
    30 * clf.length + 40, "AUC gain from AI-use answers");
  chart(c4.body, (p) => hbar(p, { labels: imp.map((x) => x.feature), values: imp.map((x) => x.drop), color: p.s1, fmt: (v) => sg(v, 3) }),
    200, "Permutation importance");
}

export function oversampling(main, S) {
  const O = S.oversampling;
  main.append(
    pageHead("Machine learning · check", "Oversampling cannot create information",
      "Six ways of rebalancing the classes were compared with none, applied correctly (inside the training folds) and incorrectly "
      + "(to everyone before the data are split, so synthetic copies of test people leak into training)."),
    kpis([
      { n: sg(Math.max(...O.flatMap((o) => o.rows.filter((r) => r.gain !== undefined).map((r) => r.gain)))), l: "best AUC gain from any strategy applied correctly (Holm p = 1.00 across 24 comparisons)" },
      { n: Math.max(...O.flatMap((o) => o.rows.map((r) => r.leaky_auc || 0))).toFixed(2), l: "highest AUC reached by oversampling before the split: an illusion" },
      { n: S.ml.leakage_demo.inside.toFixed(2) + " → " + S.ml.leakage_demo.leaky.toFixed(2), l: "the same model, before and after leaking SMOTENC copies into the test folds" },
    ]));
  const cards = O.map((o) => {
    const c = card({ title: o.target, sub: `${o.n} respondents, ${o.yes} reported it. Valid: rebalancing inside the training folds. Invalid: rebalancing everyone before splitting.` });
    c.draw = () => chart(c.body, (p) => groupedHbar(p, { labels: o.rows.map((r) => r.strategy), min: 0.4, max: 1, fmt: (v) => v.toFixed(2),
      series: [{ name: "Valid", values: o.rows.map((r) => r.auc), color: p.s1 },
               { name: "Invalid (leaky)", values: o.rows.map((r) => (r.leaky_auc === undefined ? null : r.leaky_auc)), color: p.s2 }] }), 330, o.target);
    return c;
  });
  main.append(grid(cards[0], cards[1]), grid(cards[2], cards[3]),
    callout(h("b", null, "Why the invalid AUC climbs. "), "A synthetic case is built from real neighbours. If it is made before the split, "
      + "near-copies of a test person sit in the training data, and the model recognises them rather than predicting them. "
      + "The more synthetic data, the higher the false accuracy. Correctly applied, oversampling only rebalances the classes."));
  cards.forEach((c) => c.draw());
}
