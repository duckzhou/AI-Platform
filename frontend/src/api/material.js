import request from './request'

export const getMaterials = (params) => {
  return request.get('/materials', { params })
}

export const uploadMaterial = (data) => {
  return request.post('/materials/upload', data, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}

export const deleteMaterial = (materialId) => {
  return request.delete(`/materials/${materialId}`)
}

export const getCategories = () => {
  return request.get('/materials/categories')
}

export const getTags = () => {
  return request.get('/materials/tags')
}
