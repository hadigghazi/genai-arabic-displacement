# -*- coding: utf-8 -*-
"""
Cross-check SPSS against Python, number by number.

SPSS runs 01 and 02 with every table exported as XML (OMS FORMAT=OXML). This script reads that XML
and compares the key numbers with values recomputed here independently, using SPSS's own conventions
(classical OLS errors, asymptotic Wilcoxon without continuity correction, exact sign test for n <= 25,
Mann-Whitney without continuity correction, Cronbach's alpha on listwise cases).

Run with Anaconda's Python:  python analysis/crosscheck_spss.py <path to oms.xml> <path to the .sav's coded.csv folder>
Exit code 1 if any number differs beyond rounding.
"""
import sys, os
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

OMS = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
d = pd.read_csv(os.path.join(HERE, 'data', 'scored.csv'))
d['zero'] = 0
d['SocialLoss'] = -d.SocialMedia
d['Under25'] = (d.Age25 == 0).astype(int)
prim = d                      # primary sample: all respondents
oth = d[d.core == 1]          # sensitivity: the plan's core sample

# ---------------------------------------------------------------- read every SPSS table
root = ET.parse(OMS).getroot()
NS = root.tag.split('}')[0] + '}'
tables = []
for pt in root.iter(NS + 'pivotTable'):
    cells = []
    def walk(el, path):
        for ch in el:
            tag = ch.tag.replace(NS, '')
            if tag in ('category', 'group'):
                walk(ch, path + [ch.get('text') or ch.get('varName') or ''])
            elif tag == 'dimension':
                walk(ch, path)
            elif tag == 'cell':
                num = ch.get('number')
                cells.append((path, float(num) if num not in (None, '') else None, ch.get('text')))
            else:
                walk(ch, path)
    walk(pt, [])
    tables.append((pt.get('subType'), cells))


def tabs(sub):
    return [c for s, c in tables if s == sub]


def get(cells, *keys):
    """The number in the cell whose path contains every key (exact match on category text)."""
    hits = [n for p, n, t in cells if all(k in p for k in keys) and n is not None]
    if len(hits) != 1:
        raise KeyError('%d cells match %s' % (len(hits), keys))
    return hits[0]


results = []
DETAILS = []


def check(label, spss_val, py_val, tol):
    ok = abs(spss_val - py_val) <= tol
    results.append(ok)
    DETAILS.append({'statistic': label, 'spss': float(spss_val), 'python': float(py_val), 'tolerance': tol, 'agree': bool(ok)})
    print('%-4s %-62s SPSS %10.4f   Python %10.4f' % ('OK' if ok else 'DIFF', label, spss_val, py_val))


# ---------------------------------------------------------------- independent Python values
def wil_z(x):
    x = pd.Series(x).dropna().round(9)
    r = stats.wilcoxon(x, zero_method='wilcox', correction=False, method='approx')
    return -abs(r.zstatistic), r.pvalue                     # SPSS prints Z as negative


def alpha(X):
    X = X.dropna(); k = X.shape[1]
    return k / (k - 1) * (1 - X.var(ddof=1).sum() / X.sum(axis=1).var(ddof=1))


def ols_b(formula, data, term):
    return smf.ols(formula, data).fit().params[term]


# reliability (02 runs it on the primary sample)
rel = tabs('Reliability Statistics')
for i, (nm, cols) in enumerate([('Displacement', ['d_WorkStudy', 'd_Writing', 'd_Self', 'd_Personal', 'd_Family', 'd_Fusha', 'd_Religion', 'd_Consume']),
                                ('Ability decline', ['Abil_Lexical', 'Abil_Fluency', 'Abil_ArabicOnly']),
                                ('Quality gap', ['Gap_Understand', 'Gap_Accuracy', 'Gap_Voice', 'Gap_Equal_r']),
                                ('Quality gap, 3 items', ['Gap_Understand', 'Gap_Accuracy', 'Gap_Equal_r'])]):
    check('alpha, %s (primary)' % nm, get(rel[i], "Cronbach's Alpha"), alpha(prim[cols]), .0006)

# Wilcoxon, in syntax order
wt = tabs('Wilcoxon Test Statistics')
wilcox = [('H1a Fusha (primary)', prim.d_Fusha), ('H1b work/study (primary)', prim.d_WorkStudy),
          ('H2a work/study vs family (primary, complete cases)',
           prim[['Disp_WorkStudy', 'Disp_Personal', 'Disp_Family']].dropna().eval('Disp_Family - Disp_WorkStudy')),
          ('H2b Fusha vs dialect (primary)', (prim.DialectLoss - prim.Disp_Fusha))]
for i, (lab, x) in enumerate(wilcox):
    z, p = wil_z(x)
    check('Wilcoxon Z, ' + lab, get(wt[i], 'Z'), z, .0006)
    check('Wilcoxon p, ' + lab, get(wt[i], 'Asymp. Sig. (2-tailed)'), p, .0006)

# sign tests (exact for n <= 25 in SPSS)
st = tabs('Sign Test Statistics')
for i, (lab, x) in enumerate([('H1a Fusha (primary)', prim.d_Fusha), ('H1b work/study (primary)', prim.d_WorkStudy)]):
    x = x.dropna(); less, more = int((x < 0).sum()), int((x > 0).sum())
    py_p = stats.binomtest(less, less + more, .5).pvalue
    cells = st[i]
    try:
        sp = get(cells, 'Exact Sig. (2-tailed)')
    except KeyError:
        sp = get(cells, 'Asymp. Sig. (2-tailed)')
        nn = less + more
        zc = (abs(less - nn / 2) - .5) / np.sqrt(nn / 4)          # SPSS's large-n sign test uses a continuity correction
        py_p = 2 * stats.norm.sf(zc)
    check('sign test p, ' + lab, sp, py_p, .0006)

# Friedman, H2a (primary, complete cases)
fr = tabs('Friedman Test Statistics')[0]
X = prim[['Disp_WorkStudy', 'Disp_Personal', 'Disp_Family']].dropna()
check('Friedman chi-square, H2a (primary)', get(fr, 'Chi-Square'), stats.friedmanchisquare(*[X[c] for c in X.columns]).statistic, .002)

# Mann-Whitney, stable vs changed (primary; then primary under 25)
mw = tabs('Mann Whitney Test Statistics')
for i, sub in enumerate([prim, prim[prim.Age25 == 0]]):
    a, b = sub.loc[sub.stable == 1, 'd_WorkStudy'].dropna(), sub.loc[sub.stable == 0, 'd_WorkStudy'].dropna()
    p = stats.mannwhitneyu(a, b, alternative='two-sided', use_continuity=False, method='asymptotic').pvalue
    check('Mann-Whitney p, stable vs changed (%s)' % ('primary' if i == 0 else 'primary, under 25'), get(mw[i], 'Asymp. Sig. (2-tailed)'), p, .0006)

# regressions: unstandardized B, in syntax order
co = tabs('Coefficients')
H3 = 'Displacement ~ AI_Intensity + EnglishShare + QualityGap'
regs = [  # (table index, model label, formula, data, term)
    (0, '2', H3 + ' + Age25 + EventMove', prim, 'EnglishShare'),
    (0, '2', H3 + ' + Age25 + EventMove', prim, 'AI_Intensity'),
    (1, '1', 'AbilityDecline ~ Displacement + Age25 + EventMove', prim, 'Displacement'),
    (2, '1', H3 + ' + Age25 + EventMove + SocialLoss', prim, 'EnglishShare'),
    (3, '1', 'd_WorkStudy ~ stable + Age25', prim, 'stable'),
    (6, '1', H3, prim, 'EnglishShare'),
    (7, '1', 'AbilityDecline ~ Displacement', prim, 'Displacement'),
    (12, '1', 'Displacement4 ~ AI_Intensity + EnglishShare + QualityGap + Age25 + EventMove', prim, 'EnglishShare'),
    (13, '1', 'AbilityDecline ~ Displacement4 + Age25 + EventMove', prim, 'Displacement4'),
    (14, '1', H3 + ' + Age25 + EventMove', oth, 'EnglishShare'),
    (15, '1', 'AbilityDecline ~ Displacement + Age25 + EventMove', oth, 'Displacement'),
]
for ti, model, f, data, term in regs:
    lab = 'B %s in "%s"%s' % (term, f.split('~')[0].strip() + ' ~ ...' + f.split('+')[-1], ' (core sample)' if data is oth else '')
    check(lab[:62], get(co[ti], model, term, 'B'), ols_b(f, data, term), .0006)

# the straight-liner models run under TEMPORARY SELECT IF: their n must exclude id 13 (and id 29, already missing)
ns = prim[prim.straightline == 0]
check('B EnglishShare, H3 without straight-liners', get(co[4], '1', 'EnglishShare', 'B'), ols_b(H3 + ' + Age25 + EventMove', ns, 'EnglishShare'), .0006)
check('B Displacement, H4 without straight-liners', get(co[5], '1', 'Displacement', 'B'), ols_b('AbilityDecline ~ Displacement + Age25 + EventMove', ns, 'Displacement'), .0006)

# descriptives of the eight change items (primary)
ds = tabs('Descriptive Statistics')
desc = [c for c in ds if any('d_Religion' in p for p, _, _ in c)][0]
for dom in ['WorkStudy', 'Fusha', 'Religion', 'Family']:
    check('mean d_%s (primary)' % dom, get(desc, 'd_' + dom, 'Mean'), prim['d_' + dom].mean(), .0006)

print('\n%d of %d numbers agree' % (sum(results), len(results)))
import json  # noqa: E402
with open(os.path.join(HERE, 'results', 'spss_crosscheck.json'), 'w', encoding='utf-8') as f:
    json.dump({'n': int(len(d)), 'agree': int(sum(results)), 'total': len(results), 'checks': DETAILS}, f, indent=1)
sys.exit(0 if all(results) else 1)
