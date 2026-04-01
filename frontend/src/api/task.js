import request from './request'

export const getTaskFlows = (params) => {
  return request.get('/tasks/flows', { params })
}

export const getTasks = (params) => {
  return request.get('/tasks', { params })
}

export const getTaskDetail = (taskId) => {
  return request.get(`/tasks/${taskId}`)
}

export const createTextToImage = (data) => {
  return request.post('/tasks/text-to-image', data, { timeout: 120000 })
}

export const createImageToImage = (data) => {
  return request.post('/tasks/image-to-image', data, { timeout: 120000 })
}

export const createImageToVideo = (data) => {
  return request.post('/tasks/image-to-video', data, { timeout: 30000 })
}

export const createTextToVideo = (data) => {
  return request.post('/tasks/text-to-video', data)
}

export const createWorkflow = (data) => {
  return request.post('/tasks/workflow', data)
}

export const cancelTask = (taskId) => {
  return request.post(`/tasks/${taskId}/cancel`)
}

export const retryTask = (taskId) => {
  return request.post(`/tasks/${taskId}/retry`)
}

export const pollTaskStatus = (taskId) => {
  return request.post(`/tasks/${taskId}/poll`)
}
