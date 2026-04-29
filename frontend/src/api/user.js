import http from './http'

export const sendCode = (email) => {
  return http.post('/auth/send-code', { email })
}

export const login = (data) => {
  return http.post('/auth/login', data)
}

export const verify = (data) => {
  return http.post('/auth/verify', data)
}

export const getMe = () => {
  return http.get('/user/me')
}

export const updateMe = (data) => {
  return http.put('/user/me', data)
}

export const updatePrefs = (data) => {
  return http.patch('/user/prefs', data)
}

export const changePassword = (data) => {
  return http.put('/user/password', data)
}

export const listAddress = () => {
  return http.get('/user/address')
}

export const createAddress = (data) => {
  return http.post('/user/address', data)
}

export const updateAddress = (id, data) => {
  return http.put(`/user/address/${id}`, data)
}

export const deleteAddress = (id) => {
  return http.delete(`/user/address/${id}`)
}

export const setDefaultAddress = (id) => {
  return http.patch(`/user/address/${id}/default`)
}
