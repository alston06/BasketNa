import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use(config => {
	const token = localStorage.getItem('token')
	if (token) config.headers.Authorization = `Bearer ${token}`
	return config
})

export const Auth = {
	login: (email: string, password: string) => api.post('/user/login', new URLSearchParams({ username: email, password })).then(r => r.data),
	signup: (email: string, password: string) => api.post('/user/signup', { email, password }).then(r => r.data),
}

export const Products = {
	search: (query: string) => api.get('/search', { params: { query } }).then(r => r.data),
	forecast: (productId: string) => api.get(`/forecast/${productId}`).then(r => r.data),
	track: (productId: string) => api.post(`/track/${productId}`).then(r => r.data),
	tracked: () => api.get('/me/tracked').then(r => r.data),
}

export default api 