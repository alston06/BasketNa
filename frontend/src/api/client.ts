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
	view: (productId: string) => api.post(`/views/${productId}`).then(r => r.data),
	recommend: (params: { productId?: string, limit?: number }) => api.get('/recommendations', { params: { product_id: params.productId, limit: params.limit } }).then(r => r.data),
	
	// New enhanced API endpoints
	availableProducts: () => api.get('/products/available').then(r => r.data),
	bestDeals: (topN = 10) => api.get('/recommendations/best-deals', { params: { top_n: topN } }).then(r => r.data),
	forecast30Day: (productName?: string) => api.get('/forecast/30-day', { params: productName ? { product_name: productName } : {} }).then(r => r.data),
	enhancedForecast: (productName: string, retailer?: string, days = 30) => api.get(`/forecast/enhanced/${encodeURIComponent(productName)}`, { 
		params: { ...(retailer && { retailer }), days } 
	}).then(r => r.data),
	priceAnalysis: (productName: string, daysBack = 30) => api.get(`/analysis/price-trend/${encodeURIComponent(productName)}`, { 
		params: { days_back: daysBack } 
	}).then(r => r.data),
	competitiveAnalysis: (productName: string) => api.get(`/analysis/competitive/${encodeURIComponent(productName)}`).then(r => r.data),
	
	// New personalized recommendation endpoints with website links
	personalizedRecommendations: (limit = 10) => api.get('/recommendations/personalized', { params: { limit } }).then(r => r.data),
	sessionRecommendations: (sessionId: string, limit = 10) => api.get('/recommendations/session', { params: { session_id: sessionId, limit } }).then(r => r.data),
	categoryRecommendations: (category: string, limit = 5, excludeProducts: string[] = []) => api.get(`/recommendations/category/${encodeURIComponent(category)}`, { 
		params: { limit, exclude_products: excludeProducts } 
	}).then(r => r.data),
	trendingRecommendations: (limit = 10) => api.get('/recommendations/trending', { params: { limit } }).then(r => r.data),
	recordProductView: (productId: string, sessionId?: string) => api.post(`/activity/view/${productId}`, {}, { 
		params: sessionId ? { session_id: sessionId } : {} 
	}).then(r => r.data),
}

// AI Agent Tools endpoints
export const AITools = {
	getCoupons: (productName: string) => api.get(`/ai-tools/coupons/${encodeURIComponent(productName)}`).then(r => r.data),
	getReviews: (productName: string, site: 'all' | 'amazon' | 'flipkart' = 'all') => api.get(`/ai-tools/reviews/${encodeURIComponent(productName)}`, { params: { site } }).then(r => r.data),
	getComprehensiveAnalysis: (productName: string) => api.get(`/ai-tools/comprehensive/${encodeURIComponent(productName)}`).then(r => r.data),
	checkHealth: () => api.get('/ai-tools/health').then(r => r.data),
}

export default api 