# Instrument v3 — codebook (generated from instrument_v3.py; edit the .py, not this file)

Grid rows: **33**. Single/multiple-choice questions: **25**. Advertised length: about 7 minutes (confirm in pilot).

Change scale (all change grids): Much less · Less · No change · More · Much more → coded −2 … +2, 0 = No change.

Variety tags: L = spoken dialect, H = Fusha, M = mixed/any, R = reverse-coded, − = not language-specific.

## Section `consent` — About this survey  /  عن هذا الاستبيان

**[Text]** This survey is part of a master's research project at the Lebanese University and takes about 7 minutes. Taking part is voluntary and anonymous: no names or contact details are collected, so a response cannot be withdrawn once submitted. Answers are used for research only and reported as group results.

**[نص]** هذا الاستبيان جزء من مشروع بحثي لدرجة الماجستير في الجامعة اللبنانية، ويستغرق نحو 7 دقائق. المشاركة طوعية ومجهولة الهوية: لا نجمع أي أسماء أو بيانات اتصال، لذلك لا يمكن سحب الإجابة بعد إرسالها. تُستخدم الإجابات لأغراض بحثية فقط، وتُعرض النتائج بشكل إجمالي.

**Consent** (gate; role: screen)

- EN: I am 18 or older and I agree to take part.
- AR: عمري 18 عاماً أو أكثر، وأوافق على المشاركة.
- Options (EN): I agree / I do not agree
- Options (AR): أوافق / لا أوافق

## Section `elig` — Who can take part  /  من يمكنه المشاركة

**Eligible** (gate; role: screen)

- EN: Do ALL of these apply to you? • Arabic is your first language • You also use English for study or work • You have used AI tools (such as ChatGPT, Gemini or Claude) at least weekly for 6 months or more
- AR: هل تنطبق عليك كل ما يلي؟ • العربية لغتك الأولى • تستخدم الإنجليزية أيضاً في الدراسة أو العمل • تستخدم أدوات الذكاء الاصطناعي (مثل شات جي بي تي أو جيميني أو كلود) مرة أسبوعياً على الأقل منذ ستة أشهر أو أكثر
- Options (EN): Yes / No
- Options (AR): نعم / لا

## Section `you` — About you  /  معلومات عنك

**Role** (mc; role: descriptive)

- EN: You are currently…
- AR: أنت حالياً…
- Options (EN): A student / Employed / Both / Neither
- Options (AR): طالب / موظف / طالب وموظف / غير ذلك

**Education** (mc; role: covariate (sensitivity) / ML)

- EN: Education level (completed or in progress)
- AR: المستوى التعليمي (مكتمل أو قيد الدراسة)
- Options (EN): Secondary / Bachelor's / Master's or higher
- Options (AR): ثانوي / بكالوريوس / ماجستير أو أعلى

**Field** (mc; role: covariate (computing vs other) / ML)

- EN: Field of study or work
- AR: مجال الدراسة أو العمل
- Options (EN): Computing / IT / Engineering / Sciences or health / Business / Humanities, education or law / Other
- Options (AR): الحوسبة / تقنية المعلومات / الهندسة / العلوم أو الصحة / إدارة الأعمال / العلوم الإنسانية أو التربية أو القانون / غير ذلك

**Age** (mc; role: covariate / ML)

- EN: Age
- AR: العمر
- Options (EN): Under 25 / 25 to 34 / 35 to 44 / 45 or over
- Options (AR): أقل من 25 / من 25 إلى 34 / من 35 إلى 44 / 45 فأكثر

**Gender** (mc; role: descriptive)

- EN: Gender
- AR: الجنس
- Options (EN): Female / Male / Prefer not to say
- Options (AR): أنثى / ذكر / أفضّل عدم الإجابة

**Country_GrewUp** (mc; role: CORE sample rule)

- EN: Where did you grow up?
- AR: أين نشأت؟
- Options (EN): Lebanon / Syria, Jordan or Palestine / The Gulf / Egypt or North Africa / Another Arab country / Outside the Arab world
- Options (AR): لبنان / سوريا أو الأردن أو فلسطين / الخليج / مصر أو شمال أفريقيا / بلد عربي آخر / خارج العالم العربي

**Country_Now** (mc; role: CORE sample rule)

- EN: Where do you live now?
- AR: أين تعيش الآن؟
- Options (EN): Lebanon / Syria, Jordan or Palestine / The Gulf / Egypt or North Africa / Another Arab country / Outside the Arab world
- Options (AR): لبنان / سوريا أو الأردن أو فلسطين / الخليج / مصر أو شمال أفريقيا / بلد عربي آخر / خارج العالم العربي

**Moved_Since2022** (mc; role: CORE sample rule)

- EN: Have you moved to another country since 2022?
- AR: هل انتقلت للعيش في بلد آخر منذ عام 2022؟
- Options (EN): Yes / No
- Options (AR): نعم / لا

## Section `ai` — Your use of AI tools  /  استخدامك لأدوات الذكاء الاصطناعي

**AI_Start** (mc; role: tenure covariate)

- EN: When did you start using AI tools regularly (at least weekly)?
- AR: متى بدأت باستخدام أدوات الذكاء الاصطناعي بانتظام (مرة أسبوعياً على الأقل)؟
- Options (EN): 2022 or earlier / 2023 / 2024 / 2025 / 2026
- Options (AR): 2022 أو قبل ذلك / 2023 / 2024 / 2025 / 2026

**AI_Freq** (mc; role: descriptive / X check)

- EN: How often do you use AI tools?
- AR: كم مرة تستخدم أدوات الذكاء الاصطناعي؟
- Options (EN): Once a week / A few days a week / Once a day / Several times a day
- Options (AR): مرة في الأسبوع / بضعة أيام في الأسبوع / مرة في اليوم / عدة مرات في اليوم

**AI_TaskShare** (mc; role: X (AI intensity component))

- EN: How much of your work or study do you do with the help of AI?
- AR: كم من عملك أو دراستك تنجزه بمساعدة الذكاء الاصطناعي؟
- Options (EN): Very little / Some / About half / Most / Almost all
- Options (AR): القليل جداً / بعضه / نحو النصف / معظمه / كله تقريباً

**AI_Breadth** (check; role: X (AI intensity component: count of ticks))

- EN: What do you use AI for? (tick all that apply)
- AR: فيمَ تستخدم الذكاء الاصطناعي؟ (اختر كل ما ينطبق)
- Options (EN): Writing or editing / Coding / Searching for information / Translation / Studying / Emails and messages / Ideas / Personal advice
- Options (AR): الكتابة أو التحرير / البرمجة / البحث عن معلومات / الترجمة / الدراسة / البريد والرسائل / توليد الأفكار / نصائح شخصية

**AI_Lang** (mc; role: X (language routed through AI))

- EN: In which language do you usually write to AI?
- AR: بأي لغة تكتب للذكاء الاصطناعي عادةً؟
- Options (EN): Always Arabic / Mostly Arabic / Both equally / Mostly English / Always English / Another language
- Options (AR): العربية دائماً / العربية غالباً / الاثنتان بالتساوي / الإنجليزية غالباً / الإنجليزية دائماً / لغة أخرى

**AI_Content** (mc; role: X (exposure channel: recognised AI-generated content))

- EN: How often do you come across AI-generated content (videos, voice-overs, summaries in search results)?
- AR: كم تصادف محتوى مولّداً بالذكاء الاصطناعي (فيديوهات، تعليق صوتي، ملخّصات في نتائج البحث)؟
- Options (EN): Never / Rarely / Sometimes / Often / Every day
- Options (AR): لا أصادفه / نادراً / أحياناً / كثيراً / يومياً

**AI_ContentLang** (mc; role: X (consumption-side language choice at an AI-created choice point))

- EN: When the same content is available in AI-generated Arabic voice and in the original English, which do you usually choose?
- AR: عندما يتوفّر المحتوى نفسه بصوت عربي مولّد بالذكاء الاصطناعي وبالإنجليزية الأصلية، ماذا تختار عادةً؟
- Options (EN): Always Arabic / Mostly Arabic / Depends on the topic / Mostly English / Always English
- Options (AR): العربية دائماً / العربية غالباً / بحسب الموضوع / الإنجليزية غالباً / الإنجليزية دائماً

**Events** (check; role: covariate (EventMove / EventOther); also defines stable work/study status for ArUse_WorkStudy: stable = none of started university, graduated, new job, and Role != Neither)

- EN: Since you started using AI regularly, did any of these also happen? (tick all that apply)
- AR: منذ أن بدأت باستخدام الذكاء الاصطناعي بانتظام، هل حدث لك أيضاً أيٌّ مما يلي؟ (اختر كل ما ينطبق)
- Options (EN): Started university / Graduated / New job / Started studying or working in English / Moved to another country / None of these
- Options (AR): بدأت الجامعة / تخرّجت / بدأت عملاً جديداً / بدأت الدراسة أو العمل بالإنجليزية / انتقلت إلى بلد آخر / لا شيء مما سبق

**FushaPreAI** (mc; role: filter for Abil_Register + covariate)

- EN: Before using AI, did you write in Fusha (assignments, exams, official letters)?
- AR: قبل استخدامك للذكاء الاصطناعي، هل كنت تكتب بالفصحى (واجبات، امتحانات، رسائل رسمية)؟
- Options (EN): Yes, regularly / Sometimes / No
- Options (AR): نعم، بانتظام / أحياناً / لا

## Section `cur` — Your languages today  /  لغاتك اليوم

**CurUse** (grid; role: RQ1 current level (descriptive; never a covariate))

- EN: These days, which language do you mostly use for each of these?
- AR: هذه الأيام، ما اللغة التي تستخدمها غالباً في كلٍّ مما يلي؟
- Help (EN): Arabic means your dialect or Fusha.

| Code | Var. | English | العربية |
|---|---|---|---|
| CurUse_WorkStudy |  | Work or studies | العمل أو الدراسة |
| CurUse_Writing |  | Writing messages and posts | كتابة الرسائل والمنشورات |
| CurUse_Self |  | Talking to myself or writing my own notes | التحدث مع نفسي أو كتابة ملاحظاتي الخاصة |
| CurUse_Personal |  | Personal matters | الأمور الشخصية |
| CurUse_Family |  | With my family or friends | مع العائلة أو الأصدقاء |
| CurUse_Religion |  | Religious texts | النصوص الدينية |
| CurUse_Formal |  | Reading or writing formal texts (news, documents, articles) | قراءة أو كتابة نصوص رسمية (أخبار، وثائق، مقالات) |
| CurUse_Consume |  | Following content (videos, articles) | متابعة المحتوى (فيديوهات، مقالات) |
- Options (EN): Mostly Arabic / Arabic and English / Mostly English / Another language / Not applicable
- Options (AR): العربية غالباً / العربية والإنجليزية / الإنجليزية غالباً / لغة أخرى / لا ينطبق

## Section `change` — Has AI changed your Arabic?  /  هل غيّر الذكاء الاصطناعي عربيتك؟

**[Text]** On this page we ask whether AI has changed how you use Arabic. • Compare now with before you started using AI regularly. • Mixing Arabic and English is normal.

**[نص]** في هذه الصفحة نسألك: هل غيّر الذكاء الاصطناعي طريقة استخدامك للعربية؟ • قارن بين الآن وما قبل استخدامك المنتظم للذكاء الاصطناعي. • خلط العربية بالإنجليزية أمر طبيعي.

**ArUse** (grid; role: Displacement (ArUse_*), Switching (Switch_Mode))

- EN: Because of AI, do you now do each of these less or more?
- AR: بسبب الذكاء الاصطناعي، هل أصبحت تقوم بكلٍّ مما يلي أقل أم أكثر؟
- Help (EN): Compare now with before you started using AI regularly.

| Code | Var. | English | العربية |
|---|---|---|---|
| ArUse_WorkStudy | M | Using Arabic in my work or studies | استخدام العربية في عملي أو دراستي |
| ArUse_Writing | M | Writing messages or posts in Arabic | كتابة الرسائل أو المنشورات بالعربية |
| ArUse_Self | L | Using Arabic when I talk to myself or write my own notes | استخدام العربية عندما أحدّث نفسي أو أكتب ملاحظاتي الخاصة |
| ArUse_Personal | L | Using Arabic for personal matters | استخدام العربية في الحديث عن أموري الشخصية |
| ArUse_Family | L | Using Arabic with my family or friends | استخدام العربية مع عائلتي أو أصدقائي |
| ArUse_Fusha | H | Reading or writing Fusha (news, documents, articles) | قراءة الفصحى أو كتابتها (أخبار، وثائق، مقالات) |
| ArUse_Religion | H | Reading or listening to religious texts | قراءة نصوص دينية أو الاستماع إليها |
| ArUse_Consume | M | Following content in Arabic (videos, articles) | متابعة محتوى بالعربية (فيديوهات، مقالات) |
| Switch_Mode | M | Switching between Arabic and English while working or studying | التنقّل بين العربية والإنجليزية أثناء العمل أو الدراسة |
- Options (EN): Much less / Less / No change / More / Much more
- Options (AR): أقل بكثير / أقل / لم يتغيّر / أكثر / أكثر بكثير

**SwitchEng** (mc; role: HEADLINE: self-reported AI-driven substitution where Arabic was available)

- EN: Has it happened that you did something in English, although you could have done it in Arabic, because AI helps you better in English?
- AR: هل حدث أن أنجزت عملاً بالإنجليزية، مع أنه كان بإمكانك إنجازه بالعربية، لأن الذكاء الاصطناعي يساعدك أفضل بالإنجليزية؟
- Options (EN): Never / Once or twice / Sometimes / Often / Most of the time
- Options (AR): لم يحدث / مرة أو مرتين / أحياناً / كثيراً / في معظم الأحيان

**SocialMedia** (mc; role: RIVAL DRIVER: same window and scale as ArUse, so AI-attributed change can be compared within person)

- EN: Over the same period, because of social media, do you now use Arabic less or more?
- AR: خلال الفترة نفسها، بسبب وسائل التواصل الاجتماعي، هل أصبحت تستخدم العربية أقل أم أكثر؟
- Options (EN): Much less / Less / No change / More / Much more
- Options (AR): أقل بكثير / أقل / لم يتغيّر / أكثر / أكثر بكثير

**Abil** (grid; role: AbilityDecline (Abil_Register analysed only if FushaPreAI != No))

- EN: Because of AI, has each of these become harder or easier for you, when you use Arabic on your own without AI?
- AR: بسبب الذكاء الاصطناعي، هل أصبح كلٌّ مما يلي أصعب أم أسهل عليك، عندما تستخدم العربية بنفسك من دون مساعدته؟
- Help (EN): Compare now with before you started using AI regularly.

| Code | Var. | English | العربية |
|---|---|---|---|
| Abil_Lexical | L | Finding the everyday Arabic word I need | تذكّر الكلمة العربية اليومية التي أحتاجها |
| Abil_Fluency | L | Speaking my dialect smoothly, without pausing for words | التحدث بلهجتي بطلاقة دون التوقف بحثاً عن الكلمات |
| Abil_ArabicOnly | M | Saying what I mean fully in Arabic, without English words | التعبير عمّا أريده بالعربية كاملاً دون كلمات إنجليزية |
| Abil_Register | H | Writing a formal text in Fusha (e.g. a letter or report) | كتابة نص رسمي بالفصحى (مثل رسالة أو تقرير) |
- Options (EN): Much harder / Harder / No change / Easier / Much easier
- Options (AR): أصعب بكثير / أصعب / لم يتغيّر / أسهل / أسهل بكثير

## Section `views` — Your views and language background  /  رأيك وخلفيتك اللغوية

**Future** (grid; role: EXPLORATORY: expected encroachment into domains Arabic still holds)

- EN: In two years, do you think you will use Arabic more or less than you do today for each of these?
- AR: برأيك، بعد سنتين، هل ستستخدم العربية في كلٍّ مما يلي أكثر أم أقل مما تستخدمها اليوم؟

| Code | Var. | English | العربية |
|---|---|---|---|
| Future_WorkStudy | M | Work or studies | العمل أو الدراسة |
| Future_Writing | M | Writing messages and posts | كتابة الرسائل والمنشورات |
| Future_Self | L | Talking to myself or writing my own notes | التحدث مع نفسي أو كتابة ملاحظاتي الخاصة |
| Future_Personal | L | Personal matters | الأمور الشخصية |
| Future_Family | L | With my family or friends | مع العائلة أو الأصدقاء |
| Future_Formal | H | Reading or writing formal texts | قراءة أو كتابة نصوص رسمية |
| Future_Religion | H | Religious texts | النصوص الدينية |
| Future_Consume | M | Following content (videos, articles) | متابعة المحتوى (فيديوهات، مقالات) |
- Options (EN): Much less / Less / The same as now / More / Much more
- Options (AR): أقل بكثير / أقل / كما هي الآن / أكثر / أكثر بكثير

**Gap** (grid; role: X Perceived quality gap)

- EN: How much do you agree?
- AR: إلى أي حد توافق على ما يلي؟
- Help (EN): If you rarely use AI in Arabic, answer from your impression.

| Code | Var. | English | العربية |
|---|---|---|---|
| Gap_Understand | - | AI understands me better in English than in Arabic | يفهمني الذكاء الاصطناعي بالإنجليزية أفضل من العربية |
| Gap_Accuracy | - | AI gives less accurate answers in Arabic than in English | يعطي الذكاء الاصطناعي إجابات أقل دقة بالعربية منها بالإنجليزية |
| Gap_Voice | - | AI-generated Arabic voices and videos sound less natural than English ones | الأصوات والفيديوهات العربية المولّدة بالذكاء الاصطناعي أقل طبيعية من الإنجليزية |
| Gap_Equal | R | AI answers in Arabic are as good as in English (reverse-coded) | إجابات الذكاء الاصطناعي بالعربية جيدة مثل إجاباته بالإنجليزية |
- Options (EN): Strongly disagree / Disagree / Neutral / Agree / Strongly agree
- Options (AR): أعارض بشدة / أعارض / محايد / أوافق / أوافق بشدة

**L1_Home** (check; role: eligibility check)

- EN: Languages spoken at home when you were a child (tick all)
- AR: اللغات التي كنت تتحدثها في البيت في طفولتك (اختر كل ما ينطبق)
- Options (EN): Arabic / English / French / Other
- Options (AR): العربية / الإنجليزية / الفرنسية / غير ذلك

**Sch_SciLang** (mc; role: Medium covariate (rival explanation))

- EN: At school, you studied science and maths mostly in…
- AR: في المدرسة، درست العلوم والرياضيات غالباً باللغة…
- Options (EN): Arabic / English / French / Other
- Options (AR): العربية / الإنجليزية / الفرنسية / غير ذلك

**Uni_Lang** (mc; role: Medium covariate (rival explanation))

- EN: At university, your courses were mostly in…
- AR: في الجامعة، كانت مقرراتك غالباً باللغة…
- Options (EN): Arabic / English / French / Mixed / I did not go to university
- Options (AR): العربية / الإنجليزية / الفرنسية / مختلطة / لم ألتحق بالجامعة

**Eng_Prof** (mc; role: sensitivity covariate / ML)

- EN: Your English level
- AR: مستواك في الإنجليزية
- Options (EN): Weak / Average / Good / Very good / Excellent
- Options (AR): ضعيف / متوسط / جيد / جيد جداً / ممتاز

**Open** (para; role: 1-3 illustrative quotes only)

- EN: Anything else about how AI has affected your Arabic? (optional)
- AR: هل تودّ إضافة أي شيء عن تأثير الذكاء الاصطناعي على عربيتك؟ (اختياري)
- Help (EN): Please don't mention names of people or places of work.
