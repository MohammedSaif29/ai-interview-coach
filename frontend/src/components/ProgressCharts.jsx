/*
  Progress charts for the dashboard, drawn with Recharts (a React chart library).

  Colour choices were checked with a colour-blindness validator, not by eye:
  the brand teal was too grey for a chart line, so charts use a brighter teal,
  and orange for the second series.
*/
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { formatDateTime, formatShortDate } from '../lib/format.js'

const COLORS = {
  content: '#00897b',
  delivery: '#eb6834',
  grid: '#e8ebf0',   // one step off the white surface: visible but quiet
  axisText: '#5b6478',
  crosshair: '#c5cbd5',
}

const axisProps = {
  tickLine: false,
  tick: { fill: COLORS.axisText, fontSize: 12 },
}

function reducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

export default function ProgressCharts({ trend }) {
  // Turn API data into chart rows: one row per session
  const data = trend.map((point, i) => ({
    n: i + 1,
    when: formatDateTime(point.created_at),
    shortDate: formatShortDate(point.created_at),
    content: point.content_score,
    delivery: point.delivery_score,
    fillers: point.fillers_per_minute,
    wpm: point.words_per_minute,
  }))
  const animate = !reducedMotion()

  return (
    <section className="rounded-2xl border border-line bg-white p-6 sm:p-8" aria-labelledby="progress-title">
      <h2 id="progress-title" className="text-lg font-semibold">Your progress</h2>
      <p className="mt-1 text-sm text-muted">Your last {data.length} sessions, oldest on the left.</p>

      {/* Chart 1: two series, so it gets a legend */}
      <div className="mt-6 flex flex-wrap items-baseline justify-between gap-3">
        <h3 className="font-semibold">Scores</h3>
        <div className="flex gap-4 text-sm text-muted">
          <LegendItem color={COLORS.content} label="Content" />
          <LegendItem color={COLORS.delivery} label="Delivery" />
        </div>
      </div>
      <div className="mt-3 h-60">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 8, right: 12, bottom: 0, left: -16 }}>
            <CartesianGrid vertical={false} stroke={COLORS.grid} />
            <XAxis dataKey="n" {...axisProps} axisLine={{ stroke: COLORS.grid }} />
            <YAxis domain={[0, 10]} ticks={[0, 5, 10]} {...axisProps} axisLine={false} width={40} />
            <Tooltip content={<ChartTooltip />} cursor={{ stroke: COLORS.crosshair, strokeWidth: 1 }} />
            {[
              { key: 'content', name: 'Content' },
              { key: 'delivery', name: 'Delivery' },
            ].map(({ key, name }) => (
              <Line
                key={key}
                type="linear"
                dataKey={key}
                name={name}
                stroke={COLORS[key]}
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
                // white ring around each dot keeps it readable where lines cross
                dot={{ r: 4, strokeWidth: 2, stroke: '#fff', fill: COLORS[key] }}
                activeDot={{ r: 5, strokeWidth: 2, stroke: '#fff', fill: COLORS[key] }}
                connectNulls // sessions that weren't scored don't break the line
                isAnimationActive={animate}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Chart 2: one series, so the title names it and no legend is needed */}
      <div className="mt-8 border-t border-line pt-6">
        <h3 className="font-semibold">Filler words per minute</h3>
        <p className="mt-1 text-sm text-muted">Lower is better.</p>
        <div className="mt-3 h-44">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 8, right: 12, bottom: 0, left: -16 }}>
              <CartesianGrid vertical={false} stroke={COLORS.grid} />
              <XAxis dataKey="n" {...axisProps} axisLine={{ stroke: COLORS.grid }} />
              <YAxis allowDecimals={false} {...axisProps} axisLine={false} width={40} />
              <Tooltip content={<ChartTooltip bars />} cursor={{ fill: 'rgba(22, 33, 58, 0.04)' }} />
              <Bar
                dataKey="fillers"
                name="filler words per minute"
                fill={COLORS.delivery}
                maxBarSize={24}
                radius={[4, 4, 0, 0]} // rounded top, square at the baseline
                isAnimationActive={animate}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* The same numbers as a table: nothing should be readable ONLY by hovering */}
      <details className="mt-6 border-t border-line pt-4">
        <summary className="cursor-pointer text-sm font-semibold text-brand">Show as a table</summary>
        <div className="mt-3 overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead className="text-muted">
              <tr>
                <th className="py-2 pr-4 font-medium">Session</th>
                <th className="py-2 pr-4 font-medium">Date</th>
                <th className="py-2 pr-4 font-medium">Content</th>
                <th className="py-2 pr-4 font-medium">Delivery</th>
                <th className="py-2 pr-4 font-medium">Fillers per min</th>
                <th className="py-2 font-medium">Words per min</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {data.map((row) => (
                <tr key={row.n}>
                  <td className="py-2 pr-4">{row.n}</td>
                  <td className="py-2 pr-4 whitespace-nowrap">{row.shortDate}</td>
                  <td className="py-2 pr-4">{row.content ?? 'Not scored'}</td>
                  <td className="py-2 pr-4">{row.delivery}</td>
                  <td className="py-2 pr-4">{row.fillers}</td>
                  <td className="py-2">{row.wpm}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </details>
    </section>
  )
}

// Legend key mirrors the mark: a short line for line charts
function LegendItem({ color, label }) {
  return (
    <span className="flex items-center gap-2">
      <span className="h-0.5 w-4 rounded-full" style={{ background: color }} aria-hidden="true" />
      {label}
    </span>
  )
}

// One tooltip lists every series at that point. Values lead, labels follow.
function ChartTooltip({ active, payload, bars = false }) {
  if (!active || !payload?.length) return null
  const row = payload[0].payload
  // Build the rows from the data itself (not from `payload`), because Recharts leaves out
  // series with no value, and we want to show "Not scored" instead of hiding it.
  const items = bars
    ? [{ name: 'filler words per minute', value: row.fillers, color: COLORS.delivery }]
    : [
        { name: 'Content', value: row.content, color: COLORS.content },
        { name: 'Delivery', value: row.delivery, color: COLORS.delivery },
      ]
  return (
    <div className="rounded-lg border border-line bg-white px-3 py-2 text-sm shadow-[0_6px_20px_-8px_rgba(22,33,58,0.3)]">
      <p className="text-xs text-muted">
        Session {row.n}, {row.when}
      </p>
      {items.map((item) => (
        <p key={item.name} className="mt-1 flex items-center gap-2">
          <span
            className={bars ? 'size-2.5 rounded-sm' : 'h-0.5 w-3 rounded-full'}
            style={{ background: item.color }}
            aria-hidden="true"
          />
          <span className="font-semibold">{item.value ?? 'Not scored'}</span>
          <span className="text-muted">{item.name}</span>
        </p>
      ))}
    </div>
  )
}
