# -*- coding: utf-8 -*-
"""
Cross-check SPSS against Python, number by number.

SPSS runs 01 and 02 with every table exported as XML (OMS FORMAT=OXML). This script reads that XML
and compares the key numbers with values recomputed here independently, using SPSS's own conventions
(classical OLS errors, asymptotic Wilcoxon without continuity correction, exact sign test for n <= 25,
Mann-Whitney without continuity correction, Cronbach's alpha on listwise cases, tie-corrected Friedman).

Tables are taken in the order 02_hypotheses.sps produces them, and every lookup checks that the table is the
intended one (the pair of variables, or the predictors of the regression), so an edit to 02 that shifts the
order fails loudly instead of comparing the wrong numbers. Agreement means equal to a relative 1e-6.

Run with Anaconda's Python:  python analysis/crosscheck_spss.py <path to oms.xml>
Writes results/spss_crosscheck.json (each check with the group and label the website shows).
Exit code 1 if any number differs.
"""
import json
import os
import sys
import xml.etree.ElementTree as ET

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

OMS = sys.argv[1]
HERE = os.path.dirname(os.path.abspath(__file__))
d = pd.read_csv(os.path.join(HERE, 'data', 'scored.csv'))
d['zero'] = 0
d['SocialLoss'] = -d.SocialMedia
d['SocialDecrease'] = (d.SocialMedia < 0).astype(int)
d['RegisterDecline'] = -d.Abil_Register_f
prim = d                      # all respondents
core = d[d.core == 1]         # sensitivity: the core sample

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


DETAILS = []


def check(group, label, spss_val, py_val):
    ok = bool(np.isclose(spss_val, py_val, rtol=1e-6, atol=1e-12))
    DETAILS.append({'group': group, 'statistic': label, 'spss': float(spss_val), 'python': float(py_val), 'agree': ok})
    print('%-4s %-66s SPSS %12.6f   Python %12.6f' % ('OK' if ok else 'DIFF', label, spss_val, py_val))


# ---------------------------------------------------------------- reliability
REL = 'Reliability'
rel = tabs('Reliability Statistics')
for i, (lab, cols) in enumerate([('decrease score (8 areas)', ['d_WorkStudy', 'd_Writing', 'd_Self', 'd_Personal', 'd_Family', 'd_Fusha', 'd_Religion', 'd_Consume']),
                                 ('difficulty without AI', ['Abil_Lexical', 'Abil_Fluency', 'Abil_ArabicOnly']),
                                 ('perceived quality gap (4 items)', ['Gap_Understand', 'Gap_Accuracy', 'Gap_Voice', 'Gap_Equal_r']),
                                 ('perceived quality gap (3 items)', ['Gap_Understand', 'Gap_Accuracy', 'Gap_Equal_r'])]):
    X = prim[cols].dropna(); k = X.shape[1]
    check(REL, 'Cronbach’s α, ' + lab, get(rel[i], "Cronbach's Alpha"),
          k / (k - 1) * (1 - X.var(ddof=1).sum() / X.sum(axis=1).var(ddof=1)))

# ---------------------------------------------------------------- Wilcoxon signed-rank, in syntax order
DIR = 'Direction and order'
wt, wr = tabs('Wilcoxon Test Statistics'), tabs('Wilcoxon Ranks')
WIL = [  # (table, second - first as SPSS prints it, data, group, label, listwise columns)
    (0, 'd_Fusha', 'zero', prim, DIR, 'H1a Fusha', None),
    (1, 'd_WorkStudy', 'zero', prim, DIR, 'H1b work or study', None),
    (2, 'Disp_Family', 'Disp_WorkStudy', prim, DIR, 'H2a work or study vs family', 'H2a'),
    (2, 'Disp_Personal', 'Disp_WorkStudy', prim, DIR, 'H2a work or study vs personal matters', 'H2a'),
    (2, 'Disp_Family', 'Disp_Personal', prim, DIR, 'H2a personal matters vs family', 'H2a'),
    (3, 'DialectLoss', 'Disp_Fusha', prim, DIR, 'H2b Fusha vs dialect', None),
    (4, 'Displacement', 'SocialLoss', prim, 'Social media', 'social media vs AI, all areas', None),
    (4, 'FormalLoss', 'SocialLoss', prim, 'Social media', 'social media vs AI, formal areas', None),
    (5, 'd_WorkStudy', 'zero', prim[prim.stable == 1], 'Group comparisons', 'work or study, unchanged setting', None),
    (10, 'Disp_Family', 'Disp_WorkStudy', core, 'Core sample', 'H2a work or study vs family', 'H2a'),
    (11, 'DialectLoss', 'Disp_Fusha', core, 'Core sample', 'H2b Fusha vs dialect', None),
]
H2A = ['Disp_WorkStudy', 'Disp_Personal', 'Disp_Family']
for ti, b, a, data, grp, lab, lw in WIL:
    src = data[H2A].dropna() if lw == 'H2a' else data
    x = (src[b] - src[a]).dropna().round(9)
    key = '%s - %s' % (b, a)
    r = stats.wilcoxon(x, zero_method='wilcox', correction=False, method='approx')
    check(grp, 'Wilcoxon |z|, ' + lab, abs(get(wt[ti], 'Z', key)), abs(r.zstatistic))
    check(grp, 'Wilcoxon p, ' + lab, get(wt[ti], 'Asymp. Sig. (2-tailed)', key), r.pvalue)
    # direction: SPSS's negative ranks are second < first
    check(grp, 'decreases (negative ranks), ' + lab, get(wr[ti], key, 'Negative Ranks', 'N'), (x < 0).sum())
    check(grp, 'increases (positive ranks), ' + lab, get(wr[ti], key, 'Positive Ranks', 'N'), (x > 0).sum())

# ---------------------------------------------------------------- sign tests (exact for n <= 25 in SPSS)
st = tabs('Sign Test Statistics')
SIGN = [(0, 'Switch_Mode', prim, 'Direction and order', 'switching, more vs less'),
        (1, 'd_Fusha', prim, DIR, 'H1a Fusha'), (2, 'd_WorkStudy', prim, DIR, 'H1b work or study'),
        (3, 'd_WorkStudy', prim[prim.stable == 1], 'Group comparisons', 'work or study, unchanged setting'),
        (4, 'd_WorkStudy', prim[(prim.stable == 1) & (prim.Events_4 == 0)], 'Group comparisons',
         'work or study, unchanged setting and no English-medium start')]
for ti, v, data, grp, lab in SIGN:
    x = data[v].dropna(); less, more = int((x < 0).sum()), int((x > 0).sum())
    key = '%s - zero' % v
    try:
        sp = get(st[ti], 'Exact Sig. (2-tailed)', key)
        py = stats.binomtest(less, less + more, .5).pvalue
    except KeyError:
        sp = get(st[ti], 'Asymp. Sig. (2-tailed)', key)
        nn = less + more                                      # SPSS's large-n sign test: continuity-corrected z
        py = 2 * stats.norm.sf((abs(less - nn / 2) - .5) / np.sqrt(nn / 4))
    check(grp, 'sign test p, ' + lab, sp, py)

# ---------------------------------------------------------------- Friedman and Kendall's W (complete cases)
for i, (data, grp) in enumerate([(prim, DIR), (core, 'Core sample')]):
    X = data[H2A].dropna()
    chi = stats.friedmanchisquare(*[X[c] for c in H2A]).statistic
    check(grp, 'Friedman χ², H2a order', get(tabs('Friedman Test Statistics')[i], 'Chi-Square'), chi)
    check(grp, 'Kendall’s W, H2a order', get(tabs('Kendall Test Statistics')[i], "Kendall's W"), chi / (len(X) * 2))

# ---------------------------------------------------------------- Mann-Whitney
mw = tabs('Mann Whitney Test Statistics')
MW = [(0, 'Displacement', prim, 'SocialDecrease', 'Social media', 'AI decrease, with vs without a social-media decrease'),
      (1, 'd_WorkStudy', prim, 'Events_1', 'Group comparisons', 'work or study, started university vs not'),
      (2, 'd_WorkStudy', prim, 'stable', 'Group comparisons', 'work or study, unchanged vs changed setting'),
      (3, 'd_WorkStudy', prim[prim.Age25 == 0], 'stable', 'Group comparisons', 'same, under 25 only')]
for ti, v, data, g, grp, lab in MW:
    a, b = data.loc[data[g] == 1, v].dropna(), data.loc[data[g] == 0, v].dropna()
    p = stats.mannwhitneyu(a, b, alternative='two-sided', use_continuity=False, method='asymptotic').pvalue
    check(grp, 'Mann–Whitney p, ' + lab, get(mw[ti], 'Asymp. Sig. (2-tailed)', v), p)

# ---------------------------------------------------------------- regressions, in syntax order
co = tabs('Coefficients')
H3 = 'AI_Intensity + EnglishShare + QualityGap'
cooks = smf.ols('AbilityDecline ~ Displacement + Age25 + EventMove', prim).fit().get_influence().cooks_distance[0]
h4rows = prim.dropna(subset=['AbilityDecline', 'Displacement', 'Age25', 'EventMove']).index
noinf = prim.drop(index=h4rows[int(np.argmax(cooks))])
ns = prim[prim.straightline == 0]
REG = 'Regression'
REGS = [  # (table, model, formula, data, terms to check, label)
    (0, '2', 'Displacement ~ Age25 + EventMove + ' + H3, prim, ['AI_Intensity', 'EnglishShare', 'QualityGap'], 'H3'),
    (1, '1', 'AbilityDecline ~ Displacement + Age25 + EventMove', prim, ['Displacement'], 'H4'),
    (2, '1', 'Displacement ~ AI_Intensity + Age25 + EventMove', prim, ['AI_Intensity'], 'intensity alone'),
    (3, '1', 'Displacement ~ QualityGap + Age25 + EventMove', prim, ['QualityGap'], 'quality gap alone'),
    (4, '1', 'Displacement ~ %s + Age25 + EventMove + SocialLoss' % H3, prim, ['EnglishShare'], 'social media controlled'),
    (5, '1', 'AbilityDecline ~ Displacement + Age25 + EventMove + SocialLoss', prim, ['Displacement'], 'social media controlled'),
    (6, '1', 'd_WorkStudy ~ stable + Age25', prim, ['stable'], 'age controlled'),   # TEMPORARY covered only the M-W test
    (7, '1', 'Displacement ~ %s + Age25 + EventMove + Events_1 + Events_2 + Events_3' % H3, prim, ['EnglishShare'], 'life transitions controlled'),
    (8, '1', 'AbilityDecline ~ Displacement + Age25 + EventMove + Events_1 + Events_2 + Events_3', prim, ['Displacement'], 'life transitions controlled'),
    (9, '1', 'Displacement ~ %s + Age25 + EventMove' % H3, ns, ['EnglishShare'], 'without straight-liners'),
    (10, '1', 'AbilityDecline ~ Displacement + Age25 + EventMove', ns, ['Displacement'], 'without straight-liners'),
    (11, '1', 'Displacement ~ %s + Age25 + EventMove' % H3, noinf, ['EnglishShare'], 'without the most influential case'),
    (12, '1', 'AbilityDecline ~ Displacement + Age25 + EventMove', noinf, ['Displacement'], 'without the most influential case'),
    (13, '1', 'Displacement ~ ' + H3, prim, ['EnglishShare'], 'no covariates'),
    (14, '1', 'AbilityDecline ~ Displacement', prim, ['Displacement'], 'no covariates'),
    (15, '1', 'Displacement ~ %s + Age25' % H3, prim, ['EnglishShare'], 'age only'),
    (16, '1', 'AbilityDecline ~ Displacement + Age25', prim, ['Displacement'], 'age only'),
    (17, '1', 'Displacement ~ %s + Age25 + EventMove + Eng_Prof' % H3, prim, ['EnglishShare'], 'English proficiency added'),
    (18, '1', 'AbilityDecline ~ Displacement + Age25 + EventMove + Eng_Prof', prim, ['Displacement'], 'English proficiency added'),
    (19, '1', 'Displacement ~ %s + Age25 + EventMove + Computing + AI_TenureRank' % H3, prim, ['EnglishShare'], 'field and AI tenure added'),
    (20, '1', 'AbilityDecline ~ Displacement + Age25 + EventMove + Computing + AI_TenureRank', prim, ['Displacement'], 'field and AI tenure added'),
    (21, '1', 'Displacement4 ~ %s + Age25 + EventMove' % H3, prim, ['EnglishShare'], 'four-area score'),
    (22, '1', 'AbilityDecline ~ Displacement4 + Age25 + EventMove', prim, ['Displacement4'], 'four-area score'),
    (23, '1', 'DialectLoss ~ %s + Age25 + EventMove' % H3, prim, ['EnglishShare'], 'dialect areas only'),
    (24, '1', 'AbilityDecline ~ DialectLoss + Age25 + EventMove', prim, ['DialectLoss'], 'dialect areas only'),
    (25, '1', 'Displacement ~ %s + Age25 + EventMove' % H3, core, ['EnglishShare'], 'core sample'),
    (26, '1', 'AbilityDecline ~ Displacement + Age25 + EventMove', core, ['Displacement'], 'core sample'),
]
assert len(co) == len(REGS), 'SPSS printed %d coefficient tables, expected %d' % (len(co), len(REGS))
NAMES = {'AI_Intensity': 'intensity', 'EnglishShare': 'English share', 'QualityGap': 'quality gap', 'Displacement': 'decrease',
         'Displacement4': 'decrease (four areas)', 'DialectLoss': 'decrease (dialect areas)', 'stable': 'unchanged setting'}
for ti, model, f, data, terms, lab in REGS:
    preds = {t.strip() for t in f.split('~')[1].split('+')}
    in_table = {p[1] for p, n, t in co[ti] if p and p[0] == model and len(p) > 1 and p[1] != '(Constant)'}
    assert in_table == preds, 'coefficient table %d has %s, expected %s' % (ti, sorted(in_table), sorted(preds))
    fit = smf.ols(f, data).fit()
    for t in terms:
        y = f.split('~')[0].strip()
        check(REG, 'b, %s → %s (%s)' % (NAMES.get(t, t), 'difficulty' if y == 'AbilityDecline' else NAMES.get(y, y), lab),
              get(co[ti], model, t, 'B'), fit.params[t])
        if lab in ('H3', 'H4'):
            check(REG, 'classical SE, %s (%s)' % (NAMES.get(t, t), lab), get(co[ti], model, t, 'Std. Error'), fit.bse[t])

# ---------------------------------------------------------------- Spearman correlations
sp = [c for c in tabs('Correlations') if any("Spearman's rho" in p for p, _, _ in c)]


def rho(cells, a, b, data):
    x = data[[a, b]].dropna()
    hit = [n for p, n, t in cells if p == ["Spearman's rho", a, 'Correlation Coefficient', b]]
    assert len(hit) == 1, (a, b)
    return hit[0], stats.spearmanr(x[a], x[b]).statistic


for a, b, grp, lab in [('Displacement', 'AbilityDecline', 'Correlations', 'decrease and difficulty (H4)'),
                       ('EnglishShare', 'Eng_Prof', 'Correlations', 'English share and English proficiency'),
                       ('Displacement', 'SocialLoss', 'Social media', 'AI decrease and social-media decrease'),
                       ('Displacement', 'Switch_Mode', 'Correlations', 'decrease and change in switching')]:
    check(grp, 'Spearman ρ, ' + lab, *rho(sp[0], a, b, prim))
check('Correlations', 'Spearman ρ, harder Fusha writing and decrease (E3)', *rho(sp[1], 'RegisterDecline', 'Displacement', prim))

# ---------------------------------------------------------------- influence and descriptives
check('Regression', 'largest Cook’s distance in H4', get(tabs('Descriptive Statistics')[-1], 'cook_h4', 'Maximum'), cooks.max())
desc = [c for c in tabs('Descriptive Statistics') if any('d_Religion' in p for p, _, _ in c)][0]
for dom, lab in [('WorkStudy', 'work or study'), ('Fusha', 'Fusha'), ('Religion', 'religious texts'), ('Family', 'family and friends')]:
    check('Descriptives', 'mean change, ' + lab, get(desc, 'd_' + dom, 'Mean'), prim['d_' + dom].mean())

agree = sum(c['agree'] for c in DETAILS)
print('\n%d of %d numbers agree' % (agree, len(DETAILS)))
with open(os.path.join(HERE, 'results', 'spss_crosscheck.json'), 'w', encoding='utf-8') as f:
    json.dump({'n': int(len(d)), 'agree': int(agree), 'total': len(DETAILS), 'checks': DETAILS}, f, ensure_ascii=False, indent=1)
sys.exit(0 if agree == len(DETAILS) else 1)
