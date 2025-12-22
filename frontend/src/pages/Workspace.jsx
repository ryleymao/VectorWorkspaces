import { useState, useEffect } from 'react'
import axios from 'axios'

export default function Workspace() {
  const [workspace, setWorkspace] = useState(null)
  const [members, setMembers] = useState([])
  const [inviteCode, setInviteCode] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [message, setMessage] = useState('')

  useEffect(() => {
    fetchData()
  }, [])

  const fetchData = async () => {
    try {
      const [workspaceRes, membersRes] = await Promise.all([
        axios.get('/api/v1/workspace/info'),
        axios.get('/api/v1/workspace/members')
      ])
      setWorkspace(workspaceRes.data)
      setMembers(membersRes.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load workspace data')
    } finally {
      setLoading(false)
    }
  }

  const generateInviteCode = async () => {
    try {
      const response = await axios.post('/api/v1/workspace/invite-code')
      setInviteCode(response.data.invite_code)
      setMessage('Invite code generated!')
      setTimeout(() => setMessage(''), 3000)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate invite code')
    }
  }

  if (loading) {
    return <div className="flex items-center justify-center py-12">Loading...</div>
  }

  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="space-y-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-6">Workspace Settings</h1>

          {workspace && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Workspace Name</label>
                <p className="mt-1 text-gray-900">{workspace.name}</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Member Count</label>
                <p className="mt-1 text-gray-900">{workspace.member_count}</p>
              </div>
            </div>
          )}
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Invite Code</h2>
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
          <div className="flex items-center space-x-4">
            {inviteCode && (
              <code className="flex-1 bg-gray-100 px-4 py-2 rounded font-mono text-sm">
                {inviteCode}
              </code>
            )}
            <button
              onClick={generateInviteCode}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Generate Invite Code
            </button>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Members</h2>
          <div className="space-y-2">
            {members.map((member) => (
              <div key={member.id} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <div>
                  <p className="font-medium">{member.name}</p>
                  <p className="text-sm text-gray-600">{member.email}</p>
                </div>
                <span className="px-2 py-1 text-xs font-semibold rounded bg-blue-100 text-blue-800">
                  {member.role}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

