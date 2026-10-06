# -*- coding: utf-8 -*-
"""
Raw Google Forms export -> numeric CSV + SPSS syntax.

Run:   python analysis/prepare_data.py
Reads:  analysis/data/responses-raw-2026-10-04.xlsx  (frozen copy of the final export, 105 responses;
        earlier exports of 40 and 65 responses are identical to its first rows)
Writes: analysis/data/coded.csv            numeric codes only, one row per respondent
        analysis/data/open_answers.md      the optional free-text answers, kept locally, not analysed (consent: group results only)
        analysis/data/scored.csv           coded.csv + every computed score (for the Python/ML side)
        analysis/spss/01_import_and_score.sps   imports coded.csv, labels it, computes scores, saves .sav

Columns are matched to the instrument (instrument_data.py) by position AND checked against the
Arabic question text, so a reordered form fails loudly instead of mislabelling silently.
Scores are computed twice -- in the SPSS syntax and here -- and the means printed at the end
are what SPSS should reproduce. That is the check that the two agree.
"""
import io, os, re, sys
import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
from instrument_data import S, SECTIONS          # noqa: E402
from instrument_v3 import opts, resolve          # noqa: E402

RAW = os.path.join(HERE, 'data', 'responses-raw-2026-10-04.xlsx')
OUT_CSV = os.path.join(HERE, 'data', 'coded.csv')
OUT_SCORED = os.path.join(HERE, 'data', 'scored.csv')
OUT_OPEN = os.path.join(HERE, 'data', 'open_answers.md')
OUT_SPS = os.path.join(HERE, 'spss', '01_import_and_score.sps')

GRID_LABEL = {'CurUse': 'Language today', 'ArUse': 'Because of AI, less or more', 'Abil': 'Without AI, harder or easier',
              'Future': 'In two years, Arabic more or less', 'Gap': 'Agree'}
# change-grid row -> the current-use row that says whether the domain applies to this person at all
APPLIES = {'WorkStudy': 'WorkStudy', 'Writing': 'Writing', 'Self': 'Self', 'Personal': 'Personal',
           'Family': 'Family', 'Fusha': 'Formal', 'Religion': 'Religion', 'Consume': 'Consume'}
DOMAINS = list(APPLIES)


def norm(t):
    return re.sub(r'[\s•]+', '', str(t))


def codes_for(it):
    """Numeric code for each option, in option order."""
    if it.get('scale') in S:
        return [int(str(c).lstrip('M')) for c in S[it['scale']]['codes']]
    if it['type'] == 'gate':
        return [1, 0]
    return list(range(1, len(opts(it, 'ar')) + 1))


def build_columns():
    """One entry per export column, in export order (Timestamp first)."""
    cols = []
    for sec in SECTIONS:
        for it in sec['items']:
            t = it['type']
            if t == 'text':
                continue
            q_ar, q_en = resolve(it.get('q'), 'ar'), resolve(it.get('q'), 'en')
            if t == 'grid':
                for r in it['rows']:
                    cols.append(dict(kind='grid', item=it, name=r[0], q_ar=q_ar, row_ar=r[2],
                                     label='%s: %s' % (GRID_LABEL[it['code']], r[1])))
            elif t == 'para':
                cols.append(dict(kind='para', item=it, name=it['code'], q_ar=q_ar, label=q_en))
            elif t == 'check':
                cols.append(dict(kind='check', item=it, name=it['code'], q_ar=q_ar, label=q_en))
            else:
                cols.append(dict(kind='single', item=it, name=it['code'], q_ar=q_ar, label=q_en))
    return cols


def main():
    raw = pd.read_excel(RAW)
    spec = build_columns()
    assert raw.shape[1] == len(spec) + 1, 'export has %d columns, instrument expects %d' % (raw.shape[1], len(spec) + 1)

    out = pd.DataFrame({'id': range(1, len(raw) + 1)})
    meta = []          # (name, label, value_labels or None, missing_values or None)
    problems = []

    for k, c in enumerate(spec, start=1):
        head = raw.columns[k]
        h = norm(head)
        if not h.startswith(norm(c['q_ar'])[:25]):
            problems.append('column %d header does not match %s' % (k, c['name']))
        if c['kind'] == 'grid' and not h.endswith(norm(c['row_ar']) + ']'):
            problems.append('column %d row does not match %s' % (k, c['name']))
        col = raw[head]
        it = c['item']

        if c['kind'] == 'para':
            continue                                     # free text is kept out of the SPSS file

        o_ar, o_en, cd = opts(it, 'ar'), opts(it, 'en'), codes_for(it)
        if it['type'] == 'gate':
            o_ar, o_en = [it['yes']['ar'], it['no']['ar']], [it['yes']['en'], it['no']['en']]

        if c['kind'] == 'check':
            for j, (oa, oe) in enumerate(zip(o_ar, o_en), start=1):
                out['%s_%d' % (c['name'], j)] = col.fillna('').apply(lambda v: int(oa in [x.strip() for x in str(v).split(',')]))
                meta.append(('%s_%d' % (c['name'], j), '%s: %s' % (c['label'], oe), {0: 'Not ticked', 1: 'Ticked'}, None))
            unknown = {x.strip() for v in col.dropna() for x in str(v).split(',')} - set(o_ar)
            if unknown:
                problems.append('%s has unrecognised ticks: %s' % (c['name'], unknown))
            continue

        m = dict(zip(o_ar, cd))
        # compare as text: Excel stores answers like "2024" as numbers
        mapped = col.map(lambda v: m.get(str(v).strip()) if pd.notna(v) else np.nan)
        bad = col[mapped.isna() & col.notna()].unique()
        if len(bad):
            problems.append('%s has unrecognised answers: %s' % (c['name'], list(bad)))
        out[c['name']] = mapped
        missing = None
        if it.get('scale') == 'curuse':
            missing = [4, 5]                             # another language / not applicable: off the Arabic-English continuum
        elif c['name'] == 'AI_Lang':
            missing = [6]                                # another language
        labels = dict(zip(cd, o_en))
        lab = c['label']
        if c['name'] == 'Role':
            labels[4] = 'Other'          # respondents saw "غير ذلك" (other), not "neither"
        if c['name'] == 'Gap_Equal':
            lab = 'Agree: AI answers in Arabic are as good as in English (stored as answered; Gap_Equal_r is reversed)'
        meta.append((c['name'], lab, labels, missing))

    if problems:
        print('STOPPING -- the export does not match the instrument:')
        print('\n'.join('  - ' + p for p in problems))
        sys.exit(1)

    out.to_csv(OUT_CSV, index=False)

    # ---- open answers: kept locally, not analysed or quoted (the consent page promised group results only)
    para = [c for c in spec if c['kind'] == 'para'][0]
    pcol = raw[raw.columns[spec.index(para) + 1]]
    with io.open(OUT_OPEN, 'w', encoding='utf-8') as f:
        f.write('# Open answers (optional question)\n\n')
        for i, v in zip(out['id'], pcol):
            if isinstance(v, str) and v.strip():
                f.write('**%d.** %s\n\n' % (i, v.strip()))

    scored = score(out.copy())
    scored.to_csv(OUT_SCORED, index=False)
    write_sps(meta, [n for n, *_ in meta])

    print('respondents: %d | coded variables: %d | open answers: %d'
          % (len(out), out.shape[1] - 1, int(pcol.fillna('').str.strip().ne('').sum())))
    print('wrote %s\n      %s\n      %s\n      %s' % (OUT_CSV, OUT_SCORED, OUT_OPEN, OUT_SPS))
    print('\nSPSS check -- after running the syntax, DESCRIPTIVES should show these means:')
    for v in ['Displacement', 'Displacement4', 'NetLoss', 'DialectLoss', 'DomainsLost', 'FormalLoss', 'AnyFormalLoss',
              'AbilityDecline', 'AbilityDecline4', 'QualityGap', 'QualityGap3', 'Expected', 'AI_BreadthCount',
              'AI_Intensity', 'AI_Intensity3', 'SwitchEng_bin']:
        print('  %-16s mean %+.3f  (n=%d)' % (v, scored[v].mean(), scored[v].notna().sum()))
    print('  flags: ' + '  '.join('%s=%d' % (f, scored[f].sum()) for f in
                                  ['excl_region', 'moved', 'core', 'stable', 'straightline', 'Age25', 'Computing', 'EventMove', 'Medium']))


def score(d):
    """Same definitions as the SPSS syntax. Keep the two in step.

    Each primary score is the best-justified option at its decision point; the alternative is kept
    as a sensitivity score (suffix 4 or 3) and reported. The comparison and the reasons are in
    analysis/ANALYSIS-DECISIONS.md. Loss and decline scores: HIGHER = MORE LOSS. The d_X items stay
    raw change (-2..+2, negative = less Arabic).
    """
    nv = lambda X: X.notna().sum(axis=1)
    for dom in DOMAINS:
        a, cu = d['ArUse_' + dom], d['CurUse_' + APPLIES[dom]]
        d['d_' + dom] = a.where(cu != 5)                 # domain does not apply -> missing, not "no change"
    D = d[['d_' + x for x in DOMAINS]]
    d['DomainsValid'] = nv(D)
    # displacement over every domain that applies (at least 6 of 8); the 27 Sep plan's 4-domain version is a sensitivity
    d['Displacement'] = -D.mean(axis=1).where(d['DomainsValid'] >= 6)
    P = d[['d_Writing', 'd_Self', 'd_Personal', 'd_Family']]
    d['Displacement4'] = -P.mean(axis=1).where(nv(P) >= 3)
    d['NetLoss'] = (d['Displacement'] > 0).astype(float).where(d['Displacement'].notna())
    for dom in ('Fusha', 'WorkStudy', 'Personal', 'Family'):
        d['Disp_' + dom] = -d['d_' + dom]
    d['DialectLoss'] = -d[['d_Self', 'd_Personal', 'd_Family']].mean(axis=1)  # H2b: mean of the dialect items
    d['DomainsLost'] = (D <= -1).sum(axis=1)
    F2 = d[['d_WorkStudy', 'd_Fusha']]                    # formal = the H1 domains; messages and posts are everyday writing
    d['FormalLoss'] = -F2.mean(axis=1)
    fmin = F2.min(axis=1)
    d['AnyFormalLoss'] = (fmin <= -1).astype(float).where(fmin.notna())
    d['Abil_Register_f'] = d['Abil_Register'].where(d['FushaPreAI'] != 3)   # never wrote Fusha before AI -> nothing to lose
    A3 = d[['Abil_Lexical', 'Abil_Fluency', 'Abil_ArabicOnly']]
    d['AbilityDecline'] = -A3.mean(axis=1).where(nv(A3) >= 2)                 # same 3 items for everyone
    A4 = d[['Abil_Lexical', 'Abil_Fluency', 'Abil_ArabicOnly', 'Abil_Register_f']]
    d['AbilityDecline4'] = -A4.mean(axis=1).where(nv(A4) >= 3)               # sensitivity: + Fusha register item
    d['Gap_Equal_r'] = 6 - d['Gap_Equal']
    G = d[['Gap_Understand', 'Gap_Accuracy', 'Gap_Voice', 'Gap_Equal_r']]
    d['QualityGap'] = G.mean(axis=1).where(nv(G) >= 3)                       # 30 Sep codebook: Gap_Voice is part of the gap grid
    d['QualityGap3'] = d[['Gap_Understand', 'Gap_Accuracy', 'Gap_Equal_r']].mean(axis=1)   # without the AI-voice item (sensitivity)
    Fu = d[[c for c in d.columns if c.startswith('Future_')]]
    d['Expected'] = Fu.mean(axis=1).where(nv(Fu) >= 6)                        # change; negative = less Arabic expected
    d['AI_BreadthCount'] = d[['AI_Breadth_%d' % i for i in range(1, 9)]].sum(axis=1)
    z = lambda s: (s - s.mean()) / s.std(ddof=1)
    d['AI_Intensity'] = pd.concat([z(d['AI_TaskShare']), z(d['AI_BreadthCount'])], axis=1).mean(axis=1)    # frequency left out: 79 of 105 (75%) at its ceiling
    d['AI_Intensity3'] = pd.concat([z(d['AI_Freq']), z(d['AI_TaskShare']), z(d['AI_BreadthCount'])], axis=1).mean(axis=1)  # sensitivity
    d['EnglishShare'] = d['AI_Lang'].where(d['AI_Lang'] != 6)                 # 6 = another language -> missing (plan 7.1)
    d['AI_TenureRank'] = 6 - d['AI_Start']               # 5 = started 2022 or earlier (longest use)
    d['SwitchEng_bin'] = (d['SwitchEng'] >= 3).astype(int)
    # covariates (plan 7.3)
    d['Age25'] = (d['Age'] >= 2).astype(int)
    d['Computing'] = (d['Field'] == 1).astype(int)
    d['EventMove'] = ((d['Events_4'] == 1) | (d['Events_5'] == 1)).astype(int)
    d['Medium'] = (d['Sch_SciLang'].isin([2, 3]) | d['Uni_Lang'].isin([2, 3, 4])).astype(int)
    # flags
    d['excl_region'] = ((d['Country_GrewUp'] == 6) | (d['Country_Now'] == 6)).astype(int)
    d['moved'] = ((d['Moved_Since2022'] == 1) | (d['Events_5'] == 1)).astype(int)
    d['core'] = ((d['excl_region'] == 0) & (d['moved'] == 0)).astype(int)      # the plan's core sample (sensitivity analysis)
    d['stable'] = ((d['Events_1'] == 0) & (d['Events_2'] == 0) & (d['Events_3'] == 0) & (d['Role'] != 4)).astype(int)
    G9 = d[['ArUse_' + x for x in DOMAINS] + ['Switch_Mode']]
    d['straightline'] = (G9.eq(-2).all(axis=1) | G9.eq(2).all(axis=1)).astype(int)   # plan 7.0.5
    return d


def q(s):
    # labels must sit on one line: a line break inside a quoted string breaks the SPSS command
    s = re.sub(r'\s*\n\s*(?:•\s*)?', '; ', str(s).strip())
    return '"%s"' % s.replace('"', '""')


def write_sps(meta, names):
    fmt = {n: 'F3.0' for n in names}
    L = []
    w = L.append
    w('* ' + '=' * 78 + '.')
    w('* 01_import_and_score.sps -- GENERATED by analysis/prepare_data.py. Edit the .py, not this file.')
    w('* Imports coded.csv, labels it, flags exclusions, computes every score, saves the .sav.')
    w('* Before running: set the folder in FILE HANDLE below. Run all (Ctrl+A, then Run).')
    w('* ' + '=' * 78 + '.')
    w('')
    w("FILE HANDLE proj /NAME='C:\\Users\\User\\ai-language-gap-paper\\analysis'.")
    w('')
    w('GET DATA /TYPE=TXT')
    w("  /FILE='proj/data/coded.csv'")
    w("  /ENCODING='UTF8' /DELCASE=LINE /DELIMITERS=\",\" /QUALIFIER='\"' /ARRANGEMENT=DELIMITED /FIRSTCASE=2")
    w('  /VARIABLES=')
    w('    id F3.0')
    for n in names:
        w('    %s %s' % (n, fmt[n]))
    w('.')
    w('')
    w('VARIABLE LABELS')
    w('  id "Respondent number (order of submission)"')
    for n, lab, _, _ in meta:
        w('  /%s %s' % (n, q(lab[:250])))
    w('.')
    w('')
    w('VALUE LABELS')
    first = True
    for n, _, vl, _ in meta:
        if not vl:
            continue
        w(('  ' if first else '  /') + n + ' ' + ' '.join('%d %s' % (k, q(v)) for k, v in vl.items()))
        first = False
    w('.')
    w('')
    for n, _, _, mv in meta:
        if mv:
            w('MISSING VALUES %s (%s).' % (n, ','.join(str(x) for x in mv)))
    w('')
    w('* ---------------------------------------------------------------- flags.')
    w('COMPUTE excl_region = (Country_GrewUp = 6 OR Country_Now = 6).')
    w('COMPUTE moved = (Moved_Since2022 = 1 OR Events_5 = 1).')
    w('* core: sensitivity sample - grew up and lives in the Arab region, no move since 2022.')
    w('* The primary analysis uses all respondents.')
    w('COMPUTE core = (excl_region = 0 AND moved = 0).')
    w('* stable: same workplace or university throughout the AI period (no new university, graduation or job; role not "other").')
    w('COMPUTE stable = (Events_1 = 0 AND Events_2 = 0 AND Events_3 = 0 AND Role <> 4).')
    g9 = ', '.join(['ArUse_' + x for x in DOMAINS] + ['Switch_Mode'])
    w('* straightline: every change row "much less" or every row "much more" (sensitivity only).')
    w('COMPUTE straightline = (MAX(%s) = -2 OR MIN(%s) = 2).' % (g9, g9))
    w('')
    w('* ---------------------------------------------------------------- domain change, filtered.')
    w('* A domain that does not apply (Language today = 5, not applicable) is set to missing.')
    w('* So "does not do this" is not counted as "AI changed nothing".')
    w('* VALUE() is needed: 5 is declared user-missing, and a plain comparison with it would never be true.')
    w('DO REPEAT a = %s' % ' '.join('ArUse_' + x for x in DOMAINS))
    w('         /c = %s' % ' '.join('CurUse_' + APPLIES[x] for x in DOMAINS))
    w('         /f = %s.' % ' '.join('d_' + x for x in DOMAINS))
    w('  COMPUTE f = a.')
    w('  IF (VALUE(c) = 5) f = $SYSMIS.')
    w('END REPEAT.')
    dl = ' '.join('d_' + x for x in DOMAINS)
    dc = ', '.join('d_' + x for x in DOMAINS)
    w('')
    w('* ---------------------------------------------------------------- scores.')
    w('* Loss and decline scores: HIGHER = MORE LOSS. d_X stay raw change (negative = less Arabic).')
    w('* Suffix 4 or 3 = sensitivity variant; the unsuffixed score is the primary one (see ANALYSIS-DECISIONS.md).')
    w('COMPUTE DomainsValid = NVALID(%s).' % dc)
    w('COMPUTE Displacement = -MEAN.6(%s).' % dc)
    w('COMPUTE Displacement4 = -MEAN.3(d_Writing, d_Self, d_Personal, d_Family).')
    w('COMPUTE NetLoss = (Displacement > 0).')
    for dom in ('Fusha', 'WorkStudy', 'Personal', 'Family'):
        w('COMPUTE Disp_%s = -d_%s.' % (dom, dom))
    w('COMPUTE DialectLoss = -MEAN(d_Self, d_Personal, d_Family).')
    w('COUNT DomainsLost = %s (LO THRU -1).' % dl)
    w('COMPUTE FormalLoss = -MEAN(d_WorkStudy, d_Fusha).')
    w('COMPUTE AnyFormalLoss = (MIN(d_WorkStudy, d_Fusha) <= -1).')
    w('* Fusha writing ability only counts for people who wrote Fusha before AI (FushaPreAI 3 = No).')
    w('COMPUTE Abil_Register_f = Abil_Register.')
    w('IF (FushaPreAI = 3) Abil_Register_f = $SYSMIS.')
    w('COMPUTE AbilityDecline = -MEAN.2(Abil_Lexical, Abil_Fluency, Abil_ArabicOnly).')
    w('COMPUTE AbilityDecline4 = -MEAN.3(Abil_Lexical, Abil_Fluency, Abil_ArabicOnly, Abil_Register_f).')
    w('COMPUTE Gap_Equal_r = 6 - Gap_Equal.')
    w('COMPUTE QualityGap = MEAN.3(Gap_Understand, Gap_Accuracy, Gap_Voice, Gap_Equal_r).')
    w('COMPUTE QualityGap3 = MEAN(Gap_Understand, Gap_Accuracy, Gap_Equal_r).')
    fut = [n for n in names if n.startswith('Future_')]
    w('COMPUTE Expected = MEAN.6(%s).' % ', '.join(fut))
    w('COMPUTE AI_BreadthCount = SUM(%s).' % ', '.join('AI_Breadth_%d' % i for i in range(1, 9)))
    w('COMPUTE EnglishShare = AI_Lang.')
    w('COMPUTE AI_TenureRank = 6 - AI_Start.')
    w('COMPUTE SwitchEng_bin = (SwitchEng >= 3).')
    w('COMPUTE Age25 = (Age >= 2).')
    w('COMPUTE Computing = (Field = 1).')
    w('COMPUTE EventMove = (Events_4 = 1 OR Events_5 = 1).')
    w('COMPUTE Medium = (ANY(Sch_SciLang, 2, 3) OR ANY(Uni_Lang, 2, 3, 4)).')
    w('DESCRIPTIVES AI_Freq AI_TaskShare AI_BreadthCount /SAVE.')
    w('* AI intensity = mean of z(task share) and z(breadth). Frequency is descriptive only.')
    w('COMPUTE AI_Intensity = MEAN(ZAI_TaskShare, ZAI_BreadthCount).')
    w('COMPUTE AI_Intensity3 = MEAN(ZAI_Freq, ZAI_TaskShare, ZAI_BreadthCount).')
    w('EXECUTE.')
    w('')
    w('VARIABLE LABELS')
    for k, (n, lab) in enumerate([
        ('excl_region', 'Grew up or lives outside the Arab world'),
        ('moved', 'Moved country since 2022 or since starting AI'),
        ('core', 'Core sample (sensitivity): grew up and lives in the Arab region, no move since 2022'),
        ('stable', 'Same workplace or university throughout the AI period'),
        ('straightline', 'Every change row much less, or every row much more'),
        ('DomainsValid', 'Number of domains that apply'),
        ('Displacement', 'Displacement: minus mean AI-attributed change over the domains that apply (6+ of 8); higher = more loss'),
        ('Displacement4', 'Displacement over writing, self, personal, family only (sensitivity); higher = more loss'),
        ('NetLoss', 'Net loss: Displacement above 0'),
        ('Disp_Fusha', 'Loss in Fusha (minus change); higher = more loss'),
        ('Disp_WorkStudy', 'Loss in work or study (minus change); higher = more loss'),
        ('Disp_Personal', 'Loss in personal matters (minus change); higher = more loss'),
        ('Disp_Family', 'Loss with family or friends (minus change); higher = more loss'),
        ('DialectLoss', 'Loss in the spoken-dialect domains: self, personal, family; higher = more loss'),
        ('DomainsLost', 'Number of domains with less Arabic because of AI (0-8)'),
        ('FormalLoss', 'Loss in the formal domains (the H1 domains): work/study, Fusha; higher = more loss'),
        ('AnyFormalLoss', 'Less Arabic in work/study or Fusha'),
        ('AbilityDecline', 'Ability decline without AI: lexical, fluency, Arabic only; higher = harder'),
        ('AbilityDecline4', 'Ability decline incl. Fusha register item (sensitivity); higher = harder'),
        ('QualityGap', 'Perceived AI quality gap, Arabic vs English (4 items, 1..5, higher = bigger gap)'),
        ('QualityGap3', 'Perceived quality gap without the AI-voice item (sensitivity)'),
        ('Expected', 'Expected change in Arabic use over two years (-2..+2, negative = less)'),
        ('AI_BreadthCount', 'Number of AI uses ticked (0-8)'),
        ('AI_Intensity', 'AI intensity: mean z of share of work and breadth'),
        ('AI_Intensity3', 'AI intensity incl. frequency (sensitivity)'),
        ('EnglishShare', 'English share of AI use: 1 always Arabic .. 5 always English'),
        ('AI_TenureRank', 'AI tenure rank (5 = started 2022 or earlier)'),
        ('SwitchEng_bin', 'Substituted English for Arabic at least sometimes'),
        ('Age25', 'Aged 25 or over'),
        ('Computing', 'Field: computing / IT'),
        ('EventMove', 'Moved country or started studying/working in English during the AI period'),
        ('Medium', 'Foreign-medium school science or university (English, French or mixed)'),
        ('Abil_Register_f', 'Without AI, writing formal Fusha: harder or easier; missing if no Fusha writing before AI'),
        ('Gap_Equal_r', 'Gap_Equal reversed (6 - answer): higher = AI worse in Arabic')]
        + [('d_' + x, 'AI-attributed change, %s; not applicable = missing; -2 much less .. +2 much more' % x) for x in DOMAINS]):
        w('  %s%s %s' % ('/' if k else '', n, q(lab)))   # no slash before the first variable
    w('.')
    w('VALUE LABELS excl_region moved core stable straightline NetLoss AnyFormalLoss SwitchEng_bin Age25 Computing EventMove Medium 0 "No" 1 "Yes".')
    w('VALUE LABELS %s -2 "Much less" -1 "Less" 0 "No change" 1 "More" 2 "Much more".' % ' '.join('d_' + x for x in DOMAINS))
    w('VALUE LABELS Abil_Register_f -2 "Much harder" -1 "Harder" 0 "No change" 1 "Easier" 2 "Much easier".')
    w('VALUE LABELS Gap_Equal_r 1 "Strongly agree (as good)" 2 "Agree" 3 "Neutral" 4 "Disagree" 5 "Strongly disagree (not as good)".')
    w('')
    w('* Reliability is computed in 02_hypotheses.sps, on the primary sample.')
    w('')
    w('* ---------------------------------------------------------------- check against prepare_data.py output.')
    w('DESCRIPTIVES Displacement Displacement4 NetLoss DialectLoss DomainsLost FormalLoss AnyFormalLoss AbilityDecline')
    w('  AbilityDecline4 QualityGap QualityGap3 Expected AI_BreadthCount AI_Intensity AI_Intensity3 SwitchEng_bin /STATISTICS=MEAN STDDEV MIN MAX.')
    w('FREQUENCIES excl_region moved core stable straightline Age25 Computing EventMove Medium.')
    w('')
    w("SAVE OUTFILE='proj/data/ai-arabic-survey.sav'.")
    os.makedirs(os.path.dirname(OUT_SPS), exist_ok=True)
    io.open(OUT_SPS, 'w', encoding='utf-8-sig').write('\n'.join(L) + '\n')


if __name__ == '__main__':
    main()
