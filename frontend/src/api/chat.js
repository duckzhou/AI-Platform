import request from './request'

export const getChatModels = () => {
  return request.get('/chat/models')
}

export const getSessions = (params) => {
  return request.get('/chat/sessions', { params })
}

export const createSession = () => {
  return request.post('/chat/sessions')
}

export const getMessages = (sessionId, params) => {
  return request.get(`/chat/sessions/${sessionId}/messages`, { params })
}

export const sendMessage = (data) => {
  return request.post('/chat/send', data)
}

export const sendMessageStream = (data) => {
  return fetch('/api/v1/chat/send-stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify(data)
  })
}

export const renameSession = (sessionId, data) => {
  return request.put(`/chat/sessions/${sessionId}`, data)
}

export const deleteSession = (sessionId) => {
  return request.delete(`/chat/sessions/${sessionId}`)
}
