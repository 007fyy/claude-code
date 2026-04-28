import http from './http'

export const sendCode = (phone) => http.post('/auth/send-code', { phone })

export const login = (phone, code) => http.post('/auth/login', { phone, code })

export const getMe = () => http.get('/user/me')

export const updateMe = (data) => http.put('/user/me', data)

export const updatePrefs = (data) => http.patch('/user/prefs', data)

export const listAddress = () => http.get('/user/address')

export const createAddress = (data) => http.post('/user/address', data)

export const updateAddress = (id, data) => http.put(`/user/address/${id}`, data)

export const deleteAddress = (id) => http.delete(`/user/address/${id}`)

export const setDefaultAddress = (id) => http.patch(`/user/address/${id}/default`)
