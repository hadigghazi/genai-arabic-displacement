// ECharts with the dblp Explorer's theme. ECharts draws to a canvas, which cannot resolve CSS custom
// properties, so every colour is read off the document as a literal when an option is built, and every
// live chart is rebuilt when the theme changes.
const echarts = window.echarts;
const live = new Set();

export function tok(name) { return getComputedStyle(document.documentElement).getPropertyValue(name).trim(); }

export function palette() {
  return {
    s1: tok("--s1"), s2: tok("--s2"), s3: tok("--s3"), s4: tok("--s4"), s5: tok("--s5"), s6: tok("--s6"),
    good: tok("--good"), bad: tok("--bad"), neutral: tok("--neutral"),
    seq: [1, 2, 3, 4, 5].map((i) => tok("--seq-" + i)),
    ink: tok("--ink"), ink2: tok("--ink-2"), muted: tok("--muted"), rule: tok("--rule-2"), surface: tok("--chart-surface"),
  };
}

/** blend two hex colours: t = 0 -> a, t = 1 -> b */
export function mix(a, b, t) {
  const p = (x) => [1, 3, 5].map((i) => parseInt(x.slice(i, i + 2), 16));
  const A = p(a), B = p(b);
  return "#" + A.map((v, i) => Math.round(v + (B[i] - v) * t).toString(16).padStart(2, "0")).join("");
}

/** Mount a chart: build(palette, width) -> option. Rebuilt on theme change and when its box changes width. */
export function chart(parent, build, height = 260, label = "chart") {
  const box = document.createElement("div");
  box.className = "chartbox";
  box.style.height = height + "px";
  box.setAttribute("role", "img");
  box.setAttribute("aria-label", label);
  parent.append(box);
  const inst = echarts.init(box, null, { renderer: "canvas" });
  let width = box.clientWidth;
  const entry = { inst, render: () => inst.setOption(build(palette(), box.clientWidth), { notMerge: true }) };
  entry.ro = new ResizeObserver(() => {
    inst.resize();
    if (Math.abs(box.clientWidth - width) > 40) { width = box.clientWidth; entry.render(); }
  });
  entry.ro.observe(box);
  entry.render();
  live.add(entry);
  return entry;
}
export function disposeCharts() {
  for (const e of live) { e.ro.disconnect(); e.inst.dispose(); }
  live.clear();
}
export function rerenderCharts() { for (const e of live) e.render(); }

// ------------------------------------------------------------------ option parts
const FONT = '"IBM Plex Sans", system-ui, sans-serif';

export function base(p, { legend = null } = {}) {
  return {
    backgroundColor: "transparent",
    textStyle: { fontFamily: FONT, color: p.ink2 },
    animationDuration: 300,
    grid: { left: 8, right: 16, top: legend ? 34 : 10, bottom: 6, containLabel: true },
    legend: legend
      ? { show: true, top: 0, left: 0, icon: "circle", itemWidth: 9, itemHeight: 9, itemGap: 14,
          textStyle: { color: p.ink2, fontSize: 12 }, data: legend }
      : { show: false },
    tooltip: {
      backgroundColor: p.surface, borderColor: p.rule, borderWidth: 1, padding: [8, 10],
      textStyle: { color: p.ink, fontFamily: FONT, fontSize: 12 },
      extraCssText: "box-shadow: 0 4px 16px rgba(0,0,0,.12); border-radius: 6px;",
    },
  };
}
const catAxis = (p, data, extra = {}) => ({
  type: "category", data, inverse: true, axisLine: { show: false }, axisTick: { show: false },
  axisLabel: { color: p.ink2, fontSize: 12, ...extra },
});
const valAxis = (p, extra = {}) => ({
  type: "value", axisLabel: { color: p.muted, fontSize: 11 }, splitLine: { lineStyle: { color: p.rule } },
  nameTextStyle: { color: p.muted, fontSize: 11 }, ...extra,
});
const dot = (p, color) => `<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${color};margin-right:6px"></span>`;

/** Horizontal bars with value labels. */
export function hbar(p, { labels, values, color, fmt = (v) => v, max, tip }) {
  return {
    ...base(p),
    grid: { left: 8, right: 44, top: 4, bottom: 4, containLabel: true },
    xAxis: { type: "value", max, show: false },
    yAxis: catAxis(p, labels),
    tooltip: { ...base(p).tooltip, trigger: "axis", axisPointer: { type: "shadow", shadowStyle: { color: p.rule, opacity: .5 } },
               formatter: (ps) => tip ? tip(ps[0].dataIndex) : `${ps[0].name}<br><b>${fmt(ps[0].value)}</b>` },
    series: [{ type: "bar", data: values, barMaxWidth: 16, itemStyle: { color: color || p.s1, borderRadius: [0, 4, 4, 0] },
               label: { show: true, position: "right", color: p.ink2, fontSize: 11.5, formatter: (d) => fmt(d.value) } }],
  };
}

/** Vertical bars with value labels. */
export function vbar(p, { labels, values, color, fmt = (v) => v, yName, tip, min }) {
  return {
    ...base(p),
    grid: { left: 8, right: 10, top: 22, bottom: 4, containLabel: true },
    xAxis: { type: "category", data: labels, axisLine: { lineStyle: { color: p.rule } }, axisTick: { show: false },
             axisLabel: { color: p.ink2, fontSize: 11.5, interval: 0 } },
    yAxis: valAxis(p, { name: yName, min }),
    tooltip: { ...base(p).tooltip, trigger: "axis", axisPointer: { type: "shadow", shadowStyle: { color: p.rule, opacity: .5 } },
               formatter: (ps) => tip ? tip(ps[0].dataIndex) : `${ps[0].name}<br><b>${fmt(ps[0].value)}</b>` },
    series: [{ type: "bar", data: values, barMaxWidth: 38, itemStyle: { color: color || p.s1, borderRadius: [4, 4, 0, 0] },
               label: { show: true, position: "top", color: p.ink2, fontSize: 11.5, formatter: (d) => fmt(d.value) } }],
  };
}

/** Grouped horizontal bars: series = [{name, values, color}]. */
export function groupedHbar(p, { labels, series, fmt = (v) => v, min, max }) {
  return {
    ...base(p, { legend: series.map((s) => s.name) }),
    grid: { left: 8, right: 40, top: 34, bottom: 4, containLabel: true },
    xAxis: { type: "value", min, max, show: false },
    yAxis: catAxis(p, labels),
    tooltip: { ...base(p).tooltip, trigger: "axis", axisPointer: { type: "shadow", shadowStyle: { color: p.rule, opacity: .5 } },
               formatter: (ps) => `${ps[0].name}<br>` + ps.filter((x) => x.value !== null && x.value !== undefined)
                 .map((x) => `${dot(p, x.color)}${x.seriesName}: <b>${fmt(x.value)}</b>`).join("<br>") },
    series: series.map((s) => ({
      name: s.name, type: "bar", data: s.values, barMaxWidth: 12, barGap: "25%", itemStyle: { color: s.color, borderRadius: [0, 3, 3, 0] },
      label: { show: true, position: "right", color: p.ink2, fontSize: 11, formatter: (d) => (d.value === null ? "" : fmt(d.value)) },
    })),
  };
}

/** The domain profile: less on the left, more on the right, "no change" centred on zero. */
export function diverging(p, domains, width = 800) {
  const narrow = width < 560;
  const rows = [...domains].sort((a, b) => b.less - a.less);
  const share = (d, i) => (100 * d.counts[i]) / d.n;
  const col = { ml: p.s2, l: mix(p.s2, p.surface, 0.5), nc: p.neutral, m: mix(p.s1, p.surface, 0.5), mm: p.s1 };
  const ser = (name, i, sign, color, half, label) => ({
    name, type: "bar", stack: "all", barWidth: 18, emphasis: { disabled: true },
    itemStyle: { color, borderColor: p.surface, borderWidth: 1 },
    data: rows.map((d) => sign * share(d, i) * (half ? 0.5 : 1)),
    label: label && !narrow ? { show: true, position: sign < 0 ? "left" : "right", color: p.ink2, fontSize: 11.5, formatter: label } : undefined,
  });
  const lim = Math.ceil(Math.max(...rows.map((d) => Math.max(100 * d.less + 50 * d.same, 100 * d.more + 50 * d.same))) / 10) * 10;
  return {
    ...base(p, { legend: ["Much less", "Less", "No change", "More", "Much more"] }),
    grid: { left: 8, right: 16, top: narrow ? 56 : 34, bottom: 20, containLabel: true },
    xAxis: valAxis(p, { min: -lim, max: lim, axisLabel: { color: p.muted, fontSize: 11, formatter: (v) => Math.abs(v) + "%" } }),
    yAxis: catAxis(p, rows.map((d) => (narrow ? d.label.replace(/ \(.*\)$/, "").replace(" and own notes", "") : `${d.label} (${d.n})`)), narrow ? { fontSize: 11 } : {}),
    tooltip: { ...base(p).tooltip, trigger: "axis", axisPointer: { type: "shadow", shadowStyle: { color: p.rule, opacity: .5 } },
      formatter: (ps) => {
        const d = rows[ps[0].dataIndex];
        const names = ["Much less", "Less", "No change", "More", "Much more"];
        const cols = [col.ml, col.l, col.nc, col.m, col.mm];
        return `<b>${d.label}</b> (n = ${d.n})<br>` + names.map((n, i) => `${dot(p, cols[i])}${n}: <b>${share(d, i).toFixed(0)}%</b> (${d.counts[i]})`).join("<br>");
      } },
    series: [
      ser("No change", 2, -1, col.nc, true),
      ser("Less", 1, -1, col.l),
      ser("Much less", 0, -1, col.ml, false, (x) => Math.round(100 * rows[x.dataIndex].less) + "%"),
      ser("No change", 2, 1, col.nc, true),
      ser("More", 3, 1, col.m),
      ser("Much more", 4, 1, col.mm, false, (x) => Math.round(100 * rows[x.dataIndex].more) + "%"),
    ],
  };
}

/** Estimates with intervals. rows: [{label, b, lo, hi, on, tip}] */
export function forest(p, { rows, ref = 0, xName, fmt = (v) => v.toFixed(2) }) {
  return {
    ...base(p),
    grid: { left: 8, right: 18, top: 8, bottom: xName ? 30 : 8, containLabel: true },
    xAxis: valAxis(p, { name: xName, nameLocation: "middle", nameGap: 24 }),
    yAxis: catAxis(p, rows.map((r) => r.label)),
    tooltip: { ...base(p).tooltip, trigger: "item",
      formatter: (x) => { const r = rows[x.dataIndex]; return r.tip || `${r.label}<br><b>${fmt(r.b)}</b> [${fmt(r.lo)}, ${fmt(r.hi)}]`; } },
    series: [
      { type: "custom", data: rows.map((r, i) => [r.lo, r.hi, r.b, i]), encode: { x: [0, 1, 2], y: 3 },
        renderItem: (params, api) => {
          const i = api.value(3), a = api.coord([api.value(0), i]), b = api.coord([api.value(1), i]), m = api.coord([api.value(2), i]);
          const c = rows[params.dataIndex].on ? p.s1 : p.muted;
          return { type: "group", children: [
            { type: "line", shape: { x1: a[0], y1: a[1], x2: b[0], y2: b[1] }, style: { stroke: c, lineWidth: 2 } },
            { type: "circle", shape: { cx: m[0], cy: m[1], r: 5 }, style: { fill: c, stroke: p.surface, lineWidth: 2 } },
          ] };
        } },
      { type: "scatter", data: [], silent: true,
        markLine: { silent: true, symbol: "none", label: { show: false }, lineStyle: { color: p.muted, type: "dashed", width: 1 }, data: [{ xAxis: ref }] } },
    ],
  };
}

/** Several scores per category as dots: series = [{name, values, color, symbol}]. refs = [{x, label}] */
export function dots(p, { labels, series, refs = [], min, max, fmt = (v) => v.toFixed(2) }) {
  return {
    ...base(p, { legend: series.map((s) => s.name) }),
    grid: { left: 8, right: 18, top: 34, bottom: 8, containLabel: true },
    xAxis: valAxis(p, { min, max }),
    yAxis: catAxis(p, labels),
    tooltip: { ...base(p).tooltip, trigger: "axis", axisPointer: { type: "shadow", shadowStyle: { color: p.rule, opacity: .5 } },
      formatter: (ps) => `${labels[ps[0].value[1]]}<br>` + ps.map((x) => `${dot(p, x.color)}${x.seriesName}: <b>${fmt(x.value[0])}</b>`).join("<br>") },
    series: [
      ...series.map((s) => ({ name: s.name, type: "scatter", symbol: s.symbol || "circle", symbolSize: 11,
        itemStyle: { color: s.color, borderColor: p.surface, borderWidth: 1.5 },
        data: s.values.map((v, i) => (v === null ? null : [v, i])).filter(Boolean) })),
      { type: "scatter", data: [], silent: true,
        markLine: { silent: true, symbol: "none", lineStyle: { color: p.muted, type: "dashed", width: 1 },
          label: { show: true, position: "insideEndTop", color: p.muted, fontSize: 10.5, formatter: (x) => x.name },
          data: refs.map((r) => ({ xAxis: r.x, name: r.label })) } },
    ],
  };
}
