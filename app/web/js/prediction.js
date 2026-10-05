// Chapter 6: can we predict who reports a decrease? Cross-validated models, the usability rules, oversampling.
import { h, f, sg, fp, pe, ci, kpis, card, grid, table, flag } from "./ui.js";
import { chart, dots, forest, groupedHbar, hbar } from "./charts.js";
import { chapterHead, sec, prose, takeaway, howWeKnow, storyNav } from "./story.js";

const CRIT = ["Beats chance", "Stable", "Not just age", "Classifies"];

export function prediction(main, S) {
  const T = S.ml.targets, clf = T.filter((t) => t.kind === "clf"), usable = T.filter((t) => t.usability.usable);
  const formal = T.find((t) => t.id === "AnyFormalLoss");
  const O = S.oversampling;
  const auc = card({ title: "How well each outcome is predicted", span2: true,
    sub: "AUC on people the model was not trained on: the chance that it ranks someone who reported the decrease above someone who did not. Dashed lines: chance (0.50) and the usability threshold (0.70)." });
  const rules = card({ title: "Four rules, fixed before the models were run", span2: true,
    sub: "1 better than chance after correcting for the many outcomes; 2 mean AUC of at least 0.70 over ten other random splits, none below 0.65; 3 still better than chance without the age question; 4 balanced accuracy of at least 0.65." },
    table([
      { label: "Outcome", get: (r) => r.t.label, class: "strong" },
      { label: "Score", num: true, get: (r) => `${r.t.metric} ${f(r.t.blocks.with_ai.score)}` },
      ...CRIT.map((name, i) => ({ label: `${i + 1} ${name}`, get: (r) => {
        const c = r.criteria[i];
        return c.result === "n/a" ? h("span", { class: "muted" }, "n/a") : flag(c.result === "PASS" ? "pass" : "fail", c.result === "PASS" ? "good" : "bad");
      } })),
      { label: "Usable", get: (r) => (r.usable ? flag("usable", "good") : h("span", { class: "muted" }, "no")) },
    ], T.map((t) => ({ t, ...t.usability }))));
  const gain = card({ title: "What AI-use answers add", sub: "Change in AUC from background alone to background plus AI use, with 95% CIs. None is significant." });
  const imp = S.ml.importance.AnyFormalLoss;
  const relies = card({ title: "What the background model relies on", sub: "Any formal-domain decrease: drop in AUC when one input is shuffled on held-out people." });
  const ov = [O[0], O[2]].map((o) => {
    const c = card({ title: o.target, sub: `${o.n} respondents, ${o.yes} reported it.` });
    c.draw = () => chart(c.body, (p) => groupedHbar(p, { labels: o.rows.map((r) => r.strategy), min: 0.4, max: 1, fmt: (v) => v.toFixed(2),
      series: [{ name: "Valid (inside the training folds)", values: o.rows.map((r) => r.auc), color: p.s1 },
               { name: "Invalid (before the split)", values: o.rows.map((r) => (r.leaky_auc === undefined ? null : r.leaky_auc)), color: p.s2 }] }), 320, o.target);
    return c;
  });
  const maxLeak = Math.max(...O.flatMap((o) => o.rows.map((r) => r.leaky_auc || 0)));
  const bestGain = Math.max(...O.flatMap((o) => o.rows.filter((r) => r.gain !== undefined).map((r) => r.gain)));
  main.append(
    chapterHead("prediction", "If the language of AI use goes with the decrease, can answers about AI use predict who will report it? "
      + "Thirteen outcomes were modelled and judged by four rules written down before the models were run."),
    kpis([
      { n: usable.length, l: "usable models: any formal-domain decrease, work or study, self-talk" },
      { n: f(formal.blocks.with_ai.score), l: "AUC for any formal-domain decrease (0.50 = chance)" },
      { n: sg(formal.delta_ai.d), l: `AUC added by AI-use answers, 95% CI ${ci(formal.delta_ai.ci[0], formal.delta_ai.ci[1])}` },
    ]),
    sec("Three outcomes can be predicted", auc,
      takeaway("Answers about background and AI use identify who reports a decrease in formal areas, in work or study and in self-talk, with moderate accuracy.")),
    sec("Judged by rules fixed in advance", rules,
      prose("A model counts as usable only if it passes all four rules. The rules were written before the models were run on the full sample, "
        + "so no threshold was chosen after seeing which model would clear it.")),
    sec("Background and AI use overlap", grid(gain, relies),
      prose("Answers about AI use alone predict about as well as background alone, and adding one to the other changes little. "
        + "The two carry overlapping information: English level, a background answer, goes with writing to AI in English. "
        + `The comparison could detect gains of about ${f(S.ml.min_detectable_gain.auc)} AUC, so small gains cannot be ruled out.`)),
    sec("A note on oversampling",
      prose("With few people in some groups, it is tempting to create synthetic respondents. Six ways of doing so were compared with none, "
        + "applied correctly, inside the training data only, and incorrectly, to everyone before the data are split."),
      grid(ov[0], ov[1]),
      takeaway(`Applied correctly, oversampling gained at most ${sg(bestGain)} AUC. Applied before the split, it reached ${f(maxLeak)}: synthetic copies of test people leak into training, and the model recognises them instead of predicting them.`)),
    howWeKnow("Models, validation and tests", h("div", { class: "prose" }, h("ul", null,
      h("li", null, h("b", null, "Question: "), "does information about AI use improve prediction beyond background characteristics (age, field, education, English level, an English-medium start)?"),
      h("li", null, h("b", null, "Models: "), "L2 logistic or ridge regression with fixed settings; random forests and gradient boosting as checks, which never beat the linear models."),
      h("li", null, h("b", null, "Validation: "), "repeated 10×5-fold cross-validation, with SMOTENC oversampling inside the training folds only."),
      h("li", null, h("b", null, "Tests: "), "Nadeau–Bengio corrected t-tests for comparisons between models; permutation tests (500, the whole pipeline refitted) against chance; Holm’s correction."),
      h("li", null, h("b", null, "Usable models, across all 13 outcomes: "), `Holm p ${fp(S.ml.holm_13.AnyFormalLoss)} for each of the three.`)))),
    storyNav("prediction"));
  chart(auc.body, (p) => dots(p, { labels: clf.map((t) => t.label), min: 0.4, max: 0.85,
    refs: [{ x: 0.5, label: "chance" }, { x: 0.7, label: "usable" }],
    series: [
      { name: "Background", values: clf.map((t) => t.blocks.background.score), color: p.muted },
      { name: "Background + AI use", values: clf.map((t) => t.blocks.with_ai.score), color: p.s1, symbol: "diamond" },
      { name: "AI use only", values: clf.map((t) => t.blocks.ai_only.score), color: p.s2, symbol: "triangle" },
    ] }), 34 * clf.length + 50, "AUC by outcome");
  chart(gain.body, (p) => forest(p, { rows: clf.map((t) => ({ label: t.label, b: t.delta_ai.d, lo: t.delta_ai.ci[0], hi: t.delta_ai.ci[1], on: false,
    tip: `${t.label}<br>ΔAUC <b>${sg(t.delta_ai.d)}</b> ${ci(t.delta_ai.ci[0], t.delta_ai.ci[1])}, p ${pe(t.delta_ai.p)}` })), xName: "change in AUC" }),
    30 * clf.length + 40, "AUC gain from AI-use answers");
  chart(relies.body, (p) => hbar(p, { labels: imp.map((x) => x.feature), values: imp.map((x) => x.drop), color: p.s1, fmt: (v) => sg(v, 3) }), 200, "Permutation importance");
  ov.forEach((c) => c.draw());
}
