/**
 * 在浏览器控制台粘贴此代码来快速登录
 * 用户名: admin
 * 密码: admin123
 */

(async function() {
  try {
    const response = await fetch('http://localhost:8000/api/auth/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: 'admin',
        password: 'admin123'
      })
    })

    const data = await response.json()

    if (data.data && data.data.access) {
      localStorage.setItem('access_token', data.data.access)
      localStorage.setItem('refresh_token', data.data.refresh)
      console.log('✅ 登录成功！用户:', data.data.user.username)
      console.log('📝 Token 已保存到 localStorage')
      console.log('🔄 请刷新页面或访问管理后台')
      console.log('   管理后台: http://localhost:5173/admin')
      console.log('   创建文章: http://localhost:5173/admin/posts/new')

      // 可选：自动刷新页面
      // location.reload()
    } else {
      console.error('❌ 登录失败:', data)
    }
  } catch (error) {
    console.error('❌ 请求失败:', error)
  }
})()
