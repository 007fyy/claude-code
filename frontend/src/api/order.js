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

export const getOrderStatusCounts = () => {
  return http.get('/order/status_counts')
}

export const applyRefund = (data) => {
  return http.post('/order/refund/apply', data)
}

export const confirmReceive = (orderId) => {
  return http.post('/order/confirm_receive', null, { params: { order_id: orderId } })
}

export const adminOrderList = (params) => {
  return http.get('/order/admin/list', { params })
}

export const adminShipOrder = (orderId, trackingNo = '') => {
  return http.post('/order/admin/ship', null, { params: { order_id: orderId, tracking_no: trackingNo } })
}

export const adminCompleteOrder = (orderId) => {
  return http.post('/order/admin/complete', null, { params: { order_id: orderId } })
}

export const adminApproveRefund = (orderId) => {
  return http.post('/order/admin/refund/approve', null, { params: { order_id: orderId } })
}
