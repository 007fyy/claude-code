import http from './http'

export const recordView = (spuId) => {
  return http.post('/history/record', { spu_id: spuId })
}

export const getHistoryList = () => {
  return http.get('/history/list')
}

export const clearHistory = () => {
  return http.delete('/history/clear')
}
