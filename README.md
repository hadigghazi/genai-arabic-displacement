# Is Generative AI Displacing Arabic?

Survey instrument, analysis code and results for the paper

> H. Ghazi, "Is Generative AI Displacing Arabic? Perceived Change in Arabic Use Among Lebanese
> Arabic–English Bilinguals." Lebanese University, 2026.

An anonymous Arabic online survey (n = 105) asked Lebanese Arabic–English bilinguals whether, because
of AI, they now use Arabic less or more in eight domains. The study tests the direction and domain order of
the reported change (H1–H2), its predictors and correlates (H3–H5), and whether information about AI use
improves cross-validated prediction of who reports a decrease (RQ4).

## Contents

| Path | What it is |
|---|---|
| `paper/` | LaTeX source (`main.tex`, `refs.bib`, IEEEtran) and the compiled `main.pdf`. Compile with XeLaTeX (`latexmk -xelatex main.tex`); the Arabic text uses the Sakkal Majalla font (on Overleaf, select XeLaTeX and use Amiri instead). |
| `instrument-v3.md` | The questionnaire as fielded: every item in Arabic and English, with response options and coding. |
| `instrument_data.py`, `instrument_v3.py` | Single source of the items and the generator for the codebook, `instrument-v3.json` and the form script. |
| `build-form-v3-ar.gs` | Google Apps Script that builds the fielded Arabic Google Form. |
| `analysis/prepare_data.py` | Raw form export → coded and scored data; also writes `spss/01_import_and_score.sps`. |
| `analysis/spss/` | SPSS 23 syntax: import and scoring (01), hypothesis tests (02); `output/` holds the SPSS 23 output of the final run (PDF and Viewer file). |
| `analysis/03_python_stats.py` | Everything SPSS 23 cannot do: HC3 inference, Holm, Page's test, bootstraps, Firth logit, omega, sensitivity analyses. |
| `analysis/04_figures.py` | Figure 1. |
| `analysis/05_ml.py`, `06_ml_more_targets.py`, `07_oversampling_check.py`, `08_usability_main_targets.py` | Machine learning (RQ4): nested feature blocks, repeated cross-validation, corrected tests, permutation tests, further targets, oversampling check, and the four usable-model criteria applied to every target. |
| `analysis/crosscheck_spss.py`, `analysis/lint_sps.py` | SPSS–Python cross-check (104 statistics agree; `results/spss_crosscheck.json`) and a static check of the SPSS syntax. |
| `analysis/ANALYSIS-DECISIONS.md` | Decision log: every analysis choice, its alternatives, and where each alternative is reported. |
| `analysis/results/` | All outputs: `python_stats.txt`, `ml_results.txt`, `ml_more_targets.txt`, `oversampling_check.txt`, `ml_usability.txt`, tables and figures. |
| `analysis/requirements.txt` | Package versions used. |
| `analysis/09_export_model.py` | Fits the usable models on all respondents and exports their coefficients (no individual data) to `app/model/model.json`. |
| `app/` | The study website: FastAPI service, findings and machine-learning pages and the live model (`web/`), tests, Dockerfile. |
| `analysis/10_export_site_data.py` | Writes the website's group-level numbers (`app/web/data/study.json`), recomputing the headline tests and checking them against `python_stats.txt`. |
| `docker-compose.prod.yml`, `.github/workflows/app.yml` | Deployment: GitHub Actions tests, builds the image to GHCR and restarts it on the VM behind Caddy. |

## Data

Individual responses are not included: participants were told that answers would be reported as group
results. The scripts expect the form export at `analysis/data/responses-raw-2026-10-04.xlsx`.

## Reproducing the analysis

```bash
pip install -r analysis/requirements.txt
python analysis/prepare_data.py           # coded.csv, scored.csv, spss/01_import_and_score.sps
# SPSS 23: set the folder in analysis/prepare_data.py (written into 01) and in analysis/spss/02_hypotheses.sps;
# run 01, then run 02 between  OMS /SELECT TABLES /DESTINATION FORMAT=OXML OUTFILE='oms.xml'.  and  OMSEND.
python analysis/crosscheck_spss.py oms.xml   # results/spss_crosscheck.json (104 statistics)
python analysis/03_python_stats.py        # results/python_stats.txt
python analysis/04_figures.py             # results/fig1_*
python analysis/05_ml.py                  # results/ml_results.txt (over an hour; cached in analysis/.mlcache, so an interrupted run resumes)
python analysis/06_ml_more_targets.py     # results/ml_more_targets.txt
python analysis/07_oversampling_check.py  # results/oversampling_check.txt
python analysis/08_usability_main_targets.py  # results/ml_usability.txt
python analysis/09_export_model.py        # app/model/model.json (commit it; CI tests and deploys the app)
python analysis/10_export_site_data.py    # app/web/data/study.json, the website's numbers
```

Python 3.13. The ML scripts use `ML_JOBS` parallel workers (default 12; set it to your core count); `ML_QUICK=1` runs a quick smoke test.

## Study website

`app/` is the study's website at https://arabic-ai.hadighazi.com, told as one story in eight chapters: the
question, how we asked, where Arabic is used less, the language of AI use, the shift that began before AI,
whether it can be predicted, a live model to try, and what it means, followed by the paper (read, download,
cite) and the references. Each chapter keeps its statistics in collapsible "How we know" boxes. The pages read
`app/web/data/study.json` (group-level results only, written by `analysis/10_export_site_data.py`); the paper
is copied in by `paper/publish.py` on every deploy; the form posts to `/api/predict`, which scores answers in
memory and never stores them. Run it locally with
`python paper/publish.py paper app/web/research && docker build --target runtime -t arabic-ai app && docker run --rm -p 8082:8000 arabic-ai`.

## License

Code and instrument: MIT License (see `LICENSE`). Individual survey responses are not part of the repository.
