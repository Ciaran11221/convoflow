// Displays streaming text with a blinking cursor to show it's live
export default function StreamingMessage({ content }) {
  return (
    <span>
      {content}
      <span className="animate-pulse">▌</span>
    </span>
  )
}