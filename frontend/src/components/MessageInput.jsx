import { useState, useRef } from 'react'

export default function MessageInput({ onSend, isStreaming }) {
  const [input, setInput] = useState('')
  const [uploading, setUploading] = useState(false)
  const [uploadedFile, setUploadedFile] = useState(null)
  const fileRef = useRef()

  const handleSend = () => {
    if (!input.trim() || isStreaming) return
    onSend(input)
    setInput('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const handleFileUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await fetch('/upload', { method: 'POST', body: formData })
      const data = await res.json()
      setUploadedFile(data.uploaded)
      // Pre-fill the input so user knows what to ask
      setInput(`Read the file ${data.uploaded} and summarise it`)
    } catch (err) {
      console.error('Upload error:', err)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="flex flex-col gap-2 p-4 border-t border-gray-200 bg-white">

      {/* Show uploaded file name if present */}
      {uploadedFile && (
        <div className="text-xs text-green-600 font-medium">
          ✓ Uploaded: {uploadedFile}
        </div>
      )}

      <div className="flex gap-2">
        {/* Hidden file input triggered by the button below */}
        <input
          type="file"
          ref={fileRef}
          onChange={handleFileUpload}
          className="hidden"
          accept=".txt,.md,.csv,.json"
        />

        <button
          onClick={() => fileRef.current.click()}
          disabled={uploading || isStreaming}
          className="px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
        >
          {uploading ? 'Uploading...' : '📎 Upload'}
        </button>

        <textarea
          className="flex-1 resize-none rounded-lg border border-gray-300 p-3 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={2}
          placeholder="Type a message... (Enter to send, Shift+Enter for new line)"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isStreaming}
        />

        <button
          className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          onClick={handleSend}
          disabled={isStreaming || !input.trim()}
        >
          {isStreaming ? '...' : 'Send'}
        </button>
      </div>
    </div>
  )
}