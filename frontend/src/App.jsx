import MessageList from './components/MessageList'
import MessageInput from './components/MessageInput'
import { useChat } from './hooks/useChat'

export default function App() {
  const { messages, isStreaming, streamingContent, sendMessage, clearChat } = useChat()

  return (
    <div className="flex flex-col h-screen bg-gray-50">

      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 bg-white border-b border-gray-200 shadow-sm">
        <div>
          <h1 className="text-xl font-semibold text-gray-800">ConvoFlow</h1>
          <p className="text-xs text-gray-500">AI assistant with memory and tool use</p>
        </div>
        <button
          onClick={clearChat}
          className="text-sm text-gray-500 hover:text-red-500 transition-colors"
        >
          Clear chat
        </button>
      </div>

      {/* Messages */}
      <MessageList
        messages={messages}
        streamingContent={streamingContent}
        isStreaming={isStreaming}
      />

      {/* Input */}
      <MessageInput onSend={sendMessage} isStreaming={isStreaming} />

    </div>
  )
}