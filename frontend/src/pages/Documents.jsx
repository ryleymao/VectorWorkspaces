import { useState } from 'react'
import axios from 'axios'

export default function Documents() {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const handleFileChange = (e) => {
    setFile(e.target.files[0])
    setMessage('')
    setError('')
  }

  const handleUpload = async (e) => {
    e.preventDefault()
    if (!file) {
      setError('Please select a file')
      return
    }

    setUploading(true)
    setError('')
    setMessage('')

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await axios.post('/api/v1/ingestion/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })

      setMessage('Document uploaded successfully!')
      setFile(null)
      document.getElementById('file-input').value = ''
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-6">Upload Document</h1>

        {message && (
          <div className="mb-4 bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded">
            {message}
          </div>
        )}

        {error && (
          <div className="mb-4 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleUpload} className="space-y-4">
          <div>
            <label htmlFor="file-input" className="block text-sm font-medium text-gray-700 mb-2">
              Select File (PDF, TXT, MD)
            </label>
            <input
              id="file-input"
              type="file"
              accept=".pdf,.txt,.md"
              onChange={handleFileChange}
              className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
            />
          </div>

          <button
            type="submit"
            disabled={uploading || !file}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {uploading ? 'Uploading...' : 'Upload Document'}
          </button>
        </form>
      </div>
    </div>
  )
}

