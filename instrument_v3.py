# -*- coding: utf-8 -*-
"""
Single source of truth for the v3 questionnaire.
Run:  python instrument_v3.py
Writes: instrument-v3.md (codebook), instrument-v3.json (for the docx), build-form-v3.gs (Apps Script)
"""
import json, io, os

HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------------ scales
from instrument_data import S, T, SECTIONS  # all wording lives in instrument_data.py

FORM = {
 'title': 'AI tools and everyday language use  |  أدوات الذكاء الاصطناعي واستخدام اللغة في الحياة اليومية',
 'desc': 'About 7 minutes. Anonymous. Choose your language to begin.\nنحو 7 دقائق. مجهول الهوية. اختر لغتك للبدء.',
 'confirm': 'Thank you for your time.  |  شكراً على وقتك.',
 'picker': 'Please choose your language  |  يرجى اختيار لغتك',
}


def resolve(txt, lang):
    if txt is None: return ''
    if isinstance(txt, str): return T[txt][lang] if txt in T else txt
    return txt[lang]


def opts(it, lang):
    if it.get('scale') in S:
        return S[it['scale']][lang]
    if it.get('scale') == 'change_plus_none':
        return S['change'][lang] + [it['extra_opt'][lang]]
    o = it.get('o')
    if isinstance(o, str) and o.startswith('same:'):
        src = o.split(':')[1]
        for sec in SECTIONS:
            for x in sec['items']:
                if x.get('code') == src: return x['o'][lang]
    return o[lang] if o else []


def helptext(it, lang):
    h = it.get('help')
    parts = []
    if it.get('help_pre'): parts.append(it['help_pre'][lang])
    if h == 'reminder_def': parts += [T['arabic_def'][lang], T['reminder'][lang]]
    elif isinstance(h, str) and h in T: parts.append(T[h][lang])
    elif isinstance(h, dict): parts.append(h[lang])
    return '\n\n'.join(parts)


def export_json():
    out = []
    for sec in SECTIONS:
        s = {'id': sec['id'], 'title_en': sec['title']['en'], 'title_ar': sec['title']['ar'], 'items': []}
        for it in sec['items']:
            d = {'code': it.get('code'), 'type': it['type'], 'role': it.get('role', ''),
                 'q_en': resolve(it.get('q'), 'en'), 'q_ar': resolve(it.get('q'), 'ar'),
                 'help_en': helptext(it, 'en'), 'help_ar': helptext(it, 'ar'),
                 'opts_en': opts(it, 'en') if it['type'] not in ('gate', 'text', 'para') else
                    ([it['yes']['en'], it['no']['en']] if it['type'] == 'gate' else []),
                 'opts_ar': opts(it, 'ar') if it['type'] not in ('gate', 'text', 'para') else
                    ([it['yes']['ar'], it['no']['ar']] if it['type'] == 'gate' else []),
                 'rows': [{'code': r[0], 'en': r[1], 'ar': r[2], 'variety': r[3] if len(r) > 3 else ''} for r in it.get('rows', [])]}
            s['items'].append(d)
        out.append(s)
    io.open(os.path.join(HERE, 'instrument-v3.json'), 'w', encoding='utf-8').write(json.dumps(out, ensure_ascii=False, indent=1))
    return out


def count(data):
    g = sum(len(i['rows']) for s in data for i in s['items'] if i['type'] == 'grid')
    q = sum(1 for s in data for i in s['items'] if i['type'] in ('mc', 'mc_route', 'check', 'gate'))
    return g, q


def export_md(data):
    g, q = count(data)
    L = ['# Instrument v3 — codebook (generated from instrument_v3.py; edit the .py, not this file)', '',
         f'Grid rows: **{g}**. Single/multiple-choice questions: **{q}**. Advertised length: about 7 minutes (confirm in pilot).', '',
         'Change scale (all change grids): ' + ' · '.join(S['change']['en']) + ' → coded −2 … +2, 0 = No change.', '',
         'Variety tags: L = spoken dialect, H = Fusha, M = mixed/any, R = reverse-coded, − = not language-specific.', '']
    for s in data:
        L.append(f"## Section `{s['id']}` — {s['title_en']}  /  {s['title_ar']}")
        L.append('')
        for i in s['items']:
            if i['type'] == 'text':
                L.append('**[Text]** ' + i['help_en'].replace('\n', ' '))
                L.append('')
                L.append('**[نص]** ' + i['help_ar'].replace('\n', ' '))
                L.append('')
                continue
            L.append(f"**{i['code']}** ({i['type']}; role: {i['role']})")
            L.append('')
            L.append(f"- EN: {i['q_en']}".replace('\n', ' '))
            L.append(f"- AR: {i['q_ar']}".replace('\n', ' '))
            if i['help_en']:
                L.append(f"- Help (EN): {i['help_en']}".replace('\n', ' '))
            if i['rows']:
                L.append('')
                L.append('| Code | Var. | English | العربية |')
                L.append('|---|---|---|---|')
                for r in i['rows']:
                    L.append(f"| {r['code']} | {r['variety']} | {r['en']} | {r['ar']} |")
            if i['opts_en']:
                L.append(f"- Options (EN): {' / '.join(i['opts_en'])}")
                L.append(f"- Options (AR): {' / '.join(i['opts_ar'])}")
            L.append('')
    io.open(os.path.join(HERE, 'instrument-v3.md'), 'w', encoding='utf-8').write('\n'.join(L))
    return g, q


GS = r'''/**
 * build-form-v3.gs  —  GENERATED by instrument_v3.py. Do not edit by hand; edit the .py and regenerate.
 *
 * Builds ONE Google Form with a language picker routing to an English or an Arabic chain.
 * HOW TO RUN: script.google.com -> New project -> paste -> Run buildForm -> approve -> read Execution log.
 *
 * AFTER BUILDING, BY HAND:
 *   1. Settings: Collect email OFF; Limit to 1 response OFF; Allow response editing OFF;
 *      "Restrict to users in <organisation>" OFF.
 *   2. Optional: Shuffle row order inside grids only.
 *   3. TEST on a phone: consent "No" -> form ends; eligibility "No" -> form ends; 7 pages in total;
 *      every grid shows 5 columns without sideways scrolling; last page -> submits.
 *   4. Pilot in a COPY of the form (File -> Make a copy). Never pilot in the live form.
 */

var DATA = __DATA__;
var FORM = __FORM__;

function codeMap_(lang, code, title, i) { Logger.log(['MAP', lang, code, i, title].join(' | ')); }

function chain_(form, lang, skipFirstBreak) {
  var pb = {};        // section id -> PageBreakItem
  var routes = [];    // deferred routing
  var first = null;
  DATA.forEach(function (sec) {
    if (skipFirstBreak && !first) { first = 'page1'; }
    else { var p = form.addPageBreakItem().setTitle(sec['title_' + lang]); pb[sec.id] = p; if (!first) first = p; }
    sec.items.forEach(function (it) {
      var q = it['q_' + lang], h = it['help_' + lang], o = it['opts_' + lang];
      if (it.type === 'text') {
        form.addSectionHeaderItem().setTitle(q || (lang === 'ar' ? 'تعليمات' : 'Instructions')).setHelpText(h);
      } else if (it.type === 'gate') {
        var g = form.addMultipleChoiceItem().setTitle(q).setRequired(true);
        if (h) g.setHelpText(h);
        g.setChoices([g.createChoice(o[0], FormApp.PageNavigationType.CONTINUE),
                      g.createChoice(o[1], FormApp.PageNavigationType.SUBMIT)]);
        codeMap_(lang, it.code, q, 0);
      } else if (it.type === 'mc') {
        var m = form.addMultipleChoiceItem().setTitle(q).setChoiceValues(o).setRequired(true);
        if (h) m.setHelpText(h);
        codeMap_(lang, it.code, q, 0);
      } else if (it.type === 'mc_route') {
        var r = form.addMultipleChoiceItem().setTitle(q).setRequired(true);
        if (h) r.setHelpText(h);
        routes.push({ item: r, it: it, opts: o });
        codeMap_(lang, it.code, q, 0);
      } else if (it.type === 'check') {
        var c = form.addCheckboxItem().setTitle(q).setChoiceValues(o).setRequired(true);
        if (h) c.setHelpText(h);
        codeMap_(lang, it.code, q, 0);
      } else if (it.type === 'grid') {
        var gr = form.addGridItem().setTitle(q)
          .setRows(it.rows.map(function (x) { return x[lang]; })).setColumns(o).setRequired(true);
        if (h) gr.setHelpText(h);
        it.rows.forEach(function (x, i) { codeMap_(lang, x.code, x[lang], i); });
      } else if (it.type === 'para') {
        var pa = form.addParagraphTextItem().setTitle(q).setRequired(false);
        if (h) pa.setHelpText(h);
        codeMap_(lang, it.code, q, 0);
      }
    });
  });
  // wire routing now that every section exists
  var ROUTE_TARGET = { 'A': 'A', 'extra': 'extra', 'WS': 'WS', 'SW': 'SW', 'REG': 'REG', 'D': 'D' };
  routes.forEach(function (rt) {
    var ok = rt.it.route.correct_index, choices = [];
    rt.opts.forEach(function (txt, i) {
      var target = ok.indexOf(i) >= 0 ? rt.it.route.correct_to : rt.it.route.else_to;
      choices.push(rt.item.createChoice(txt, pb[ROUTE_TARGET[target]]));
    });
    rt.item.setChoices(choices);
  });
  return first;
}

function buildForm() {
  var form = FormApp.create(FORM.title);
  form.setTitle(FORM.title).setDescription(FORM.desc)
      .setCollectEmail(false).setLimitOneResponsePerUser(false)
      .setProgressBar(true).setAllowResponseEdits(false)
      .setConfirmationMessage(FORM.confirm);
  var picker = form.addMultipleChoiceItem().setTitle(FORM.picker).setRequired(true);
  var enFirst = chain_(form, 'en');
  var arFirst = chain_(form, 'ar');
  picker.setChoices([picker.createChoice('English', enFirst), picker.createChoice('العربية', arFirst)]);
  // The last page of the English chain must end the form rather than fall into the Arabic chain.
  // PageBreakItem.setGoToPage sets where to go after the page BEFORE this break.
  arFirst.setGoToPage(FormApp.PageNavigationType.SUBMIT);
  Logger.log('EDIT URL : ' + form.getEditUrl());
  Logger.log('LIVE URL : ' + form.getPublishedUrl());
}
'''


GS_AR_MAIN = r'''
function buildFormArabic() {
  var form = FormApp.create(FORM_AR.title);
  form.setTitle(FORM_AR.title).setDescription(FORM_AR.desc)
      .setCollectEmail(false).setLimitOneResponsePerUser(false)
      .setProgressBar(true).setAllowResponseEdits(false)
      .setConfirmationMessage(FORM_AR.confirm);
  chain_(form, 'ar', true);   // consent sits on page 1; every later section gets its own page
  Logger.log('EDIT URL : ' + form.getEditUrl());
  Logger.log('LIVE URL : ' + form.getPublishedUrl());
}
'''
FORM_AR = {'title': 'أدوات الذكاء الاصطناعي واستخدام اللغة في الحياة اليومية',
           'desc': 'استبيان مجهول الهوية يستغرق نحو 7 دقائق، ضمن مشروع بحثي في الجامعة اللبنانية.',
           'confirm': 'شكراً على وقتك.'}

def export_gs(data):
    # compact data for Apps Script (rows as objects with en/ar)
    js = []
    for s in data:
        items = []
        for i in s['items']:
            src = next(it for sec in SECTIONS if sec['id'] == s['id'] for it in sec['items'] if it.get('code') == i['code'] and it['type'] == i['type'])
            items.append({'code': i['code'], 'type': i['type'],
                          'q_en': i['q_en'], 'q_ar': i['q_ar'], 'help_en': i['help_en'], 'help_ar': i['help_ar'],
                          'opts_en': i['opts_en'], 'opts_ar': i['opts_ar'],
                          'rows': [{'code': r['code'], 'en': r['en'], 'ar': r['ar']} for r in i['rows']],
                          'route': src.get('route')})
        js.append({'id': s['id'], 'title_en': s['title_en'], 'title_ar': s['title_ar'], 'items': items})
    code = GS.replace('__DATA__', json.dumps(js, ensure_ascii=False, indent=1)).replace('__FORM__', json.dumps(FORM, ensure_ascii=False))
    io.open(os.path.join(HERE, 'build-form-v3.gs'), 'w', encoding='utf-8').write(code)
    main_start = code.index('function buildForm()')
    ar = code[:main_start].replace('build-form-v3.gs  —  GENERATED', 'build-form-v3-ar.gs  —  ARABIC-ONLY, GENERATED')
    ar = ar.replace('var FORM = ', 'var FORM_AR = ' + json.dumps(FORM_AR, ensure_ascii=False) + ';' + chr(10) + 'var FORM = ')
    ar = ar.replace('Run buildForm', 'Run buildFormArabic').replace(' * Builds ONE Google Form with a language picker routing to an English or an Arabic chain.', ' * Builds the Arabic-only Google Form (no language picker).').replace('   2. Replace the [University] / [Researcher name] / [Supervisor name] / [emails] placeholders in the consent text.' + chr(10), '')
    io.open(os.path.join(HERE, 'build-form-v3-ar.gs'), 'w', encoding='utf-8').write(ar + GS_AR_MAIN)


if __name__ == '__main__':
    d = export_json()
    g, q = export_md(d)
    export_gs(d)
    print(f'grid rows={g}  choice questions={q}  -> instrument-v3.md, instrument-v3.json, build-form-v3.gs')
