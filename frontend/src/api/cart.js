import http from './http'

export const addToCart = (data) => {
  return http.post('/cart/add', data)
}

export const getCartList = () => {
  return http.get('/cart/list')
}

export const updateCart = (data) => {
  return http.put('/cart/update', data)
}

export const removeCart = (cartItemId) => {
  return http.delete(`/cart/remove/${cartItemId}`)
}
