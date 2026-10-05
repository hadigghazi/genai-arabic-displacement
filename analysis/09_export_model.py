# -*- coding: utf-8 -*-
"""
Fits the usable models (results/ml_usability.txt) on all respondents and exports them for the web app.

Each model is the exact pipeline of 05_ml.py (linear background + AI use: StandardScaler -> SMOTENC ->
L2 logistic regression, same seed), fitted once on everyone. Only the numbers needed to score a new
person are exported: the scaler's means and standard deviations and the logistic coefficients. The fitted
pipeline itself is NOT saved, because SMOTENC keeps the training rows (its nearest-neighbour index), and
individual responses must never leave this machine.

The export is checked against scikit-learn: the JSON formula must reproduce predict_proba for every
respondent, and the app's tests replay synthetic answer profiles (not respondents) with their expected scores.

Run with Anaconda's Python:  C:\\Users\\User\\anaconda3\\python.exe analysis\\09_export_model.py
Writes app/model/model.json.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
with open(os.path.join(HERE, '05_ml.py'), encoding='utf-8') as f:
    _src = f.read()
exec(compile(_src.split('# ------------------------------------------------------------------ main evaluation')[0],
             os.path.join(HERE, '05_ml.py'), 'exec'))
sys.path.insert(0, ROOT)
from instrument_data import SECTIONS  # noqa: E402

OUT = os.path.join(ROOT, 'app', 'model', 'model.json')
M1 = M0 + AI
prim = ALL.copy()

LABELS = {
    'AnyFormalLoss': {'en': 'Less Arabic in formal areas (work or study, or Fusha)',
                      'ar': 'استخدام أقل للعربية في المجالات الرسمية (العمل أو الدراسة، أو الفصحى)'},
    'Loss_WorkStudy': {'en': 'Less Arabic in work or study',
                       'ar': 'استخدام أقل للعربية في العمل أو الدراسة'},
    'Loss_Self': {'en': 'Less Arabic when talking to yourself or writing your own notes',
                  'ar': 'استخدام أقل للعربية عند التحدث مع نفسك أو كتابة ملاحظاتك الخاصة'},
}
USABILITY_LABEL = {'AnyFormalLoss': 'any formal-domain loss', 'Loss_WorkStudy': 'loss: WorkStudy',
                   'Loss_Self': 'loss: Self'}

# ------------------------------------------------------------------ which models are usable, and how good
with open(os.path.join(HERE, 'results', 'ml_usability.txt'), encoding='utf-8') as f:
    usab = f.read()
usable = re.search(r'^usable: (.*)$', usab, re.M).group(1).split(', ')
assert set(usable) == set(LABELS), 'usable models changed: %s - update LABELS' % usable
tab = pd.read_csv(os.path.join(HERE, 'results', 'ml_table.csv'))


def usability(tgt):
    block = usab.split('    %s\n' % USABILITY_LABEL[tgt])[1].split('->')[0]
    m = re.search(r'AUC over splits ([\d.]+) \(([\d.]+) to ([\d.]+)\)', block)
    return {'perm_p_holm': float(re.search(r'permutation Holm p ([\d.]+)', block).group(1)),
            'auc_splits': {'mean': float(m.group(1)), 'min': float(m.group(2)), 'max': float(m.group(3))},
            'without_age_perm_p': float(re.search(r'without the age dummy: permutation p ([\d.]+)', block).group(1)),
            'balanced_accuracy': float(re.search(r'balanced accuracy over splits ([\d.]+)', block).group(1))}


# ------------------------------------------------------------------ answers -> features (same as prepare_data.py)
def features(a):
    """a: raw answers with the form's codes (1 = first option). Returns the model's 12 features."""
    return {'Age25': int(a['Age'] >= 2), 'Computing': int(a['Field'] == 1), 'Education': a['Education'],
            'Eng_Prof': a['Eng_Prof'], 'EventMove': int(4 in a['Events'] or 5 in a['Events']),
            'AI_TaskShare': a['AI_TaskShare'], 'AI_BreadthCount': len(a['AI_Breadth']), 'AI_Freq': a['AI_Freq'],
            'AI_TenureRank': 6 - a['AI_Start'], 'EnglishShare': a['AI_Lang'], 'AI_Content': a['AI_Content'],
            'AI_ContentLang': a['AI_ContentLang']}


SYNTHETIC = [  # invented answer profiles for the app's tests - not respondents
    {'Age': 1, 'Education': 3, 'Field': 1, 'Eng_Prof': 5, 'Events': [1, 4], 'AI_Start': 1, 'AI_Freq': 4,
     'AI_TaskShare': 5, 'AI_Breadth': [1, 2, 3, 4, 5, 6, 7, 8], 'AI_Lang': 5, 'AI_Content': 5, 'AI_ContentLang': 5},
    {'Age': 3, 'Education': 1, 'Field': 5, 'Eng_Prof': 2, 'Events': [6], 'AI_Start': 5, 'AI_Freq': 1,
     'AI_TaskShare': 1, 'AI_Breadth': [3], 'AI_Lang': 1, 'AI_Content': 1, 'AI_ContentLang': 1},
    {'Age': 1, 'Education': 2, 'Field': 2, 'Eng_Prof': 4, 'Events': [], 'AI_Start': 3, 'AI_Freq': 3,
     'AI_TaskShare': 3, 'AI_Breadth': [1, 3, 5, 7], 'AI_Lang': 3, 'AI_Content': 3, 'AI_ContentLang': 3},
    {'Age': 2, 'Education': 3, 'Field': 3, 'Eng_Prof': 3, 'Events': [3, 5], 'AI_Start': 2, 'AI_Freq': 2,
     'AI_TaskShare': 4, 'AI_Breadth': [2, 4], 'AI_Lang': 4, 'AI_Content': 4, 'AI_ContentLang': 2},
    {'Age': 4, 'Education': 2, 'Field': 6, 'Eng_Prof': 1, 'Events': [2], 'AI_Start': 4, 'AI_Freq': 4,
     'AI_TaskShare': 2, 'AI_Breadth': [1, 2, 3, 4, 5, 6], 'AI_Lang': 2, 'AI_Content': 2, 'AI_ContentLang': 4},
]

# ------------------------------------------------------------------ fit and export
models = []
for tgt in ['AnyFormalLoss', 'Loss_WorkStudy', 'Loss_Self']:
    X, y = data(prim, tgt, M1)
    pipe = model('clf', 'linear', M1).fit(X, y)
    sc, lr = pipe.named_steps['scale'], pipe.named_steps['model']
    mean, scale, coef, b0 = sc.mean_, sc.scale_, lr.coef_[0], float(lr.intercept_[0])
    # the exported formula must reproduce scikit-learn exactly
    manual = 1 / (1 + np.exp(-(((X - mean) / scale) @ coef + b0)))
    assert np.max(np.abs(manual - pipe.predict_proba(X)[:, 1])) < 1e-12, tgt
    row = tab[(tab.target == tgt) & (tab.features == 'M1 + AI use') & (tab.model == 'linear')].iloc[0]
    tests = []
    for prof in SYNTHETIC:
        f = features(prof)
        tests.append({'answers': prof,
                      'score': float(pipe.predict_proba(np.array([[f[c] for c in M1]], float))[0, 1])})
    models.append({
        'id': tgt, 'label': LABELS[tgt], 'n_yes': int(y.sum()), 'n_no': int(len(y) - y.sum()),
        'cv': dict({'auc': round(float(row.score), 4), 'balanced_accuracy_headline': round(float(row.bal_acc), 4)},
                   **usability(tgt)),
        'intercept': b0,
        'features': [{'name': c, 'mean': float(m), 'sd': float(s), 'coef': float(w)}
                     for c, m, s, w in zip(M1, mean, scale, coef)],
        'tests': tests})
    print('%-15s n=%d (%d yes)  CV AUC %.2f  intercept %+.3f' % (tgt, len(y), y.sum(), row.score, b0))

# ------------------------------------------------------------------ the questions the form asks (as fielded)
ITEMS = ['Age', 'Education', 'Field', 'Eng_Prof', 'Events', 'AI_Start', 'AI_Freq', 'AI_TaskShare', 'AI_Breadth',
         'AI_Lang', 'AI_Content', 'AI_ContentLang']
by_code = {it['code']: it for sec in SECTIONS for it in sec['items'] if it.get('code')}
questions = []
for code in ITEMS:
    it = by_code[code]
    opts = [{'code': i + 1, 'en': en, 'ar': ar} for i, (en, ar) in enumerate(zip(it['o']['en'], it['o']['ar']))]
    if code == 'AI_Lang':
        opts = [o for o in opts if o['code'] != 6]   # "another language" was set to missing in the analysis
    questions.append({'code': code, 'type': 'check' if it['type'] == 'check' else 'single',
                      'q': it['q'], 'options': opts})

FEATURE_TEXT = {
    'Age25': {'en': 'Age 25 or over', 'ar': 'العمر 25 عاماً أو أكثر'},
    'Computing': {'en': 'Field: computing / IT', 'ar': 'المجال: الحوسبة / تقنية المعلومات'},
    'Education': {'en': 'Education level', 'ar': 'المستوى التعليمي'},
    'Eng_Prof': {'en': 'English level', 'ar': 'مستوى الإنجليزية'},
    'EventMove': {'en': 'Started studying or working in English, or moved country', 'ar': 'بدء الدراسة أو العمل بالإنجليزية، أو الانتقال إلى بلد آخر'},
    'AI_TaskShare': {'en': 'Share of work or study done with AI', 'ar': 'نسبة العمل أو الدراسة بمساعدة الذكاء الاصطناعي'},
    'AI_BreadthCount': {'en': 'Number of things you use AI for', 'ar': 'عدد استخدامات الذكاء الاصطناعي'},
    'AI_Freq': {'en': 'How often you use AI', 'ar': 'عدد مرات استخدام الذكاء الاصطناعي'},
    'AI_TenureRank': {'en': 'How long you have used AI regularly', 'ar': 'مدة الاستخدام المنتظم للذكاء الاصطناعي'},
    'EnglishShare': {'en': 'Writing to AI in English', 'ar': 'الكتابة للذكاء الاصطناعي بالإنجليزية'},
    'AI_Content': {'en': 'Seeing AI-generated content', 'ar': 'مصادفة محتوى مولّد بالذكاء الاصطناعي'},
    'AI_ContentLang': {'en': 'Choosing the English original over AI Arabic voice', 'ar': 'اختيار الأصل الإنجليزي بدل الصوت العربي المولّد'},
}

out = {
    'study': {'title': 'Is Generative AI Displacing Arabic? Perceived Change in Arabic Use Among Lebanese Arabic-English Bilinguals',
              'author': 'Hadi Ghazi, Lebanese University', 'n': int(len(prim)),
              'collected': '30 September to 4 October 2026'},
    'method': 'L2 logistic regression (C = 1) on standardised features, SMOTENC oversampling inside training; '
              'evaluated by repeated 10x5-fold cross-validation and permutation tests; fitted on all respondents.',
    'threshold': 0.5,
    'feature_order': M1,
    'feature_text': FEATURE_TEXT,
    'questions': questions,
    'models': models,
}
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print('wrote', OUT)
