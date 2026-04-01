import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getProfile } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  // State
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)
  const quota = ref({
    free_quota: 0,
    remaining_quota: 0,
    total_recharge: 0,
    total_used: 0
  })

  // Getters
  const isLoggedIn = computed(() => !!token.value)
  const username = computed(() => userInfo.value?.username || '用户')

  // Actions
  const setToken = (newToken) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
  }

  const clearToken = () => {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  const login = async (account, password) => {
    const res = await loginApi({ account, password })
    if (res.code === 200) {
      setToken(res.data.access_token)
      userInfo.value = res.data.user
      return true
    }
    return false
  }

  const logout = () => {
    clearToken()
  }

  const fetchProfile = async () => {
    const res = await getProfile()
    if (res.code === 200) {
      userInfo.value = res.data
    }
  }

  const setQuota = (newQuota) => {
    quota.value = newQuota
  }

  return {
    token,
    userInfo,
    quota,
    isLoggedIn,
    username,
    setToken,
    clearToken,
    login,
    logout,
    fetchProfile,
    setQuota
  }
})
