import request from './request'

export const register = (data) => {
  return request.post('/auth/register', data)
}

export const login = (data) => {
  return request.post('/auth/login', data)
}

export const getProfile = () => {
  return request.get('/auth/profile')
}

export const updateProfile = (data) => {
  return request.put('/auth/profile', data)
}

export const changePassword = (data) => {
  return request.post('/auth/change-password', data)
}
