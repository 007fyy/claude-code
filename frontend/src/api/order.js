import http from './http'

export const createOrder = (data) => http.post('/order/create', data)
export const payOrder = (data) => http.post('/order/pay', data)
export const cancelOrder = (orderId) =>
  http.post('/order/cancel', null, { params: { order_id: orderId } })
export const getOrderList = (params) => http.get('/order/list', { params })
export const getOrderDetail = (orderId) => http.get(`/order/${orderId}`)
export const applyRefund = (data) => http.post('/order/refund/apply', data)
