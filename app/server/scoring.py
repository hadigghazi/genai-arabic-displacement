"""Scores a person's answers with the exported models (model/model.json, written by analysis/09_export_model.py).

Each model is a logistic regression, exported as its logit at a shared reference profile (the respondents'
average answers, rounded) plus a weight per unit of each answer, so scoring is a few lines of arithmetic and
the server needs neither scikit-learn nor the training data. Each model has its own threshold for "likely".
"""
import json
import math
import os
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parent.parent / 'model' / 'model.json'


def derive_features(a):
    """Survey answers (form codes, 1 = first option) -> the model's 12 features, exactly as prepare_data.py."""
    return {
        'Age25': int(a['Age'] >= 2),
        'Computing': int(a['Field'] == 1),
        'Education': a['Education'],
        'Eng_Prof': a['Eng_Prof'],
        'EventMove': int(4 in a['Events'] or 5 in a['Events']),
        'AI_TaskShare': a['AI_TaskShare'],
        'AI_BreadthCount': len(a['AI_Breadth']),
        'AI_Freq': a['AI_Freq'],
        'AI_TenureRank': 6 - a['AI_Start'],
        'EnglishShare': a['AI_Lang'],
        'AI_Content': a['AI_Content'],
        'AI_ContentLang': a['AI_ContentLang'],
    }


class Models:
    def __init__(self, path=None):
        path = Path(path or os.environ.get('MODEL_PATH') or DEFAULT_PATH)
        with open(path, encoding='utf-8') as f:
            self.spec = json.load(f)
        self.questions = {q['code']: q for q in self.spec['questions']}
        self.reference = self.spec['reference_profile']

    def card(self):
        """Everything the page shows, without the test fixtures."""
        out = {k: v for k, v in self.spec.items() if k != 'models'}
        out['models'] = [{k: v for k, v in m.items() if k not in ('tests', 'features', 'logit_at_reference')}
                         for m in self.spec['models']]
        return out

    def validate(self, a):
        """Returns a list of problems; empty when every answer is one of the form's options."""
        errors = []
        for code, q in self.questions.items():
            allowed = {o['code'] for o in q['options']}
            v = a.get(code)
            if q['type'] == 'check':
                if not isinstance(v, list) or not v or any(x not in allowed for x in v) or len(set(v)) != len(v):
                    errors.append('%s: tick at least one of %s' % (code, sorted(allowed)))
                elif code == 'Events' and 6 in v and len(v) > 1:
                    errors.append('Events: "None of these" cannot be ticked with another event')
            elif v not in allowed:
                errors.append('%s: choose one of %s' % (code, sorted(allowed)))
        return errors

    def predict(self, a):
        x = derive_features(a)
        results = []
        for m in self.spec['models']:
            # contribution = how far this answer moves the logit away from the reference profile's
            contrib = [{'feature': f['name'], 'value': x[f['name']],
                        'contribution': f['per_unit'] * (x[f['name']] - self.reference[f['name']])}
                       for f in m['features']]
            logit = m['logit_at_reference'] + sum(c['contribution'] for c in contrib)
            score = 1.0 / (1.0 + math.exp(-logit))
            contrib.sort(key=lambda c: abs(c['contribution']), reverse=True)
            results.append({'id': m['id'], 'label': m['label'], 'score': score, 'logit': logit,
                            'threshold': m['threshold'], 'likely': score >= m['threshold'], 'contributions': contrib})
        return {'features': x, 'results': results}
