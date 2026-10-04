# -*- coding: utf-8 -*-
"""
Applies the four usable-model criteria (fixed 2 Oct 2026 for the extension targets, and on 3 Oct 2026 extended in
advance to every ML target) to the targets of 05_ml.py, for the linear background + AI-use model (M1):

  1 better than chance: permutation p for linear M1, Holm-adjusted within 05's families (the overall pair; the
    domains), below .05 - read from results/ml_table.csv;
  2 not split luck: over 10 other random splits, mean AUC >= .70 and none below .65 (count: Q2 > 0 at every split
    and a significant paired gain over predicting the mean);
  3 not carried by the respondents aged 25+: M1 without the age dummy still beats chance (permutation p < .05);
  4 classification: balanced accuracy >= .65 averaged over the 10 splits.

Machinery executed from 05_ml.py (same models, SMOTENC inside the folds, cached permutation tests).
Run with Anaconda's Python:  C:\\Users\\User\\anaconda3\\python.exe analysis\\08_usability_main_targets.py
Writes analysis/results/ml_usability.txt.
"""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, '05_ml.py'), encoding='utf-8') as f:
    _src = f.read()
exec(compile(_src.split('# ------------------------------------------------------------------ main evaluation')[0],
             os.path.join(HERE, '05_ml.py'), 'exec'))

OUT = os.path.join(HERE, 'results', 'ml_usability.txt')
prim = ALL.copy()
TG, _ = targets(prim)
M1 = M0 + AI
M1_NOAGE = [c for c in M1 if c != 'Age25']
tab = pd.read_csv(os.path.join(HERE, 'results', 'ml_table.csv'))


def _seed(tgt, kind, seed):
    X, y = data(prim, tgt, M1)
    res = run_cv(kind, model(kind, 'linear', M1), X, y, splits(kind, y, R, seed))
    s = summary(kind, res, y)
    return s['main'], s.get('bacc', np.nan)


say('=' * 100)
say('USABLE-MODEL CRITERIA for the targets of 05_ml.py (linear background + AI use, all respondents, n=%d)%s'
    % (len(prim), ' [QUICK MODE: NOT FOR REPORTING]' if QUICK else ''))
say('=' * 100)
rows = []
for tgt, kind, lab, fam in TG:
    hit = tab[(tab.target == tgt) & (tab.features == 'M1 + AI use') & (tab.model == 'linear')]
    p_holm = float(hit.perm_p_holm.iloc[0])
    rs = np.array(Parallel(n_jobs=JOBS)(delayed(_seed)(tgt, kind, SEED + 1000 * (i + 1)) for i in range(SEEDS)))
    X, y = data(prim, tgt, M1_NOAGE)
    _, p_noage, _ = perm_test(kind, model(kind, 'linear', M1_NOAGE), X, y, B_LIN)
    log('%s done' % tgt)
    c1 = p_holm < .05
    if kind == 'clf':
        c2 = rs[:, 0].mean() >= .70 and rs[:, 0].min() >= .65
        c2txt = 'AUC over splits %.2f (%.2f to %.2f): need mean >= .70 and min >= .65' % (rs[:, 0].mean(), rs[:, 0].min(), rs[:, 0].max())
        c4 = np.nanmean(rs[:, 1]) >= .65
        c4txt = 'balanced accuracy over splits %.2f: need >= .65' % np.nanmean(rs[:, 1])
    else:
        Xb, yb = data(prim, tgt, M1)
        folds = splits(kind, yb, R)
        m1 = run_cv(kind, model(kind, 'linear', M1), Xb, yb, folds)['main']
        base = run_cv(kind, model(kind, 'baseline', M1), Xb, yb, folds)['main']
        gm, gci, gp = nb_test(m1 - base)
        c2 = rs[:, 0].min() > 0 and gp < .05 and gm > 0
        c2txt = 'Q2 over splits %.2f (min %.2f), gain over the mean %+.2f p %s: need min > 0 and p < .05' % (rs[:, 0].mean(), rs[:, 0].min(), gm, fmtp(gp))
        c4, c4txt = True, 'not applicable (count)'
    c3 = p_noage < .05
    ok = c1 and c2 and c3 and c4
    rows.append(dict(target=tgt, usable=ok))
    say('    %s' % lab)
    say('        1 better than chance      %-5s  permutation Holm p %s' % ('PASS' if c1 else 'fail', fmtp(p_holm)))
    say('        2 not split luck          %-5s  %s' % ('PASS' if c2 else 'fail', c2txt))
    say('        3 not carried by age 25+  %-5s  without the age dummy: permutation p %s' % ('PASS' if c3 else 'fail', fmtp(p_noage)))
    say('        4 classification          %-5s  %s' % (('PASS' if c4 else 'fail') if kind == 'clf' else 'n/a', c4txt))
    say('        -> %s' % ('USABLE (within this sample)' if ok else 'not usable'))
say('')
say('usable: %s' % (', '.join(r['target'] for r in rows if r['usable']) or 'none'))
say('runtime %.0f s' % (time.time() - T0))
with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')
print('\n'.join(lines))
