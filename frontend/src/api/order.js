import http from './http'

export const createOrder = (data) => {
  return http.post('/order/create', data)
}

export const payOrder = (data) => {
  return http.post('/order/pay', data)
}

export const cancelOrder = (orderId) => {
  return http.post('/order/cancel', null, { params: { order_id: orderId } })
}

export const getOrderList = (params) => {
  return http.get('/order/list', { params })
}

export const getOrderDetail = (orderId) => {
  return http.get(`/order/${orderId}`)
}

export const applyRefund = (data) => {
  return http.post('/order/refund/apply', data)
}
