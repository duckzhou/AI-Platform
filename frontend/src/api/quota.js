import request from './request'

export const getQuotaInfo = () => {
  return request.get('/quota/info')
}

export const getQuotaLogs = (params) => {
  return request.get('/quota/logs', { params })
}
