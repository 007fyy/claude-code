import http from './http'

export const toggleFavorite = (spuId) => {
  return http.post('/favorite/toggle', { spu_id: spuId })
}

export const getFavoriteList = () => {
  return http.get('/favorite/list')
}

export const checkFavorite = (spuId) => {
  return http.get('/favorite/check', { params: { spu_id: spuId } })
}
