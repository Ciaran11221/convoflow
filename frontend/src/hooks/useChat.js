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
      const needsTool = userInput.toLowerCase().includes('read the file') ||
                  userInput.toLowerCase().includes('read ') ||
                  userInput.toLowerCase().includes('summarise') ||
                  userInput.toLowerCase().includes('summarize') ||
                  userInput.toLowerCase().includes('calculate') ||
                  userInput.toLowerCase().includes('what is ')

      if (needsTool) {
        // Use regular /chat endpoint for tool use (calculator, file reading)
        const response = await fetch('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: userInput, session_id: SESSION_ID })
        })
        const data = await response.json()
        setMessages(prev => [...prev, { role: 'assistant', content: data.response }])
        setStreamingContent('')

      } else {
        // Use streaming endpoint for normal conversation
        const response = await fetch('/chat/stream', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: userInput, session_id: SESSION_ID })
        })

        const reader = response.body.getReader()
        const decoder = new TextDecoder()
        let fullContent = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break

          const chunk = decoder.decode(value)
          const lines = chunk.split('\n')

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const token = line.slice(6)

              if (token === '[DONE]') {
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