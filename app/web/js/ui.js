// DOM and number helpers shared by every page.

/** h("div", {class: "card", onclick: fn}, child, "text", [more]) -> element */
export function h(tag, props, ...children) {
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(props || {})) {
    if (v === null || v === undefined || v === false) continue;
    if (k === "class") e.className = v;
    else if (k === "style") Object.assign(e.style, v);
    else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
    else e.setAttribute(k, v === true ? "" : v);
  }
  for (const c of children.flat(Infinity)) {
    if (c === null || c === undefined || c === false) continue;
    e.append(c instanceof Node ? c : String(c));
  }
  return e;
}

const MINUS = "−";
/** fixed decimals with a real minus sign */
export function f(x, d = 2) {
  const s = Math.abs(x).toFixed(d);
  return (x < 0 && Number(s) !== 0 ? MINUS : "") + s;
}
/** always signed: +0.17, −0.30 */
export function sg(x, d = 2) {
  const s = Math.abs(x).toFixed(d);
  return (Number(s) === 0 ? "" : x > 0 ? "+" : MINUS) + s;
}
export function pct(x, d = 0) { return (x * 100).toFixed(d) + "%"; }
/** p-values the way the paper prints them */
export function fp(p) {
  if (p < 0.001) return "< 0.001";
  if (p < 0.1) return p.toFixed(3);
  return p.toFixed(2);
}
/** "= 0.035" or "< 0.001", to follow a "p" */
export function pe(p) { const s = fp(p); return s.startsWith("<") ? s : "= " + s; }
export function ci(lo, hi, d = 2) { return `[${f(lo, d)}, ${f(hi, d)}]`; }

export function pageHead(eyebrow, title, ...lead) {
  return h("div", { class: "pagehead" },
    h("div", { class: "eyebrow" }, eyebrow),
    h("h2", null, title),
    lead.length ? h("p", null, ...lead) : null);
}

export function kpis(items) {
  return h("div", { class: "kpis" }, items.map((k) =>
    h("div", { class: "kpi" }, h("div", { class: "n num" }, k.n), h("div", { class: "l" }, k.l))));
}

/** A card. Returns the section; append content with card.body.append(...). */
export function card({ title, sub, span2, tag, id }, ...content) {
  const body = h("div", { class: "body" }, ...content);
  const sec = h("section", { class: "card" + (span2 ? " span2" : ""), id },
    h("div", { class: "cardhead" }, h("h3", null, title), tag ? h("span", { class: "srctag" + (tag === "Live" ? " live" : "") }, tag) : null),
    sub ? h("div", { class: "cardsub" }, sub) : null,
    body);
  sec.body = body;
  return sec;
}

export function grid(...cards) { return h("div", { class: "grid" }, ...cards); }

/** columns: [{label, num, get(row) -> node|string, class}] */
export function table(columns, rows) {
  return h("div", { class: "tablewrap" },
    h("table", { class: "data" },
      h("thead", null, h("tr", null, columns.map((c) => h("th", { class: c.num ? "num" : null }, c.label)))),
      h("tbody", null, rows.map((r) => r.group
        ? h("tr", { class: "group" }, h("td", { colspan: columns.length }, r.group))
        : h("tr", null, columns.map((c) => h("td", { class: [c.num ? "num" : "", c.class || ""].join(" ").trim() || null }, c.get(r))))))));
}

export function callout(...content) { return h("div", { class: "callout" }, ...content); }

export function flag(text, kind) { return h("span", { class: "flag" + (kind ? " " + kind : "") }, text); }

export function link(page, text) { return h("a", { href: "#" + page }, text); }
