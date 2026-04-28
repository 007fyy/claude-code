import http from './http'

export const addToCart = (data) => http.post('/cart/add', data)
export const getCartList = () => http.get('/cart/list')
export const updateCart = (data) => http.put('/cart/update', data)
export const removeCart = (cartItemId) => http.delete(`/cart/remove/${cartItemId}`)
