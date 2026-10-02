# Analysis decisions

Decision log for the paper: every analysis choice, the alternatives considered, and where each alternative
is reported. Checked by independent audits and a number-by-number SPSS–Python cross-check (34 of 34
statistics agree; `crosscheck_spss.py`). Respondent ids are row numbers in the (unshared) data.

**How choices were made.** At each decision point the options were compared on construct validity,
statistical power at this sample size, and how well the choice holds up with a reviewer — not on which
gives the smaller p-value. Every alternative is reported as a labelled sensitivity analysis in
`results/python_stats.txt`. **Several alternatives change the Holm-adjusted Family B conclusions
(H3 English share, H4); those rows are marked "Differs", and the paper presents H3 and H4 as
dependent on the definition.** Family A (H1a, H1b, H2a) holds under every alternative.

**Documents written before the data** (first response 30 Sep 2026, 17:57): an analysis plan (27 Sep 2026)
and a study proposal with the codebook (30 Sep 2026); neither is included here. Neither was registered, so
the 27 Sep document is "the analysis plan written before data collection", not a pre-registration.

## Results at a glance (primary sample, n = 37)

| | Result | Holds under the alternatives? |
|---|---|---|
| H1a Fusha | Less Arabic: 16 less vs 3 more (16 of the 33 to whom Fusha applies, 48% — a net direction, not a majority); Wilcoxon z = −3.04, Holm p = .005 | Yes, every alternative |
| H1b work/study | Less Arabic: 25 less vs 0 more; z = −4.56, Holm p < .001 | Yes, except that the plan's own test — only people whose setting did not change — could not be run (proxy n = 8: 3 less vs 0 more, p = .25). The direction holds; a change of setting is not ruled out (decision 7) |
| H2a Fishman order | family < personal < work/study; Page one-sided exact p < .001; Friedman χ²(2) = 30.16, W = .44 | Yes, except the plan's stable-setting test, which could not be run (proxy n = 7, p = .062). The order also matches where AI is used, so it does not by itself confirm Fishman's account; H2b, which would, is not supported |
| H2b Fusha > dialect | Not supported (z = 1.14, p = .26) | — |
| H3 overall | Not supported: the three predictors jointly F(3,30) = 1.46, p = .24 (HC3) | Joint p between .16 and .60 under every alternative, except the 4-domain (.051) and dialect-only (.055) displacement |
| H3 English share | b = .22, p = .045, Holm .136 | **Differs**: positive in every specification; Holm-significant only with the plan's 4-domain displacement (.027) or dialect-only displacement (.036) |
| H4 | b = .44, p = .006, Holm .024; wild bootstrap Holm .0496 | **Differs**: not Holm-significant with no covariates (.18), the plan's age-only covariates (.087), the 4-domain displacement (.067), the dialect-only displacement (.14) or without id 13 (.29); with all 40, b = .12, unadjusted p = .73 |
| H5 | Not supported: a = −.06 (p = .55); indirect −.024, 95% CI [−.138, .041] | Underpowered at this n (see decision 16) |
| RQ4 (ML) | No evidence that AI-use information improves prediction (ΔQ² −.27, ΔAUC −.01; Holm p = .26, .94; AI use alone at chance). Background predicts the count above chance only through age (5 people) | **Yes for AI use**: the increment is never above +.02 in any sensitivity row and is negative at 10 of 10 and 9 of 10 random splits. **Differs for background**: without age neither overall target is predicted (p = .31, .44); any formal loss is borderline (p = .052) |

## Decisions

| # | Decision | Options | Chosen | Why | Where the alternative is reported |
|---|---|---|---|---|---|
| 1 | Primary sample | The 37 who grew up in and live in an Arabic-speaking country and have not moved country since 2022; or all 40 | **37 (core)** | Pre-specified: the 27 Sep plan (section 6.2) defines this CORE sample to hold migration constant, and the 30 Sep codebook tags the three country questions as the "CORE sample rule" (the proposal states the regional part). The first pass on 2 Oct used all 40; the analysis then returned to the plan's sample, knowing that this changes H4. Excluded: id 21 (grew up and lives outside the Arab world), id 25 (moved since 2022), id 38 (moved; lives outside) | Robustness (c), same models on all 40. **Differs for H4** (b = .12, p = .73), entirely because of id 21 (Cook's distance 1.78; without id 21, b = .43, p = .008) |
| 2 | Displacement score | Mean over all 8 domains (at least 6 applying); or the 27 Sep plan's 4 domains (writing, self, personal, family) | **8 domains** | The plan's 4-domain score was designed when work/study was asked only of people whose setting had not changed, Fusha and work/study were the separate H1 items, and religion and content were not yet measured. In the fielded form all 8 domains are asked of everyone, and the 30 Sep proposal frames displacement over all the RQ1 domains. **This departs from the plan.** The plan also treated displacement as a formative index (no alpha); in the data the domains covary strongly (mean inter-item r .48, alpha .88, omega .88 [.75, .93], n = 30 complete cases), so the score is read as one "AI-attributed domain loss" and alpha/omega are reported descriptively | Sensitivity rows "4-domain" and "dialect-only". **Differs**: with the 4-domain score, English share is Holm-significant (.027) and H4 is not (.067) |
| 3 | AI intensity | Share of work + breadth (the 27 Sep plan's definition); or also frequency (added in the first pass) | **Share of work + breadth, as planned** | The plan lists frequency as descriptive only. The plan's rule (drop a component with over 60% in one category) keeps both components: share of work, largest category 53% (49% in core); breadth 23%. Frequency has 33 of 40 (30 of 37) in its top category and barely varies | Sensitivity "intensity including frequency" (no change) |
| 4 | Ability decline (H4, H5) | 3 items asked of everyone (the plan); or 4 including the Fusha-register item, which applies only to the 28 of 37 (31 of 40) who wrote Fusha before AI | **3 items, as planned** | Every respondent's score uses the same items. Omega .83 [.62, .93] | Sensitivity "including the Fusha-register item" (H4 stronger: Holm .003); E3 analyses the register item on its own |
| 5 | Quality gap (H3) | 4 items including the AI-voice item (in the gap grid of the 30 Sep codebook); or the 27 Sep plan's 3 items, written before the voice item was added | **4 items** | Covers both channels of the study's framing — what people write to AI and what AI produces. **Departs from the 27 Sep plan**, whose own rule for the reversed item is applied (corrected item-total r = .47, above .20; kept) | Sensitivity "without the AI-voice item" (no change) |
| 6 | Multiple-testing correction | Holm within the plan's two families; or across all 8 domains | **The plan's families:** A = {H1a, H1b, H2a, H2b}; B = {the three H3 predictors, H4} | Correction matches the hypotheses tested. H2a's p is one-sided (Page's test of a predicted order); every other p is two-sided. Holm across 8 domains is shown on the descriptive profile as a strict check | RQ1 profile (p_Holm8 column) |
| 7 | H1b and H2a sample | Whole primary sample; or only respondents whose work/study setting did not change (the 27 Sep plan) | **Whole primary sample** | The plan's Status_Stable question was removed on 30 Sep and never asked, so the group can only be approximated from the life-events item: strict proxy (no new university, graduation or job; role not "other") n = 8; counting graduation as the same setting, as the plan's wording did, n = 16. With 8 people no test is informative (3 non-zero answers: smallest possible p .25) | Robustness (d): strict proxy −0.50 (exact p .25), Page one-sided exact p .062 (n = 7); graduation counted n = 16, −0.69, exact p .008. The raw "stable vs changed" gap (−0.50 vs −1.04, Mann-Whitney p = .061) is **confounded with age and cannot be tested**: 4 of the 8 strictly stable are aged 25+ and report no change, leaving 4 stable under-25s (−1.00 vs −1.04, n = 28; p = .92; adjusted for age, b = +0.22, p = .62 — too few to conclude anything). Exploratory, against it: those who started university during the period report more work/study loss (−1.31, n = 13 vs −0.70, n = 23; Mann-Whitney p = .016). The paper must say that change of setting is an open rival explanation for H1b |
| 8 | H1 test | Wilcoxon signed-rank (named in the 30 Sep proposal); or the exact sign test (the 27 Sep plan's specification) | **Wilcoxon**, sign test alongside | Uses the size of the change. **Departs from the 27 Sep plan**; the two tests agree everywhere | Same output lines |
| 9 | Covariates (H3–H5) | Age + EventMove; none; age only (the plan's small-sample rule); the plan's full set; + English level | **Age (25+) and EventMove** | Age is in the plan's confirmatory covariates and its small-sample rule. EventMove (in this sample: started English-medium study or work, n = 8; nobody ticked "moved") is the most direct rival explanation, also in the plan's set. Education medium could not be used: all 40 studied school science in English or French. Five predictors at n = 36 is the ceiling | Robustness (f). **Differs for H4**: no covariates Holm .18; age only Holm .087 |
| 10 | Regression inference | Classical OLS; HC3 | **HC3 with t(df) tests** | Small n and unequal spread. SPSS 23's REGRESSION has no HC3 option (GENLIN offers only HC0-type errors with Wald χ²), so the paper reports HC3 from Python and SPSS shows classical errors. The H3 omnibus is the joint test of the three H3 predictors, not the model F (the model's HC3 F is significant only because of the age dummy). A wild bootstrap (restricted, Rademacher, 9,999 reps) checks every Family B p | — |
| 11 | Mediation (H5) | PROCESS in SPSS; the same model in Python | **Python**: OLS paths, HC3 path tests, 5,000-resample percentile bootstrap, fixed seed, same covariates | SPSS 23 cannot run PROCESS (v5 needs SPSS 26+) | — |
| 12 | "Not applicable today" | Set that domain's change to missing; or only when the change answer is "no change" | **Set to missing** (written before the data; conservative) | It removes 7 "less" answers, all in the primary sample | Sensitivity (g): Fusha stronger (z = −3.47); H4 stronger (Holm .002) |
| 13 | Straight-liners (ids 13, 29: every change row "much less") | Keep; exclude | **Keep** | Answering at an extreme is not proof of carelessness. In practice this concerns id 13 only: id 29 marked work/study, formal texts and religion as not applicable, so it has 5 applicable domains, no displacement score and no work/study or Fusha change, and enters no confirmatory test | Robustness (e), i.e. without id 13. **Differs for H4**: b = .41, p = .078 (Holm .29) |
| 14 | Binary robustness (net loss) | Ordinary logit; Firth logit with covariates | **Firth logit** with the H3 predictors and covariates | Ordinary logit does not converge (the covariates separate the outcome; only 8 of 36 have no net loss). Even so, events per predictor are 1.6: indicative only. It does not support H3 (all p ≥ .26) | Robustness (b) |
| 15 | Standardisation of AI intensity | z on all 40; z on the 37 | **All 40** | Keeps SPSS (DESCRIPTIVES /SAVE on the open file) and Python identical; negligible difference | — |
| 16 | The 27 Sep plan's small-sample rule (section 7.6) | The rule: below N = 100, H5 becomes the single confirmatory test and H3/H4 keep only Medium and age; below ≈78, H5 is reported as underpowered and the paper leads with the domain profile | **Set aside on 2 Oct (after the data), except that H5 is reported as underpowered**; its machine-learning clause (logistic regression against the baseline only) is set aside too — see ML5 | Two families are kept because Family A is within-person and well powered (H1a, H1b and H2a all p < .005), and H3/H4 are what the paper's argument needs; H5 needs ≈78 even for medium paths and has 36. The paper still leads with the domain profile (Figure 1) | The rule's covariate set (age only) is run in robustness (f). **Differs for H4** (Holm .087) |

## Further notes

- **Sample size and collection.** 40 responses (37 analysed), collected 30 Sep 17:57 – 1 Oct 22:15, 2026 (36 on 30 Sep, 4 on 1 Oct). The plan aimed at about 150 collected and 120 analysed; collection was closed at 40, before any analysis. The smallest correlation detectable with 80% power is r = .45, so the H3–H5 results are weak evidence either way.
- **Launch before the scheduled checks.** The proposal scheduled back-translation for 1–2 Oct, the pretest for 2–3 Oct and the launch for 5 Oct. The form went live on 30 Sep, so the scheduled back-translation and pretest did not precede it, and the stated "about 7 minutes" was not pilot-timed. Only the author reviewed the wording before launch. The ethics statement is in the paper.
- **Items removed before launch.** The practice items, attention check and placebo (tea/coffee) row in the 27 Sep plan were dropped before 30 Sep. The 30 Sep prune removed the overall-influence question, the dialect-attachment grid, the pre-AI ability grid, the question on which form of Arabic people use with AI, and the question on whether they were already at their current workplace or university when they started using AI. The checks built on these could not be run. **The fielded change grids also lack the plan's reminder** ("'No change' means AI has not changed this for you, even if ... it changed for other reasons such as a new job, university or moving country"; 27 Sep plan, instrument section), so respondents were never told to exclude change with other causes — the only cue was "compare now with before you started using AI regularly".
- **Sample composition (analysed sample, n = 37).** Grew up in Lebanon 35, the Gulf 2; all 37 live in Lebanon; 32 are under 25; 26 work or study in computing; 28 wrote Fusha before AI. (All 40: grew up in Lebanon 37, live in Lebanon 38, under 25 35, computing 28, wrote Fusha 31.) Results describe young, mostly computing-trained Lebanese bilinguals.
- **Age.** 5 respondents are aged 25 or over (all in the primary sample). Four report no AI-attributed change in any domain; the fifth (id 34) reports less Arabic only in work or study (displacement 0.125, against a mean of 0.57 under 25). The age coefficient in H3 rests on these 5 people.
- **AI or technology in general.** People who report AI-attributed loss also report social-media-attributed loss (ρ = .56). Averaged over all 8 domains, social media is blamed for more loss than AI (+0.72 vs +0.49, p = .014); for the formal domains the two are equal (+0.72 vs +0.72, p = .65). Among the 15 who do not blame social media, AI-attributed displacement is small and not significant (+0.14, p = .25); among the 21 who do, +0.74 (Mann-Whitney p = .0002). With social-media attribution as a covariate, English share is no longer significant (p = .098). The data cannot separate an AI-specific effect from a general "technology is eroding my Arabic" belief — this is a limitation and an interesting result in its own right.
- **Exploratory, planned before the data.** E1 (switching as a second mediator): neither indirect effect differs from zero. E3: among the 28 who wrote Fusha before AI, a harder time writing formal Fusha goes with more displacement (Spearman ρ = .57, p = .002).
- **Influence.** H4's direction does not rest on one person, but **its Holm-level significance does**: dropping any one of three respondents pushes it past the Holm threshold of .0125 (without id 3, p = .018; without id 22, p = .013; without id 13, p = .078). H4 is therefore reported as positive in every core specification and Holm-significant in about half.
- **Tools.** SPSS 23 for descriptives, reliability, Wilcoxon, sign, Friedman and Mann-Whitney tests and classical regressions; Python (statsmodels, scipy) for HC3, Holm, Page's test, the bootstraps, the Firth logit, omega and exact p-values for groups with 15 or fewer non-zero answers (SPSS prints only the normal approximation there); scikit-learn and imbalanced-learn for the machine learning. Package versions are pinned in `requirements.txt`, and `ml_results.txt` records them with a checksum of the data.

## Machine learning (RQ4)

Script `05_ml.py`, output `results/ml_results.txt` and `results/ml_table.csv`. The two documents written
before the data differ: the 27 Sep plan (continuous target; fixed, untuned models; repeated CV with
Nadeau–Bengio corrected tests; a permutation test against chance; a decision rule for flexible models;
and a shortfall rule — below N = 100, logistic regression against the baseline only) and the 30 Sep
proposal (domain-loss targets; random forest and gradient boosting alongside logistic regression; tuning
in an inner CV loop; SMOTENC oversampling inside training folds; ROC-AUC, PR-AUC, per-class recall,
permutation importance).

**When the design was fixed.** The plan required the ML script to be written and run on simulated data
before launch, changing only the input path afterwards. That was not done: `05_ml.py` was written on
2 Oct, after the data, so the whole ML design is post hoc relative to the plan and is reported as such.
Before the first version was fixed, the class counts and one table of feature–target correlations were
seen. The first full run was then reviewed independently (four reviewers — leakage, statistics, code,
consistency with this record — a skeptic re-checking each reviewer's findings by rerunning code, and a
completeness critic): 15 findings, every one confirmed by its skeptic and none refuted, plus 4 from the
critic's own reruns. The design below is the revised one; the changes are listed after the table.

| # | Decision | Options | Chosen | Why |
|---|---|---|---|---|
| ML1 | Question | Does AI use predict domain loss at all; or does it add to background | **Does AI-use information improve out-of-sample prediction beyond background** (both documents) | A model that predicts only through age says nothing about AI. The test is the increment M1 − M0 |
| ML2 | Targets | Continuous displacement and NetLoss (plan); domains lost, any formal loss, single domains (proposal) | **The proposal's**: (a) number of domains lost (count, regression; n = 37); (b) any formal-domain loss (work/study or formal texts; 27 vs 9); (c) loss in each domain whose smaller class has at least 8 respondents | The proposal is the later document; (a) keeps the plan's preference for a continuous primary target. 8 is what SMOTENC's 5 neighbours need in every 5-fold training set; it drops family (7) and religion (3). (a) and (b) are the overall pair; (c) is secondary. The plan's own targets (4-domain displacement; NetLoss from it) and the 8-domain versions are sensitivity rows |
| ML3 | Features | The plan's nested sets; other lists | **The plan's sets, adapted to the fielded form.** M0 background: age 25+, computing field, education, English proficiency, started English-medium study/work. M1 = M0 + AI use: the plan's five (share of work, breadth, frequency, tenure, English share) and the proposal's two (exposure to AI-generated content, its language). M2 = M1 + quality gap | The plan's "Medium" is constant (all 40 studied school science in English or French) and is dropped; university language is 33 of 37 English (dropped); "survey version" does not apply. The plan's M1 is a sensitivity row. **Extra blocks** (linear model; permutation tests on the overall targets): *M0 without age* (5 people are 25+); *M0 + school language* — English- vs French-medium school science, **post hoc**: in neither document, it was put into the first version's M0 after the correlation table was seen, and is now exploratory only; *AI use only* — exploratory direct comparison with background. **Never features**: the change grid (the targets), current use, ability, expectations, substitution, switching, social-media attribution |
| ML4 | Tuning | Inner-loop tuning (proposal); fixed settings (plan) | **Fixed, the plan's settings**: L2 logistic / ridge (C = 1, α = 1); random forest (500 trees, leaf ≥ 5); histogram boosting (depth 2, rate .05, 100 iterations, leaf ≥ 10); dummy baseline | An inner fold here holds about 23 people: tuning would mostly fit noise and blur the M1 − M0 comparison. **Departs from the proposal** |
| ML5 | Primary model | All three equal (proposal); logistic against the baseline only (plan's shortfall rule) | **Linear model primary**; forest and boosting reported; block increments tested | **Departs from the plan's shortfall rule** (decided 2 Oct, after the data — see decision 16), because the proposal specifies the flexible models. They are judged by the plan's decision rule: a flexible model adds something only if it beats the linear one by ≥ .08 AUC (≥ .05 Q², the margin set here) with corrected p < .05; otherwise "no detectable nonlinear structure at this N" |
| ML6 | Imbalance | SMOTENC inside training folds (proposal); class weights (plan); none | **SMOTENC inside each training fold**, after scaling; plain SMOTE for a block with no binary feature | As specified in the proposal, done the valid way. SMOTENC gives a synthetic case's binary features the most common value among its 5 nearest same-class neighbours — with 6–8 minority cases per fold, close to the class mode — so coefficients for direction come from a class-weighted fit without oversampling. Class weights and no handling are sensitivity rows. Oversampling rebalances classes; it adds no information and does not raise the effective sample size. Done before splitting it leaks synthetic copies into the test folds — the output shows the inflated AUC, as a warning, not a result |
| ML7 | Validation and metrics | — | **10 × 5-fold CV** (stratified for classification), the same splits for every model and block. AUC = mean over the 50 test folds; for the count, Q² = 1 − MSE / Var(y) per fold. From each repeat's pooled out-of-fold predictions: PR-AUC (chance ≈ the share with loss), recall per class and balanced accuracy at 0.5, the Brier skill score against the training prevalence, MAE and RMSE. **No interval on a single model's score.** The same CV on 10 other split seeds shows how much the headline depends on the split | Per-fold scores pair across models, which the corrected test needs. With 7–8 people (1–2 in the minority class) per test fold, a per-fold interval for one model covers only about 86–90% in simulation, so chance is judged by permutation. The Brier skill score and RMSE are the plan's metrics; the skill score also shows that SMOTENC's probabilities are shifted (AUC, a ranking measure, is not affected) |
| ML8 | Inference | — | **Nadeau–Bengio corrected t on paired per-fold differences**: the RQ4 test is the linear M1 − M0 (Holm within the overall pair and within the domains), with its minimum detectable gain; also M2 − M1, flexible − linear, AI use only − M0, and, for the count, model − predicting the mean. **Permutation tests**: outcome shuffled, the whole pipeline refit, splits redrawn; the statistic is the headline score itself (all 10 repeats); 500 permutations; linear M0 and M1 for every target, the extra blocks for the overall targets; forest and boosting only where they pass the decision rule | A permutation test rejects "no association"; for the count it does not show that the model beats predicting the mean, which is tested separately. The paired corrected test is conservative here. Any AUC above .90 is treated as leakage |
| ML9 | Interpretation | — | Only primary-block models that beat chance after Holm, and an M1 model only if it also beats M0. Grouped permutation importance on held-out folds (correlated items shuffled together: AI intensity; AI content); class-weighted standardised coefficients for direction | "How the model uses inputs, not population effects" |
| ML10 | Sample | — | **Core 37** | Sensitivity rows: all 40; decision 12's not-applicable alternative; without the straight-liners (ids 13, 29) |

**What the review changed.** (1) School language left M0 (not pre-specified; see ML3). (2) The permutation
statistic had used 2 of the 10 repeats; with so few, which single domain passed Holm depended on the random
split (writing at the script's seed, work/study at another), so it now uses the full CV (500 instead of
1,000 permutations, for run time; smallest p .002). (3) Single-model intervals were dropped (under-coverage),
and PR-AUC now comes from pooled predictions: per-fold average precision in 7-person folds has a chance level
well above the share with loss. (4) The count's permutation p had been read as "beats predicting the mean";
that is now tested directly. (5) Added: the plan's Brier skill score and RMSE, the plan's actual targets
(the first run's "plan's targets" row had used the 8-domain scores), sensitivity rows for decisions 12 and
13, the M0-without-age, AI-only and compact-AI blocks, split-seed stability, the minimum detectable gain,
and the package versions and a data checksum in the output. (6) Direction coefficients come from
class-weighted fits; an M1 model's AI-feature importances are not interpreted unless M1 beats M0.

Note on oversampling: it is used, inside the training folds; it corrects class imbalance for the classifier
but cannot create information, so it does not fix the small sample.

**Results (core sample, linear model unless stated; `results/ml_results.txt`).**

- **No evidence that AI-use information improves prediction (RQ4 not supported).** Adding the AI-use block changes out-of-sample performance by ΔQ² −.27 [−.62, +.08] for domains lost and ΔAUC −.01 [−.34, +.32] for any formal loss (Holm p = .26 and .94). On 10 other random splits the change is negative at 10 of 10 and 9 of 10. AI use on its own predicts neither target better than chance (Q² −.36, p = .43; AUC .52, p = .40). Across every sensitivity row (all 40, decisions 12 and 13, the plan's AI block and targets, class weights or no imbalance handling) the AI-use increment is never above +.02. Adding the quality gap does not help either (ΔQ² −.09, ΔAUC −.06, both p > .3).
- **How large a gain could have been missed.** The corrected test has 80% power only for gains of about .50 Q² or .47 AUC, so on its own it cannot exclude even a large gain. A compact AI block — the two H3 predictors, intensity and English share — bounds the gain more tightly: ΔQ² −.03 [−.14, +.09], ΔAUC +.01 [−.20, +.23]. In words: no detectable improvement; gains above about .1 Q² are unlikely, and the AUC bound is wide — not "AI use has no effect".
- **Background predicts reported loss only through age.** Background is associated with the number of domains lost beyond chance (Q² .14, permutation p = .004, Holm .008), but its gain over simply predicting the mean is not established (+.20 [−.15, +.56], p = .26), and without the age-25+ dummy — 5 people, 4 of whom report no change anywhere — the association disappears (Q² −.17, p = .31). For any formal loss, background is borderline (AUC .71, p = .052; without age .52). Among single domains only writing is predicted above chance after Holm (AUC .76, Holm .036; .71–.76 across splits), again mainly through age; work/study, self-talk, personal matters and following content are not (Holm .32–.46), and Fusha is at chance (.40).
- **Domain pattern of the AI block (descriptive).** Its contribution is positive at all 10 splits for self-talk (+.05), personal matters (+.08) and Fusha (+.08), and negative at all 10 for writing (−.14) and following content (−.16) — none significant (Holm ≥ .25). Not to be interpreted beyond "no domain shows a reliable gain".
- **Flexible models: no detectable nonlinear structure at this N.** Forest and boosting never pass the decision rule and are often clearly worse (e.g. writing: −.35 AUC, p = .001).
- **What the background models use** (models that beat chance after Holm): for domains lost, age 25+ (older: less loss) far ahead of computing field (less loss) and education; for writing, age 25+, then starting English-medium study or work (more loss) and English proficiency (more loss).
- **School language (post hoc, exploratory).** Adding English- vs French-medium school science raises prediction (domains lost Q² .22; any formal loss AUC .83, p = .006): French-schooled respondents report more loss (3.9 vs 2.7 domains; Mann-Whitney p = .14 on its own) and lower English proficiency (3.1 vs 4.0). This contrast was chosen after the data and is partly entangled with the not-applicable rule: all 7 respondents with fewer than 8 applicable domains are English-schooled. A hypothesis for future work, not a finding.
- **Probabilities.** The Brier skill scores are small or negative (any formal loss +.05; +.20 without oversampling): SMOTENC shifts the predicted probabilities, so the models rank people but do not give usable risk estimates.
- **Oversampling before the split** raises the apparent AUC for any formal loss from .70 to .90 (linear) and from .56 to .80 (forest) — the leakage the design avoids, and the answer to "can oversampling fix the small sample": it can only make the numbers look better.

In short: the ML agrees with H3. No measure of how people use AI — intensity, language, tenure, exposure to AI content, the quality gap — improved prediction of who reports AI-attributed domain loss; what little is predictable comes from age, and that rests on 5 respondents. At n = 37 the evidence bounds only large gains, so the conclusion is "no detectable predictive value of AI use", with the sample size as the main limitation.


### ML extension: the other targets listed before the data (pre-specified 2 Oct 2026, 20:10, before any model on them was run)

Notes written before launch listed, besides the domain-loss targets above, three
more targets, all predicted from the same inputs (background + AI use): **substitution** (the original primary
target), **expected loss in the next two years**, and **"harder to use Arabic without AI"**. None was modelled in
`05_ml.py`. They are run in `06_ml_more_targets.py` with the same machinery (same blocks, models, SMOTENC inside
the folds, 10 × 5 CV, Nadeau–Bengio tests, permutation tests on the full CV, 10-seed stability check). Fixed now,
before running:

- **Targets** (core sample). (1) *Substitution*: SwitchEng "sometimes" or more vs "never" / "once or twice" — the cut
  fixed before the data (its pre-data rule, move the cut if over 85% fall above it, does not apply: 25 of 37);
  25 vs 12. (2) *Expected loss*: number of the 8 two-year rows answered "less" or "much less" (0–8, mean 3.7;
  regression, the same form as the domains-lost target). The pre-data list said "yes/no per domain"; one count
  is used instead to keep the number of tests down, and the yes/no "any expected loss" split is 30 vs 7, too
  unbalanced. (3) *Any AI-attributed difficulty*: AbilityDecline above 0 (the mean of the three ability items on the
  "harder" side; here identical to "any item harder", 12 = 12); 12 vs 25.
- **Blocks**: M0 background, M1 = M0 + AI use (the primary predictive model), AI use only, M1 without the age
  dummy. M2 (+ quality gap) is reported for (2) and (3) only: for substitution it is close to definitional (the
  item states "because AI helps you better in English"), as noted before the data.
- **What "usable" means** — a model counts as a usable predictive model only if it meets all four:
  1. better than chance: permutation p, Holm-adjusted across the three new targets, below .05 (linear M1);
  2. not split luck: averaged over 10 other random splits, AUC at least .70 with no split below .65 (for the
     count: Q² above 0 at every split, and a significant gain over predicting the mean in the paired test);
  3. not carried by the 5 respondents aged 25+: the same model without the age dummy still beats chance
     (permutation p below .05);
  4. classification only: balanced accuracy at least .65 (averaged over splits).
  If no target meets all four, the result is reported as such; no further targets or settings are tried.
- **Multiplicity, stated in the paper**: with these, 11 targets were modelled in total. Holm across all 11 is
  reported as the strictest check.
- **Seen before this point**: the target distributions above; for target (3), the H5 total effect of AI
  intensity on ability decline (c = −.10, not significant). No other association between these targets and the
  features had been computed.

**Result (`06_ml_more_targets.py`, `results/ml_more_targets.txt`): no usable model.** No target meets any of the
four criteria (linear M1; permutation Holm p = 1.00 for all three):
- *Substitution*: AUC .32 (background alone .29), below chance at every split (.31–.36); balanced accuracy .40.
  Fitted and scored on the same 37 people the model reaches AUC .79 — the gap is overfitting 12 features to 37
  people. The below-chance value is a known cross-validation artefact when features carry no signal (it falls
  inside the permutation null, 3rd–10th percentile; an independent from-scratch reproduction confirmed the numbers,
  the label orientation and the mechanism). No feature relates strongly to substitution (all |ρ| ≤ .29; English
  share +.04). Do not present it as an inverse relationship.
- *Expected loss in two years*: background alone predicts no better than the mean (Q² +.02; gain over the mean
  +.05, p = .78); adding AI use makes it worse (ΔQ² −.62 [−1.18, −.06], p = .03 — overfitting, not a finding).
- *Any AI-attributed difficulty*: AUC .54 (background .57), permutation p = .37; balanced accuracy .49.
- Holm across all 11 targets modelled: smallest adjusted p .42.
- The same verdict holds with class weights or no imbalance handling (SMOTENC lowers the substitution AUC by
  about .07).

**The closest candidate in the whole project fails too.** Writing loss from background (`05_ml.py`) passes the
chance and split-stability criteria (Holm .036; AUC .73 averaged over 10 other splits, range .71–.76) but fails
criterion 3: without the age dummy its AUC is .51 (permutation p = .50) — it only learns that the 5 respondents
aged 25+ report no loss — and its balanced accuracy is .63. Checked after its results were known
(`results/writing_check.py`); reported as a check, not as a new test. Single AI-use items on their own
(frequency, breadth, share of work: AUC about .62, unadjusted p ≥ .06, picked after seeing the data) are
exploratory associations at most.

**In short**: across every target listed before the data, background and self-reported AI use do not give a
usable predictive model at n = 37. This is the ML result, reported with the leakage demonstration; no further targets or settings were tried.

**Oversampling check (`07_oversampling_check.py`, `results/oversampling_check.txt`).** To test whether a different
or stronger oversampling could produce a usable model, six strategies were compared with no oversampling on the
four most promising binary targets (background + AI use, linear model, same splits): class weights, random
duplication, SMOTENC to balance, SMOTENC amplified (both classes grown to 5x the majority), SMOTENC + Tomek
cleaning, and noise augmentation (5 jittered copies of everyone). Applied correctly, inside the training folds,
none improves on no oversampling (best +.04 AUC; Holm across 24 comparisons, all 1.00), and amplification makes it
worse (−.17 and −.13). The best valid result (noise augmentation, any formal loss, AUC .74 across splits) fails
the age criterion: without the age dummy it is .57, permutation p = .30. Applied the leaky way — resample
everything, then cross-validate — every target looks usable, up to AUC .96, including substitution, which has no
signal at all (.32 valid, .84 leaky). In short: oversampling cannot add information; done before splitting
it manufactures a model from nothing.

## Cannot be checked from the data

- Whether the respondent who started using AI in 2026 met the 6-month rule (start month not asked).
- Completion times (Google Forms does not record them).
- Whether "not applicable today" together with "much less because of AI" means stopping because of AI, or a misreading.
