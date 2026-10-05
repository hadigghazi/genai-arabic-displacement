// The site is one story told in chapters. This module holds the chapter list and the building blocks every
// chapter uses: its head (with the chapter stepper), sections, takeaways, evidence cards, timelines, the
// collapsible "How we know" boxes, citation pills, reference lists and the previous/next links.
import { h } from "./ui.js";

export const CHAPTERS = [
  { id: "question", title: "The question", teaser: "Why ask whether AI is changing how bilinguals use Arabic, and what we expected." },
  { id: "study", title: "How we asked", teaser: "The survey, the core question and the 105 people who answered it." },
  { id: "where", title: "Where Arabic is used less", teaser: "Eight areas of daily life, from work and study to religion." },
  { id: "language", title: "The language of AI use", teaser: "What goes with the decrease, and what does not." },
  { id: "wider", title: "A shift that began before AI", teaser: "Social media, and the changes of early adulthood." },
  { id: "prediction", title: "Can we predict it?", teaser: "Machine learning, judged by rules fixed in advance." },
  { id: "model", title: "Try the model", teaser: "Answer the survey’s questions and see what the models predict." },
  { id: "meaning", title: "What it means", teaser: "The answer, the scorecard, its limits and the next steps." },
];
export const HOME = { id: "home", title: "Home" };
export const PAPER = { id: "paper", title: "Paper & materials" };
export const ORDER = [HOME, ...CHAPTERS, PAPER];

export function chapterNo(id) { return CHAPTERS.findIndex((c) => c.id === id) + 1; }

/** The eight chapters as a clickable progress bar. */
export function stepper(id) {
  const n = chapterNo(id);
  return h("nav", { class: "stepper", "aria-label": "Chapter progress" }, CHAPTERS.map((c, i) =>
    h("a", { href: "#" + c.id, title: `${i + 1}. ${c.title}`, class: i + 1 < n ? "done" : i + 1 === n ? "now" : "", "aria-current": i + 1 === n ? "step" : null },
      h("span", null, String(i + 1)))));
}

export function chapterHead(id, ...lede) {
  const n = chapterNo(id);
  return h("header", { class: "chapterhead" },
    stepper(id),
    h("div", { class: "eyebrow" }, `Chapter ${n} of ${CHAPTERS.length}`),
    h("h2", null, CHAPTERS[n - 1].title),
    lede.length ? h("p", { class: "lede" }, ...lede) : null);
}

const slug = (t) => String(t).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");

/** A section of a chapter: a heading (also listed in the "On this page" panel), then any content. */
export function sec(title, ...content) {
  return h("section", { class: "storysec", id: title ? "s-" + slug(title) : null, "data-title": title || null },
    title ? h("h3", null, title) : null, ...content);
}

/** Paragraphs of running text: each argument is one paragraph (a string, or an array of strings and nodes). */
export function prose(...paras) {
  return h("div", { class: "prose" }, paras.map((p) => h("p", null, ...(Array.isArray(p) ? p : [p]))));
}

/** The one sentence a reader should leave a section with. */
export function takeaway(...text) { return h("p", { class: "takeaway" }, ...text); }

/** Cards that each carry one piece of evidence: [{label, title, text, cites: [keys]}]. */
export function evidence(S, items) {
  return h("div", { class: "evidence" }, items.map((it) => h("div", { class: "evcard" + (it.accent ? " accent" : "") },
    h("div", { class: "evlabel" }, it.label),
    h("div", { class: "evtitle" }, it.title),
    h("p", null, it.text),
    it.cites ? h("div", { class: "evcite" }, cite(S, ...it.cites)) : null)));
}

/** A vertical timeline: [{when, title, text, cites, now}]. */
export function timeline(S, items) {
  return h("ol", { class: "timeline" }, items.map((it) => h("li", { class: it.now ? "now" : "" },
    h("div", { class: "tlwhen" }, it.when),
    h("div", { class: "tlbody" }, h("b", null, it.title), h("p", null, it.text, it.cites ? [" ", cite(S, ...it.cites)] : null)))));
}

/** "How we know": the tests behind a section, closed until opened. onOpen runs once, on first opening. */
export function howWeKnow(summary, content, onOpen) {
  const d = h("details", { class: "howwe" }, h("summary", null, h("span", { class: "hw" }, "How we know"), h("span", null, summary)),
    h("div", { class: "inner" }, content));
  if (onOpen) {
    let done = false;
    d.addEventListener("toggle", () => { if (d.open && !done) { done = true; onOpen(); } });
  }
  return d;
}

/** Citation pills that link to the sources and show the title on hover. */
export function cite(S, ...keys) {
  return h("span", { class: "cites" }, keys.map((k) => {
    const r = S.references[k];
    const label = `${r.short} ${r.year}`;
    return r.url
      ? h("a", { class: "cite", href: r.url, target: "_blank", rel: "noopener", "data-tip": `${r.title}. ${r.venue}` }, label)
      : h("span", { class: "cite", "data-tip": `${r.title}. ${r.venue}` }, label);
  }));
}

function refRow(r) {
  return h("li", { class: "ref" },
    h("div", { class: "refwho" }, h("b", null, r.short), h("span", null, r.year)),
    h("div", { class: "refwhat" },
      r.url ? h("a", { href: r.url, target: "_blank", rel: "noopener" }, r.title) : h("span", null, r.title),
      h("div", { class: "refmeta" }, r.authors, r.venue ? ` · ${r.venue}` : "", r.url && r.url.includes("doi.org") ? h("span", { class: "doi" }, "DOI") : null)));
}

/** A list of sources for the keys given (or every reference), sorted by author. */
export function sources(S, keys) {
  const R = S.references;
  const list = (keys || Object.keys(R)).map((k) => R[k]).sort((a, b) => a.short.localeCompare(b.short) || a.year.localeCompare(b.year));
  return h("ol", { class: "reflist" }, list.map(refRow));
}

/** Previous and next, at the bottom of every page of the story. */
export function storyNav(id) {
  const i = ORDER.findIndex((c) => c.id === id);
  const label = (c) => (chapterNo(c.id) ? `Chapter ${chapterNo(c.id)}` : c.id === "home" ? "Start" : "Read more");
  const prev = ORDER[i - 1], next = ORDER[i + 1];
  return h("nav", { class: "storynav", "aria-label": "Chapters" },
    prev ? h("a", { class: "prev", href: "#" + prev.id }, h("small", null, "← " + label(prev)), h("b", null, prev.title)) : h("span"),
    next ? h("a", { class: "next", href: "#" + next.id }, h("small", null, label(next) + " →"), h("b", null, next.title)) : h("span"));
}

/** The right-hand panel: where this page sits in the story, its sections (highlighted while reading), next/previous. */
export function rail(id, article) {
  const i = ORDER.findIndex((c) => c.id === id);
  const n = chapterNo(id);
  const secs = [...article.querySelectorAll("section.storysec[data-title]")];
  const items = secs.map((s) => h("button", { type: "button", class: "tocitem", onclick: () => s.scrollIntoView({ behavior: "smooth", block: "start" }) }, s.dataset.title));
  const prev = ORDER[i - 1], next = ORDER[i + 1];
  const box = h("div", { class: "railbox" },
    h("div", { class: "railhead" }, n ? `Chapter ${n} of ${CHAPTERS.length}` : id === "paper" ? "Read more" : ""),
    h("div", { class: "railtitle" }, ORDER[i].title),
    items.length ? h("div", { class: "toclabel" }, "On this page") : null,
    items.length ? h("nav", { class: "toc", "aria-label": "On this page" }, items) : null,
    h("div", { class: "railnav" },
      prev ? h("a", { href: "#" + prev.id }, "← ", prev.title) : null,
      next ? h("a", { href: "#" + next.id, class: "railnext" }, next.title, " →") : null));
  // highlight the section being read
  if (secs.length && "IntersectionObserver" in window) {
    const visible = new Map();
    const io = new IntersectionObserver((entries) => {
      for (const e of entries) visible.set(e.target, e.isIntersecting ? e.boundingClientRect.top : null);
      let best = null;
      for (const [s, top] of visible) if (top !== null && (best === null || top < visible.get(best))) best = s;
      if (best) items.forEach((b, k) => b.classList.toggle("on", secs[k] === best));
    }, { rootMargin: "-15% 0px -55% 0px" });
    secs.forEach((s) => io.observe(s));
    box.disconnect = () => io.disconnect();
  }
  return h("aside", { class: "rail" }, box);
}
