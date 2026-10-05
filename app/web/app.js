// Renders the form from /api/model, posts answers to /api/predict and shows the three models' results.
// Everything is driven by `state`, so switching language re-renders without losing answers.
(function () {
  'use strict';

  var T = {
    en: {
      brand: 'Generative AI and Arabic',
      switchTo: 'العربية',
      title: 'Is AI reducing your Arabic?',
      lead: 'A research model built from a survey of 105 Lebanese Arabic–English bilinguals. Answer 12 questions about yourself and how you use AI tools, and see whether people with answers like yours tended to report using less Arabic because of AI.',
      privacy: 'Your answers are scored on the spot and are not stored.',
      tickAll: 'Tick all that apply',
      submit: 'See the results',
      missing: 'Please answer every question marked with a dot.',
      failed: 'The model could not be reached. Please try again.',
      results: 'Results',
      resultsLead: 'Each bar places you between people who did not report the decrease and people who did. The score orders people; it is not a percentage chance.',
      likely: 'Likely to report this',
      unlikely: 'Unlikely to report this',
      lower: 'did not report it',
      higher: 'reported it',
      moved: 'What moved your score most',
      raises: 'raises',
      lowers: 'lowers',
      tested: function (m) {
        return 'Tested on people it was not trained on, this model ranked someone who reported the decrease above someone who did not ' +
          pct(m.cv.auc) + ' of the time, and classified ' + pct(m.cv.balanced_accuracy) + ' correctly (balanced).';
      },
      sample: function (m) { return m.n_yes + ' of ' + (m.n_yes + m.n_no) + ' respondents reported this decrease.'; },
      aboutTitle: 'About the model',
      about: [
        'Data: an anonymous Arabic online survey of 105 Lebanese Arabic–English bilinguals who use AI regularly, collected from 30 September to 4 October 2026.',
        'Model: one logistic regression per outcome, on 12 answers about background and AI use, fitted on all respondents.',
        'Testing: repeated 10×5-fold cross-validation and permutation tests. Each model passed four criteria fixed in advance: better than chance after correction for many tests, stable across random splits (AUC at least 0.70), still above chance without the age question, and balanced accuracy of at least 0.65.',
        'What it predicts: what people report, not how their Arabic actually changed.',
        'Answers about AI use did not make the models significantly more accurate than background answers alone.',
        'The models were validated within this sample only and have not yet been tested on new people.'
      ],
      footer: 'From the study “Is Generative AI Displacing Arabic? Perceived Change in Arabic Use Among Lebanese Arabic–English Bilinguals”, Hadi Ghazi, Lebanese University.'
    },
    ar: {
      brand: 'الذكاء الاصطناعي واللغة العربية',
      switchTo: 'English',
      title: 'هل يقلّل الذكاء الاصطناعي من استخدامك للعربية؟',
      lead: 'نموذج بحثي مبني على استبيان شمل 105 من ثنائيي اللغة العربية والإنجليزية في لبنان. أجب عن 12 سؤالاً عنك وعن استخدامك لأدوات الذكاء الاصطناعي، لترى إن كان من تشبه إجاباتُهم إجاباتِك قد أفادوا بأنهم صاروا يستخدمون العربية أقل بسبب الذكاء الاصطناعي.',
      privacy: 'تُحسب النتيجة فوراً ولا تُحفظ إجاباتك.',
      tickAll: 'اختر كل ما ينطبق',
      submit: 'اعرض النتائج',
      missing: 'يرجى الإجابة عن كل سؤال عليه نقطة.',
      failed: 'تعذّر الوصول إلى النموذج. يرجى المحاولة مرة أخرى.',
      results: 'النتائج',
      resultsLead: 'يضعك كل شريط بين من لم يُفيدوا بهذا التراجع ومن أفادوا به. النتيجة ترتّب الأشخاص، وليست نسبة احتمال.',
      likely: 'يُرجَّح أن تُفيد بهذا',
      unlikely: 'لا يُرجَّح أن تُفيد بهذا',
      lower: 'لم يُفيدوا به',
      higher: 'أفادوا به',
      moved: 'أكثر ما أثّر في نتيجتك',
      raises: 'يرفع',
      lowers: 'يخفض',
      tested: function (m) {
        return 'عند اختباره على أشخاص لم يُدرَّب عليهم، رتّب النموذج من أفاد بالتراجع فوق من لم يُفد به في ' +
          pct(m.cv.auc) + ' من الحالات، وصنّف ' + pct(m.cv.balanced_accuracy) + ' تصنيفاً صحيحاً (دقة متوازنة).';
      },
      sample: function (m) { return 'أفاد ' + m.n_yes + ' من أصل ' + (m.n_yes + m.n_no) + ' مشاركاً بهذا التراجع.'; },
      aboutTitle: 'عن النموذج',
      about: [
        'البيانات: استبيان إلكتروني مجهول الهوية باللغة العربية شمل 105 من ثنائيي اللغة العربية والإنجليزية في لبنان ممن يستخدمون الذكاء الاصطناعي بانتظام، جُمع بين 30 أيلول و4 تشرين الأول 2026.',
        'النموذج: انحدار لوجستي لكل نتيجة، يعتمد على 12 إجابة عن الخلفية واستخدام الذكاء الاصطناعي، ومدرَّب على جميع المشاركين.',
        'الاختبار: تحقق متقاطع متكرر (10×5) واختبارات التبديل. اجتاز كل نموذج أربعة معايير حُدّدت مسبقاً: أفضل من الصدفة بعد تصحيح تعدد الاختبارات، وثابت عبر تقسيمات عشوائية مختلفة (AUC لا يقل عن 0.70)، ويبقى أفضل من الصدفة من دون سؤال العمر، ودقة متوازنة لا تقل عن 0.65.',
        'ما الذي يتنبأ به: ما يُفيد به الأشخاص، لا التغيّر الفعلي في عربيتهم.',
        'لم تجعل الإجاباتُ عن استخدام الذكاء الاصطناعي النماذجَ أدق بشكل ملحوظ من الإجابات عن الخلفية وحدها.',
        'جرى التحقق من النماذج ضمن هذه العيّنة فقط، ولم تُختبر بعد على أشخاص جدد.'
      ],
      footer: 'من دراسة «هل يُزيح الذكاء الاصطناعي التوليدي اللغة العربية؟ التغيّر المُدرَك في استخدام العربية لدى ثنائيي اللغة العربية والإنجليزية في لبنان»، هادي غازي، الجامعة اللبنانية.'
    }
  };

  var NONE_OF_THESE = { Events: 6 };   // ticking "None of these" clears the other events, and vice versa

  var state = { lang: initialLang(), answers: {}, card: null, result: null, error: '' };

  function pct(x) { return Math.round(x * 100) + '%'; }
  function $(id) { return document.getElementById(id); }
  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined) e.textContent = text;
    return e;
  }
  function initialLang() {
    try { var s = localStorage.getItem('lang'); if (s === 'en' || s === 'ar') return s; } catch (e) { /* storage blocked */ }
    return (navigator.language || '').toLowerCase().indexOf('ar') === 0 ? 'ar' : 'en';
  }

  // ------------------------------------------------------------------ rendering
  function render() {
    var t = T[state.lang];
    document.documentElement.lang = state.lang;
    document.documentElement.dir = state.lang === 'ar' ? 'rtl' : 'ltr';
    document.title = t.title;
    $('brand').textContent = t.brand;
    $('lang').textContent = t.switchTo;
    $('title').textContent = t.title;
    $('lead').textContent = t.lead;
    $('privacy').textContent = t.privacy;
    $('submit').textContent = t.submit;
    $('footer').textContent = t.footer;
    if (!state.card) return;
    renderQuestions();
    renderError();
    renderResults();
    renderAbout();
  }

  function renderQuestions() {
    var box = $('questions');
    box.textContent = '';
    state.card.questions.forEach(function (q, i) {
      var fs = el('fieldset', 'q');
      fs.id = 'q-' + q.code;
      var lg = el('legend');
      lg.appendChild(el('span', 'num', String(i + 1)));
      lg.appendChild(el('span', 'qtext', q.q[state.lang]));
      if (q.type === 'single') lg.appendChild(el('span', 'req', '•'));
      fs.appendChild(lg);
      var opts = el('div', 'opts');
      q.options.forEach(function (o) {
        var id = q.code + '-' + o.code;
        var input = el('input');
        input.type = q.type === 'check' ? 'checkbox' : 'radio';
        input.name = q.code;
        input.id = id;
        input.value = o.code;
        input.checked = q.type === 'check' ? (state.answers[q.code] || []).indexOf(o.code) >= 0 : state.answers[q.code] === o.code;
        input.addEventListener('change', function () { onChange(q, o.code, input.checked); });
        var label = el('label', 'opt');
        label.htmlFor = id;
        label.appendChild(input);
        label.appendChild(el('span', '', o[state.lang]));
        opts.appendChild(label);
      });
      fs.appendChild(opts);
      box.appendChild(fs);
    });
  }

  function onChange(q, code, checked) {
    if (q.type === 'single') {
      state.answers[q.code] = code;
    } else {
      var list = (state.answers[q.code] || []).filter(function (c) { return c !== code; });
      if (checked) {
        var none = NONE_OF_THESE[q.code];
        if (none !== undefined) list = code === none ? [] : list.filter(function (c) { return c !== none; });
        list.push(code);
      }
      state.answers[q.code] = list;
      if (NONE_OF_THESE[q.code] !== undefined) renderQuestions();
    }
    var fs = $('q-' + q.code);
    if (fs) fs.classList.remove('missing');
  }

  function renderError() {
    var p = $('formError');
    p.hidden = !state.error;
    p.textContent = state.error ? T[state.lang][state.error] : '';
  }

  function featureText(name) { return state.card.feature_text[name][state.lang]; }

  function renderResults() {
    var box = $('results');
    box.textContent = '';
    if (!state.result) { box.hidden = true; return; }
    var t = T[state.lang];
    box.hidden = false;
    box.appendChild(el('h2', '', t.results));
    box.appendChild(el('p', 'lead small', t.resultsLead));
    var byId = {};
    state.card.models.forEach(function (m) { byId[m.id] = m; });
    state.result.results.forEach(function (r) {
      var m = byId[r.id];
      var card = el('article', 'card' + (r.likely ? ' is-likely' : ''));
      var head = el('div', 'card-head');
      head.appendChild(el('h3', '', r.label[state.lang]));
      head.appendChild(el('span', 'badge', r.likely ? t.likely : t.unlikely));
      card.appendChild(head);

      var meter = el('div', 'meter');
      var track = el('div', 'track');
      var mark = el('div', 'mark');
      mark.style.insetInlineStart = (r.score * 100).toFixed(1) + '%';
      track.appendChild(el('div', 'mid'));
      track.appendChild(mark);
      meter.appendChild(track);
      var ends = el('div', 'ends');
      ends.appendChild(el('span', '', t.lower));
      ends.appendChild(el('span', '', t.higher));
      meter.appendChild(ends);
      card.appendChild(meter);

      card.appendChild(el('p', 'sub', t.moved));
      var ul = el('ul', 'moves');
      r.contributions.slice(0, 3).forEach(function (c) {
        var li = el('li', c.contribution >= 0 ? 'up' : 'down');
        li.appendChild(el('span', 'arrow', c.contribution >= 0 ? '▲' : '▼'));
        li.appendChild(el('span', '', featureText(c.feature)));
        li.appendChild(el('span', 'dir', c.contribution >= 0 ? t.raises : t.lowers));
        ul.appendChild(li);
      });
      card.appendChild(ul);
      card.appendChild(el('p', 'fine', t.tested(m) + ' ' + t.sample(m)));
      box.appendChild(card);
    });
  }

  function renderAbout() {
    var t = T[state.lang];
    var box = $('about');
    box.textContent = '';
    box.appendChild(el('h2', '', t.aboutTitle));
    var ul = el('ul');
    t.about.forEach(function (s) { ul.appendChild(el('li', '', s)); });
    box.appendChild(ul);
  }

  // ------------------------------------------------------------------ actions
  function submit(ev) {
    ev.preventDefault();
    var firstMissing = null;
    state.card.questions.forEach(function (q) {
      var fs = $('q-' + q.code);
      var ok = q.type === 'check' || state.answers[q.code] !== undefined;
      fs.classList.toggle('missing', !ok);
      if (!ok && !firstMissing) firstMissing = fs;
    });
    if (firstMissing) {
      state.error = 'missing';
      renderError();
      firstMissing.scrollIntoView({ behavior: 'smooth', block: 'center' });
      return;
    }
    var body = {};
    state.card.questions.forEach(function (q) { body[q.code] = q.type === 'check' ? (state.answers[q.code] || []) : state.answers[q.code]; });
    $('submit').disabled = true;
    fetch('api/predict', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (res) {
        state.result = res;
        state.error = '';
        renderError();
        renderResults();
        $('results').scrollIntoView({ behavior: 'smooth', block: 'start' });
      })
      .catch(function () { state.error = 'failed'; renderError(); })
      .then(function () { $('submit').disabled = false; });
  }

  $('lang').addEventListener('click', function () {
    state.lang = state.lang === 'ar' ? 'en' : 'ar';
    try { localStorage.setItem('lang', state.lang); } catch (e) { /* storage blocked */ }
    render();
  });
  $('form').addEventListener('submit', submit);

  render();
  fetch('api/model')
    .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
    .then(function (card) { state.card = card; render(); })
    .catch(function () { $('loading').textContent = T[state.lang].failed; });
})();
