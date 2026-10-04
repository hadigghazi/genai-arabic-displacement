# -*- coding: utf-8 -*-
"""
RQ4, machine learning: can background and AI-use information predict who reports AI-attributed domain
loss, overall and in individual domains, better than background alone? Design and its reasons are in
analysis/ANALYSIS-DECISIONS.md (section "Machine learning").

  Targets      (a) DomainsLost: number of applicable domains with less Arabic because of AI (regression)
               (b) AnyFormalLoss: less Arabic in work/study or formal texts (classification)
               (c) loss in each single domain, where both classes have at least 8 respondents, the
                   minimum for SMOTENC's 5 neighbours in every 5-fold training set
  Features     nested blocks: M0 background (the 27 Sep plan's list without the constant Medium) ->
               M1 = M0 + AI use -> M2 = M1 + perceived quality gap. No outcome item is ever a feature
               (change grid, current-use grid, ability, expectations, substitution, switching,
               social-media attribution). Extra blocks, linear model only: M0 without age (sensitivity),
               M0 + school language (post hoc), AI use alone (exploratory direct comparison).
  Models       fixed and untuned (the 27 Sep plan's settings): L2 logistic / ridge (primary), random
               forest, histogram gradient boosting, and a dummy baseline.
  Imbalance    SMOTENC inside each training fold only (the 30 Sep proposal).
  Validation   10 x 5-fold, stratified for classification, the same splits for every model and block.
  Inference    Nadeau-Bengio corrected resampled t on paired per-fold differences (M1 - M0, M2 - M1,
               flexible - linear, and for the count, model - mean); permutation tests against chance
               (linear model on M0 and M1, and the extra blocks on the overall targets; forest and
               boosting only where they pass the plan's decision rule against the linear model, since
               otherwise they are never interpreted); Holm within the overall pair and within the domains.
               Single-model scores carry no interval: at 7-8 people per test fold a per-fold interval
               under-covers, so chance is judged by the permutation tests.

Run with Anaconda's Python:  C:\\Users\\User\\anaconda3\\python.exe analysis\\05_ml.py
Set ML_QUICK=1 for a fast smoke test (few repeats and permutations; numbers not for reporting).
Reads analysis/data/scored.csv; writes analysis/results/ml_results.txt and ml_table.csv.
"""
import os
os.environ.setdefault('LOKY_MAX_CPU_COUNT', str(max(1, (os.cpu_count() or 2) - 2)))
import sys, time, hashlib, warnings
import numpy as np
import pandas as pd
import scipy
import sklearn
import imblearn
from scipy import stats
from joblib import Parallel, delayed
from sklearn.base import clone
from sklearn.dummy import DummyClassifier, DummyRegressor
from sklearn.ensemble import (RandomForestClassifier, RandomForestRegressor,
                              HistGradientBoostingClassifier, HistGradientBoostingRegressor)
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.metrics import roc_auc_score, average_precision_score, mean_squared_error, mean_absolute_error
from sklearn.model_selection import RepeatedStratifiedKFold, RepeatedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from statsmodels.stats.multitest import multipletests
from imblearn.over_sampling import SMOTENC, SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

warnings.filterwarnings('ignore')
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data', 'scored.csv')
OUT = os.path.join(HERE, 'results', 'ml_results.txt')
TABLE = os.path.join(HERE, 'results', 'ml_table.csv')
QUICK = os.environ.get('ML_QUICK') == '1'
# Resumable runs: each finished piece (one cross-validation job, one permutation test) is cached on disk, keyed by
# the data file and the run mode, so an interrupted run continues where it stopped. Results are unchanged, because
# every piece uses its own fixed seed. Delete analysis/.mlcache to start afresh.
from joblib import Memory
with open(os.path.join(HERE, 'data', 'scored.csv'), 'rb') as _f:
    _DATA_MD5 = hashlib.md5(_f.read()).hexdigest()
MEM = Memory(os.path.join(HERE, '.mlcache', '%s-%s' % (_DATA_MD5[:12], 'quick' if QUICK else 'full')), verbose=0)
SEED = 20261002
K = 5
R = 3 if QUICK else 10                 # repeats of 5-fold CV
R_PERM = R                             # the permutation statistic is the headline score itself (all repeats)
B_LIN = 30 if QUICK else 500           # permutations, linear model (min p .002, enough for Holm over 6)
SEEDS = 3 if QUICK else 10             # split seeds for the stability check
B_FLEX = 20 if QUICK else 200          # permutations, forest and boosting (each fit is ~30x slower)
JOBS = int(os.environ.get('ML_JOBS', 12))  # throughput peaks at 12 workers on this machine (hybrid cores)
MIN_CLASS = 8
MARGIN_AUC, MARGIN_R2 = .08, .05       # the plan's decision rule for "a flexible model adds something"

ALL = pd.read_csv(DATA)
ALL['SchoolEnglish'] = (ALL.Sch_SciLang == 2).astype(int)      # 2 = English vs 3 = French or 1 = Arabic (one respondent)
ALL['SocialLoss'] = -ALL.SocialMedia
ALL['NetLoss4'] = (ALL.Displacement4 > 0).astype(float).where(ALL.Displacement4.notna())   # the plan's NetLoss
DOM = ['WorkStudy', 'Writing', 'Self', 'Personal', 'Family', 'Fusha', 'Religion', 'Consume']
for dom in DOM:
    ALL['Loss_' + dom] = (ALL['d_' + dom] < 0).astype(float).where(ALL['d_' + dom].notna())
# decision 12's alternative: drop a domain only when 'not applicable today' goes with 'no change'
D2 = pd.DataFrame({dom: ALL['ArUse_' + dom].where(~((ALL['CurUse_' + cu] == 5) & (ALL['ArUse_' + dom] == 0)))
                   for dom, cu in zip(DOM, ['WorkStudy', 'Writing', 'Self', 'Personal', 'Family', 'Formal', 'Religion', 'Consume'])})
ALL['DomainsLost_na'] = (D2 <= -1).sum(axis=1)
_fmin = D2[['WorkStudy', 'Fusha']].min(axis=1)
ALL['AnyFormalLoss_na'] = (_fmin <= -1).astype(float).where(_fmin.notna())
prim = ALL.copy()                      # primary sample: all respondents (decision of 3 Oct 2026)
core_df = ALL[ALL.core == 1].copy()       # the plan's core sample (sensitivity)
REG_TARGETS = {'DomainsLost', 'Displacement', 'Displacement4', 'DomainsLost_na'}

M0 = ['Age25', 'Computing', 'Education', 'Eng_Prof', 'EventMove']       # the plan's M0; Medium is constant (dropped)
AI = ['AI_TaskShare', 'AI_BreadthCount', 'AI_Freq', 'AI_TenureRank', 'EnglishShare', 'AI_Content', 'AI_ContentLang']
SETS = {'M0 background': M0, 'M1 + AI use': M0 + AI, 'M2 + quality gap': M0 + AI + ['QualityGap']}
EXTRA = {'M0 without age': [c for c in M0 if c != 'Age25'],              # sensitivity: 5 people are 25+
         'M0 + school language': M0 + ['SchoolEnglish'],                 # post hoc (not in either pre-data document)
         'AI use only': AI}                                              # exploratory: AI use against background
BINARY = {'Age25', 'Computing', 'EventMove', 'SchoolEnglish'}
GROUPS = [('age 25+', ['Age25']), ('computing field', ['Computing']), ('education', ['Education']),
          ('English proficiency', ['Eng_Prof']), ('started English-medium study/work', ['EventMove']),
          ('school science in English', ['SchoolEnglish']),
          ('AI intensity (share, breadth, frequency)', ['AI_TaskShare', 'AI_BreadthCount', 'AI_Freq']),
          ('AI tenure', ['AI_TenureRank']), ('English share of AI use', ['EnglishShare']),
          ('AI-generated content (exposure, language)', ['AI_Content', 'AI_ContentLang']),
          ('quality gap', ['QualityGap'])]

lines = []
say = lambda *a: lines.append(' '.join(str(x) for x in a))
fmtp = lambda p: '<.001' if p < .001 else '%.3f' % p
T0 = time.time()
log = lambda msg: print('[%5.0f s] %s' % (time.time() - T0, msg), flush=True)


# ------------------------------------------------------------------ models
def model(kind, name, cols, balance='smote'):
    """A fresh, unfitted pipeline. kind: 'clf' or 'reg'. balance: 'smote', 'weight' or 'none' (clf only).
    SMOTENC gives each synthetic case's binary features the most common value among its 5 nearest
    same-class neighbours (at this n, close to the class mode); with no binary feature, plain SMOTE."""
    if kind == 'reg':
        est = {'linear': Ridge(alpha=1.0),
               'forest': RandomForestRegressor(n_estimators=500, min_samples_leaf=5, random_state=SEED, n_jobs=1),
               'boosting': HistGradientBoostingRegressor(max_depth=2, learning_rate=.05, max_iter=100,
                                                         min_samples_leaf=10, random_state=SEED),
               'baseline': DummyRegressor(strategy='mean')}[name]
        return Pipeline([('scale', StandardScaler()), ('model', est)])
    cw = 'balanced' if balance == 'weight' else None
    est = {'linear': LogisticRegression(C=1.0, max_iter=2000, class_weight=cw),
           'forest': RandomForestClassifier(n_estimators=500, min_samples_leaf=5, class_weight=cw,
                                            random_state=SEED, n_jobs=1),
           'boosting': HistGradientBoostingClassifier(max_depth=2, learning_rate=.05, max_iter=100,
                                                      min_samples_leaf=10, class_weight=cw, random_state=SEED),
           'baseline': DummyClassifier(strategy='prior')}[name]
    if balance == 'smote' and name != 'baseline':
        cat = [i for i, c in enumerate(cols) if c in BINARY]
        sampler = (SMOTENC(categorical_features=cat, k_neighbors=5, random_state=SEED) if cat
                   else SMOTE(k_neighbors=5, random_state=SEED))
        return ImbPipeline([('scale', StandardScaler()), ('smote', sampler), ('model', est)])
    return Pipeline([('scale', StandardScaler()), ('model', est)])


def splits(kind, y, repeats, seed=SEED):
    cv = (RepeatedStratifiedKFold if kind == 'clf' else RepeatedKFold)(n_splits=K, n_repeats=repeats, random_state=seed)
    return list(cv.split(np.zeros((len(y), 1)), y))


def run_cv(kind, pipe, X, y, folds, keep=False):
    """Per-fold scores (AUC, or Q2* = 1 - MSE_fold / Var(y)) and, per repeat, the pooled out-of-fold
    predictions plus a reference prediction (the training-fold prevalence or mean) for skill scores.
    keep=True also returns each fold's fitted model (for permutation importance)."""
    n = len(y)
    var_y = np.var(y)
    reps = len(folds) // K
    oof = np.full((reps, n), np.nan)
    ref = np.full((reps, n), np.nan)
    f_main, fitted = [], []
    for j, (tr, te) in enumerate(folds):
        m = clone(pipe).fit(X[tr], y[tr])
        if kind == 'clf':
            p = m.predict_proba(X[te])[:, 1]
            f_main.append(roc_auc_score(y[te], p))
        else:
            p = m.predict(X[te])
            f_main.append(1 - mean_squared_error(y[te], p) / var_y)
        oof[j // K, te] = p
        ref[j // K, te] = y[tr].mean()
        if keep:
            fitted.append(m)
    return dict(main=np.array(f_main), oof=oof, ref=ref, fitted=fitted)


def summary(kind, res, y):
    """Headline numbers: the mean per-fold AUC (or Q2) and, from each repeat's pooled out-of-fold predictions
    (averaged over repeats): average precision, recall per class and balanced accuracy at 0.5, and the Brier
    skill score against the training prevalence (classification); MAE and RMSE (regression)."""
    out = dict(main=res['main'].mean())
    if kind == 'clf':
        out['ap'] = np.mean([average_precision_score(y, o) for o in res['oof']])
        r1 = [((o >= .5) & (y == 1)).sum() / (y == 1).sum() for o in res['oof']]
        r0 = [((o < .5) & (y == 0)).sum() / (y == 0).sum() for o in res['oof']]
        out.update(rec1=np.mean(r1), rec0=np.mean(r0), bacc=np.mean([(a + b) / 2 for a, b in zip(r1, r0)]))
        out['bss'] = np.mean([1 - np.mean((o - y) ** 2) / np.mean((f - y) ** 2) for o, f in zip(res['oof'], res['ref'])])
    else:
        out['mae'] = np.mean([mean_absolute_error(y, o) for o in res['oof']])
        out['rmse'] = np.mean([np.sqrt(mean_squared_error(y, o)) for o in res['oof']])
    return out


# ------------------------------------------------------------------ inference
def nb_test(diff):
    """Nadeau-Bengio corrected resampled t on paired per-fold differences: variance inflated by
    n_test/n_train = 1/(K-1) for overlapping training sets."""
    J = len(diff)
    m, v = diff.mean(), diff.var(ddof=1)
    se = np.sqrt((1 / J + 1 / (K - 1)) * v)
    if se == 0:
        return m, (m, m), 1.0
    t = m / se
    h = stats.t.ppf(.975, J - 1) * se
    return m, (m - h, m + h), 2 * stats.t.sf(abs(t), J - 1)


def perm_stat(kind, pipe, X, y, seed):
    """The permutation-test statistic: mean per-fold score over R_PERM repeats of 5-fold CV (splits re-drawn on y)."""
    return run_cv(kind, pipe, X, y, splits(kind, y, R_PERM, seed))['main'].mean()


def perm_test(kind, pipe, X, y, B):
    obs = perm_stat(kind, pipe, X, y, SEED)
    rng = np.random.default_rng(SEED)
    perms = [rng.permutation(y) for _ in range(B)]
    null = np.array(Parallel(n_jobs=JOBS)(delayed(perm_stat)(kind, pipe, X, yp, SEED) for yp in perms))
    return obs, (1 + np.sum(null >= obs)) / (1 + B), null.mean()


perm_test = MEM.cache(perm_test)


def _group_drop(kind, res, X, y, folds, idx, seed, n_perm):
    rng = np.random.default_rng(seed)
    drops = []
    for j, (tr, te) in enumerate(folds):
        m, base = res['fitted'][j], res['main'][j]
        for _ in range(n_perm):
            Xt = X[te].copy()
            Xt[:, idx] = Xt[rng.permutation(len(te))][:, idx]
            if kind == 'clf':
                s = roc_auc_score(y[te], m.predict_proba(Xt)[:, 1])
            else:
                s = 1 - mean_squared_error(y[te], m.predict(Xt)) / np.var(y)
            drops.append(base - s)
    return np.mean(drops)


def importance(kind, res, X, y, folds, cols, n_perm=20):
    """Grouped permutation importance on held-out folds: drop in the per-fold score when a block of
    correlated features is shuffled together (one shared row permutation) in the test fold."""
    todo = [(g, [cols.index(c) for c in gc if c in cols]) for g, gc in GROUPS]
    todo = [(g, idx) for g, idx in todo if idx]
    drops = Parallel(n_jobs=JOBS)(delayed(_group_drop)(kind, res, X, y, folds, idx, SEED + i, n_perm)
                                  for i, (g, idx) in enumerate(todo))
    return sorted(zip([g for g, _ in todo], drops), key=lambda r: -r[1])


# ------------------------------------------------------------------ targets
def targets(df):
    T = [('DomainsLost', 'reg', 'domains lost (count)', 'overall'),
         ('AnyFormalLoss', 'clf', 'any formal-domain loss', 'overall')]
    skipped = []
    for dom in DOM:
        y = df['Loss_' + dom].dropna()
        small = int(min((y == 1).sum(), (y == 0).sum()))
        if small >= MIN_CLASS:
            T.append(('Loss_' + dom, 'clf', 'loss: ' + dom, 'domain'))
        else:
            skipped.append('%s (smaller class %d)' % (dom, small))
    return T, skipped


def data(df, target, cols):
    s = df[cols + [target]].dropna()
    return s[cols].to_numpy(float), s[target].to_numpy(float if target in REG_TARGETS else int)


# ------------------------------------------------------------------ main evaluation
TG, skipped = targets(prim)
NAMES = ['linear', 'forest', 'boosting']
ALLSETS = dict(SETS, **EXTRA)
jobs = []
for tgt, kind, _, _ in TG:
    for sname in SETS:
        for mname in NAMES + (['baseline'] if sname == 'M0 background' else []):
            jobs.append((tgt, kind, sname, mname))
    for sname in EXTRA:
        jobs.append((tgt, kind, sname, 'linear'))
# every block of a target must use the same rows, or the per-fold differences would not pair
for tgt, kind, _, _ in TG:
    assert len({len(data(prim, tgt, c)[1]) for c in ALLSETS.values()}) == 1, tgt


def evaluate(tgt, kind, sname, mname, keep=False):
    cols = ALLSETS[sname]
    X, y = data(prim, tgt, cols)
    return run_cv(kind, model(kind, mname, cols), X, y, splits(kind, y, R), keep=keep)


log('main evaluation: %d jobs' % len(jobs))
evaluate_cached = MEM.cache(evaluate)
results = dict(zip(jobs, Parallel(n_jobs=JOBS)(delayed(evaluate_cached)(*j) for j in jobs)))
log('main evaluation done')

say('=' * 100)
say('RQ4 MACHINE LEARNING. Primary sample: all respondents (n=%d). %d x 5-fold CV%s; fixed models; SMOTENC inside training folds.' % (len(prim), R, ' [QUICK MODE: NOT FOR REPORTING]' if QUICK else ''))
say('Decisions and their alternatives: analysis/ANALYSIS-DECISIONS.md, section "Machine learning".')
with open(DATA, 'rb') as f:
    md5 = hashlib.md5(f.read()).hexdigest()
say('Python %s | numpy %s | scipy %s | scikit-learn %s | imbalanced-learn %s | scored.csv md5 %s' % (
    sys.version.split()[0], np.__version__, scipy.__version__, sklearn.__version__, imblearn.__version__, md5))
say('=' * 100)
say('')
say('FEATURES')
for sname, cols in ALLSETS.items():
    say('    %-22s %s' % (sname, ', '.join(cols)))
say('    M0 is the 27 Sep plan\'s background list without "Medium" (constant in this sample: everyone studied school science or university in English or French).')
say('    "M0 + school language" is post hoc: the English-vs-French contrast is in neither pre-data document.')
say('    never features: the change grid, current-use grid, ability, expectations, substitution, switching, social-media attribution')
say('TARGETS (primary sample: all respondents)')
for tgt, kind, lab, fam in TG:
    X, y = data(prim, tgt, M0)
    if kind == 'clf':
        say('    %-16s n=%d  loss %d / no loss %d  (%s)' % (tgt, len(y), int(y.sum()), int(len(y) - y.sum()), fam))
    else:
        say('    %-16s n=%d  mean %.2f  SD %.2f  range %d-%d  (%s)' % (tgt, len(y), y.mean(), y.std(ddof=1), y.min(), y.max(), fam))
say('    not modelled (fewer than %d in the smaller class): %s' % (MIN_CLASS, '; '.join(skipped)))
say('')
say('Reading the tables. AUC = area under the ROC curve, mean over the 50 test folds (chance = .50). The other')
say('numbers come from each repeat\'s pooled out-of-fold predictions, averaged over repeats: PR-AUC = average')
say('precision for "loss" (chance = the share with loss); recall per class and balanced accuracy at 0.5; BSS =')
say('Brier skill score against predicting the training prevalence (SMOTENC rebalances the training data, so its')
say('probabilities are not calibrated: AUC measures ranking, BSS penalises the shift). For the count: Q2 = 1 -')
say('MSE / Var(y) per test fold (0 = no better than predicting the mean), MAE and RMSE. No interval is given for a')
say('single model: with 7-8 people per test fold a per-fold interval under-covers. Chance is judged by the')
say('permutation tests; comparisons between models use paired, corrected intervals.')

table = []
for tgt, kind, lab, fam in TG:
    _, y = data(prim, tgt, M0)
    say('')
    say('-' * 100)
    say('%s  (%s)' % (lab.upper(), tgt))
    if kind == 'clf':
        say('    %-22s %-9s %-6s %-7s %-9s %-9s %-8s %-6s' % ('features', 'model', 'AUC', 'PR-AUC', 'rec loss', 'rec none', 'bal acc', 'BSS'))
    else:
        say('    %-22s %-9s %-6s %-6s %-6s' % ('features', 'model', 'Q2', 'MAE', 'RMSE'))
    for sname in ALLSETS:
        for mname in NAMES + ['baseline']:
            if (tgt, kind, sname, mname) not in results:
                continue
            s = summary(kind, results[(tgt, kind, sname, mname)], y)
            if kind == 'clf':
                say('    %-22s %-9s %-6.2f %-7.2f %-9.2f %-9.2f %-8.2f %+.2f' % (sname, mname, s['main'], s['ap'], s['rec1'], s['rec0'], s['bacc'], s['bss']))
                if s['main'] > .90:
                    say('    LEAKAGE ALARM: AUC above .90 - investigate before reporting')
            else:
                say('    %-22s %-9s %+-6.2f %-6.2f %-6.2f' % (sname, mname, s['main'], s['mae'], s['rmse']))
            table.append(dict(target=tgt, family=fam, kind=kind, n=len(y), prevalence=y.mean() if kind == 'clf' else np.nan,
                              features=sname, model=mname, score=s['main'], pr_auc=s.get('ap'), recall_loss=s.get('rec1'),
                              recall_none=s.get('rec0'), bal_acc=s.get('bacc'), brier_skill=s.get('bss'),
                              mae=s.get('mae'), rmse=s.get('rmse')))
    if kind == 'clf':
        say('    PR-AUC chance level = %.2f' % y.mean())

# ------------------------------------------------------------------ increments (same splits, so per-fold differences pair)
say('')
say('=' * 100)
say('DOES AI-USE INFORMATION IMPROVE PREDICTION? Paired per-fold differences, Nadeau-Bengio corrected 95% CI')
say('=' * 100)
inc = []
for tgt, kind, lab, fam in TG:
    for mname in NAMES:
        a, b, c = [results[(tgt, kind, s, mname)]['main'] for s in SETS]
        for step, d in [('M1 - M0 (AI use)', b - a), ('M2 - M1 (quality gap)', c - b)]:
            m, ci, p = nb_test(d)
            inc.append(dict(target=tgt, family=fam, model=mname, step=step, diff=m, lo=ci[0], hi=ci[1], p=p))
    m, ci, p = nb_test(results[(tgt, kind, 'AI use only', 'linear')]['main'] - results[(tgt, kind, 'M0 background', 'linear')]['main'])
    inc.append(dict(target=tgt, family=fam, model='linear', step='AI use only - M0 (expl.)', diff=m, lo=ci[0], hi=ci[1], p=p))
inc = pd.DataFrame(inc)
for fam in ['overall', 'domain']:
    sel = (inc.family == fam) & (inc.model == 'linear') & (inc.step == 'M1 - M0 (AI use)')
    inc.loc[sel, 'p_holm'] = multipletests(inc.loc[sel, 'p'], method='holm')[1]
say('    difference in AUC (classification) or Q2 (count); positive = the added block helps. p_Holm: linear model,')
say('    M1 - M0, within the overall pair and within the domains (the RQ4 test). "AI use only - M0" is an exploratory')
say('    direct comparison: AI-use information alone against background alone. Everything else is descriptive.')
for tgt, kind, lab, fam in TG:
    say('    %s' % lab)
    for _, r in inc[inc.target == tgt].iterrows():
        holm = '  p_Holm %s' % fmtp(r.p_holm) if pd.notna(r.get('p_holm')) else ''
        say('        %-9s %-26s %+.3f [%+.3f, %+.3f]  p %s%s' % (r.model, r.step, r['diff'], r.lo, r.hi, fmtp(r.p), holm))
say('    Smallest gain the RQ4 test could detect (80% power, two-sided .05, from the corrected SE of linear M1 - M0):')
for tgt, kind, lab, fam in TG[:2]:
    d = results[(tgt, kind, 'M1 + AI use', 'linear')]['main'] - results[(tgt, kind, 'M0 background', 'linear')]['main']
    se = np.sqrt((1 / len(d) + 1 / (K - 1)) * d.var(ddof=1))
    say('        %-26s %s %.2f' % (lab, 'AUC' if kind == 'clf' else 'Q2', (stats.t.ppf(.975, len(d) - 1) + stats.t.ppf(.80, len(d) - 1)) * se))

# ------------------------------------------------------------------ flexible vs linear (the plan's decision rule)
say('')
say('FLEXIBLE VS LINEAR (the plan\'s decision rule: a flexible model adds something only if it beats the linear model')
say('by at least %.2f AUC (%.2f Q2) AND the corrected test gives p < .05; otherwise "no detectable nonlinear structure at this N")' % (MARGIN_AUC, MARGIN_R2))
adds = {}
for tgt, kind, lab, fam in TG:
    for sname in SETS:
        lin = results[(tgt, kind, sname, 'linear')]['main']
        for mname in ['forest', 'boosting']:
            m, ci, p = nb_test(results[(tgt, kind, sname, mname)]['main'] - lin)
            ok = m >= (MARGIN_AUC if kind == 'clf' else MARGIN_R2) and p < .05
            adds[(tgt, sname, mname)] = ok
            say('    %-26s %-18s %-9s %+.3f [%+.3f, %+.3f] p %s  -> %s' % (lab, sname, mname, m, ci[0], ci[1], fmtp(p),
                                                                       'ADDS SOMETHING' if ok else 'no'))

# ------------------------------------------------------------------ against chance, and (count) against the mean
say('')
say('=' * 100)
say('BETTER THAN CHANCE? Permutation tests (outcome shuffled, whole pipeline refit, splits redrawn; statistic = mean')
say('per-fold score over the same %d repeats of 5-fold as the headline; %d permutations for the linear model). Forest and boosting' % (R_PERM, B_LIN))
say('are tested (%d permutations) only where they pass the decision rule above; otherwise they are never interpreted.' % B_FLEX)
say('A permutation test rejects "no association"; for the count, whether the model beats predicting the mean is a')
say('separate question, answered below by a paired comparison with the baseline.')
say('=' * 100)
perm = []
plan = []
for tgt, kind, lab, fam in TG:
    for sname in SETS:
        for mname in NAMES:
            if mname == 'linear' and sname != 'M2 + quality gap':
                plan.append((tgt, kind, fam, sname, mname, B_LIN))
            elif mname != 'linear' and adds[(tgt, sname, mname)]:
                plan.append((tgt, kind, fam, sname, mname, B_FLEX))
    if fam == 'overall':
        for sname in EXTRA:
            plan.append((tgt, kind, fam, sname, 'linear', B_LIN))
for tgt, kind, fam, sname, mname, B in plan:
    cols = ALLSETS[sname]
    X, y = data(prim, tgt, cols)
    obs, p, nullmean = perm_test(kind, model(kind, mname, cols), X, y, B)
    log('permutation %s %s %s: p=%.3f' % (tgt, sname, mname, p))
    perm.append(dict(target=tgt, family=fam, kind=kind, features=sname, model=mname, obs=obs, null=nullmean, p=p, B=B))
perm = pd.DataFrame(perm)
for fam in ['overall', 'domain']:
    for (sname, mname), g in perm[perm.family == fam].groupby(['features', 'model']):
        perm.loc[g.index, 'p_holm'] = multipletests(g.p, method='holm')[1]
for tgt, kind, lab, fam in TG:
    say('    %s' % lab)
    for _, r in perm[perm.target == tgt].iterrows():
        say('        %-22s %-9s %s = %+.3f (permutation null mean %+.3f)  p %s  p_Holm %s  (B=%d)' % (
            r.features, r.model, 'AUC' if kind == 'clf' else 'Q2', r.obs, r.null, fmtp(r.p), fmtp(r.p_holm), r.B))
    if kind == 'reg':
        for sname in ['M0 background', 'M1 + AI use']:
            m, ci, p = nb_test(results[(tgt, kind, sname, 'linear')]['main'] - results[(tgt, kind, 'M0 background', 'baseline')]['main'])
            say('        %-22s linear vs predicting the mean: Q2 gain %+.3f [%+.3f, %+.3f]  p %s' % (sname, m, ci[0], ci[1], fmtp(p)))
say('    Holm within the overall pair and within the domains, separately for each feature set and model.')
log('permutation tests done')

# ------------------------------------------------------------------ interpretation, only where a model beats chance
say('')
say('=' * 100)
say('WHAT THE MODELS USE ("how the model uses inputs, not population effects"). Only primary-block models that beat')
say('chance after Holm; an M1 model only if it also beats M0 (otherwise its AI-feature importances are noise around M0).')
say('=' * 100)
rq4 = inc[(inc.model == 'linear') & (inc.step == 'M1 - M0 (AI use)')].set_index('target')['p_holm']
passed = perm[(perm.p_holm < .05) & perm.features.isin(list(SETS)) &
              ((perm.features == 'M0 background') | perm.target.map(lambda t: rq4.get(t, 1) < .05))]
if passed.empty:
    say('    No model qualifies: nothing is interpreted.')
for _, r in passed.iterrows():
    kind = r.kind
    cols = ALLSETS[r.features]
    X, y = data(prim, r.target, cols)
    folds = splits(kind, y, R)
    res = run_cv(kind, model(kind, r.model, cols), X, y, folds, keep=True)
    say('    %s, %s, %s: grouped permutation importance (drop in per-fold %s when the block is shuffled)' % (
        r.target, r.features, r.model, 'AUC' if kind == 'clf' else 'Q2'))
    for gname, drop in importance(kind, res, X, y, folds, cols):
        say('        %-44s %+.3f' % (gname, drop))
    if r.model == 'linear':
        full = model(kind, 'linear', cols, 'weight').fit(X, y)        # no oversampling: SMOTENC distorts binary features
        coef = full.named_steps['model'].coef_.ravel()
        say('        standardised %s coefficients (fit on everyone%s; direction only):' % (
            'logistic' if kind == 'clf' else 'ridge', ', class-weighted, no oversampling' if kind == 'clf' else ''))
        say('        ' + '  '.join('%s %+.2f' % (c, b) for c, b in sorted(zip(cols, coef), key=lambda t: -abs(t[1]))))
log('interpretation done; sensitivity')

# ------------------------------------------------------------------ sensitivity (linear model, the two overall targets)
say('')
say('=' * 100)
say('SENSITIVITY: the alternative at each decision point (linear model, %d x 5-fold; scores, and paired differences' % R)
say('from the same alternative\'s M0)')
say('=' * 100)


def quick(df, tgt, kind, cols, balance='smote', mname='linear'):
    X, y = data(df, tgt, cols)
    return run_cv(kind, model(kind, mname, cols, balance), X, y, splits(kind, y, R)), y


def line(label, res, kind, y, ref=None, extra=''):
    s = summary(kind, res, y)
    txt = '    %-66s n=%d  %s %+.2f' % (label, len(y), 'AUC' if kind == 'clf' else 'Q2', s['main'])
    if kind == 'clf':
        txt += '  bal acc %.2f  BSS %+.2f' % (s['bacc'], s['bss'])
    if ref is not None:
        m, ci, p = nb_test(res['main'] - ref['main'])
        txt += '  | vs M0 %+.3f [%+.3f, %+.3f] p %s' % (m, ci[0], ci[1], fmtp(p))
    say(txt + extra)


def sens_perm(df, tgt, kind, cols):
    X, y = data(df, tgt, cols)
    return perm_test(kind, model(kind, 'linear', cols), X, y, B_LIN)[1]


for tgt, kind in [('DomainsLost', 'reg'), ('AnyFormalLoss', 'clf')]:
    say('  %s' % tgt)
    for lab, df, t in [('decision 12 alternative (n/a dropped only with "no change")', prim, tgt + '_na'),
                       ('without the straight-liners (ids %s)' % prim.loc[prim.straightline == 1, 'id'].tolist(), prim[prim.straightline == 0], tgt),
                       ('core sample (the plan\'s rule)', core_df, tgt)]:
        r0, y = quick(df, t, kind, SETS['M0 background'])
        r1, _ = quick(df, t, kind, SETS['M1 + AI use'])
        line(lab + ', M0', r0, kind, y, extra='  | permutation p %s' % fmtp(sens_perm(df, t, kind, SETS['M0 background'])))
        line(lab + ', M1', r1, kind, y, r0)
        log('sensitivity %s %s' % (tgt, lab))
    r0, y = quick(prim, tgt, kind, SETS['M0 background'])
    rc, _ = quick(prim, tgt, kind, M0 + ['AI_Intensity', 'EnglishShare'])
    line('compact AI block (the H3 predictors: intensity, English share)', rc, kind, y, r0)
    r0, y = quick(prim, tgt, kind, SETS['M0 background'])
    r1, _ = quick(prim, tgt, kind, M0 + AI[:5])
    line('M1 as in the 27 Sep plan (without the two AI-content items)', r1, kind, y, r0)
    rs, _ = quick(prim, tgt, kind, M0 + ['SocialLoss'])
    line('exploratory: M0 + social-media attribution (not AI use)', rs, kind, y, r0)
    if kind == 'clf':
        for bal, lab in [('weight', 'class weights instead of SMOTENC (the 27 Sep plan)'), ('none', 'no imbalance handling')]:
            a, y = quick(prim, tgt, kind, SETS['M0 background'], bal)
            b, _ = quick(prim, tgt, kind, SETS['M1 + AI use'], bal)
            line(lab + ', M0', a, kind, y)
            line(lab + ', M1', b, kind, y, a)

say('  the 27 Sep plan\'s own targets (4-domain displacement; NetLoss = 4-domain displacement above 0)')
for tgt, kind in [('Displacement4', 'reg'), ('NetLoss4', 'clf'), ('Displacement', 'reg'), ('NetLoss', 'clf')]:
    if tgt == 'Displacement':
        say('  the 8-domain versions (decision 2)')
    _, y = data(prim, tgt, M0)
    if kind == 'clf' and min(y.sum(), len(y) - y.sum()) < MIN_CLASS:
        say('    %s: smaller class %d, below %d - not modelled' % (tgt, min(y.sum(), len(y) - y.sum()), MIN_CLASS))
        continue
    r0, y = quick(prim, tgt, kind, SETS['M0 background'])
    r1, _ = quick(prim, tgt, kind, SETS['M1 + AI use'])
    line('%s, M0' % tgt, r0, kind, y)
    line('%s, M1' % tgt, r1, kind, y, r0)

# ------------------------------------------------------------------ split-seed stability (linear model)
def _seed_run(tgt, kind, seed):
    out = []
    for cols in (SETS['M0 background'], SETS['M1 + AI use']):
        X, y = data(prim, tgt, cols)
        out.append(run_cv(kind, model(kind, 'linear', cols), X, y, splits(kind, y, R, seed))['main'])
    return out[0].mean(), out[1].mean(), (out[1] - out[0]).mean()


say('')
say('SPLIT-SEED STABILITY (linear model): the headline uses one random split; the same %d x 5-fold CV on %d other split' % (R, SEEDS))
say('seeds gives (mean, min-max). Remaining split-to-split noise in a %d-repeat mean is roughly the min-max spread.' % R)
log('seed stability')
for tgt, kind, lab, fam in TG:
    rs = np.array(Parallel(n_jobs=JOBS)(delayed(_seed_run)(tgt, kind, SEED + 1000 * (i + 1)) for i in range(SEEDS)))
    say('    %-26s M0 %+.2f (%+.2f to %+.2f)   M1 %+.2f (%+.2f to %+.2f)   M1 - M0 %+.3f (%+.3f to %+.3f), positive at %d of %d seeds' % (
        lab, rs[:, 0].mean(), rs[:, 0].min(), rs[:, 0].max(), rs[:, 1].mean(), rs[:, 1].min(), rs[:, 1].max(),
        rs[:, 2].mean(), rs[:, 2].min(), rs[:, 2].max(), int((rs[:, 2] > 0).sum()), SEEDS))

# ------------------------------------------------------------------ why oversampling must stay inside the folds
say('')
say('WHY OVERSAMPLING STAYS INSIDE THE TRAINING FOLDS (AnyFormalLoss, M1). Oversampling first and then splitting')
say('puts synthetic copies of training cases into the test folds, so the score measures memory, not prediction.')
log('leakage demonstration')
X, y = data(prim, 'AnyFormalLoss', SETS['M1 + AI use'])
cat = [i for i, c in enumerate(SETS['M1 + AI use']) if c in BINARY]
Xr, yr = SMOTENC(categorical_features=cat, k_neighbors=5, random_state=SEED).fit_resample(X, y)
for mname in ['linear', 'forest']:
    inside = run_cv('clf', model('clf', mname, SETS['M1 + AI use']), X, y, splits('clf', y, R))['main'].mean()
    wrong = run_cv('clf', model('clf', mname, SETS['M1 + AI use'], 'none'), Xr, yr, splits('clf', yr, R))['main'].mean()
    say('    %-8s inside the folds (correct) AUC %.2f   |   before the split (leaks) AUC %.2f on n=%d' % (mname, inside, wrong, len(yr)))

say('')
say('runtime %.0f s' % (time.time() - T0))
pd.DataFrame(table).merge(perm[['target', 'features', 'model', 'p', 'p_holm']].rename(columns={'p': 'perm_p', 'p_holm': 'perm_p_holm'}),
                          on=['target', 'features', 'model'], how='left').round(4).to_csv(TABLE, index=False)
with open(OUT, 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines) + '\n')
print('\n'.join(lines))
print('written to', OUT)
