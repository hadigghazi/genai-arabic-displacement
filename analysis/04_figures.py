# -*- coding: utf-8 -*-
"""
Figure 1: AI-attributed change in Arabic use by domain (primary sample), as diverging stacked bars
centred on the middle of "no change". Also writes the figure's data as a table.

Run with Anaconda's Python:  C:\\Users\\User\\anaconda3\\python.exe analysis\\04_figures.py
Writes analysis/results/fig1_domain_profile.pdf (for LaTeX), .png (preview) and fig1_domain_profile.csv.

Colours: a blue-red diverging pair with a neutral midpoint. Each arm was checked as an ordinal ramp
(monotone lightness, light end at least 2:1 against the page) and the two arms against each other,
including under simulated colour-vision deficiency (dataviz validate_palette.js, 2 Oct 2026).
"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'results')
d = pd.read_csv(os.path.join(HERE, 'data', 'scored.csv'))
d = d[d.core == 1]

NAMES = {'WorkStudy': 'Work or study', 'Writing': 'Messages and posts', 'Self': 'Self-talk and private notes',
         'Personal': 'Personal matters', 'Family': 'Family and friends', 'Fusha': 'Fusha (formal texts)',
         'Religion': 'Religious texts', 'Consume': 'Following content'}
LEVELS = [(-2, 'Much less', '#b73737'), (-1, 'Less', '#ef9790'), (0, 'No change', '#f0efec'),
          (1, 'More', '#86b6ef'), (2, 'Much more', '#256abf')]
INK, INK2, MUTED, GRID, BASE, SURFACE = '#0b0b0b', '#52514e', '#898781', '#e1e0d9', '#c3c2b7', '#ffffff'

rows = []
for dom, nm in NAMES.items():
    x = d['d_' + dom].dropna()
    rows.append(dict(domain=nm, n=len(x), mean=x.mean(), **{lab: 100 * (x == v).mean() for v, lab, _ in LEVELS}))
T = pd.DataFrame(rows)
T['Less, total'] = T['Much less'] + T['Less']
T = T.sort_values('Less, total', ascending=True).reset_index(drop=True)      # most loss at the top
T.round(1).to_csv(os.path.join(OUT, 'fig1_domain_profile.csv'), index=False)

plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9})
fig, ax = plt.subplots(figsize=(6.6, 3.9))
fig.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE)
y = np.arange(len(T))
h = 0.62
for i, r in T.iterrows():
    left = -(r['Much less'] + r['Less'] + r['No change'] / 2)          # centre on the middle of "no change"
    for v, lab, col in LEVELS:
        w = r[lab]
        if w <= 0:
            continue
        ax.barh(i, w, left=left, height=h, color=col, edgecolor=SURFACE, linewidth=1.5, zorder=3)
        if lab == 'No change':                                          # the neutral is pale: outline its extent
            ax.barh(i, w, left=left, height=h, fill=False, edgecolor=BASE, linewidth=0.6, zorder=4)
        left += w
    lo = -(r['Much less'] + r['Less'] + r['No change'] / 2)
    hi = r['More'] + r['Much more'] + r['No change'] / 2
    ax.text(lo - 1.5, i, '%.0f%%' % r['Less, total'], ha='right', va='center', color=INK2, fontsize=8)
    if r['More'] + r['Much more'] > 0:
        ax.text(hi + 1.5, i, '%.0f%%' % (r['More'] + r['Much more']), ha='left', va='center', color=MUTED, fontsize=8)

ax.set_yticks(y)
ax.set_yticklabels(['%s  (n = %d)' % (r.domain, r.n) for r in T.itertuples()], color=INK)
ax.axvline(0, color=BASE, linewidth=0.8, zorder=2)
ax.set_xlim(-100, 60)
ticks = np.arange(-100, 51, 25)
ax.set_xticks(ticks)
ax.set_xticklabels(['%d%%' % abs(t) for t in ticks], color=MUTED)
ax.xaxis.grid(True, color=GRID, linewidth=0.5, zorder=0)
ax.tick_params(axis='both', length=0)
for s in ax.spines.values():
    s.set_visible(False)
ax.set_xlabel('% of respondents  (left of centre: less Arabic because of AI;  right: more)', color=INK2, fontsize=8.5)
handles = [plt.Rectangle((0, 0), 1, 1, facecolor=c, edgecolor=BASE if l == 'No change' else c, linewidth=0.6) for _, l, c in LEVELS]
ax.legend(handles, [l for _, l, _ in LEVELS], loc='lower left', bbox_to_anchor=(0.0, 1.0), ncol=5, frameon=False,
          fontsize=8.5, handlelength=1.2, columnspacing=1.1, borderaxespad=0.2)
ax.set_title('Because of AI, do you now use Arabic less or more?', loc='left', color=INK, fontsize=10, pad=24)
fig.tight_layout()
for ext in ('pdf', 'png'):
    fig.savefig(os.path.join(OUT, 'fig1_domain_profile.' + ext), dpi=220, facecolor=SURFACE, bbox_inches='tight', pad_inches=0.05)
print(T.round(1).to_string(index=False))
print('wrote', os.path.join(OUT, 'fig1_domain_profile.pdf'))

# ---------------------------------------------------------------- column-width version for the IEEE two-column paper
# 3.5 in wide, 8 pt Times New Roman labels (IEEE guidance), no in-figure title (the caption carries it).
plt.rcParams.update({'font.family': 'Times New Roman', 'font.size': 8})
fig, ax = plt.subplots(figsize=(3.5, 2.55))
fig.patch.set_facecolor(SURFACE); ax.set_facecolor(SURFACE)
SHORT = {'Work or study': 'Work or study', 'Messages and posts': 'Messages, posts', 'Following content': 'Following content',
         'Fusha (formal texts)': 'Fusha (formal texts)', 'Self-talk and private notes': 'Self-talk, own notes',
         'Personal matters': 'Personal matters', 'Family and friends': 'Family, friends', 'Religious texts': 'Religious texts'}
for i, r in T.iterrows():
    left = -(r['Much less'] + r['Less'] + r['No change'] / 2)
    for v, lab, col in LEVELS:
        w = r[lab]
        if w <= 0:
            continue
        ax.barh(i, w, left=left, height=h, color=col, edgecolor=SURFACE, linewidth=0.8, zorder=3)
        if lab == 'No change':
            ax.barh(i, w, left=left, height=h, fill=False, edgecolor=BASE, linewidth=0.4, zorder=4)
        left += w
    lo = -(r['Much less'] + r['Less'] + r['No change'] / 2)
    hi = r['More'] + r['Much more'] + r['No change'] / 2
    ax.text(lo - 1.5, i, '%.0f%%' % r['Less, total'], ha='right', va='center', color=INK2, fontsize=7)
    if r['More'] + r['Much more'] > 0:
        ax.text(hi + 1.5, i, '%.0f%%' % (r['More'] + r['Much more']), ha='left', va='center', color=MUTED, fontsize=7)
ax.set_yticks(y)
ax.set_yticklabels(['%s (%d)' % (SHORT[r.domain], r.n) for r in T.itertuples()], color=INK)
ax.axvline(0, color=BASE, linewidth=0.6, zorder=2)
ax.set_xlim(-100, 60)
ax.set_xticks(ticks)
ax.set_xticklabels(['%d%%' % abs(t) for t in ticks], color=MUTED)
ax.xaxis.grid(True, color=GRID, linewidth=0.4, zorder=0)
ax.tick_params(axis='both', length=0, pad=2)
for s in ax.spines.values():
    s.set_visible(False)
ax.set_xlabel('Respondents (%), less Arabic (left) or more (right)', color=INK2, fontsize=8)
handles = [plt.Rectangle((0, 0), 1, 1, facecolor=c, edgecolor=BASE if l == 'No change' else c, linewidth=0.4) for _, l, c in LEVELS]
ax.legend(handles, [l for _, l, _ in LEVELS], loc='lower left', bbox_to_anchor=(-0.02, 1.0), ncol=5, frameon=False,
          fontsize=7, handlelength=1.0, handletextpad=0.4, columnspacing=0.8, borderaxespad=0.1)
fig.tight_layout(pad=0.2)
for ext in ('pdf', 'png'):
    fig.savefig(os.path.join(OUT, 'fig1_domain_profile_column.' + ext), dpi=300, facecolor=SURFACE, bbox_inches='tight', pad_inches=0.02)
print('wrote', os.path.join(OUT, 'fig1_domain_profile_column.pdf'))
