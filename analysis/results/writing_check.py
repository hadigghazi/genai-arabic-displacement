# Apply the extension's usability criteria to the best earlier candidate: writing loss from background (linear M0).
# Run from anywhere:  python analysis/results/writing_check.py   (executes the machinery of analysis/05_ml.py)
import os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))     # the analysis folder
__file__ = os.path.join(HERE, '05_ml.py')
src = open(__file__, encoding='utf-8').read()
exec(compile(src.split('# ------------------------------------------------------------------ main evaluation')[0], __file__, 'exec'))
tgt, kind = 'Loss_Writing', 'clf'
for lab, cols in [('M0 background', M0), ('M0 without age', [c for c in M0 if c != 'Age25'])]:
    X, y = data(core, tgt, cols)
    obs, p, nm = perm_test(kind, model(kind, 'linear', cols), X, y, B_LIN)
    print('%-16s AUC %.3f  permutation p %.3f (null mean %.3f)' % (lab, obs, p, nm), flush=True)
X, y = data(core, tgt, M0)
def one(seed):
    s = summary(kind, run_cv(kind, model(kind, 'linear', M0), X, y, splits(kind, y, R, seed)), y)
    return s['main'], s['bacc']
rs = Parallel(n_jobs=JOBS)(delayed(one)(SEED + 1000 * (i + 1)) for i in range(10))
a = np.array([r[0] for r in rs]); b = np.array([r[1] for r in rs])
print('M0 over 10 other splits: AUC %.2f (%.2f to %.2f), balanced accuracy %.2f (%.2f to %.2f)' % (a.mean(), a.min(), a.max(), b.mean(), b.min(), b.max()))
