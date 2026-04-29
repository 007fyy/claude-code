import http from './http'

export const getGoodsList = (params) => {
  return http.get('/goods/list', { params })
}

export const getGoodsDetail = (spuId) => {
  return http.get(`/goods/${spuId}`)
}
