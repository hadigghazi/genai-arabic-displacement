# -*- coding: utf-8 -*-
"""
Everything SPSS 23 cannot do, for the analysis set out in analysis/ANALYSIS-DECISIONS.md:
  - Holm correction within the two confirmatory families
      A: H1a (Fusha), H1b (work/study), H2a (Fishman order), H2b (Fusha vs dialect)
      B: the three H3 coefficients and the H4 slope
  - Page's trend test (H2a), exact and tie-aware, one-sided because the hypothesis is directional
  - HC3-robust regressions with t-based inference (SPSS 23's REGRESSION has no HC3 option), the joint
    test of the three H3 predictors, and a wild-bootstrap check of every family-B coefficient
  - the H5 mediation, estimated as in PROCESS model 4 (percentile bootstrap of a*b), and the planned
    exploratory parallel-mediator model E1
  - exact signed-rank p-values for very small groups, effect sizes, Wilson intervals, omega
  - robustness checks, and every alternative definition as a labelled sensitivity analysis

Run with Anaconda's Python (scipy, statsmodels, scikit-learn):
    C:\\Users\\User\\anaconda3\\python.exe analysis\\03_python_stats.py
Reads analysis/data/scored.csv (from prepare_data.py); writes analysis/results/python_stats.txt.

Conventions: d_X are raw change (-2..+2, negative = less Arabic). Displacement, Disp_X, DialectLoss,
FormalLoss and AbilityDecline run the other way: HIGHER = MORE LOSS.
"""
import io, os, itertools
from collections import Counter, defaultdict
import numpy as np
import pandas as pd
import patsy
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.multitest import multipletests
from sklearn.decomposition import FactorAnalysis

HERE = os.path.dirname(os.path.abspath(__file__))
ALL = pd.read_csv(os.path.join(HERE, 'data', 'scored.csv'))
PRIMARY = 'core'     # 'core' = the 37 who grew up and live in the Arab region and did not move (primary); 'all' = all 40
ALL['SocialLoss'] = -ALL.SocialMedia             # same direction as the loss scores
ALL['stable_grad'] = ((ALL.Events_1 == 0) & (ALL.Events_3 == 0) & (ALL.Role != 4)).astype(int)   # graduating counts as same setting
d = ALL[ALL.core == 1].copy() if PRIMARY == 'core' else ALL
OTHER = ALL if PRIMARY == 'core' else ALL[ALL.core == 1].copy()
LAB = '(core sample)' if PRIMARY == 'core' else '(all respondents)'
OL = '(all respondents)' if PRIMARY == 'core' else '(core sample)'
OUT = os.path.join(HERE, 'results', 'python_stats.txt')
os.makedirs(os.path.dirname(OUT), exist_ok=True)

DOM = ['WorkStudy', 'Writing', 'Self', 'Personal', 'Family', 'Fusha', 'Religion', 'Consume']
COV = ['Age25', 'EventMove']                      # confounders: age, and starting English-medium study/work or moving
BOOT, SEED = 5000, 20261002
lines = []
say = lambda *a: lines.append(' '.join(str(x) for x in a))
fmtp = lambda p: '<.0001' if p < .0001 else '%.4f' % p
cv = lambda covs: ''.join(' + ' + c for c in covs)


# ------------------------------------------------------------------ tests
def wilson(k, n, z=1.959964):
    if n == 0:
        return np.nan, np.nan
    p = k / n
    den = 1 + z * z / n
    c = (p + z * z / (2 * n)) / den
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return c - h, c + h


def wilcoxon_signed(x, exact_max=15):
    """One-sample (or paired-difference) Wilcoxon signed-rank test against 0. Zeros dropped, tie-corrected.
    z carries DIRECTION (positive = values above 0). With more than 15 non-zero values the p is the normal
    approximation without continuity correction, as SPSS 23 computes it; with 15 or fewer it is the exact
    conditional p (every sign pattern over the observed ranks equally likely), because the approximation is
    not valid there. SPSS prints only the approximation, so those few lines will differ from SPSS."""
    x = pd.Series(x).dropna().round(9)                 # merge float-split ties in differences of means
    nz = x[x != 0].values
    if len(nz) == 0:
        return dict(n=len(x), n_nz=0, z=0.0, p=1.0, r=0.0, method='-')
    r = stats.wilcoxon(x, zero_method='wilcox', correction=False, method='approx')
    rk = stats.rankdata(np.abs(nz))
    wp, mu = rk[nz > 0].sum(), rk.sum() / 2
    z = np.sign(wp - mu) * abs(r.zstatistic)
    if len(nz) <= exact_max:
        sums = np.array([rk[np.array(b, bool)].sum() for b in itertools.product([0, 1], repeat=len(nz))])
        p, method = float(np.mean(np.abs(sums - mu) >= abs(wp - mu) - 1e-9)), 'exact'
    else:
        p, method = r.pvalue, 'asymptotic'
    return dict(n=len(x), n_nz=len(nz), z=z, p=p, r=z / np.sqrt(len(x)), method=method)


def sign_test(x):
    """Exact binomial sign test of less vs more, zeros excluded."""
    x = pd.Series(x).dropna()
    less, more = int((x < 0).sum()), int((x > 0).sum())
    return dict(less=less, more=more, p=stats.binomtest(less, less + more, .5).pvalue if less + more else 1.0)


def mann_whitney(a, b):
    """Mann-Whitney U, normal approximation with tie correction and no continuity correction (SPSS's
    Asymp. Sig.). Returns the signed Z (positive = a ranks higher) and the two-sided p."""
    a, b = pd.Series(a).dropna(), pd.Series(b).dropna()
    r = stats.mannwhitneyu(a, b, alternative='two-sided', use_continuity=False, method='asymptotic')
    z = np.sign(r.statistic - len(a) * len(b) / 2) * stats.norm.isf(r.pvalue / 2)
    return z, r.pvalue


def page_exact(data, cols):
    """Page's L trend test, exact and tie-aware: the null distribution of L is built row by row from every
    permutation of that row's own (mid)ranks. One-sided: columns must be in the PREDICTED INCREASING order."""
    X = data[cols].dropna().values
    w = np.arange(1, len(cols) + 1)
    R = np.apply_along_axis(stats.rankdata, 1, X)
    L = float((R * w).sum())
    dist = {0.0: 1.0}
    for row in R:
        perms = Counter(round(float(np.dot(pp, w)), 9) for pp in itertools.permutations(row))
        tot = sum(perms.values())
        new = defaultdict(float)
        for a, pa in dist.items():
            for v, c in perms.items():
                new[round(a + v, 9)] += pa * c / tot
        dist = new
    return L, float(sum(pr for l, pr in dist.items() if l >= L - 1e-9)), len(X)


def page(data, cols, label):
    L, p, n = page_exact(data, cols)
    cc = data[cols].dropna()                          # the test uses complete cases, so the means shown do too
    say('    Page %-24s n=%2d  L=%.1f  one-sided exact p=%s   (complete-case means: %s)' % (label, n, L, fmtp(p),
        ', '.join('%s %+.2f' % (c, cc[c].mean()) for c in cols)))
    return p


# ------------------------------------------------------------------ regression
def ols(formula, data, title=None):
    m = smf.ols(formula, data=data).fit(cov_type='HC3', use_t=True)
    if title:
        est = data.loc[m.model.data.row_labels]      # standardized betas use the model's own (listwise) sample
        say('\n' + title)
        say('    n=%d  R2=%.3f  adj R2=%.3f  | HC3 Wald F(%d,%d)=%.2f p=%s'
            % (int(m.nobs), m.rsquared, m.rsquared_adj, int(m.df_model), int(m.df_resid), float(m.fvalue), fmtp(float(m.f_pvalue))))
        ci = m.conf_int()
        y = formula.split('~')[0].strip()
        for k in m.params.index:
            beta = '' if k == 'Intercept' else '  beta=%+.2f' % (m.params[k] * est[k].std() / est[y].std())
            say('    %-14s b=%+.3f  HC3 SE=%.3f  t(%d)=%+.2f  p=%s  95%% CI [%+.3f, %+.3f]%s'
                % (k, m.params[k], m.bse[k], int(m.df_resid), m.tvalues[k], fmtp(m.pvalues[k]), ci.loc[k, 0], ci.loc[k, 1], beta))
    return m


def hc3_t(X, Y, j):
    """HC3 t-statistics of coefficient j for every column of Y (vectorised, for the wild bootstrap)."""
    XtXi = np.linalg.inv(X.T @ X)
    A = XtXi @ X.T
    h = np.einsum('ij,jk,ik->i', X, XtXi, X)
    B = A @ Y
    E = Y - X @ B
    V = ((A[j] ** 2)[:, None] * (E ** 2) / ((1 - h) ** 2)[:, None]).sum(axis=0)
    return B[j] / np.sqrt(V)


def wild_p(formula, data, term, reps=9999):
    """Wild bootstrap p for one coefficient: the null is imposed (restricted model without the term),
    Rademacher weights, HC3 t as the statistic. A small-sample check on the HC3 p-values."""
    y, X = patsy.dmatrices(formula, data, return_type='dataframe')
    j = list(X.columns).index(term)
    Xv, yv = X.values, y.values.ravel()
    t_obs = hc3_t(Xv, yv[:, None], j)[0]
    X0 = np.delete(Xv, j, axis=1)
    f0 = X0 @ np.linalg.lstsq(X0, yv, rcond=None)[0]
    e0 = yv - f0
    rng = np.random.default_rng(SEED)
    V = rng.choice([-1.0, 1.0], size=(len(yv), reps))
    t_star = hc3_t(Xv, f0[:, None] + e0[:, None] * V, j)
    return float((np.sum(np.abs(t_star) >= abs(t_obs)) + 1) / (reps + 1))


def family_b(data, label, covs=COV, disp='Displacement', abil='AbilityDecline', x='AI_Intensity', gap='QualityGap', wild=False):
    """H3 and H4 with Holm across the three H3 coefficients and the H4 slope."""
    f3 = '%s ~ %s + EnglishShare + %s%s' % (disp, x, gap, cv(covs))
    f4 = '%s ~ %s%s' % (abil, disp, cv(covs))
    m3 = ols(f3, data, 'H3 %s' % label)
    jt = m3.wald_test('%s = 0, EnglishShare = 0, %s = 0' % (x, gap), use_f=True, scalar=True)
    say('    joint test of the three H3 predictors (HC3): F(3,%d)=%.2f p=%s' % (int(m3.df_resid), float(jt.statistic), fmtp(float(jt.pvalue))))
    m4 = ols(f4, data, 'H4 %s' % label)
    terms = [(f3, x, 'intensity'), (f3, 'EnglishShare', 'English share'), (f3, gap, 'quality gap'), (f4, disp, 'H4')]
    ps = [m3.pvalues[x], m3.pvalues['EnglishShare'], m3.pvalues[gap], m4.pvalues[disp]]
    adj = multipletests(ps, method='holm')[1]
    say('    Holm family B: ' + '   '.join('%s p=%s -> %s' % (h, fmtp(p), fmtp(a)) for (_, _, h), p, a in zip(terms, ps, adj)))
    if wild:
        wp = [wild_p(f, data, t) for f, t, _ in terms]
        wadj = multipletests(wp, method='holm')[1]
        say('    wild bootstrap (restricted, Rademacher, HC3-t, %d reps): ' % 9999
            + '   '.join('%s p=%s -> Holm %s' % (h, fmtp(p), fmtp(a)) for (_, _, h), p, a in zip(terms, wp, wadj)))


def firth(formula, data):
    """Firth-penalised logistic regression (the standard remedy for separation), with penalised
    likelihood-ratio tests for each coefficient."""
    y, X = patsy.dmatrices(formula, data, return_type='dataframe')
    yv, names = y.values.ravel(), list(X.columns)

    def fit(Xv):
        b = np.zeros(Xv.shape[1])
        def pll(b):
            p = 1 / (1 + np.exp(-Xv @ b)); W = p * (1 - p)
            return np.sum(yv * np.log(p) + (1 - yv) * np.log(1 - p)) + 0.5 * np.linalg.slogdet(Xv.T @ (Xv * W[:, None]))[1]
        for _ in range(200):
            p = 1 / (1 + np.exp(-Xv @ b)); W = p * (1 - p)
            inv = np.linalg.inv(Xv.T @ (Xv * W[:, None]))
            Xs = Xv * np.sqrt(W)[:, None]
            h = np.einsum('ij,jk,ik->i', Xs, inv, Xs)
            step = inv @ (Xv.T @ (yv - p + h * (0.5 - p)))
            old = pll(b)
            while pll(b + step) < old - 1e-12 and np.max(np.abs(step)) > 1e-10:
                step /= 2
            b = b + step
            if np.max(np.abs(step)) < 1e-9:
                break
        return b, pll(b), np.sqrt(np.diag(inv))
    Xv = X.values
    b, ll, se = fit(Xv)
    out = []
    for j, nm in enumerate(names):
        _, ll0, _ = fit(np.delete(Xv, j, axis=1))
        out.append((nm, b[j], se[j], stats.chi2.sf(2 * (ll - ll0), 1)))
    return out, int(len(yv)), int(yv.sum())


def mediation(df, x, m, y, covs, title):
    c = cv(covs)
    df = df[[x, m, y] + covs].dropna().reset_index(drop=True)
    fa = smf.ols('%s ~ %s%s' % (m, x, c), df).fit(cov_type='HC3', use_t=True)
    fb = smf.ols('%s ~ %s + %s%s' % (y, x, m, c), df).fit(cov_type='HC3', use_t=True)
    fc = smf.ols('%s ~ %s%s' % (y, x, c), df).fit(cov_type='HC3', use_t=True)
    a, b = fa.params[x], fb.params[m]
    rng = np.random.default_rng(SEED)
    ind = np.empty(BOOT)
    for i in range(BOOT):
        s = df.iloc[rng.integers(0, len(df), len(df))].reset_index(drop=True)
        ind[i] = smf.ols('%s ~ %s%s' % (m, x, c), s).fit().params[x] * smf.ols('%s ~ %s + %s%s' % (y, x, m, c), s).fit().params[m]
    lo, hi = np.percentile(ind, [2.5, 97.5])
    say('\n' + title)
    say('    n=%d  covariates: %s' % (len(df), ', '.join(covs) or 'none'))
    say('    a  (X->M)     = %+.3f  HC3 p=%s' % (a, fmtp(fa.pvalues[x])))
    say('    b  (M->Y | X) = %+.3f  HC3 p=%s' % (b, fmtp(fb.pvalues[m])))
    say("    c' (direct)   = %+.3f  HC3 p=%s   c (total) = %+.3f" % (fb.params[x], fmtp(fb.pvalues[x]), fc.params[x]))
    say('    indirect a*b  = %+.4f  95%% percentile CI [%+.4f, %+.4f]  (%d resamples, seed %d)  -> %s'
        % (a * b, lo, hi, BOOT, SEED, 'excludes 0' if lo > 0 or hi < 0 else 'includes 0'))
    say('    standardized indirect = %+.3f' % (a * b * df[x].std() / df[y].std()))


def parallel_mediation(df, x, m1, m2, y, covs, title):
    """E1: two mediators in parallel (PROCESS model 4 with two M); each indirect effect and their contrast."""
    c = cv(covs)
    df = df[[x, m1, m2, y] + covs].dropna().reset_index(drop=True)

    def est(s):
        a1 = smf.ols('%s ~ %s%s' % (m1, x, c), s).fit().params[x]
        a2 = smf.ols('%s ~ %s%s' % (m2, x, c), s).fit().params[x]
        fb = smf.ols('%s ~ %s + %s + %s%s' % (y, x, m1, m2, c), s).fit().params
        return a1 * fb[m1], a2 * fb[m2]
    i1, i2 = est(df)
    rng = np.random.default_rng(SEED)
    bs = np.array([est(df.iloc[rng.integers(0, len(df), len(df))].reset_index(drop=True)) for _ in range(BOOT)])
    say('\n' + title)
    say('    n=%d  covariates: %s' % (len(df), ', '.join(covs) or 'none'))
    for nm, v, col in [('via ' + m1, i1, bs[:, 0]), ('via ' + m2, i2, bs[:, 1]), ('contrast (1 - 2)', i1 - i2, bs[:, 0] - bs[:, 1])]:
        lo, hi = np.percentile(col, [2.5, 97.5])
        say('    %-24s %+.4f  95%% CI [%+.4f, %+.4f]' % (nm, v, lo, hi))


def influence(data, label):
    h = data.dropna(subset=['Displacement', 'AbilityDecline'] + COV)
    f = 'AbilityDecline ~ Displacement' + cv(COV)
    cook = pd.Series(smf.ols(f, h).fit().get_influence().cooks_distance[0], index=h.id.values).sort_values(ascending=False)
    cut = 4 / len(cook)
    say("    H4 influence %s: largest Cook's distances (rule of thumb 4/n = %.2f): %s"
        % (label, cut, ', '.join('id %d: %.2f' % (i, v) for i, v in cook.head(3).items())))
    for drop in [[cook.index[0]], [cook.index[1]], list(cook[cook > cut].index)]:
        m = smf.ols(f, h[~h.id.isin(drop)]).fit(cov_type='HC3', use_t=True)
        say('      without id(s) %-14s b=%+.3f p=%s n=%d' % (','.join(str(int(i)) for i in drop), m.params['Displacement'],
                                                            fmtp(m.pvalues['Displacement']), int(m.nobs)))


def omega(X, boot=2000):
    """McDonald's omega total from a one-factor model on standardized items, with a bootstrap CI.
    Loadings keep their signs: (sum of loadings)^2 does not depend on the factor's arbitrary sign."""
    def om(Z):
        sd = Z.std(ddof=1)
        if (sd == 0).any():
            return np.nan                      # a resample in which an item never varies: omega undefined
        Z = (Z - Z.mean()) / sd
        fa = FactorAnalysis(n_components=1, random_state=0).fit(Z.values)
        lam, psi = fa.components_[0], fa.noise_variance_
        return lam.sum() ** 2 / (lam.sum() ** 2 + psi.sum())
    X = X.dropna()
    rng = np.random.default_rng(SEED)
    bs = np.array([om(X.iloc[rng.integers(0, len(X), len(X))]) for _ in range(boot)])
    k = X.shape[1]; C = X.corr().values
    alpha = k / (k - 1) * (1 - X.var(ddof=1).sum() / X.sum(axis=1).var(ddof=1))
    return om(X), np.nanpercentile(bs, [2.5, 97.5]), alpha, C[np.triu_indices(k, 1)].mean(), len(X), int(np.isnan(bs).sum())


# ================================================================== output
say('=' * 96)
say('Python statistics. Primary sample: %s (n=%d). Covariates: %s.' % (LAB[1:-1], len(d), ', '.join(COV)))
say('Decisions and their alternatives: analysis/ANALYSIS-DECISIONS.md')
say('p-values are two-sided except Page\'s trend test (one-sided: the order is predicted).')
say('=' * 96)

say('\nPARTICIPANTS')
say('    submitted %d -> consented %d -> eligible %d -> analysed %d' % (len(ALL), int(ALL.Consent.sum()), int(ALL.Eligible.sum()), len(d)))
say('    outside the primary sample: ids %s (21 grew up and lives outside the Arab world; 25 moved country since 2022;'
    ' 38 moved and now lives outside)' % ALL.loc[ALL.core == 0, 'id'].tolist())
say('    analysed sample: grew up in Lebanon %d, the Gulf %d; live in Lebanon %d; under 25: %d; computing/IT: %d;'
    ' wrote Fusha before AI (yes or sometimes): %d'
    % ((d.Country_GrewUp == 1).sum(), (d.Country_GrewUp == 3).sum(), (d.Country_Now == 1).sum(),
       (d.Age25 == 0).sum(), d.Computing.sum(), (d.FushaPreAI != 3).sum()))
say('    EventMove in the analysed sample = started studying or working in English: n=%d (nobody ticked "moved")' % d.EventMove.sum())
say('    same work/study setting throughout the AI period: strict n=%d; counting graduation as the same setting n=%d'
    % (d.stable.sum(), d.stable_grad.sum()))
say('    straight-liners (every change row "much less"): ids %s. Id 29 has only 5 applicable domains (work/study,'
    ' formal texts and religion marked not applicable), so it has no displacement score and no work/study or'
    ' Fusha change: it enters no confirmatory test.' % d.loc[d.straightline == 1, 'id'].tolist())
say('    power: with n=%d, the smallest correlation detectable at 80%% power (alpha .05, two-sided) is r = %.2f'
    % (len(d), np.tanh((1.959964 + 0.841621) / np.sqrt(len(d) - 3))))

# ------------------------------------------------------------------ RQ1 profile
say('\nRQ1 DOMAIN PROFILE %s, descriptive. d_X = AI-attributed change.' % LAB)
say('    z carries direction (negative = less Arabic); r = z / sqrt(n). The 8-domain Holm column is a strict')
say('    check on the profile, not a confirmatory family.')
say('    %-10s %3s %15s %7s %7s %6s %7s %8s %8s %6s' % ('domain', 'n', 'less% [95% CI]', 'same%', 'more%', 'mean', 'z', 'p', 'p_Holm8', 'r'))
rows = []
for dom in DOM:
    x = d['d_' + dom].dropna()
    w = wilcoxon_signed(x)
    lo, hi = wilson(int((x < 0).sum()), len(x))
    rows.append((dom, len(x), 100 * (x < 0).mean(), 100 * lo, 100 * hi, 100 * (x == 0).mean(), 100 * (x > 0).mean(), x.mean(), w['z'], w['p'], w['r']))
for r, ph in zip(rows, multipletests([r[9] for r in rows], method='holm')[1]):
    say('    %-10s %3d %4.0f [%2.0f, %2.0f] %7.0f %7.0f %+6.2f %+7.2f %8s %8s %+6.2f'
        % (r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7], r[8], fmtp(r[9]), fmtp(ph), r[10]))
k = int((d.SwitchEng >= 3).sum()); lo, hi = wilson(k, len(d))
say('    substitution (did something in English although Arabic was possible, at least sometimes): %d/%d = %.0f%% [%.0f, %.0f]'
    % (k, len(d), 100 * k / len(d), 100 * lo, 100 * hi))
say('    domains lost per person (applicable domains only): %s (mean %.2f)' % (d.DomainsLost.value_counts().sort_index().to_dict(), d.DomainsLost.mean()))

# ------------------------------------------------------------------ confirmatory
say('\n' + '=' * 96)
say('CONFIRMATORY')
say('=' * 96)


def family_a(data, label):
    say('\nFAMILY A %s (Holm across H1a, H1b, H2a, H2b)' % label)
    ps = []
    for h, col in [('H1a Fusha', 'd_Fusha'), ('H1b work/study', 'd_WorkStudy')]:
        w, s = wilcoxon_signed(data[col]), sign_test(data[col])
        say('    %-15s Wilcoxon z=%+.2f p=%s (%s) r=%+.2f n=%d | exact sign test %d less vs %d more p=%s'
            % (h, w['z'], fmtp(w['p']), w['method'], w['r'], w['n'], s['less'], s['more'], fmtp(s['p'])))
        ps.append(w['p'])
    say('    H2a Fishman order, predicted rising loss: family < personal < work/study')
    ps.append(page(data, ['Disp_Family', 'Disp_Personal', 'Disp_WorkStudy'], ''))
    X = data[['Disp_WorkStudy', 'Disp_Personal', 'Disp_Family']].dropna()
    fr = stats.friedmanchisquare(*[X[c] for c in X.columns])
    w = wilcoxon_signed(X.Disp_WorkStudy - X.Disp_Family)
    say('        Friedman chi2(2)=%.2f p=%s Kendall W=%.2f n=%d | work/study vs family Wilcoxon z=%+.2f p=%s (%s)'
        % (fr.statistic, fmtp(fr.pvalue), fr.statistic / (len(X) * 2), len(X), w['z'], fmtp(w['p']), w['method']))
    w = wilcoxon_signed(data.Disp_Fusha - data.DialectLoss)
    say('    H2b Fusha vs dialect Wilcoxon on (Fusha loss - dialect loss) z=%+.2f p=%s (%s) r=%+.2f n=%d (mean difference %+.2f)'
        % (w['z'], fmtp(w['p']), w['method'], w['r'], w['n'], (data.Disp_Fusha - data.DialectLoss).mean()))
    ps.append(w['p'])
    adj = multipletests(ps, method='holm')[1]
    say('    Holm: ' + '   '.join('%s p=%s -> %s' % (h, fmtp(p), fmtp(a)) for h, p, a in zip(['H1a', 'H1b', 'H2a', 'H2b'], ps, adj)))


family_a(d, LAB)
family_b(d, LAB[:-1] + ', HC3)', wild=True)
say('\nH5  X = AI_Intensity, M = Displacement, Y = AbilityDecline (PROCESS model 4 logic). Underpowered at this n.')
mediation(d, 'AI_Intensity', 'Displacement', 'AbilityDecline', COV, '    primary')

# ------------------------------------------------------------------ robustness
say('\n' + '=' * 96)
say('ROBUSTNESS')
say('=' * 96)
say('\n(a) AI or technology in general? Social media is ONE overall question; the AI scores average domains,')
say('    so the comparison is a bracket, not a verdict. SocialLoss = -SocialMedia (higher = more loss).')
for v in ['Displacement', 'FormalLoss']:
    x = d[[v, 'SocialLoss']].dropna()
    rho = stats.spearmanr(x[v], x.SocialLoss)
    w = wilcoxon_signed(x[v] - x.SocialLoss)
    say('    %-13s AI %+.2f vs social media %+.2f | Spearman rho=%.2f p=%s | paired Wilcoxon z=%+.2f p=%s n=%d'
        % (v, x[v].mean(), x.SocialLoss.mean(), rho.statistic, fmtp(rho.pvalue), w['z'], fmtp(w['p']), len(x)))
g1 = d.loc[d.SocialMedia < 0, 'Displacement'].dropna(); g0 = d.loc[d.SocialMedia >= 0, 'Displacement'].dropna()
w0 = wilcoxon_signed(g0); zmw, pmw = mann_whitney(g1, g0)
say('    exploratory split: displacement among those who also blame social media n=%d mean %+.2f | who do not n=%d mean %+.2f'
    ' (vs 0: z=%+.2f p=%s) | Mann-Whitney Z=%+.2f p=%s' % (len(g1), g1.mean(), len(g0), g0.mean(), w0['z'], fmtp(w0['p']), zmw, fmtp(pmw)))
ols('Displacement ~ AI_Intensity + EnglishShare + QualityGap' + cv(COV) + ' + SocialLoss', d,
    '    H3 + social-media attribution as a covariate')

say('\n(b) Binary robustness: Firth logistic regression of NetLoss (displacement above 0) on the H3 predictors and covariates')
res, nn, ev = firth('NetLoss ~ AI_Intensity + EnglishShare + QualityGap' + cv(COV), d)
for nm, b, se, p in res:
    say('    %-14s b=%+.3f  OR=%.2f  penalised-LR p=%s' % (nm, b, np.exp(b), fmtp(p)))
say('    n=%d  NetLoss=1 for %d, 0 for %d  (events per predictor %.1f: indicative only)' % (nn, ev, nn - ev, min(ev, nn - ev) / 5))

say('\n(c) The other sample: %s, n=%d (same models)' % (OL[1:-1], len(OTHER)))
family_a(OTHER, OL)
family_b(OTHER, OL[:-1] + ', HC3)')
mediation(OTHER, 'AI_Intensity', 'Displacement', 'AbilityDecline', COV, '    H5 ' + OL)
say('')
influence(d, LAB)
influence(OTHER, OL)

say('\n(d) Change of setting as a rival explanation for the work/study loss')
for lab, sub in [('same setting (strict, stable)', d[d.stable == 1]), ('same setting (graduation counted as same)', d[d.stable_grad == 1]),
                 ('setting changed (strict)', d[d.stable == 0]), ('did not start English study/work', d[d.EventMove == 0])]:
    w, s = wilcoxon_signed(sub.d_WorkStudy), sign_test(sub.d_WorkStudy)
    say('    work/study, %-42s n=%2d mean %+.2f | Wilcoxon z=%+.2f p=%s (%s) | sign %d less vs %d more p=%s'
        % (lab, w['n'], sub.d_WorkStudy.mean(), w['z'], fmtp(w['p']), w['method'], s['less'], s['more'], fmtp(s['p'])))
z1, p1 = mann_whitney(d.loc[d.stable == 1, 'd_WorkStudy'], d.loc[d.stable == 0, 'd_WorkStudy'])
u = d[d.Age25 == 0]
z2, p2 = mann_whitney(u.loc[u.stable == 1, 'd_WorkStudy'], u.loc[u.stable == 0, 'd_WorkStudy'])
say('    stable vs changed, Mann-Whitney: all Z=%+.2f p=%s | under 25 only (means %+.2f, n=%d vs %+.2f, n=%d) Z=%+.2f p=%s'
    % (z1, fmtp(p1), u.loc[u.stable == 1, 'd_WorkStudy'].mean(), int((u.stable == 1).sum()),
       u.loc[u.stable == 0, 'd_WorkStudy'].mean(), int((u.stable == 0).sum()), z2, fmtp(p2)))
say('    (%d of the %d strictly stable respondents are aged 25+, and those report no change in any domain)'
    % (int(((d.stable == 1) & (d.Age25 == 1)).sum()), int(d.stable.sum())))
ols('d_WorkStudy ~ stable + Age25', d, '    work/study change on stable setting, adjusted for age')
page(d[d.stable == 1], ['Disp_Family', 'Disp_Personal', 'Disp_WorkStudy'], '(strictly stable only)')

say('\n(e) Without the straight-liners (in practice id 13: id 29 is already outside every confirmatory test)')
ns = d[d.straightline == 0]
w = wilcoxon_signed(ns.d_Fusha)
say('    H1a Fusha: Wilcoxon z=%+.2f p=%s n=%d' % (w['z'], fmtp(w['p']), w['n']))
family_b(ns, '(without straight-liners, HC3)')

say('\n(f) Covariate sets')
family_b(d, '(no covariates, HC3)', covs=[])
family_b(d, '(age only: the 27 Sep plan\'s small-sample rule, HC3)', covs=['Age25'])
family_b(d, '(+ computing field and AI tenure, HC3)', covs=COV + ['Computing', 'AI_TenureRank'])
family_b(d, '(+ English proficiency, HC3)', covs=COV + ['Eng_Prof'])

# ------------------------------------------------------------------ sensitivity: alternative definitions
say('\n' + '=' * 96)
say('SENSITIVITY: the alternative at each decision point')
say('=' * 96)
family_b(d, '(displacement over writing, self, personal, family only - the 27 Sep plan, HC3)', disp='Displacement4', wild=True)
family_b(d, '(dialect-only displacement: self, personal, family, HC3)', disp='DialectLoss')
family_b(d, '(AI intensity including frequency, HC3)', x='AI_Intensity3')
family_b(d, '(quality gap without the AI-voice item - the 27 Sep plan, HC3)', gap='QualityGap3')
family_b(d, '(ability decline including the Fusha-register item, HC3)', abil='AbilityDecline4')
r1 = stats.spearmanr(d.Displacement, d.AbilityDecline, nan_policy='omit')
say('\n    H4 as a rank correlation: Spearman Displacement-AbilityDecline rho=%.2f p=%s' % (r1.statistic, fmtp(r1.pvalue)))
alt = d.copy()
pairs = [('WorkStudy', 'WorkStudy'), ('Writing', 'Writing'), ('Self', 'Self'), ('Personal', 'Personal'),
         ('Family', 'Family'), ('Fusha', 'Formal'), ('Religion', 'Religion'), ('Consume', 'Consume')]
for dom, cu in pairs:
    a = alt['ArUse_' + dom]
    alt['d2_' + dom] = a.where(~((alt['CurUse_' + cu] == 5) & (a == 0)))
D2 = alt[['d2_' + x for x, _ in pairs]]
alt['Displacement'] = -D2.mean(axis=1).where(D2.notna().sum(axis=1) >= 6)
removed = sum(int(((d['CurUse_' + cu] == 5) & (d['ArUse_' + dom] != 0)).sum()) for dom, cu in pairs)
say('\n(g) The not-applicable filter removes %d answers that were not "no change". Variant removing only "no change":' % removed)
w = wilcoxon_signed(alt.d2_Fusha)
say('    H1a Fusha: Wilcoxon z=%+.2f p=%s n=%d' % (w['z'], fmtp(w['p']), w['n']))
family_b(alt, '(not-applicable filter on "no change" answers only, HC3)')

# ------------------------------------------------------------------ exploratory (planned)
say('\n' + '=' * 96)
say('EXPLORATORY (planned before the data; no correction)')
say('=' * 96)
parallel_mediation(d, 'AI_Intensity', 'Displacement', 'Switch_Mode', 'AbilityDecline', COV,
                   'E1  parallel mediators: Displacement and change in switching (Switch_Mode, positive = more switching)')
e3 = d[d.FushaPreAI != 3]
say('\nE3  Fusha-register ability, among those who wrote Fusha before AI (n=%d)' % len(e3))
say('    Abil_Register_f distribution (-2 much harder .. +2 much easier): %s' % e3.Abil_Register_f.value_counts().sort_index().to_dict())
rr = stats.spearmanr(-e3.Abil_Register_f, e3.Displacement, nan_policy='omit')
say('    Spearman (register decline, Displacement) rho=%.2f p=%s' % (rr.statistic, fmtp(rr.pvalue)))

# ------------------------------------------------------------------ reliability
say('\n' + '=' * 96)
say('RELIABILITY %s: omega with bootstrap CI, alpha, mean inter-item r' % LAB)
say('=' * 96)
for nm, cols in [('Displacement (8 domains)', ['d_' + x for x in DOM]),
                 ('AbilityDecline (3 items)', ['Abil_Lexical', 'Abil_Fluency', 'Abil_ArabicOnly']),
                 ('QualityGap (4 items)', ['Gap_Understand', 'Gap_Accuracy', 'Gap_Voice', 'Gap_Equal_r']),
                 ('QualityGap3 (3 items)', ['Gap_Understand', 'Gap_Accuracy', 'Gap_Equal_r'])]:
    for sample, lab in [(d, LAB), (OTHER, OL)]:
        o, ci, al, mr, nn, bad = omega(sample[cols])
        say('    %-26s %-18s n=%d  omega=%.2f [%.2f, %.2f]  alpha=%.2f  mean inter-item r=%.2f%s'
            % (nm, lab, nn, o, ci[0], ci[1], al, mr, '  (%d of 2000 resamples skipped)' % bad if bad else ''))
say('    Displacement uses complete cases (the not-applicable filter leaves some domains missing).')

io.open(OUT, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
print('\n'.join(lines))
print('\nwritten to', OUT)
