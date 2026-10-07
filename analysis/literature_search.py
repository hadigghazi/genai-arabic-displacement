# -*- coding: utf-8 -*-
"""
Literature search behind the paper's novelty statement (Introduction).

Ten queries combining generative AI or ChatGPT with Arabic and language use, shift, attrition, choice or
diglossia were run in OpenAlex and Crossref, restricted to works published since ChatGPT's release
(30 November 2022). The 100 most relevant records per query and database were kept, and every title that
mentions Arabic was screened by hand. Run on 7 October 2026; results/literature_search.txt is that run.

    python analysis/literature_search.py
"""
import datetime
import json
import os
import time
import urllib.parse
import urllib.request

QUERIES = [
    'generative AI Arabic language use',
    'ChatGPT Arabic language use',
    'ChatGPT Arabic language shift',
    'generative AI Arabic language attrition',
    'large language model Arabic speakers language choice',
    'ChatGPT Arabic English bilingual',
    'artificial intelligence Arabic language loss',
    'generative AI first language use survey',
    'AI chatbot Arabic diglossia',
    'ChatGPT Lebanon language',
]
SINCE = '2022-11-30'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results', 'literature_search.txt')


def get(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'literature-search (research use)'})
    with urllib.request.urlopen(req, timeout=90) as r:
        return json.load(r)


def openalex(q):
    d = get('https://api.openalex.org/works?search=' + urllib.parse.quote(q)
            + '&filter=from_publication_date:' + SINCE + '&per-page=100&select=title,doi,publication_year')
    return d['meta']['count'], [(w['title'] or '').strip() for w in d['results']]


def crossref(q):
    d = get('https://api.crossref.org/works?query.bibliographic=' + urllib.parse.quote(q)
            + '&filter=from-pub-date:' + SINCE + '&rows=100&select=title,DOI')
    return d['message']['total-results'], [((w.get('title') or [''])[0]).strip() for w in d['message']['items']]


def main():
    lines = ['Literature search, run %s' % datetime.date.today().isoformat(), '']
    seen = {'OpenAlex': set(), 'Crossref': set()}
    for q in QUERIES:
        for name, fn in (('OpenAlex', openalex), ('Crossref', crossref)):
            total, titles = fn(q)
            seen[name].update(t for t in titles if t)
            lines.append('%-9s %-55s matches %8s, kept %d' % (name, q, total, len(titles)))
            time.sleep(1)
    allt = seen['OpenAlex'] | seen['Crossref']
    arabic = sorted(t for t in allt if 'arab' in t.lower())
    lines += ['', 'unique titles kept: OpenAlex %d, Crossref %d, both databases combined %d; mentioning Arabic %d'
              % (len(seen['OpenAlex']), len(seen['Crossref']), len(allt), len(arabic)), '',
              'Titles mentioning Arabic (screened by hand):'] + ['  - ' + t for t in arabic]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')
    print('\n'.join(lines[:24]))
    print('...wrote', OUT)


if __name__ == '__main__':
    main()
