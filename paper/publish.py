"""Publishes the paper on the study website: copies the PDF and writes paper.json and a BibTeX entry, and copies
the SPSS output and syntax beside it.

    python paper/publish.py paper app/web/research

The title, author, affiliation and abstract are read from main.tex, the page count from the PDF, and the
date and version from git, so the research page changes whenever the committed paper does. Standard
library only, because the deploy workflow runs it before building the site.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import zlib

SRC, OUT = sys.argv[1], sys.argv[2]
PDF_NAME = 'ghazi-2026-generative-ai-arabic.pdf'
BIB_NAME = 'ghazi-2026-generative-ai-arabic.bib'
SITE = 'https://arabic-ai.hadighazi.com/#research'

with open(os.path.join(SRC, 'main.tex'), encoding='utf-8') as f:
    tex = f.read()


def plain(s):
    """LaTeX -> text, for the few constructs the title and abstract use."""
    s = re.sub(r'\\(emph|textit|textbf)\{([^{}]*)\}', r'\2', s)
    s = s.replace('``', '“').replace("''", '”').replace('---', '—').replace('--', '–').replace('\\%', '%')
    s = s.replace('~', ' ').replace('\\', '')
    return re.sub(r'\s+', ' ', s).strip()


def one(pattern):
    m = re.search(pattern, tex, re.S)
    assert m, 'not found in main.tex: ' + pattern
    return m.group(1)


title = plain(one(r'\\title\{(.*?)\}\s*\n'))
author = plain(one(r'\\IEEEauthorblockN\{(.*?)\}'))
affiliation = plain(one(r'\\IEEEauthorblockA\{\\textit\{(.*?)\}'))
abstract = plain(one(r'\\begin\{abstract\}(.*?)\\end\{abstract\}'))
keywords = [plain(k) for k in one(r'\\begin\{IEEEkeywords\}(.*?)\\end\{IEEEkeywords\}').split(',')]


def pdf_pages(path):
    """The page tree's /Count, looking inside compressed object streams too."""
    data = open(path, 'rb').read()
    chunks = [data]
    for m in re.finditer(rb'stream\r?\n(.*?)\r?\nendstream', data, re.S):
        try:
            chunks.append(zlib.decompress(m.group(1)))
        except zlib.error:
            pass
    counts = [int(c) for chunk in chunks for c in re.findall(rb'/Type\s*/Pages\b[^>]*?/Count\s+(\d+)', chunk)]
    counts += [int(c) for chunk in chunks for c in re.findall(rb'/Count\s+(\d+)[^>]*?/Type\s*/Pages\b', chunk)]
    return max(counts) if counts else None


def git(*args):
    try:
        return subprocess.run(['git', *args], capture_output=True, text=True, check=True).stdout.strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


pdf = os.path.join(SRC, 'main.pdf')
os.makedirs(OUT, exist_ok=True)
shutil.copyfile(pdf, os.path.join(OUT, PDF_NAME))
year = '2026'
bib = ('@misc{ghazi2026genai,\n'
       '  author       = {Ghazi, Hadi},\n'
       '  title        = {%s},\n'
       '  howpublished = {%s, preprint},\n'
       '  year         = {%s},\n'
       '  url          = {%s}\n'
       '}\n') % (title.replace('–', '--'), affiliation, year, SITE)
with open(os.path.join(OUT, BIB_NAME), 'w', encoding='utf-8') as f:
    f.write(bib)
paper = {
    'title': title, 'author': author, 'affiliation': affiliation, 'abstract': abstract, 'keywords': keywords,
    'pdf': PDF_NAME, 'bib': BIB_NAME, 'bytes': os.path.getsize(pdf), 'pages': pdf_pages(pdf),
    'updated': git('log', '-1', '--format=%cI', '--', os.path.join(SRC, 'main.pdf')),
    'commit': git('log', '-1', '--format=%h', '--', os.path.join(SRC, 'main.pdf')),
}
# the SPSS materials: the output of the final run, and the syntax that produced it
SPSS = os.path.join(os.path.dirname(os.path.abspath(SRC)), 'analysis', 'spss')
paper['materials'] = []
for name, path, label in [
        ('spss-output-105.pdf', os.path.join(SPSS, 'output', 'spss-output-105.pdf'), 'SPSS 23 output, all 105 respondents (PDF)'),
        ('spss-output-105.spv', os.path.join(SPSS, 'output', 'spss-output-105.spv'), 'SPSS 23 output, all 105 respondents (SPSS Viewer file)'),
        ('01_import_and_score.sps', os.path.join(SPSS, '01_import_and_score.sps'), 'SPSS syntax 1: import, labels and scoring'),
        ('02_hypotheses.sps', os.path.join(SPSS, '02_hypotheses.sps'), 'SPSS syntax 2: the hypothesis tests')]:
    if os.path.exists(path):
        shutil.copyfile(path, os.path.join(OUT, name))
        paper['materials'].append({'file': name, 'label': label, 'bytes': os.path.getsize(path)})
with open(os.path.join(OUT, 'paper.json'), 'w', encoding='utf-8') as f:
    json.dump(paper, f, ensure_ascii=False, indent=1)
print('published %s (%s pages, %d bytes, %s) to %s' % (PDF_NAME, paper['pages'], paper['bytes'], paper['commit'], OUT))
