# -*- coding: utf-8 -*-
"""
Static checks for the SPSS syntax, run before handing it to SPSS:
  1. every comment line ends with a period (a comment that does not swallows the next command -
     that is how the Friedman test silently failed to run on 2 Oct);
  2. every command ends with a period before the next command starts;
  3. every variable name used exists in scored.csv or is created earlier in the syntax.
Run:  python analysis/lint_sps.py      (exit code 1 if anything is wrong)
"""
import io, os, re, sys
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
KNOWN = set(pd.read_csv(os.path.join(HERE, 'data', 'scored.csv'), nrows=0).columns) | {'ZAI_Freq', 'ZAI_TaskShare', 'ZAI_BreadthCount'}
KEYWORDS = set('''FILE HANDLE NAME GET DATA TYPE TXT ENCODING DELCASE LINE DELIMITERS QUALIFIER ARRANGEMENT DELIMITED FIRSTCASE
VARIABLES VARIABLE LABELS VALUE MISSING VALUES SET TVARS NAMES COMPUTE IF DO REPEAT END EXECUTE COUNT LO THRU HI
DESCRIPTIVES SAVE STATISTICS MEAN STDDEV MIN MAX FREQUENCIES RELIABILITY SCALE ALL MODEL ALPHA SUMMARY TOTAL NVALID SUM ANY
OUTFILE LEVEL NPAR TESTS WILCOXON SIGN FRIEDMAN KENDALL WITH PAIRED ANALYSIS LISTWISE REGRESSION COEFF OUTS CI R ANOVA
CHANGE COLLIN TOL DEPENDENT METHOD ENTER NONPAR CORR PRINT SPEARMAN TWOTAIL TEMPORARY SELECT AND OR NOT FILTER BY OFF
LOGISTIC TO SYSMIS UTF8 F3 CROSSTABS TABLES M W N TITLE PAIRWISE AGGREGATE MODE ADDVARIABLES OVERWRITE YES COOK
MEANS CELLS'''.split())


def lint(path):
    errs = []
    text = io.open(path, encoding='utf-8-sig').read()
    lines = text.splitlines()
    created = set()
    in_cmd = False                                    # inside an unterminated (non-comment) command
    for i, raw in enumerate(lines, 1):
        ln = raw.rstrip()
        if not ln.strip():
            continue
        if ln.startswith('*'):
            if in_cmd:
                errs.append('%d: comment starts before the previous command was ended with a period' % i)
            if not ln.endswith('.'):
                errs.append('%d: comment line does not end with a period (it will swallow the next line)' % i)
            continue
        if ln.strip() == '.':
            in_cmd = False                            # a line holding only a period ends the command
            continue
        if not ln[0].isspace() and in_cmd:
            errs.append('%d: new command starts before the previous one ended with a period' % i)
        body = re.sub(r"'[^']*'|\"[^\"]*\"", ' ', ln)  # drop quoted strings
        m = re.match(r'\s*(COMPUTE|COUNT)\s+(\w+)', body, re.I)
        if m:
            created.add(m.group(2))
        for nm in re.findall(r'/SAVE\s+\w+\((\w+)\)', body, re.I) + re.findall(r'/(\w+)\s*=\s*(?:MAX|MIN|MEAN|SUM)\(', body, re.I):
            created.add(nm)                           # REGRESSION /SAVE COOK(x), AGGREGATE /x=MAX(y)
        if re.match(r'\s*DO REPEAT', body, re.I):
            for grp in re.findall(r'/?\s*\w+\s*=\s*([\w ]+)', body):
                pass
        for tok in re.findall(r'[A-Za-z_][A-Za-z0-9_]*', body):
            if tok.upper() in KEYWORDS or tok in KNOWN or tok in created or tok in {'a', 'c', 'f', 'proj'}:
                continue
            if re.fullmatch(r'Z?[A-Za-z]+_\w+', tok) and tok in KNOWN:
                continue
            errs.append('%d: unknown name "%s"' % (i, tok))
        in_cmd = not ln.endswith('.')
    if in_cmd:
        errs.append('end of file: last command is not ended with a period')
    return errs


if __name__ == '__main__':
    bad = 0
    for f in ['01_import_and_score.sps', '02_hypotheses.sps']:
        e = lint(os.path.join(HERE, 'spss', f))
        print('%-26s %s' % (f, 'OK' if not e else '%d problem(s)' % len(e)))
        for x in e[:40]:
            print('   ', x)
        bad += len(e)
    sys.exit(1 if bad else 0)
