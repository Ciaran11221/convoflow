import { useState, useCallback } from 'react'
import { v4 as uuidv4 } from 'uuid'

// Generate a session ID once per browser session
const SESSION_ID = uuidv4()

export function useChat() {
  const [messages, setMessages] = useState([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamingContent, setStreamingContent] = useState('')

  const sendMessage = useCallback(async (userInput) => {
    if (!userInput.trim() || isStreaming) return

    // Add user message to the list immediately
    const userMessage = { role: 'user', content: userInput }
    setMessages(prev => [...prev, userMessage])
    setIsStreaming(true)
    setStreamingContent('')

    try {
      // Open SSE connection to the streaming endpoint
      const response = await fetch('/chat/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userInput, session_id: SESSION_ID })
      })

      const reader = response.body.getReader()
      const decoder = new TextDecoder()
      let fullContent = ''

      // Read tokens as they stream in
      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        const lines = chunk.split('\n')

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const token = line.slice(6) // Strip the "data: " prefix

            if (token === '[DONE]') {
              // Stream finished — move content to messages list
              setMessages(prev => [
                ...prev,
                { role: 'assistant', content: fullContent }
              ])
              setStreamingContent('')
            } else {
              fullContent += token
              setStreamingContent(fullContent)
            }
          }
        }
      }
    } catch (error) {
      console.error('Stream error:', error)
      setMessages(prev => [
        ...prev,
        { role: 'assistant', content: 'Sorry, something went wrong.' }
      ])
    } finally {
      setIsStreaming(false)
    }
  }, [isStreaming])

  const clearChat = useCallback(async () => {
    await fetch(`/clear/${SESSION_ID}`, { method: 'POST' })
    setMessages([])
    setStreamingContent('')
  }, [])

  return { messages, isStreaming, streamingContent, sendMessage, clearChat }
}