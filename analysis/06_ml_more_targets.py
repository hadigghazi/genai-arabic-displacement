# -*- coding: utf-8 -*-
"""
RQ4 extension: the three ML targets listed before the data but not modelled in 05_ml.py, predicted from the
same inputs with the same machinery, judged against "usable model" criteria fixed before running
(ANALYSIS-DECISIONS.md, "ML extension", 2 Oct 2026 20:10).

  Targets   (1) Substitution: did something in English that could have been done in Arabic, because AI works
                better in English - "sometimes" or more (59) vs "never" / "once or twice" (46)
            (2) ExpectedLoss: number of the 8 two-year rows answered "less" or "much less" (0-8; regression)
            (3) AnyDifficulty: net difficulty - the mean of the three ability items on the "harder" side (34) vs not (71)
  Blocks    M0 background; M1 = M0 + AI use (the primary predictive model); M2 = M1 + quality gap (not for
            substitution: its wording makes the quality gap close to definitional); AI use only; M1 without
            the age dummy (23 respondents are 25+).
  Usable    all four: (1) linear M1 permutation p, Holm across the three targets, < .05; (2) over 10 other
            random splits, mean AUC >= .70 and no split < .65 (count: Q2 > 0 at every split and a significant
            paired gain over predicting the mean); (3) M1 without age still beats chance (permutation p < .05);
            (4) classification: balanced accuracy >= .65 averaged over the splits.

Everything above "main evaluation" in 05_ml.py (imports, settings, data preparation, models, cross-validation,
corrected tests, permutation tests, importance) is executed from that file, so the machinery is identical.

Run with Anaconda's Python:  C:\\Users\\User\\anaconda3\\python.exe analysis\\06_ml_more_targets.py
Set ML_QUICK=1 for a fast smoke test. Writes analysis/results/ml_more_targets.txt and ml_more_targets.csv.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, '05_ml.py'), encoding='utf-8') as f:
    _src = f.read()
_marker = '# ------------------------------------------------------------------ main evaluation'
assert _src.count(_marker) == 1
exec(compile(_src.split(_marker)[0], os.path.join(HERE, '05_ml.py'), 'exec'))

OUT = os.path.join(HERE, 'results', 'ml_more_targets.txt')
TABLE = os.path.join(HERE, 'results', 'ml_more_targets.csv')
PREV = os.path.join(HERE, 'results', 'ml_table.csv')            # 05_ml.py's results, for Holm across all targets

# ------------------------------------------------------------------ targets (definitions fixed before running)
for df in (ALL,):
    df['Substitution'] = (df.SwitchEng >= 3).astype(float).where(df.SwitchEng.notna())
    fut = df[[c for c in df.columns if c.startswith('Future_')]]
    df['ExpectedLoss'] = (fut <= -1).sum(axis=1).where(fut.notna().sum(axis=1) >= 6)
    df['AnyDifficulty'] = (df.AbilityDecline > 0).astype(float).where(df.AbilityDecline.notna())
prim = ALL.copy()                      # primary sample: all respondents (decision of 3 Oct 2026)
REG_TARGETS = REG_TARGETS | {'ExpectedLoss'}
TG = [('Substitution', 'clf', 'substitution (English instead of Arabic because of AI)'),
      ('ExpectedLoss', 'reg', 'expected loss in two years (count of domains)'),
      ('AnyDifficulty', 'clf', 'harder to use Arabic without AI (any)')]
SETS6 = {'M0 background': M0, 'M1 + AI use': M0 + AI, 'M2 + quality gap': M0 + AI + ['QualityGap']}
EXTRA6 = {'M1 without age': [c for c in M0 + AI if c != 'Age25'], 'AI use only': AI}
ALLSETS6 = dict(SETS6, **EXTRA6)
NAMES = ['linear', 'forest', 'boosting']
PRIMARY = 'M1 + AI use'


def blocks_for(tgt):
    return [s for s in SETS6 if not (tgt == 'Substitution' and s == 'M2 + quality gap')]


for tgt, kind, _ in TG:
    assert len({len(data(prim, tgt, c)[1]) for c in ALLSETS6.values()}) == 1, tgt
    if kind == 'clf':
        _, y = data(prim, tgt, M0)
        assert min(y.sum(), len(y) - y.sum()) >= MIN_CLASS, tgt

# ------------------------------------------------------------------ main evaluation
jobs = []
for tgt, kind, _ in TG:
    for sname in blocks_for(tgt):
        for mname in NAMES + (['baseline'] if sname == 'M0 background' else []):
            jobs.append((tgt, kind, sname, mname))
    for sname in EXTRA6:
        jobs.append((tgt, kind, sname, 'linear'))


def evaluate6(tgt, kind, sname, mname):
    cols = ALLSETS6[sname]
    X, y = data(prim, tgt, cols)
    return run_cv(kind, model(kind, mname, cols), X, y, splits(kind, y, R))


log('main evaluation: %d jobs' % len(jobs))
evaluate6_cached = MEM.cache(evaluate6)
results = dict(zip(jobs, Parallel(n_jobs=JOBS)(delayed(evaluate6_cached)(*j) for j in jobs)))
log('main evaluation done')

say('=' * 100)
say('RQ4 EXTENSION: the other targets listed before the data. All respondents (n=%d). %d x 5-fold CV%s; fixed models;' % (len(prim), R, ' [QUICK MODE: NOT FOR REPORTING]' if QUICK else ''))
say('SMOTENC inside training folds. Machinery executed from 05_ml.py. Criteria fixed before running: ANALYSIS-DECISIONS.md, "ML extension".')
with open(DATA, 'rb') as f:
    md5 = hashlib.md5(f.read()).hexdigest()
say('Python %s | numpy %s | scipy %s | scikit-learn %s | imbalanced-learn %s | scored.csv md5 %s' % (
    sys.version.split()[0], np.__version__, scipy.__version__, sklearn.__version__, imblearn.__version__, md5))
say('=' * 100)
say('')
say('TARGETS (primary sample: all respondents)')
for tgt, kind, lab in TG:
    _, y = data(prim, tgt, M0)
    if kind == 'clf':
        say('    %-14s n=%d  yes %d / no %d   %s' % (tgt, len(y), int(y.sum()), int(len(y) - y.sum()), lab))
    else:
        say('    %-14s n=%d  mean %.2f  SD %.2f  range %d-%d   %s' % (tgt, len(y), y.mean(), y.std(ddof=1), y.min(), y.max(), lab))
say('FEATURES')
for sname, cols in ALLSETS6.items():
    say('    %-18s %s' % (sname, ', '.join(cols)))
say('    M2 is not fitted for substitution: the item says "because AI helps you better in English", so the quality gap is close to definitional.')
say('')
say('Reading the tables: as in ml_results.txt. AUC = mean over the 50 test folds; PR-AUC, recall, balanced accuracy and')
say('BSS from pooled out-of-fold predictions; Q2 = 1 - MSE / Var(y) per fold. No interval on a single model.')

table = []
for tgt, kind, lab in TG:
    _, y = data(prim, tgt, M0)
    say('')
    say('-' * 100)
    say('%s  (%s)' % (lab.upper(), tgt))
    if kind == 'clf':
        say('    %-18s %-9s %-6s %-7s %-9s %-9s %-8s %-6s' % ('features', 'model', 'AUC', 'PR-AUC', 'rec yes', 'rec no', 'bal acc', 'BSS'))
    else:
        say('    %-18s %-9s %-6s %-6s %-6s' % ('features', 'model', 'Q2', 'MAE', 'RMSE'))
    for sname in ALLSETS6:
        for mname in NAMES + ['baseline']:
            if (tgt, kind, sname, mname) not in results:
                continue
            s = summary(kind, results[(tgt, kind, sname, mname)], y)
            if kind == 'clf':
                say('    %-18s %-9s %-6.2f %-7.2f %-9.2f %-9.2f %-8.2f %+.2f' % (sname, mname, s['main'], s['ap'], s['rec1'], s['rec0'], s['bacc'], s['bss']))
                if s['main'] > .90:
                    say('    LEAKAGE ALARM: AUC above .90 - investigate before reporting')
            else:
                say('    %-18s %-9s %+-6.2f %-6.2f %-6.2f' % (sname, mname, s['main'], s['mae'], s['rmse']))
            table.append(dict(target=tgt, kind=kind, n=len(y), prevalence=y.mean() if kind == 'clf' else np.nan,
                              features=sname, model=mname, score=s['main'], pr_auc=s.get('ap'), recall_yes=s.get('rec1'),
                              recall_no=s.get('rec0'), bal_acc=s.get('bacc'), brier_skill=s.get('bss'),
                              mae=s.get('mae'), rmse=s.get('rmse')))
    if kind == 'clf':
        say('    PR-AUC chance level = %.2f' % y.mean())

# ------------------------------------------------------------------ block comparisons
say('')
say('=' * 100)
say('BLOCK COMPARISONS (paired per-fold differences, Nadeau-Bengio corrected 95% CI)')
say('=' * 100)
for tgt, kind, lab in TG:
    say('    %s' % lab)
    steps = [('M1 - M0 (AI use)', 'M1 + AI use', 'M0 background')]
    if tgt != 'Substitution':
        steps.append(('M2 - M1 (quality gap)', 'M2 + quality gap', 'M1 + AI use'))
    for mname in NAMES:
        for step, a, b in steps:
            m, ci, p = nb_test(results[(tgt, kind, a, mname)]['main'] - results[(tgt, kind, b, mname)]['main'])
            say('        %-9s %-26s %+.3f [%+.3f, %+.3f]  p %s' % (mname, step, m, ci[0], ci[1], fmtp(p)))
    for step, a, b in [('AI use only - M0', 'AI use only', 'M0 background'), ('M1 without age - M1', 'M1 without age', 'M1 + AI use')]:
        m, ci, p = nb_test(results[(tgt, kind, a, 'linear')]['main'] - results[(tgt, kind, b, 'linear')]['main'])
        say('        %-9s %-26s %+.3f [%+.3f, %+.3f]  p %s' % ('linear', step, m, ci[0], ci[1], fmtp(p)))
    if kind == 'reg':
        for sname in ['M0 background', 'M1 + AI use']:
            m, ci, p = nb_test(results[(tgt, kind, sname, 'linear')]['main'] - results[(tgt, kind, 'M0 background', 'baseline')]['main'])
            say('        linear    %-26s %+.3f [%+.3f, %+.3f]  p %s' % (sname[:2] + ' vs predicting the mean', m, ci[0], ci[1], fmtp(p)))

say('')
say('FLEXIBLE VS LINEAR (the plan\'s decision rule: >= %.2f AUC / %.2f Q2 and corrected p < .05)' % (MARGIN_AUC, MARGIN_R2))
adds = {}
for tgt, kind, lab in TG:
    for sname in blocks_for(tgt):
        lin = results[(tgt, kind, sname, 'linear')]['main']
        for mname in ['forest', 'boosting']:
            m, ci, p = nb_test(results[(tgt, kind, sname, mname)]['main'] - lin)
            ok = m >= (MARGIN_AUC if kind == 'clf' else MARGIN_R2) and p < .05
            adds[(tgt, sname, mname)] = ok
            say('    %-44s %-18s %-9s %+.3f [%+.3f, %+.3f] p %s  -> %s' % (lab, sname, mname, m, ci[0], ci[1], fmtp(p),
                                                                       'ADDS SOMETHING' if ok else 'no'))

# ------------------------------------------------------------------ permutation tests
say('')
say('=' * 100)
say('BETTER THAN CHANCE? Permutation tests (outcome shuffled, whole pipeline refit, splits redrawn; statistic = the')
say('headline score over all %d repeats; %d permutations). Holm across the three targets for each block.' % (R_PERM, B_LIN))
say('=' * 100)
plan = []
for tgt, kind, lab in TG:
    for sname in ['M1 + AI use', 'M0 background', 'AI use only', 'M1 without age']:
        plan.append((tgt, kind, sname, 'linear', B_LIN))
    for sname in blocks_for(tgt):
        for mname in ['forest', 'boosting']:
            if adds[(tgt, sname, mname)]:
                plan.append((tgt, kind, sname, mname, B_FLEX))
perm = []
for tgt, kind, sname, mname, B in plan:
    cols = ALLSETS6[sname]
    X, y = data(prim, tgt, cols)
    obs, p, nullmean = perm_test(kind, model(kind, mname, cols), X, y, B)
    log('permutation %s %s %s: p=%.3f' % (tgt, sname, mname, p))
    perm.append(dict(target=tgt, kind=kind, features=sname, model=mname, obs=obs, null=nullmean, p=p, B=B))
perm = pd.DataFrame(perm)
for (sname, mname), g in perm.groupby(['features', 'model']):
    perm.loc[g.index, 'p_holm'] = multipletests(g.p, method='holm')[1]
for tgt, kind, lab in TG:
    say('    %s' % lab)
    for _, r in perm[perm.target == tgt].iterrows():
        say('        %-18s %-9s %s = %+.3f (null mean %+.3f)  p %s  p_Holm %s  (B=%d)' % (
            r.features, r.model, 'AUC' if kind == 'clf' else 'Q2', r.obs, r.null, fmtp(r.p), fmtp(r.p_holm), r.B))

# Holm across every target modelled (05's eight + these three), linear M1
holm11 = None
if os.path.exists(PREV):
    prev = pd.read_csv(PREV)
    prev = prev[(prev.features == 'M1 + AI use') & (prev.model == 'linear')][['target', 'perm_p']].dropna()
    new = perm[(perm.features == PRIMARY) & (perm.model == 'linear')][['target', 'p']].rename(columns={'p': 'perm_p'})
    allp = pd.concat([prev, new], ignore_index=True)
    allp['p_holm_all'] = multipletests(allp.perm_p, method='holm')[1]
    holm11 = allp.set_index('target')['p_holm_all']
    say('    Strictest check - Holm across all %d targets modelled (05_ml.py and this file), linear M1:' % len(allp))
    say('        ' + '  '.join('%s %s' % (t, fmtp(v)) for t, v in holm11.items()))
log('permutation tests done')

# ------------------------------------------------------------------ split-seed stability (linear M0 and M1)
def _seed6(tgt, kind, seed):
    out = {}
    for sname in ['M0 background', 'M1 + AI use']:
        cols = ALLSETS6[sname]
        X, y = data(prim, tgt, cols)
        res = run_cv(kind, model(kind, 'linear', cols), X, y, splits(kind, y, R, seed))
        s = summary(kind, res, y)
        out[sname] = (s['main'], s.get('bacc', np.nan))
    return out


say('')
say('SPLIT-SEED STABILITY (linear): the same %d x 5-fold CV on %d other random splits - mean (min to max)' % (R, SEEDS))
stab = {}
for tgt, kind, lab in TG:
    rs = Parallel(n_jobs=JOBS)(delayed(_seed6)(tgt, kind, SEED + 1000 * (i + 1)) for i in range(SEEDS))
    m0 = np.array([r['M0 background'][0] for r in rs]); m1 = np.array([r['M1 + AI use'][0] for r in rs])
    b1 = np.array([r['M1 + AI use'][1] for r in rs])
    stab[tgt] = dict(mean=m1.mean(), min=m1.min(), max=m1.max(), bacc=np.nanmean(b1) if kind == 'clf' else np.nan)
    txt = '    %-50s M0 %+.2f (%+.2f to %+.2f)   M1 %+.2f (%+.2f to %+.2f)' % (lab, m0.mean(), m0.min(), m0.max(), m1.mean(), m1.min(), m1.max())
    if kind == 'clf':
        txt += '   M1 balanced accuracy %.2f (%.2f to %.2f)' % (np.mean(b1), b1.min(), b1.max())
    say(txt)
log('seed stability done')

# ------------------------------------------------------------------ the usability verdict (criteria fixed before running)
say('')
say('=' * 100)
say('IS THERE A USABLE PREDICTIVE MODEL? (linear M1; criteria fixed before running)')
say('=' * 100)
verdicts = {}
for tgt, kind, lab in TG:
    pr = perm[(perm.target == tgt) & (perm.features == PRIMARY) & (perm.model == 'linear')].iloc[0]
    na = perm[(perm.target == tgt) & (perm.features == 'M1 without age') & (perm.model == 'linear')].iloc[0]
    st = stab[tgt]
    c1 = pr.p_holm < .05
    if kind == 'clf':
        c2 = st['mean'] >= .70 and st['min'] >= .65
        c2txt = 'mean AUC over splits %.2f (min %.2f): need >= .70 and min >= .65' % (st['mean'], st['min'])
        c4 = st['bacc'] >= .65
        c4txt = 'balanced accuracy over splits %.2f: need >= .65' % st['bacc']
    else:
        m, ci, p = nb_test(results[(tgt, kind, PRIMARY, 'linear')]['main'] - results[(tgt, kind, 'M0 background', 'baseline')]['main'])
        c2 = st['min'] > 0 and p < .05 and m > 0
        c2txt = 'Q2 over splits %.2f (min %.2f), gain over the mean %+.2f p %s: need min > 0 and p < .05' % (st['mean'], st['min'], m, fmtp(p))
        c4, c4txt = True, 'not applicable (count)'
    c3 = na.p < .05
    ok = c1 and c2 and c3 and c4
    verdicts[tgt] = ok
    say('    %s' % lab)
    say('        1 better than chance      %-5s  permutation p %s, Holm %s' % ('PASS' if c1 else 'fail', fmtp(pr.p), fmtp(pr.p_holm)))
    say('        2 not split luck          %-5s  %s' % ('PASS' if c2 else 'fail', c2txt))
    say('        3 not carried by age 25+  %-5s  without the age dummy: permutation p %s' % ('PASS' if c3 else 'fail', fmtp(na.p)))
    say('        4 classification          %-5s  %s' % (('PASS' if c4 else 'fail') if kind == 'clf' else 'n/a', c4txt))
    say('        -> %s' % ('USABLE (at this n, within this sample)' if ok else 'not usable'))
    if holm11 is not None and ok:
        say('        strictest check, Holm across all modelled targets: %s' % fmtp(holm11.get(tgt, np.nan)))

# ------------------------------------------------------------------ what a usable model uses; calibration
for tgt, kind, lab in TG:
    if not verdicts[tgt]:
        continue
    cols = ALLSETS6[PRIMARY]
    X, y = data(prim, tgt, cols)
    folds = splits(kind, y, R)
    res = run_cv(kind, model(kind, 'linear', cols), X, y, folds, keep=True)
    say('')
    say('    %s - grouped permutation importance (drop in per-fold %s when the block is shuffled):' % (lab, 'AUC' if kind == 'clf' else 'Q2'))
    for gname, drop in importance(kind, res, X, y, folds, cols):
        say('        %-44s %+.3f' % (gname, drop))
    full = model(kind, 'linear', cols, 'weight' if kind == 'clf' else 'smote').fit(X, y)
    coef = full.named_steps['model'].coef_.ravel()
    say('        standardised coefficients (fit on everyone%s; direction only):' % (', class-weighted, no oversampling' if kind == 'clf' else ''))
    say('        ' + '  '.join('%s %+.2f' % (c, b) for c, b in sorted(zip(cols, coef), key=lambda t: -abs(t[1]))))
    if kind == 'clf':
        for bal, blab in [('weight', 'class weights, no oversampling'), ('none', 'no imbalance handling')]:
            s = summary(kind, run_cv(kind, model(kind, 'linear', cols, bal), X, y, folds), y)
            say('        %-34s AUC %.2f  balanced accuracy %.2f  BSS %+.2f' % (blab, s['main'], s['bacc'], s['bss']))
    X40, y40 = data(ALL[ALL.core == 1], tgt, cols)
    s40 = summary(kind, run_cv(kind, model(kind, 'linear', cols), X40, y40, splits(kind, y40, R)), y40)
    say('        prim sample: %s %.2f%s' % ('AUC' if kind == 'clf' else 'Q2', s40['main'], ('  balanced accuracy %.2f' % s40['bacc']) if kind == 'clf' else ''))

say('')
say('runtime %.0f s' % (time.time() - T0))
pd.DataFrame(table).merge(perm[['target', 'features', 'model', 'p', 'p_holm']].rename(columns={'p': 'perm_p', 'p_holm': 'perm_p_holm'}),
                          on=['target', 'features', 'model'], how='left').round(4).to_csv(TABLE, index=False)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')
print('\n'.join(lines))
print('written to', OUT)
