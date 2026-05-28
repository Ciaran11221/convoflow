import { useEffect, useRef } from 'react'
import StreamingMessage from './StreamingMessage'

export default function MessageList({ messages, streamingContent, isStreaming }) {
  // Auto-scroll to bottom when new messages arrive
  const bottomRef = useRef()

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingContent])

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">

      {messages.length === 0 && !isStreaming && (
        <div className="text-center text-gray-400 text-sm mt-20">
          Send a message to get started
        </div>
      )}

      {messages.map((msg, i) => (
        <div
          key={i}
          className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          <div className={`max-w-[75%] rounded-lg px-4 py-2 text-sm whitespace-pre-wrap
            ${msg.role === 'user'
              ? 'bg-blue-600 text-white'
              : 'bg-gray-100 text-gray-800'
            }`}
          >
            {msg.content}
          </div>
        </div>
      ))}

      {/* Live streaming message with blinking cursor */}
      {isStreaming && (
        <div className="flex justify-start">
          <div className="max-w-[75%] rounded-lg px-4 py-2 text-sm bg-gray-100 text-gray-800">
            {streamingContent
              ? <StreamingMessage content={streamingContent} />
              : <span className="animate-pulse text-gray-400">Thinking...</span>
            }
          </div>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  )
}