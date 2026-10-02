# -*- coding: utf-8 -*-
"""
Can any oversampling strategy produce a usable model? A demonstration for the paper's oversampling paragraph,
not a search for a reportable model.

Every strategy is run two ways on the same cross-validation splits:
  inside  - resampling is part of the model and runs on each training fold only (the valid way);
  leaky   - the whole data set is resampled first and then cross-validated, so synthetic copies of a person can
            sit in the test fold while that person is in the training fold (the invalid way).
Strategies: none; class weights; random duplication; SMOTENC to balance (the main analysis); SMOTENC amplified
(both classes grown to 5x the majority); SMOTENC + Tomek-link cleaning; noise augmentation (5 jittered copies of
every person). Targets: the four most promising binary targets, predicted from background + AI use (M1), with the
linear model. A strategy would count only if, applied inside the folds, it beats no oversampling in the corrected
paired test and meets the usability criteria of ANALYSIS-DECISIONS.md ("ML extension"); Holm across all
strategy x target comparisons.

Run with Anaconda's Python:  C:\\Users\\User\\anaconda3\\python.exe analysis\\07_oversampling_check.py
Writes analysis/results/oversampling_check.txt. Machinery (splits, CV, corrected test) is executed from 05_ml.py.
"""
import os
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(HERE, '05_ml.py'), encoding='utf-8') as f:
    _src = f.read()
exec(compile(_src.split('# ------------------------------------------------------------------ main evaluation')[0],
             os.path.join(HERE, '05_ml.py'), 'exec'))
from imblearn.over_sampling import RandomOverSampler
from imblearn.combine import SMOTETomek
from imblearn import FunctionSampler

OUT = os.path.join(HERE, 'results', 'oversampling_check.txt')
ALL['Substitution'] = (ALL.SwitchEng >= 3).astype(float).where(ALL.SwitchEng.notna())
ALL['AnyDifficulty'] = (ALL.AbilityDecline > 0).astype(float).where(ALL.AbilityDecline.notna())
core = ALL[ALL.core == 1].copy()
COLS = M0 + AI
CAT = [i for i, c in enumerate(COLS) if c in BINARY]
TARGETS = [('AnyFormalLoss', 'any formal-domain loss'), ('Loss_Writing', 'loss: writing'),
           ('Substitution', 'substitution'), ('AnyDifficulty', 'harder without AI')]


def amplify(y, factor=5):                         # grow every class to factor x the majority class
    m = max(Counter(y).values())
    return {c: factor * m for c in Counter(y)}


def augment(X, y, copies=5, sd=.3, seed=SEED):    # jittered copies; binary columns copied unchanged
    rng = np.random.default_rng(seed)
    cont = [i for i in range(X.shape[1]) if i not in CAT]
    Xs, ys = [X], [y]
    for _ in range(copies):
        Xc = X.copy()
        Xc[:, cont] += rng.normal(0, sd, size=(X.shape[0], len(cont)))
        Xs.append(Xc); ys.append(y)
    return np.vstack(Xs), np.concatenate(ys)


def sampler(name):
    return {'none': None, 'class weights': None,
            'random duplication': RandomOverSampler(random_state=SEED),
            'SMOTENC to balance': SMOTENC(categorical_features=CAT, k_neighbors=5, random_state=SEED),
            'SMOTENC amplified x5': SMOTENC(categorical_features=CAT, k_neighbors=5, random_state=SEED, sampling_strategy=amplify),
            'SMOTENC + Tomek': SMOTETomek(smote=SMOTENC(categorical_features=CAT, k_neighbors=5, random_state=SEED), random_state=SEED),
            'noise augmentation x5': FunctionSampler(func=augment, validate=False)}[name]


def pipe(name):
    lr = LogisticRegression(C=1.0, max_iter=2000, class_weight='balanced' if name == 'class weights' else None)
    s = sampler(name)
    steps = [('scale', StandardScaler())] + ([('sampler', s)] if s is not None else []) + [('model', lr)]
    return ImbPipeline(steps)


STRATS = ['none', 'class weights', 'random duplication', 'SMOTENC to balance', 'SMOTENC amplified x5',
          'SMOTENC + Tomek', 'noise augmentation x5']
LEAKY = ['random duplication', 'SMOTENC to balance', 'SMOTENC amplified x5', 'noise augmentation x5']


def run(tgt, name, leaky):
    X, y = data(core, tgt, COLS)
    if leaky:
        Xr, yr = sampler(name).fit_resample(StandardScaler().fit_transform(X), y)
        return run_cv('clf', pipe('none'), Xr, yr.astype(int), splits('clf', yr.astype(int), R)), yr.astype(int)
    return run_cv('clf', pipe(name), X, y, splits('clf', y, R)), y


jobs = [(t, s, False) for t, _ in TARGETS for s in STRATS] + [(t, s, True) for t, _ in TARGETS for s in LEAKY]
log('running %d evaluations' % len(jobs))
res = dict(zip(jobs, Parallel(n_jobs=JOBS)(delayed(run)(*j) for j in jobs)))

say('=' * 100)
say('CAN OVERSAMPLING PRODUCE A USABLE MODEL?  Core sample (n=37), background + AI use, linear model, %d x 5-fold CV.' % R)
say('Inside = resampling on training folds only (valid). Leaky = resample everything, then cross-validate (invalid).')
say('=' * 100)
comp = []
for tgt, lab in TARGETS:
    _, y = data(core, tgt, COLS)
    base = res[(tgt, 'none', False)][0]['main']
    say('')
    say('%s  (n=%d: %d yes / %d no)' % (lab.upper(), len(y), int(y.sum()), int(len(y) - y.sum())))
    say('    %-24s %-8s %-8s %-36s %s' % ('strategy', 'AUC', 'bal acc', 'vs no oversampling (inside)', 'leaky AUC (n after resampling)'))
    for s in STRATS:
        r, yy = res[(tgt, s, False)]
        sm = summary('clf', r, yy)
        if s == 'none':
            vs = '-'
        else:
            m, ci, p = nb_test(r['main'] - base)
            comp.append(dict(target=tgt, strategy=s, diff=m, p=p))
            vs = '%+.3f [%+.3f, %+.3f] p %s' % (m, ci[0], ci[1], fmtp(p))
        lk = ''
        if s in LEAKY:
            rl, yl = res[(tgt, s, True)]
            lk = '%.2f (n=%d)' % (rl['main'].mean(), len(yl))
        say('    %-24s %-8.2f %-8.2f %-36s %s' % (s, sm['main'], sm['bacc'], vs, lk))
comp = pd.DataFrame(comp)
comp['p_holm'] = multipletests(comp.p, method='holm')[1]
say('')
say('Inside the folds, best gain over no oversampling: %+.3f (%s, %s); smallest Holm-adjusted p across %d comparisons: %s' % (
    comp['diff'].max(), comp.loc[comp['diff'].idxmax(), 'strategy'], comp.loc[comp['diff'].idxmax(), 'target'],
    len(comp), fmtp(comp.p_holm.min())))
best = max(summary('clf', res[(t, s, False)][0], res[(t, s, False)][1])['main'] for t, _ in TARGETS for s in STRATS)
say('Highest valid AUC of any strategy on any target: %.2f (the usability criteria need >= .70 across splits, plus the other three).' % best)
say('Leaky AUCs rise with the amount of synthetic data - they measure how well the model recognises copies of people it')
say('has already seen, not how well it predicts new people.')
say('')
say('runtime %.0f s' % (time.time() - T0))
with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')
print('\n'.join(lines))


# ------------------------------------------------------------------ the best valid result, against the usability criteria
bt, bs = 'AnyFormalLoss', 'noise augmentation x5'
say('BEST VALID RESULT (%s, %s) against the usability criteria:' % (bs, bt))
X, y = data(core, bt, COLS)
idx = [i for i, c in enumerate(COLS) if c != 'Age25']
CAT_SAVE = CAT
def seed_auc(seed, cols_idx):
    global CAT
    return run_cv('clf', pipe(bs), X[:, cols_idx], y, splits('clf', y, R, seed))['main'].mean()
full = list(range(len(COLS)))
a = np.array(Parallel(n_jobs=JOBS)(delayed(seed_auc)(SEED + 1000 * (i + 1), full) for i in range(10)))
say('    over 10 other splits: AUC %.2f (%.2f to %.2f)   [criterion 2 needs mean >= .70 and min >= .65]' % (a.mean(), a.min(), a.max()))
CAT = [i for i, c in enumerate([COLS[j] for j in idx]) if c in BINARY]   # noise must skip the binary columns that remain
b = run_cv('clf', pipe(bs), X[:, idx], y, splits('clf', y, R))['main'].mean()
say('    without the age dummy: AUC %.2f   [criterion 3 needs it to stay above chance]' % b)
CAT = CAT_SAVE
with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')
print('\n'.join(lines[-3:]))
CAT = [i for i, c in enumerate([COLS[j] for j in idx]) if c in BINARY]
obs, p, nm = perm_test('clf', pipe(bs), X[:, idx], y, 200 if not QUICK else 20)
CAT = CAT_SAVE
say('    without the age dummy, permutation test (200 shuffles, full CV): AUC %.2f, null mean %.2f, p %s  [criterion 3 needs p < .05]' % (obs, nm, fmtp(p)))
say('    -> %s' % ('passes criterion 3' if p < .05 else 'fails criterion 3: the signal is the 5 respondents aged 25+, as in every earlier model'))
with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')
print('\n'.join(lines[-2:]))
