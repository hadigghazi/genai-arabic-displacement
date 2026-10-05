# -*- coding: utf-8 -*-
"""
Exports the aggregate results the study website shows: app/web/data/study.json.

Only group-level numbers leave this machine: counts, percentages, test statistics and model scores.
The headline statistics (the domain profile, Family A and Family B) are recomputed here at full precision so
the site rounds exactly like the paper, and are asserted to agree with results/python_stats.txt. Everything
else is read from the result files the analysis scripts wrote, and each parsed number is asserted to exist.

Run with Anaconda's Python after 03-08:  C:\\Users\\User\\anaconda3\\python.exe analysis\\10_export_site_data.py
"""
import json
import os
import re
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats
from statsmodels.stats.multitest import multipletests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from instrument_data import SECTIONS  # noqa: E402

RES = os.path.join(HERE, 'results')
OUT = os.path.join(ROOT, 'app', 'web', 'data', 'study.json')
d = pd.read_csv(os.path.join(HERE, 'data', 'scored.csv'))
core = d[d.core == 1]


def read(name):
    with open(os.path.join(RES, name), encoding='utf-8') as f:
        return f.read()


PS, MLR, MLM, USE, OVR = (read('python_stats.txt'), read('ml_results.txt'), read('ml_more_targets.txt'),
                          read('ml_usability.txt'), read('oversampling_check.txt'))


def grab(pattern, text, flags=re.M):
    m = re.search(pattern, text, flags)
    assert m, 'not found: ' + pattern
    return m


def pv(s):
    """'<.0001' or '0.0223' -> float (the bound for '<')."""
    return float(s.lstrip('<'))


# 03's own helpers (Wilson CI, Wilcoxon with tie merging and exact small-n p, sign test, Mann-Whitney, exact
# tie-aware Page test), loaded from its source so the site uses the identical code
import ast, itertools  # noqa: E401,E402
from collections import Counter, defaultdict  # noqa: E402
with open(os.path.join(HERE, '03_python_stats.py'), encoding='utf-8') as _f:
    _tree = ast.parse(_f.read())
_keep = {'wilson', 'wilcoxon_signed', 'sign_test', 'mann_whitney', 'page_exact'}
exec(compile(ast.Module([n for n in _tree.body if isinstance(n, ast.FunctionDef) and n.name in _keep], []),
             '03_python_stats.py', 'exec'))


ITEM = {it['code']: it for sec in SECTIONS for it in sec['items'] if it.get('code')}
DOM = ['WorkStudy', 'Writing', 'Self', 'Personal', 'Family', 'Fusha', 'Religion', 'Consume']
DOM_LABEL = {'WorkStudy': 'Work or study', 'Writing': 'Messages and posts', 'Self': 'Self-talk and own notes',
             'Personal': 'Personal matters', 'Family': 'Family and friends', 'Fusha': 'Fusha (formal texts)',
             'Religion': 'Religious texts', 'Consume': 'Following content'}

# ------------------------------------------------------------------ sample
def counts(code, options=None, col=None):
    it = ITEM[code]
    o = it['o'] if not isinstance(it['o'], str) else ITEM[it['o'].split(':')[1]]['o']
    opts = options or o['en']
    col = col or code
    if it['type'] == 'check':
        ns = [int(d['%s_%d' % (col, i + 1)].sum()) for i in range(len(opts))]
    else:
        vc = d[col].value_counts()
        ns = [int(vc.get(i + 1, 0)) for i in range(len(opts))]
    return {'code': code, 'q': it['q']['en'], 'type': it['type'],
            'options': [{'label': o, 'n': n} for o, n in zip(opts, ns)]}


grew_other_arab = int(d.Country_GrewUp.isin([2, 3, 4, 5]).sum())
sample = {
    'n': int(len(d)), 'core_n': int(d.core.sum()), 'moved_since_2022': int((d.Moved_Since2022 == 1).sum()),
    'grew_up_lebanon': int((d.Country_GrewUp == 1).sum()), 'live_lebanon': int((d.Country_Now == 1).sum()),
    'lebanon_either': int(((d.Country_GrewUp == 1) | (d.Country_Now == 1)).sum()),
    'items': [counts(c) for c in ['Age', 'Gender', 'Education', 'Role', 'Field', 'Eng_Prof', 'Country_GrewUp',
                                  'Country_Now', 'AI_Start', 'AI_Freq', 'AI_TaskShare', 'AI_Lang', 'AI_Breadth',
                                  'AI_Content', 'AI_ContentLang', 'FushaPreAI', 'Events']],
}
assert sample['n'] == 105 and sample['core_n'] == 89

# ------------------------------------------------------------------ RQ1 domain profile
profile = []
rows8 = []
for dom in DOM:
    x = d['d_' + dom].dropna()
    n = int(len(x))
    c = {v: int((x == v).sum()) for v in [-2, -1, 0, 1, 2]}
    less, more = c[-2] + c[-1], c[1] + c[2]
    lo, hi = wilson(less, n)
    w = wilcoxon_signed(x)
    rows8.append(w['p'])
    profile.append({'id': dom, 'label': DOM_LABEL[dom], 'n': n, 'counts': [c[v] for v in [-2, -1, 0, 1, 2]],
                    'less': less / n, 'less_ci': [lo, hi], 'same': c[0] / n, 'more': more / n,
                    'mean': float(x.mean()), 'z': float(w['z']), 'p': float(w['p']), 'r': float(w['r'])})
for row, ph in zip(profile, multipletests(rows8, method='holm')[1]):
    row['p_holm8'] = float(ph)
    line = grab(r'^\s{4}%s\s+(\d+)\s+(\d+) \[' % row['id'], PS)
    assert int(line.group(1)) == row['n'] and int(line.group(2)) == round(100 * row['less']), row['id']
dl = d.DomainsLost.value_counts()
sub_k = int((d.SwitchEng_bin == 1).sum())
sub_lo, sub_hi = wilson(sub_k, len(d))
rq1 = {'domains': profile, 'domains_lost': [int(dl.get(i, 0)) for i in range(9)],
       'any_decrease': int((d.DomainsLost >= 1).sum()), 'domains_lost_mean': float(d.DomainsLost.mean()),
       'substitution': {'k': sub_k, 'n': int(len(d)), 'ci': [sub_lo, sub_hi]},
       'social_media': [int((d.SocialMedia == v).sum()) for v in [-2, -1, 0, 1, 2]]}
assert sub_k == 59 and rq1['any_decrease'] == 68

# ------------------------------------------------------------------ Family A (recomputed, checked against 03)
def family_a(df):
    out = {}
    raw = []
    for key, col in [('H1a', 'd_Fusha'), ('H1b', 'd_WorkStudy')]:
        w, sg = wilcoxon_signed(df[col]), sign_test(df[col])
        out[key] = {'n': int(w['n']), 'less': sg['less'], 'more': sg['more'], 'z': float(w['z']), 'r': float(w['r']),
                    'p': float(w['p']), 'sign_p': float(sg['p'])}
        raw.append(w['p'])
    cc = df[['Disp_Family', 'Disp_Personal', 'Disp_WorkStudy']].dropna()
    _, page_p, _ = page_exact(df, ['Disp_Family', 'Disp_Personal', 'Disp_WorkStudy'])
    fr = stats.friedmanchisquare(*[cc[c] for c in ['Disp_WorkStudy', 'Disp_Personal', 'Disp_Family']])
    out['H2a'] = {'n': int(len(cc)), 'means': {'WorkStudy': float(cc.Disp_WorkStudy.mean()),
                                              'Personal': float(cc.Disp_Personal.mean()),
                                              'Family': float(cc.Disp_Family.mean())},
                  'page_p': float(page_p), 'chi2': float(fr.statistic), 'friedman_p': float(fr.pvalue),
                  'W': float(fr.statistic / (len(cc) * 2))}
    raw.append(page_p)
    diff = df.Disp_Fusha - df.DialectLoss
    w = wilcoxon_signed(diff)
    out['H2b'] = {'n': int(w['n']), 'mean_diff': float(diff.mean()), 'z': float(w['z']), 'p': float(w['p'])}
    raw.append(w['p'])
    for k, ph in zip(['H1a', 'H1b', 'H2a', 'H2b'], multipletests(raw, method='holm')[1]):
        out[k]['p_holm'] = float(ph)
    return out


fa, fa_core = family_a(d), family_a(core)
h = grab(r'H1a Fusha\s+Wilcoxon z=(\S+) p=(\S+).*? n=(\d+) \| exact sign test (\d+) less vs (\d+) more', PS)
assert round(fa['H1a']['z'], 2) == float(h.group(1)) and fa['H1a']['less'] == int(h.group(4))
h = grab(r'Friedman chi2\(2\)=(\S+) p=\S+ Kendall W=(\S+) n=(\d+)', PS)
assert round(fa['H2a']['chi2'], 2) == float(h.group(1)) and round(fa['H2a']['W'], 2) == float(h.group(2))
assert round(fa['H2b']['z'], 2) == float(grab(r'H2b Fusha vs dialect .*? z=(\S+) p', PS).group(1))

# ------------------------------------------------------------------ Family B (recomputed) and its specifications
def fam_b(df, disp='Displacement', cov=('Age25', 'EventMove')):
    c = ''.join(' + ' + x for x in cov)
    h3 = smf.ols('%s ~ AI_Intensity + EnglishShare + QualityGap%s' % (disp, c), df).fit(cov_type='HC3', use_t=True)
    h4 = smf.ols('AbilityDecline ~ %s%s' % (disp, c), df).fit(cov_type='HC3', use_t=True)
    ps = [h3.pvalues['AI_Intensity'], h3.pvalues['EnglishShare'], h3.pvalues['QualityGap'], h4.pvalues[disp]]
    holm = multipletests(ps, method='holm')[1]

    def term(fit, t, i=None):
        lo, hi = fit.conf_int().loc[t]
        return {'b': float(fit.params[t]), 'ci': [float(lo), float(hi)], 'p': float(fit.pvalues[t]),
                **({'p_holm': float(holm[i])} if i is not None else {})}
    jt = h3.f_test('AI_Intensity = 0, EnglishShare = 0, QualityGap = 0')
    out = {'n': int(h3.nobs), 'joint': {'F': float(np.squeeze(jt.fvalue)), 'df': [int(jt.df_num), int(jt.df_denom)],
                                       'p': float(jt.pvalue)},
           'H3a': term(h3, 'AI_Intensity', 0), 'H3b': term(h3, 'EnglishShare', 1), 'H3c': term(h3, 'QualityGap', 2),
           'H4': term(h4, disp, 3)}
    out['covariates'] = {t: term(h3, t) for t in cov}
    return out


d['SocialLoss'] = -d.SocialMedia
SPECS = [('Primary specification', d, {}), ("Plan's 4-domain score", d, {'disp': 'Displacement4'}),
         ('Dialect domains only', d, {'disp': 'DialectLoss'}), ('Age as the only covariate', d, {'cov': ('Age25',)}),
         ('No covariates', d, {'cov': ()}), ('Adding English proficiency', d, {'cov': ('Age25', 'EventMove', 'Eng_Prof')}),
         ('Adding social-media attribution', d, {'cov': ('Age25', 'EventMove', 'SocialLoss')}),
         ('Without straight-line responders', d[d.straightline == 0], {}),
         ('Without the most influential case', d[d.id != 21], {}), ('Core sample', core, {})]
fb = fam_b(d)
specs = [dict(label=lab, **fam_b(df, **kw)) for lab, df, kw in SPECS]
assert abs(fb['H3b']['b'] - 0.169198) < 1e-5 and abs(fb['H4']['p'] - 0.053237) < 1e-5
wild = grab(r'wild bootstrap .*?English share p=\S+ -> Holm (\S+).*?H4 p=\S+ -> Holm (\S+)', PS)
firth = grab(r'^\s{4}EnglishShare\s+b=\S+\s+OR=\S+\s+penalised-LR p=(\S+)', PS)
h5 = []
for m in re.finditer(r'a  \(X->M\)\s+= (\S+)\s+HC3 p=(\S+)\n\s+b  \(M->Y \| X\) = (\S+)\s+HC3 p=(\S+)\n\s+c\' \(direct\)\s+= (\S+)'
                     r'\s+HC3 p=(\S+)\s+c \(total\) = (\S+)\n\s+indirect a\*b\s+= (\S+)\s+95% percentile CI \[(\S+), (\S+)\]', PS):
    h5.append({'a': float(m.group(1)), 'a_p': pv(m.group(2)), 'b': float(m.group(3)), 'b_p': pv(m.group(4)),
               'c_direct': float(m.group(5)), 'c_total': float(m.group(7)), 'indirect': float(m.group(8)),
               'ci': [float(m.group(9)), float(m.group(10))]})
assert len(h5) == 2
infl = grab(r'H4 influence \(all respondents\): largest Cook\'s distances .*?: id 21: (\S+),', PS)
loo = grab(r'leave-one-out over all 104: p from \S+ to (\S+); single removals giving p > \.0125 [^:]*: (\d+)', PS)
rel = {}
for m in re.finditer(r'^\s{4}(\w+) \(([^)]+)\)\s+\(all respondents\)\s+n=(\d+)\s+omega=(\S+) \[(\S+), (\S+)\]\s+alpha=(\S+)', PS, re.M):
    rel[m.group(1)] = {'items': m.group(2), 'n': int(m.group(3)), 'omega': float(m.group(4)),
                       'omega_ci': [float(m.group(5)), float(m.group(6))], 'alpha': float(m.group(7))}
assert {'Displacement', 'AbilityDecline', 'QualityGap'} <= set(rel)
eng_rho = stats.spearmanr(d.EnglishShare, d.Eng_Prof, nan_policy='omit')
age = d[d.Age25 == 1]
hyp = {
    'family_a': fa, 'family_a_core': fa_core, 'family_b': fb, 'specs': specs,
    'wild_holm': {'H3b': pv(wild.group(1)), 'H4': pv(wild.group(2))}, 'firth_english_p': pv(firth.group(1)),
    'h4_spearman': float(grab(r'Spearman Displacement-AbilityDecline rho=(\S+)', PS).group(1)),
    'h4_influence': {'cooks_d': float(infl.group(1)), 'loo_max_p': pv(loo.group(1)),
                     'loo_above_holm': int(loo.group(2))},
    'h5': {'primary': h5[0], 'core': h5[1]}, 'reliability': rel,
    'english_share_vs_proficiency_rho': float(eng_rho.statistic),
    'age25': {'n': int(len(age)), 'no_change': int((age.DomainsLost == 0).sum()),
              'disp_mean': float(age.Displacement.mean()), 'disp_mean_under25': float(d[d.Age25 == 0].Displacement.mean())},
    'power_min_r': float(grab(r'smallest correlation detectable .*? is r = (\S+)', PS).group(1)),
}

# ------------------------------------------------------------------ social media and life transitions
sm = grab(r'Displacement\s+AI (\S+) vs social media (\S+) \| Spearman rho=(\S+) p=\S+ \| paired Wilcoxon z=\S+ p=(\S+)', PS)
smf_ = grab(r'FormalLoss\s+AI (\S+) vs social media (\S+) \| Spearman rho=\S+ p=\S+ \| paired Wilcoxon z=\S+ p=(\S+)', PS)
split = grab(r'blame social media n=(\d+) mean (\S+) \| who do not n=(\d+) mean (\S+) \(vs 0: z=\S+ p=(\S+)\) \| Mann-Whitney Z=\S+ p=(\S+)', PS)
uni = d[d.d_WorkStudy.notna()]
a_, b_ = uni[uni.Events_1 == 1].d_WorkStudy, uni[uni.Events_1 != 1].d_WorkStudy
st = grab(r'same setting \(strict, stable\)\s+n=(\d+) mean (\S+) \| Wilcoxon z=\S+ p=(\S+) \(exact\) \| sign (\d+) less vs (\d+) more p=(\S+)', PS)
ch = grab(r'setting changed \(strict\)\s+n=(\d+) mean (\S+)', PS)
mw = grab(r'stable vs changed, Mann-Whitney: all Z=\S+ p=(\S+) \| under 25 only .*? Z=\S+ p=(\S+)', PS)
adj = grab(r'^\s{4}stable\s+b=(\S+)\s+HC3 SE=\S+\s+t\(\d+\)=\S+\s+p=(\S+)', PS)
pst = grab(r'Page \(strictly stable only\)\s+n=(\d+)\s+L=\S+\s+one-sided exact p=(\S+)', PS)
u25 = d[d.Age25 == 0]
context = {
    'ai_vs_social': {'ai': float(sm.group(1)), 'social': float(sm.group(2)), 'rho': float(sm.group(3)), 'p': pv(sm.group(4)),
                     'formal_ai': float(smf_.group(1)), 'formal_social': float(smf_.group(2)), 'formal_p': pv(smf_.group(3))},
    'blamers': {'n': int(split.group(1)), 'mean': float(split.group(2))},
    'non_blamers': {'n': int(split.group(3)), 'mean': float(split.group(4)), 'p_vs_0': pv(split.group(5))},
    'blamers_mw_p': pv(split.group(6)),
    'under25_transition': int((u25[['Events_1', 'Events_2', 'Events_3', 'Events_4']].fillna(0).sum(axis=1) > 0).sum()),
    'under25_n': int(len(u25)),
    'events': [{'label': o, 'n': int(d['Events_%d' % (i + 1)].sum())} for i, o in enumerate(ITEM['Events']['o']['en'])],
    'started_university': {'n': int(len(a_)), 'mean': float(a_.mean()), 'rest_n': int(len(b_)), 'rest_mean': float(b_.mean()),
                           'p': float(mann_whitney(a_, b_)[1])},
    'stable': {'n': int(st.group(1)), 'mean': float(st.group(2)), 'wilcoxon_p': pv(st.group(3)), 'less': int(st.group(4)),
               'more': int(st.group(5)), 'sign_p': pv(st.group(6)), 'changed_n': int(ch.group(1)), 'changed_mean': float(ch.group(2)),
               'mw_p': pv(mw.group(1)), 'mw_p_under25': pv(mw.group(2)), 'age_adjusted_b': float(adj.group(1)),
               'age_adjusted_p': pv(adj.group(2)), 'page_n': int(pst.group(1)), 'page_p': pv(pst.group(2))},
}

# ------------------------------------------------------------------ machine learning
ML_LABEL = {'DomainsLost': 'Domains with a decrease (count)', 'AnyFormalLoss': 'Any formal-domain decrease',
            'Loss_WorkStudy': 'Work or study', 'Loss_Writing': 'Messages and posts', 'Loss_Self': 'Self-talk and own notes',
            'Loss_Personal': 'Personal matters', 'Loss_Family': 'Family and friends', 'Loss_Fusha': 'Fusha (formal texts)',
            'Loss_Religion': 'Religious texts', 'Loss_Consume': 'Following content',
            'Substitution': 'Substitution (English instead of Arabic)', 'ExpectedLoss': 'Expected decrease in two years (count)',
            'AnyDifficulty': 'Any difficulty without AI'}
TXT_LABEL = {'DomainsLost': 'domains lost (count)', 'AnyFormalLoss': 'any formal-domain loss',
             **{'Loss_' + x: 'loss: ' + x for x in DOM},
             'Substitution': 'substitution (English instead of Arabic because of AI)',
             'ExpectedLoss': 'expected loss in two years (count of domains)',
             'AnyDifficulty': 'harder to use Arabic without AI (any)'}
tab = pd.concat([pd.read_csv(os.path.join(RES, 'ml_table.csv')).assign(src='05'),
                 pd.read_csv(os.path.join(RES, 'ml_more_targets.csv')).assign(src='06')], ignore_index=True)
BLOCK = {'M0 background': 'background', 'M1 + AI use': 'with_ai', 'M2 + quality gap': 'with_gap',
         'M0 without age': 'background_no_age', 'M1 without age': 'with_ai_no_age', 'AI use only': 'ai_only'}


def section(text, start, end):
    i = text.index(start)
    return text[i:text.index(end, i)]


DELTA_05 = section(MLR, 'DOES AI-USE INFORMATION IMPROVE PREDICTION?', 'Smallest gain the RQ4 test')
DELTA_06 = section(MLM, 'BLOCK COMPARISONS', 'FLEXIBLE VS LINEAR')


def delta(tgt, which='M1 - M0 (AI use)'):
    txt = DELTA_05 if tgt in tab[tab.src == '05'].target.values else DELTA_06
    block = txt.split('    %s\n' % TXT_LABEL[tgt])[1]
    m = grab(r'linear\s+%s\s+([+-][\d.]+) \[([+-][\d.]+), ([+-][\d.]+)\]\s+p ([\d.]+)(?:\s+p_Holm ([\d.]+))?' % re.escape(which), block)
    return {'d': float(m.group(1)), 'ci': [float(m.group(2)), float(m.group(3))], 'p': float(m.group(4)),
            **({'p_holm': float(m.group(5))} if m.group(5) else {})}


def usability(text, tgt):
    block = text.split('    %s\n' % TXT_LABEL[tgt])[1].split('->')
    crit = [{'no': int(m.group(1)), 'name': m.group(2).strip(), 'result': m.group(3), 'detail': m.group(4).strip()}
            for m in re.finditer(r'^\s{8}(\d) (.+?)\s{2,}(PASS|fail|n/a)\s+(.*)$', block[0], re.M)]
    assert len(crit) == 4, tgt
    return {'criteria': crit, 'usable': block[1].split('\n')[0].strip().startswith('USABLE')}


USE_06 = section(MLM, 'IS THERE A USABLE PREDICTIVE MODEL?', 'runtime')
targets = []
for tgt in ML_LABEL:
    rows = tab[(tab.target == tgt) & (tab.model == 'linear')]
    kind = 'reg' if tgt in ('DomainsLost', 'ExpectedLoss') else 'clf'
    r0 = rows.iloc[0]
    item = {'id': tgt, 'label': ML_LABEL[tgt], 'kind': kind, 'metric': 'Q2' if kind == 'reg' else 'AUC',
            'n': int(r0.n), 'set': 'main' if r0.src == '05' else 'further', 'blocks': {}}
    if kind == 'clf':
        item['n_yes'] = int(round(r0.prevalence * r0.n))
    for _, r in rows.iterrows():
        if r.features in BLOCK:
            item['blocks'][BLOCK[r.features]] = {
                'score': float(r.score), **({'bal_acc': float(r.bal_acc)} if kind == 'clf' else {}),
                **({'perm_p_holm': float(r.perm_p_holm)} if not pd.isna(r.perm_p_holm) else {})}
    for name in ('forest', 'boosting'):
        fr = tab[(tab.target == tgt) & (tab.model == name) & (tab.features == 'M1 + AI use')]
        if len(fr):
            item['blocks']['with_ai_' + name] = {'score': float(fr.iloc[0].score)}
    item['delta_ai'] = delta(tgt)
    item['usability'] = usability(USE if r0.src == '05' else USE_06, tgt)
    targets.append(item)
mdg = grab(r'any formal-domain loss\s+AUC ([\d.]+)', section(MLR, 'Smallest gain', 'FLEXIBLE')).group(1)
mdg_q = grab(r'domains lost \(count\)\s+Q2 ([\d.]+)', section(MLR, 'Smallest gain', 'FLEXIBLE')).group(1)
holm13 = {m.group(1): float(m.group(2)) for m in re.finditer(r'(\w+) ([\d.]+)', grab(r'Holm across all 13 targets modelled[^\n]*\n\s+(.*)', MLM).group(1))}
imp = {}
for tgt in ('AnyFormalLoss', 'Loss_WorkStudy'):
    blk = MLR.split('    %s, M0 background, linear: grouped permutation importance' % tgt)[1].split('standardised')[0]
    imp[tgt] = [{'feature': m.group(1).strip(), 'drop': float(m.group(2))}
                for m in re.finditer(r'^\s{8}(\S.*?)\s{2,}([+-][\d.]+)$', blk, re.M)]
leak = grab(r'linear\s+inside the folds \(correct\) AUC ([\d.]+)\s+\|\s+before the split \(leaks\) AUC ([\d.]+) on n=(\d+)', MLR)
ml = {'targets': targets, 'min_detectable_gain': {'auc': float(mdg), 'q2': float(mdg_q)}, 'holm_13': holm13,
      'importance': imp, 'leakage_demo': {'inside': float(leak.group(1)), 'leaky': float(leak.group(2)), 'n_after': int(leak.group(3))}}
assert sum(t['usability']['usable'] for t in targets) == 3

# ------------------------------------------------------------------ oversampling check
STRATS = ['none', 'class weights', 'random duplication', 'SMOTENC to balance', 'SMOTENC amplified x5', 'SMOTENC + Tomek',
          'noise augmentation x5']
OVER_LABEL = {'ANY FORMAL-DOMAIN LOSS': 'Any formal-domain decrease', 'LOSS: WRITING': 'Messages and posts',
              'SUBSTITUTION': 'Substitution (English instead of Arabic)', 'HARDER WITHOUT AI': 'Any difficulty without AI'}
over = []
for m in re.finditer(r'^([A-Z][A-Z :-]+?)\s+\(n=(\d+): (\d+) yes / (\d+) no\)\n(.*?)(?=\n\n)', OVR, re.M | re.S):
    rows = []
    for s in STRATS:
        r = grab(r'^\s{4}%s\s+([\d.]+)\s+([\d.]+)\s+(?:([+-][\d.]+) \[([+-][\d.]+), ([+-][\d.]+)\] p ([\d.]+)|-)[ \t]*'
                 r'(?:([\d.]+) \(n=(\d+)\))?' % re.escape(s), m.group(5))
        rows.append({'strategy': s, 'auc': float(r.group(1)), 'bal_acc': float(r.group(2)),
                     **({'gain': float(r.group(3)), 'gain_ci': [float(r.group(4)), float(r.group(5))], 'p': float(r.group(6))}
                        if r.group(3) else {}),
                     **({'leaky_auc': float(r.group(7)), 'leaky_n': int(r.group(8))} if r.group(7) else {})})
    over.append({'target': OVER_LABEL[m.group(1).strip()], 'n': int(m.group(2)), 'yes': int(m.group(3)), 'rows': rows})
assert len(over) == 4
assert sum('leaky_auc' in r for o in over for r in o['rows']) == 16, 'every resampling strategy has a leaky AUC'
assert sum('gain' in r for o in over for r in o['rows']) == 24, 'every strategy has a comparison with none'

# ------------------------------------------------------------------ references (the paper's bibliography)
def read_bib(path):
    """A small BibTeX reader for refs.bib: entries of the form field = {value} with balanced braces."""
    text = io.open(path, encoding='utf-8').read()
    out = {}
    for m in re.finditer(r'@(\w+)\{([^,\s]+),', text):
        kind, key = m.group(1).lower(), m.group(2)
        if kind == 'ieeetranbstctl':
            continue
        i, depth, fields = m.end(), 1, {}
        while depth and i < len(text):
            f = re.match(r'\s*(\w+)\s*=\s*\{', text[i:])
            if not f:
                if text[i] == '}':
                    depth -= 1
                i += 1
                continue
            name, j, d = f.group(1).lower(), i + f.end(), 1
            k = j
            while d:
                d += {'{': 1, '}': -1}.get(text[k], 0)
                k += 1
            fields[name] = text[j:k - 1]
            i = k
        out[key] = (kind, fields)
    return out


ACCENT = {"'": '\u0301', '`': '\u0300', '^': '\u0302', '"': '\u0308', '~': '\u0303', '=': '\u0304', '.': '\u0307',
          'c': '\u0327', 'u': '\u0306', 'v': '\u030c', 'H': '\u030b'}


def bib_plain(v):
    """LaTeX accents ({\\'i}, {\\c{c}}, {\\u{g}}, ...) -> letters; braces and dashes -> plain text."""
    import unicodedata
    v = re.sub(r'\\([\'`^"~=.cuvH])\{?\\?([A-Za-z])\}?', lambda m: unicodedata.normalize('NFC', m.group(2) + ACCENT[m.group(1)]), v)
    return re.sub(r'\s+', ' ', v.replace('{', '').replace('}', '').replace('--', '–').replace('\\&', '&')).strip()


def bib_authors(v):
    names = []
    for a in bib_plain(v).split(' and '):
        if ',' in a:
            last, first = [x.strip() for x in a.split(',', 1)]
            names.append((last, ' '.join(w[0] + '.' for w in first.replace('-', ' ').split() if w)))
        else:
            names.append((a, ''))
    short = names[0][0] + (' et al.' if len(names) > 2 else (' and ' + names[1][0] if len(names) == 2 else ''))
    full = ', '.join((f + ' ' + l).strip() for l, f in names[:6]) + (' et al.' if len(names) > 6 else '')
    return short, full


import io  # noqa: E402
REFS = {}
for key, (kind, f) in read_bib(os.path.join(ROOT, 'paper', 'refs.bib')).items():
    short, full = bib_authors(f.get('author', f.get('organization', '')) or 'IBM Corp.')
    venue = f.get('journal') or f.get('booktitle') or f.get('publisher') or f.get('organization') or ''
    REFS[key] = {'short': short, 'authors': full, 'year': f.get('year', ''), 'title': bib_plain(f.get('title', '')),
                 'venue': bib_plain(venue), 'url': ('https://doi.org/' + f['doi']) if f.get('doi') else f.get('url', '')}
assert len(REFS) >= 35 and REFS['kubrak2025']['short'] == 'Kubrak et al.', REFS.get('kubrak2025')
assert '\\' not in json.dumps(REFS, ensure_ascii=False), 'a LaTeX command survived in the references'

# ------------------------------------------------------------------ SPSS against Python (crosscheck_spss.py)
SPSS_LABEL = {
    'alpha, Displacement (primary)': ('Reliability', 'Cronbach’s α, decrease score (8 areas)'),
    'alpha, Ability decline (primary)': ('Reliability', 'Cronbach’s α, difficulty without AI'),
    'alpha, Quality gap (primary)': ('Reliability', 'Cronbach’s α, perceived quality gap (4 items)'),
    'alpha, Quality gap, 3 items (primary)': ('Reliability', 'Cronbach’s α, perceived quality gap (3 items)'),
    'Wilcoxon Z, H1a Fusha (primary)': ('Direction and order', 'Wilcoxon z, H1a Fusha'),
    'Wilcoxon p, H1a Fusha (primary)': ('Direction and order', 'Wilcoxon p, H1a Fusha'),
    'Wilcoxon Z, H1b work/study (primary)': ('Direction and order', 'Wilcoxon z, H1b work or study'),
    'Wilcoxon p, H1b work/study (primary)': ('Direction and order', 'Wilcoxon p, H1b work or study'),
    'Wilcoxon Z, H2a work/study vs family (primary, complete cases)': ('Direction and order', 'Wilcoxon z, H2a work or study vs family'),
    'Wilcoxon p, H2a work/study vs family (primary, complete cases)': ('Direction and order', 'Wilcoxon p, H2a work or study vs family'),
    'Wilcoxon Z, H2b Fusha vs dialect (primary)': ('Direction and order', 'Wilcoxon z, H2b Fusha vs dialect'),
    'Wilcoxon p, H2b Fusha vs dialect (primary)': ('Direction and order', 'Wilcoxon p, H2b Fusha vs dialect'),
    'sign test p, H1a Fusha (primary)': ('Direction and order', 'Sign test p, H1a Fusha'),
    'sign test p, H1b work/study (primary)': ('Direction and order', 'Sign test p, H1b work or study'),
    'Friedman chi-square, H2a (primary)': ('Direction and order', 'Friedman χ², H2a order'),
    'Mann-Whitney p, stable vs changed (primary)': ('Group comparisons', 'Mann–Whitney p, unchanged vs changed setting'),
    'Mann-Whitney p, stable vs changed (primary, under 25)': ('Group comparisons', 'Mann–Whitney p, same, under 25 only'),
    'B EnglishShare in "Displacement ~ ... EventMove"': ('Regression', 'English share → decrease (H3)'),
    'B AI_Intensity in "Displacement ~ ... EventMove"': ('Regression', 'AI-use intensity → decrease (H3)'),
    'B Displacement in "AbilityDecline ~ ... EventMove"': ('Regression', 'Decrease → difficulty (H4)'),
    'B EnglishShare in "Displacement ~ ... SocialLoss"': ('Regression', 'English share, social media controlled'),
    'B stable in "d_WorkStudy ~ ... Age25"': ('Regression', 'Unchanged setting → work/study change, age controlled'),
    'B EnglishShare in "Displacement ~ ... QualityGap"': ('Regression', 'English share, no covariates'),
    'B Displacement in "AbilityDecline ~ ...AbilityDecline ~ Displa': ('Regression', 'Decrease → difficulty, no covariates'),
    'B EnglishShare in "Displacement4 ~ ... EventMove"': ('Regression', 'English share, the plan’s 4-area score'),
    'B Displacement4 in "AbilityDecline ~ ... EventMove"': ('Regression', 'Decrease → difficulty, the plan’s 4-area score'),
    'B EnglishShare in "Displacement ~ ... EventMove" (core sample)': ('Regression', 'English share, core sample'),
    'B Displacement in "AbilityDecline ~ ... EventMove" (core sampl': ('Regression', 'Decrease → difficulty, core sample'),
    'B EnglishShare, H3 without straight-liners': ('Regression', 'English share, without straight-line responders'),
    'B Displacement, H4 without straight-liners': ('Regression', 'Decrease → difficulty, without straight-line responders'),
    'mean d_WorkStudy (primary)': ('Means', 'Mean change, work or study'),
    'mean d_Fusha (primary)': ('Means', 'Mean change, Fusha'),
    'mean d_Religion (primary)': ('Means', 'Mean change, religious texts'),
    'mean d_Family (primary)': ('Means', 'Mean change, family and friends'),
}
with open(os.path.join(RES, 'spss_crosscheck.json'), encoding='utf-8') as _f:
    _cc = json.load(_f)
assert _cc['n'] == len(d) and _cc['agree'] == _cc['total'], 'SPSS and Python disagree, or the cross-check is stale'
assert {c['statistic'] for c in _cc['checks']} <= set(SPSS_LABEL), 'a cross-checked statistic has no label'
SPSS = {'n': _cc['n'], 'agree': _cc['agree'], 'total': _cc['total'],
        'checks': [{'group': SPSS_LABEL[c['statistic']][0], 'label': SPSS_LABEL[c['statistic']][1],
                    'spss': c['spss'], 'python': c['python']} for c in _cc['checks']]}

# ------------------------------------------------------------------ the questionnaire, as fielded (questions and options only)
from instrument_data import S as SCALES, T as TEXTS  # noqa: E402


def clean(t):
    return re.sub(r'\s*\((reverse-coded|R)\)', '', t)


def questionnaire():
    out = []
    for sec in SECTIONS:
        if sec['id'] == 'consent':                 # the information page, not a question
            continue
        items = []
        for it in sec['items']:
            help_ = it.get('help')
            note = TEXTS[help_] if isinstance(help_, str) else help_
            if it['type'] == 'text':
                items.append({'type': 'text', 'text': note})
                continue
            q = {'type': it['type'], 'q': it['q'], 'note': note}
            if it['type'] == 'gate':
                q['options'] = [{'en': it['yes']['en'], 'ar': it['yes']['ar']}, {'en': it['no']['en'], 'ar': it['no']['ar']}]
            elif it['type'] == 'grid':
                q['rows'] = [{'en': clean(r[1]), 'ar': r[2]} for r in it['rows']]
                sc = SCALES[it['scale']]
                q['options'] = [{'en': e, 'ar': a} for e, a in zip(sc['en'], sc['ar'])]
            elif it['type'] in ('mc', 'check'):
                o = it.get('o')
                if o is None:
                    o = SCALES[it['scale']]
                elif isinstance(o, str):
                    o = ITEM[o.split(':')[1]]['o']
                q['options'] = [{'en': e, 'ar': a} for e, a in zip(o['en'], o['ar'])]
            items.append(q)
        out.append({'title': sec['title'], 'items': items})
    return out


QUESTIONNAIRE = questionnaire()
assert 'research project' not in json.dumps(QUESTIONNAIRE).lower()    # the information page stays out
assert '"role"' not in json.dumps(QUESTIONNAIRE)                        # no internal design tags
assert 'reverse-coded' not in json.dumps(QUESTIONNAIRE)

# ------------------------------------------------------------------ instrument (the core grid, as fielded)
grid = next(it for sec in SECTIONS if sec['id'] == 'change' for it in sec['items'] if it.get('type') == 'grid')
out = {
    'study': {'title': 'Is Generative AI Displacing Arabic? Perceived Change in Arabic Use Among Lebanese Arabic-English Bilinguals',
              'author': 'Hadi Ghazi', 'affiliation': 'Lebanese University', 'collected': '30 September to 4 October 2026'},
    'sample': sample, 'rq1': rq1, 'hypotheses': hyp, 'context': context, 'ml': ml, 'oversampling': over,
    'questionnaire': QUESTIONNAIRE,
    'references': REFS,
    'spss': SPSS,
    'instrument': {'question': grid['q'],
                   'rows': [{'code': r[0].replace('ArUse_', ''), 'en': r[1], 'ar': r[2]} for r in grid['rows'] if r[0].startswith('ArUse_')],
                   'social_media_q': ITEM['SocialMedia']['q'], 'substitution_q': ITEM['SwitchEng']['q']},
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1, allow_nan=False)
print('wrote %s (%.1f KB)' % (OUT, os.path.getsize(OUT) / 1024))
