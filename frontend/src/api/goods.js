import http from './http'

export const getGoodsList = (params) => http.get('/goods/list', { params })
export const getGoodsDetail = (spuId) => http.get(`/goods/${spuId}`)

export const adminListGoods = () => http.get('/goods/admin/list')
export const adminStats = () => http.get('/goods/admin/stats')
export const getArPresets = () => http.get('/goods/admin/ar-presets')

export const createSpu = (data) => http.post('/goods/admin/spu', data)
export const updateSpu = (spuId, data) => http.put(`/goods/admin/spu/${spuId}`, data)
export const toggleSpuStatus = (spuId, status) =>
  http.patch(`/goods/admin/spu/${spuId}/status`, null, { params: { status } })

export const createSku = (spuId, data) => http.post(`/goods/admin/spu/${spuId}/sku`, data)
export const updateSku = (skuId, data) => http.put(`/goods/admin/sku/${skuId}`, data)
export const deleteSku = (skuId) => http.delete(`/goods/admin/sku/${skuId}`)

export const uploadArAsset = (skuId, file) => {
  const fd = new FormData()
  fd.append('file', file)
  return http.post(`/goods/admin/sku/${skuId}/ar-asset`, fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}
export const updateArParams = (skuId, params) =>
  http.put(`/goods/admin/sku/${skuId}/ar-params`, null, { params })

