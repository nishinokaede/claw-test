import { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'
import './passwordToggle.css'

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [userInfo, setUserInfo] = useState(null)

  const API_BASE_URL = 'http://122.51.223.247:8000'

  // 创建axios实例
  const api = axios.create({
    baseURL: API_BASE_URL,
  })

  // 请求拦截器 - 自动添加token到header
  api.interceptors.request.use(
    (config) => {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers['Authorization'] = `Bearer ${token}`
      }
      return config
    },
    (error) => {
      return Promise.reject(error)
    }
  )

  // 响应拦截器 - 自动处理token刷新
  api.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config

      // 如果是401错误且不是refresh请求，尝试刷新token
      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true

        try {
          // 尝试使用refresh_token获取新token
          const refresh_token = localStorage.getItem('refresh_token')
          if (!refresh_token) {
            throw new Error('No refresh token')
          }

          const refreshResponse = await axios.post(
            `${API_BASE_URL}/refresh`,
            {},
            {
              headers: {
                'Authorization': `Bearer ${refresh_token}`
              }
            }
          )

          // 保存新的tokens
          const { access_token, refresh_token: new_refresh_token } = refreshResponse.data
          localStorage.setItem('access_token', access_token)
          localStorage.setItem('refresh_token', new_refresh_token)

          // 重试原始请求
          originalRequest.headers['Authorization'] = `Bearer ${access_token}`
          return api(originalRequest)

        } catch (refreshError) {
          // 刷新token失败，清除登录状态
          console.error('Token刷新失败:', refreshError)
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          setIsLoggedIn(false)
          setUserInfo(null)
          return Promise.reject(refreshError)
        }
      }

      return Promise.reject(error)
    }
  )

  // 页面加载时检查token
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    if (token) {
      fetchUserInfo()
    }
  }, [])

  const fetchUserInfo = async () => {
    try {
      const response = await api.get('/users/me')
      setUserInfo(response.data)
      setIsLoggedIn(true)
    } catch (err) {
      console.error('获取用户信息失败:', err)
      // 如果是401错误，说明token无效，清除登录状态
      if (err.response?.status === 401) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        setIsLoggedIn(false)
        setUserInfo(null)
      }
    }
  }

  const handleLogin = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const response = await api.post('/login', {
        username,
        password
      })

      // 保存access_token和refresh_token
      const { access_token, refresh_token } = response.data
      localStorage.setItem('access_token', access_token)
      localStorage.setItem('refresh_token', refresh_token)

      setUserInfo({ username })
      setIsLoggedIn(true)
      setUsername('')
      setPassword('')

      console.log('登录成功，Token已保存')
      console.log('Access Token (30分钟有效):', access_token.substring(0, 50) + '...')
      console.log('Refresh Token (90天有效):', refresh_token.substring(0, 50) + '...')

    } catch (err) {
      console.error('登录错误:', err)
      setError(err.response?.data?.detail || '登录失败，请检查用户名和密码')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = async () => {
    try {
      // 调用后端登出接口
      const token = localStorage.getItem('access_token')
      if (token) {
        await api.post('/logout')
      }
    } catch (err) {
      console.error('登出请求失败:', err)
    } finally {
      // 清除本地存储
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      setIsLoggedIn(false)
      setUserInfo(null)
      console.log('已登出')
    }
  }

  // 切换密码显示/隐藏
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword)
  }

  // 显示token过期时间（用于演示）
  const showTokenInfo = () => {
    const accessToken = localStorage.getItem('access_token')
    const refreshToken = localStorage.getItem('refresh_token')
    if (accessToken && refreshToken) {
      return (
        <div className="token-info">
          <p>🔐 访问Token: 有效期30分钟</p>
          <p>🔄 刷新Token: 有效期90天</p>
          <p>✅ 自动刷新: 已启用</p>
          <p style={{fontSize: '12px', marginTop: '10px'}}>
            💡 即使访问token过期，系统也会自动使用刷新token获取新token，无需重新登录
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="App">
      <div className="container">
        <h1>JWT 认证系统 + 自动刷新</h1>

        {isLoggedIn ? (
          <div className="dashboard">
            <div className="success-message">
              <h2>🎉 登录成功！</h2>
              <p>欢迎回来，{userInfo?.username}！</p>
              {showTokenInfo()}
            </div>
            <button className="logout-btn" onClick={handleLogout}>
              退出登录
            </button>
          </div>
        ) : (
          <div className="login-form">
            <form onSubmit={handleLogin}>
              <div className="form-group">
                <label htmlFor="username">用户名</label>
                <input
                  type="text"
                  id="username"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  placeholder="请输入用户名（默认：admin）"
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="password">密码</label>
                <div className="password-input-wrapper">
                  <input
                    type={showPassword ? "text" : "password"}
                    id="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="请输入密码（默认：admin123）"
                    required
                  />
                  <button
                    type="button"
                    className="password-toggle-btn"
                    onClick={togglePasswordVisibility}
                    aria-label={showPassword ? "隐藏密码" : "显示密码"}
                  >
                    {showPassword ? "👁️" : "🙈"}
                  </button>
                </div>
              </div>

              {error && <div className="error-message">{error}</div>}

              <button type="submit" className="login-btn" disabled={loading}>
                {loading ? '登录中...' : '登录'}
              </button>
            </form>

            <div className="info-box">
              <h3>测试账号</h3>
              <p>用户名：admin</p>
              <p>密码：admin123</p>
            </div>

            <div className="feature-box">
              <h3>✨ 新功能：自动Token刷新</h3>
              <ul>
                <li>✅ 访问Token有效期：30分钟</li>
                <li>✅ 刷新Token有效期：90天</li>
                <li>✅ Token过期自动刷新，无需重新登录</li>
                <li>✅ 刷新Token也过期才需重新登录</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
