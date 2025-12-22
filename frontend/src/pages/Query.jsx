import { useState } from 'react'
import axios from 'axios'

export default function Query() {
  const [query, setQuery] = useState('')
  const [answer, setAnswer] = useState('')
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim()) return

    setLoading(true)
    setError('')
    setAnswer('')
    setSources([])

    try {
      const response = await axios.post('/api/v1/chat/query', {
        query: query,
        top_k: 5
      })

      setAnswer(response.data.answer)
      setSources(response.data.sources || [])
    } catch (err) {
      setError(err.response?.data?.detail || 'Query failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Query Knowledge Base</h1>

        <form onSubmit={handleSubmit} className="space-y-4 mb-6">
          <div>
            <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
              Ask a question
            </label>
            <textarea
              id="query"
              rows="3"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="What would you like to know?"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {loading ? 'Querying...' : 'Query'}
          </button>
        </form>

        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {answer && (
          <div className="mb-6">
            <h2 className="text-lg font-semibold mb-2">Answer</h2>
            <div className="bg-gray-50 border border-gray-200 rounded-md p-4">
              <p className="text-gray-800 whitespace-pre-wrap">{answer}</p>
            </div>
          </div>
        )}

        {sources.length > 0 && (
          <div>
            <h2 className="text-lg font-semibold mb-2">Sources</h2>
            <div className="space-y-2">
              {sources.map((source, idx) => (
                <div key={idx} className="bg-gray-50 border border-gray-200 rounded-md p-3">
                  <p className="text-sm text-gray-600">
                    <span className="font-medium">Source {idx + 1}:</span> Version {source.version} 
                    {source.similarity_score && ` (Score: ${source.similarity_score.toFixed(3)})`}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

