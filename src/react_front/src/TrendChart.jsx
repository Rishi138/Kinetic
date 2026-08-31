// Generic session-trend chart. Takes raw scale_pos history (0=good,
// 1=bad, "deviation" framing) and displays it flipped as a
// performance score (1=good, 0=bad) against a vertical band-colored
// axis. Compresses older points via bucket-averaging once the series
// grows past MAX_POINTS, so the chart stays readable across a long
// session without redraw cost blowing up.

const MAX_POINTS = 40
const CHART_W = 320
const CHART_H = 170
const AXIS_W = 7
const AXIS_MARGIN_LEFT = 6
const AXIS_GAP = 8
const PAD_TOP = 14
const PAD_BOTTOM = 14
const PAD_RIGHT = 14
const POINT_R = 2.6

const RAMP_COLORS = [
  '#2E6B3E',
  '#2E6B3E',
  '#B8791A',
  '#B8791A',
  '#C1531B',
  '#A32D2D',
]

function colorForStop(index) {
  return RAMP_COLORS[Math.min(index, RAMP_COLORS.length - 1)]
}

function safeId(str) {
  return String(str).replace(/[^a-zA-Z0-9_-]/g, '')
}

function compress(series, maxPoints) {
  if (series.length <= maxPoints) return series
  const bucketSize = Math.ceil(series.length / maxPoints)
  const out = []
  for (let i = 0; i < series.length; i += bucketSize) {
    const bucket = series.slice(i, i + bucketSize)
    const avg = bucket.reduce((a, b) => a + b, 0) / bucket.length
    out.push(avg)
  }
  return out
}

const PLOT_X0 = AXIS_MARGIN_LEFT + AXIS_W + AXIS_GAP
const PLOT_Y0 = PAD_TOP
const PLOT_Y1 = CHART_H - PAD_BOTTOM
const PLOT_H = PLOT_Y1 - PLOT_Y0

function xFor(i, n) {
  const usableW = CHART_W - PLOT_X0 - PAD_RIGHT
  if (n === 1) return PLOT_X0 + usableW / 2
  return PLOT_X0 + (i / (n - 1)) * usableW
}

// v is a 0->1 performance score, 1=good=top, 0=bad=bottom
function yFor(v) {
  return PLOT_Y0 + (1 - v) * PLOT_H
}

function linePath(values) {
  return values
    .map((v, i) => {
      const x = xFor(i, values.length)
      const y = yFor(v)
      return `${i === 0 ? 'M' : 'L'} ${x.toFixed(1)} ${y.toFixed(1)}`
    })
    .join(' ')
}

function areaPath(values) {
  if (values.length === 0) return ''
  const baseline = yFor(0)
  const line = values
    .map((v, i) => `${i === 0 ? 'M' : 'L'} ${xFor(i, values.length).toFixed(1)} ${yFor(v).toFixed(1)}`)
    .join(' ')
  const lastX = xFor(values.length - 1, values.length).toFixed(1)
  const firstX = xFor(0, values.length).toFixed(1)
  return `${line} L ${lastX} ${baseline} L ${firstX} ${baseline} Z`
}

export default function TrendChart({ title, series, bands, seriesLabels }) {
  const gradId = `axis-grad-${safeId(title)}`

  if (!series || series.every((s) => s.length === 0)) {
    return (
      <div className="trend-chart">
        <div className="trend-chart__title">{title}</div>
        <div className="trend-chart__empty">collecting…</div>
      </div>
    )
  }

  const processed = series.map((s) => compress(s.map((v) => 1 - v), MAX_POINTS))
  const seriesColors = ['#1B4B8F', '#8A8578']
  const labels = seriesLabels || processed.map((_, i) => `S${i + 1}`)

  // "good" boundary in performance terms = 1 - firstNonGoodBand
  // e.g. bands[1] = 0.35 (deviation) -> performance threshold 0.65
  const goodThreshold = bands.length > 1 ? 1 - bands[1] : null

  return (
    <div className="trend-chart">
      <div className="trend-chart__title">
        <span>{title}</span>
        <span className="trend-chart__legend">
          {labels.map((l, i) => (
            <span className="trend-chart__legend-item" key={i}>
              <span
                className="trend-chart__legend-swatch"
                style={{ background: seriesColors[i % seriesColors.length] }}
              />
              {l}
            </span>
          ))}
        </span>
      </div>

      <svg
        viewBox={`0 0 ${CHART_W} ${CHART_H}`}
        className="trend-chart__svg"
        preserveAspectRatio="none"
      >
        <defs>
          {/* offsets increase top->bottom, matching bands' own 0(good)->1(bad) order */}
          <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
            {bands.map((pos, i) => (
              <stop key={i} offset={`${pos * 100}%`} stopColor={colorForStop(i)} />
            ))}
          </linearGradient>
          {processed.map((_, si) => (
            <linearGradient id={`fill-${gradId}-${si}`} key={si} x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={seriesColors[si % seriesColors.length]} stopOpacity="0.16" />
              <stop offset="100%" stopColor={seriesColors[si % seriesColors.length]} stopOpacity="0" />
            </linearGradient>
          ))}
        </defs>

        {/* plot area background + border, drawn first so axis/lines sit on top */}
        <rect
          x={PLOT_X0}
          y={PLOT_Y0}
          width={CHART_W - PLOT_X0 - PAD_RIGHT}
          height={PLOT_H}
          fill="#FFFFFF"
          stroke="var(--line)"
          strokeWidth="1"
        />

        {/* subtle good-zone highlight band, only if we have a threshold */}
        {goodThreshold !== null && (
          <rect
            x={PLOT_X0}
            y={yFor(1)}
            width={CHART_W - PLOT_X0 - PAD_RIGHT}
            height={yFor(goodThreshold) - yFor(1)}
            fill="#2E6B3E"
            fillOpacity="0.06"
          />
        )}

        {/* reference lines at each actual band boundary (performance terms),
            so they line up exactly with the axis strip's color transitions */}
        {bands.map((pos, i) => (
          <line
            key={i}
            x1={PLOT_X0}
            x2={CHART_W - PAD_RIGHT}
            y1={yFor(1 - pos)}
            y2={yFor(1 - pos)}
            stroke="#ECEAE1"
            strokeWidth="1"
          />
        ))}

        {/* vertical band-colored axis strip, same height as plot area exactly */}
        <rect
          x={AXIS_MARGIN_LEFT}
          y={PLOT_Y0}
          width={AXIS_W}
          height={PLOT_H}
          fill={`url(#${gradId})`}
          stroke="var(--line-strong)"
          strokeWidth="1"
        />

        {processed.map((values, si) => (
          <g key={si}>
            <path d={areaPath(values)} fill={`url(#fill-${gradId}-${si})`} stroke="none" />
            <path
              d={linePath(values)}
              fill="none"
              stroke={seriesColors[si % seriesColors.length]}
              strokeWidth="1.6"
              strokeLinejoin="round"
              strokeLinecap="round"
            />
            {values.map((v, i) => (
              <circle
                key={i}
                cx={xFor(i, values.length)}
                cy={yFor(v)}
                r={POINT_R}
                fill="#FCFCFA"
                stroke={seriesColors[si % seriesColors.length]}
                strokeWidth="1.4"
              />
            ))}
          </g>
        ))}
      </svg>
    </div>
  )
}
