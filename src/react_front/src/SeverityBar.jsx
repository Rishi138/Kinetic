// Generic severity bar: takes a 0->1 scale_pos and a list of band
// positions (also 0->1), draws a smooth green->red gradient using a
// fixed color ramp (one color per band stop), and places a marker at
// scale_pos. Works for any metric that emits {scale_pos, bands} --
// no knowledge of what the metric actually measures.

// Fixed visual ramp, one color per band STOP (not per zone).
// Adjacent stops with the SAME color -> flat zone.
// Adjacent stops with DIFFERENT colors -> gradient transition.
// If a metric sends more/fewer bands than this list has colors,
// we cycle/clamp gracefully rather than break.
const RAMP_COLORS = [
  '#2E6B3E', // green
  '#2E6B3E', // green
  '#B8791A', // amber
  '#B8791A', // amber
  '#C1531B', // orange
  '#A32D2D', // red
]

function colorForStop(index) {
  return RAMP_COLORS[Math.min(index, RAMP_COLORS.length - 1)]
}

export default function SeverityBar({ scalePos, bands }) {
  if (!bands || bands.length < 2) return null

  // build a CSS linear-gradient string from band stops + ramp colors
  const stops = bands
    .map((pos, i) => `${colorForStop(i)} ${pos * 100}%`)
    .join(', ')

  const gradient = `linear-gradient(to right, ${stops})`
  const markerPct = Math.max(0, Math.min(1, scalePos)) * 100

  return (
    <div className="severity-bar">
      <div className="severity-bar__track" style={{ background: gradient }}>
        <div
          className="severity-bar__marker"
          style={{ left: `${markerPct}%` }}
        />
      </div>
    </div>
  )
}
