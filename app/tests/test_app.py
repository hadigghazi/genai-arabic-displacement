"""The app must score exactly like the fitted scikit-learn pipelines (expected scores were computed by
analysis/09_export_model.py on invented answer profiles) and must reject answers the form cannot produce."""
import math

import pytest
from fastapi.testclient import TestClient

from server.main import MODELS, app

client = TestClient(app)
CASES = [(m['id'], t['answers'], t['score']) for m in MODELS.spec['models'] for t in m['tests']]
GOOD = CASES[0][1]


def test_health():
    r = client.get('/api/health')
    assert r.status_code == 200 and r.json() == {'status': 'ok', 'models': 3}


def test_model_card_has_questions_and_no_coefficients():
    card = client.get('/api/model').json()
    assert len(card['questions']) == 12
    assert {m['id'] for m in card['models']} == {'AnyFormalLoss', 'Loss_WorkStudy', 'Loss_Self'}
    assert all('features' not in m and 'tests' not in m for m in card['models'])
    assert all(m['cv']['auc'] >= 0.70 for m in card['models'])


@pytest.mark.parametrize('target,answers,expected', CASES)
def test_scores_match_scikit_learn(target, answers, expected):
    r = client.post('/api/predict', json=answers)
    assert r.status_code == 200
    got = {x['id']: x for x in r.json()['results']}[target]
    assert got['score'] == pytest.approx(expected, abs=1e-9)
    assert got['likely'] == (expected >= 0.5)


def test_contributions_add_up_to_the_score():
    for res in client.post('/api/predict', json=GOOD).json()['results']:
        m = next(m for m in MODELS.spec['models'] if m['id'] == res['id'])
        logit = m['intercept'] + sum(c['contribution'] for c in res['contributions'])
        assert 1 / (1 + math.exp(-logit)) == pytest.approx(res['score'], abs=1e-12)


@pytest.mark.parametrize('change', [{'AI_Lang': 6}, {'Age': 0}, {'Education': 9}, {'AI_Breadth': [1, 1]},
                                    {'Events': [7]}, {'AI_Freq': 'often'}])
def test_rejects_answers_the_form_cannot_produce(change):
    assert client.post('/api/predict', json=dict(GOOD, **change)).status_code == 422


def test_rejects_missing_answers():
    bad = {k: v for k, v in GOOD.items() if k != 'AI_Lang'}
    assert client.post('/api/predict', json=bad).status_code == 422


def test_site_is_served():
    r = client.get('/')
    assert r.status_code == 200 and 'js/main.js' in r.text
    js = client.get('/js/main.js')
    assert js.status_code == 200 and 'javascript' in js.headers['content-type']


def test_study_data_is_aggregate_only():
    s = client.get('/data/study.json').json()
    assert s['sample']['n'] == 105 and len(s['rq1']['domains']) == 8
    assert sum(t['usability']['usable'] for t in s['ml']['targets']) == 3
    # group-level numbers only: no per-respondent arrays anywhere
    def walk(x):
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            assert len(x) < 105, 'a list as long as the sample'
            for v in x:
                walk(v)
    walk(s)
