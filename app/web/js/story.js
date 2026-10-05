// The site is one story told in chapters. This module holds the chapter list and the building blocks every
// chapter uses: its head, sections, takeaways, the collapsible "How we know" boxes, citations and the
// previous/next links at the bottom.
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
const HOME = { id: "home", title: "Home" };
const PAPER = { id: "paper", title: "Paper & materials" };

export function chapterNo(id) { return CHAPTERS.findIndex((c) => c.id === id) + 1; }

export function chapterHead(id, ...lede) {
  const n = chapterNo(id);
  return h("header", { class: "chapterhead" },
    h("div", { class: "eyebrow" }, `Chapter ${n} of ${CHAPTERS.length}`),
    h("h2", null, CHAPTERS[n - 1].title),
    lede.length ? h("p", { class: "lede" }, ...lede) : null);
}

/** A section of a chapter: a heading, then any content. */
export function sec(title, ...content) {
  return h("section", { class: "storysec" }, title ? h("h3", null, title) : null, ...content);
}

/** Paragraphs of running text: each argument is one paragraph (a string, or an array of strings and nodes). */
export function prose(...paras) {
  return h("div", { class: "prose" }, paras.map((p) => h("p", null, ...(Array.isArray(p) ? p : [p]))));
}

/** The one sentence a reader should leave a section with. */
export function takeaway(...text) { return h("p", { class: "takeaway" }, ...text); }

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

/** An inline citation that links to the source: "(Fishman, 1972)". */
export function cite(S, ...keys) {
  const parts = keys.map((k, i) => {
    const r = S.references[k];
    const label = `${r.short}, ${r.year}`;
    return [i ? "; " : "", r.url ? h("a", { href: r.url, target: "_blank", rel: "noopener", title: r.title }, label) : h("span", { title: r.title }, label)];
  });
  return h("span", { class: "cite" }, "(", parts, ")");
}

/** A list of sources for the keys given (or every reference). */
export function sources(S, keys) {
  const R = S.references;
  const list = (keys || Object.keys(R)).map((k) => R[k]).sort((a, b) => a.short.localeCompare(b.short) || a.year.localeCompare(b.year));
  const stop = (t) => (/[.?!]$/.test(t) ? "" : ".");      // no "expression?." or "Corp.."
  return h("ol", { class: "refs" }, list.map((r) => h("li", null,
    `${r.authors} (${r.year}). `, r.url ? h("a", { href: r.url, target: "_blank", rel: "noopener" }, r.title) : r.title,
    stop(r.title), r.venue ? ` ${r.venue}${stop(r.venue)}` : "")));
}

/** Previous and next, at the bottom of every page of the story. */
export function storyNav(id) {
  const order = [HOME, ...CHAPTERS, PAPER];
  const i = order.findIndex((c) => c.id === id);
  const label = (c) => (chapterNo(c.id) ? `Chapter ${chapterNo(c.id)}` : c.id === "home" ? "Start" : "Read more");
  const prev = order[i - 1], next = order[i + 1];
  return h("nav", { class: "storynav", "aria-label": "Chapters" },
    prev ? h("a", { class: "prev", href: "#" + prev.id }, h("small", null, "← " + label(prev)), h("b", null, prev.title)) : h("span"),
    next ? h("a", { class: "next", href: "#" + next.id }, h("small", null, label(next) + " →"), h("b", null, next.title)) : h("span"));
}
