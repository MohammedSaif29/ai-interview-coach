/*
  Shows the coach's replies with simple formatting: paragraphs, bullet and numbered
  lists, headings, **bold**, *italic* and `code`.

  SECURITY: we build React elements ourselves and never insert raw HTML
  (no dangerouslySetInnerHTML), so a reply can't inject scripts into the page.
*/
export default function MarkdownText({ text }) {
  return <div className="space-y-3">{toBlocks(text).map(renderBlock)}</div>
}

// Split the text into blocks: paragraphs, lists and headings
function toBlocks(text) {
  const blocks = []
  let current = null

  for (const rawLine of text.split('\n')) {
    const line = rawLine.trimEnd()
    const bullet = line.match(/^\s*[-*•]\s+(.*)$/)
    const numbered = line.match(/^\s*(\d+)[.)]\s+(.*)$/)
    const heading = line.match(/^#{1,6}\s+(.*)$/)

    if (!line.trim()) {
      current = null
    } else if (heading) {
      blocks.push({ type: 'heading', text: heading[1] })
      current = null
    } else if (bullet) {
      if (current?.type !== 'ul') blocks.push((current = { type: 'ul', items: [] }))
      current.items.push(bullet[1])
    } else if (numbered) {
      if (current?.type !== 'ol') blocks.push((current = { type: 'ol', items: [] }))
      current.items.push(numbered[2])
    } else if (current?.type === 'p') {
      current.lines.push(line)
    } else {
      blocks.push((current = { type: 'p', lines: [line] }))
    }
  }
  return blocks
}

function renderBlock(block, i) {
  if (block.type === 'heading') return <p key={i} className="font-semibold">{inline(block.text)}</p>
  if (block.type === 'ul') {
    return (
      <ul key={i} className="list-disc space-y-1 pl-5 marker:text-brand">
        {block.items.map((item, j) => <li key={j}>{inline(item)}</li>)}
      </ul>
    )
  }
  if (block.type === 'ol') {
    return (
      <ol key={i} className="list-decimal space-y-1 pl-5 marker:text-muted">
        {block.items.map((item, j) => <li key={j}>{inline(item)}</li>)}
      </ol>
    )
  }
  return (
    <p key={i}>
      {block.lines.map((line, j) => (
        <span key={j}>
          {j > 0 && <br />}
          {inline(line)}
        </span>
      ))}
    </p>
  )
}

// **bold**, *italic*, _italic_ and `code` inside a line
function inline(text) {
  const parts = text.split(/(\*\*[^*]+\*\*|`[^`]+`|\*[^*\s][^*]*\*|_[^_\s][^_]*_)/g)
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**') && part.length > 4) {
      return <strong key={i} className="font-semibold">{part.slice(2, -2)}</strong>
    }
    if (part.startsWith('`') && part.endsWith('`') && part.length > 2) {
      return <code key={i} className="rounded bg-ink/[0.06] px-1 py-0.5 text-[0.9em]">{part.slice(1, -1)}</code>
    }
    if ((part.startsWith('*') && part.endsWith('*')) || (part.startsWith('_') && part.endsWith('_'))) {
      if (part.length > 2) return <em key={i}>{part.slice(1, -1)}</em>
    }
    return part
  })
}
