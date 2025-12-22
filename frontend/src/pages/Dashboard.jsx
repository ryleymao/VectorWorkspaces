import { useState, useEffect } from 'react'
import axios from 'axios'

export default function Dashboard() {
  const [workspace, setWorkspace] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchWorkspaceInfo()
  }, [])

  const fetchWorkspaceInfo = async () => {
    try {
      const response = await axios.get('/api/v1/workspace/info')
      setWorkspace(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load workspace info')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center py-12">Loading...</div>
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="border-4 border-dashed border-gray-200 rounded-lg p-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Dashboard</h1>
        
        {workspace && (
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <h2 className="text-xl font-semibold mb-4">Workspace Information</h2>
            <div className="space-y-2">
              <p><span className="font-medium">Name:</span> {workspace.name}</p>
              <p><span className="font-medium">Members:</span> {workspace.member_count}</p>
              {workspace.invite_code && (
                <p><span className="font-medium">Invite Code:</span> <code className="bg-gray-100 px-2 py-1 rounded">{workspace.invite_code}</code></p>
              )}
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-2">Documents</h3>
            <p className="text-gray-600">Upload and manage your knowledge base</p>
          </div>
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-2">Query</h3>
            <p className="text-gray-600">Ask questions about your documents</p>
          </div>
          <div className="bg-white shadow rounded-lg p-6">
            <h3 className="text-lg font-semibold mb-2">Workspace</h3>
            <p className="text-gray-600">Manage team members and settings</p>
          </div>
        </div>
      </div>
    </div>
  )
}

