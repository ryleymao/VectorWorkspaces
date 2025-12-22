import { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const AuthContext = createContext()

export function useAuth() {
  return useContext(AuthContext)
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [token, setToken] = useState(localStorage.getItem('token'))
  const [loading, setLoading] = useState(true)

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      setLoading(false)
    } else {
      setLoading(false)
    }
  }, [token])

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API_URL}/api/v1/auth/login`, {
        email,
        password
      })
      const { access_token } = response.data
      setToken(access_token)
      localStorage.setItem('token', access_token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Login failed' }
    }
  }

  const register = async (email, name, password, workspaceName) => {
    try {
      const response = await axios.post(`${API_URL}/api/v1/auth/register`, {
        email,
        name,
        password,
        tenant_name: workspaceName
      })
      const { access_token } = response.data
      setToken(access_token)
      localStorage.setItem('token', access_token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
      return { success: true }
    } catch (error) {
      return { success: false, error: error.response?.data?.detail || 'Registration failed' }
    }
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('token')
    delete axios.defaults.headers.common['Authorization']
  }

  const value = {
    token,
    user,
    login,
    register,
    logout,
    loading
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

