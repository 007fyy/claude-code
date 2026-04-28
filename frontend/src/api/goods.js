import http from './http'

export const getGoodsList = (params) => http.get('/goods/list', { params })
export const getGoodsDetail = (spuId) => http.get(`/goods/${spuId}`)
