import axios from 'axios'
import { useEffect, useState } from 'react'
import { Link, useLocation } from 'react-router-dom'

type SearchItem = {
	product_id: string
	product_name: string
	site: string
	price: number
	url: string
}

type SearchResponse = {
	query: string
	items: SearchItem[]
	best_price?: SearchItem | null
}

export default function Results() {
	const { search } = useLocation()
	const params = new URLSearchParams(search)
	const q = params.get('q') || ''
	const [data, setData] = useState<SearchResponse | null>(null)
	const [isLoading, setIsLoading] = useState(false)

	useEffect(() => {
		if (!q) return
		setIsLoading(true)
		axios.get(`/api/search?query=${encodeURIComponent(q)}`)
			.then(r => setData(r.data))
			.finally(() => setIsLoading(false))
	}, [q])

	useEffect(() => {
		// Add CSS animations
		const style = document.createElement('style');
		style.textContent = `
			@keyframes fadeInUp {
				from {
					opacity: 0;
					transform: translateY(30px);
				}
				to {
					opacity: 1;
					transform: translateY(0);
				}
			}
		`;
		document.head.appendChild(style);
		return () => {
			document.head.removeChild(style);
		};
	}, [])

	if (!q) return (
		<div className="container mt-5">
			<div className="alert alert-warning">
				<h4>No search query</h4>
				<p>Please enter a search term to find products.</p>
			</div>
		</div>
	)

	if (isLoading) return (
		<div className="container mt-5">
			<div className="d-flex justify-content-center align-items-center" style={{ minHeight: '400px' }}>
				<div className="text-center">
					<div className="spinner-border text-primary mb-3" style={{ width: '3rem', height: '3rem' }} role="status">
						<span className="visually-hidden">Loading...</span>
					</div>
					<h4>Searching for "{q}"...</h4>
					<p className="text-muted">Finding the best deals across retailers</p>
				</div>
			</div>
		</div>
	)

	if (!data) return (
		<div className="container mt-5">
			<div className="alert alert-danger">
				<h4>Search failed</h4>
				<p>Unable to search for products. Please try again.</p>
			</div>
		</div>
	)

	return (
		<div className="container mt-4">
			{/* Search Header */}
			<div className="row mb-4">
				<div className="col-12">
					<div className="card shadow-lg border-0" style={{
						background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
						color: 'white'
					}}>
						<div className="card-body p-4">
							<h1 className="display-6 fw-bold mb-2">
								🔍 Search Results
							</h1>
							<p className="lead mb-0">Found {data.items.length} results for "{data.query}"</p>
						</div>
					</div>
				</div>
			</div>

			{/* Best Price Highlight */}
			{data.best_price && (
				<div className="row mb-4">
					<div className="col-12">
						<div className="alert alert-success border-0 shadow-sm" style={{
							background: 'linear-gradient(135deg, #28a745, #20c997)',
							color: 'white'
						}}>
							<div className="d-flex align-items-center">
								<div className="me-3" style={{ fontSize: '2rem' }}>🏆</div>
								<div>
									<h5 className="mb-1 fw-bold">Best Deal Found!</h5>
									<p className="mb-0">
										{data.best_price.product_name} at {data.best_price.site} for ₹{data.best_price.price.toLocaleString()}
									</p>
								</div>
							</div>
						</div>
					</div>
				</div>
			)}

			{/* Results */}
			{data.items.length === 0 ? (
				<div className="row">
					<div className="col-12">
						<div className="card shadow-lg border-0">
							<div className="card-body text-center p-5">
								<div className="mb-4" style={{ fontSize: '4rem' }}>😔</div>
								<h3 className="mb-3">No Results Found</h3>
								<p className="text-muted mb-4">
									We couldn't find any products matching "{data.query}". Try different keywords or check your spelling.
								</p>
								<Link to="/" className="btn btn-primary btn-lg px-4">
									🔍 Search Again
								</Link>
							</div>
						</div>
					</div>
				</div>
			) : (
				<div className="row">
					{data.items.map((item, index) => (
						<div key={`${item.product_id}-${item.site}`} className="col-lg-6 col-xl-4 mb-4">
							<div 
								className={`card h-100 border-0 shadow-sm ${
									data.best_price && item.site === data.best_price.site && item.product_id === data.best_price.product_id 
										? 'border-success' 
										: ''
								}`}
								style={{
									animation: `fadeInUp 0.6s ease-out ${0.1 * index}s both`,
									transition: 'all 0.3s ease',
									background: data.best_price && item.site === data.best_price.site && item.product_id === data.best_price.product_id 
										? 'linear-gradient(135deg, rgba(40, 167, 69, 0.05), rgba(32, 201, 151, 0.05))' 
										: undefined
								}}
								onMouseEnter={(e) => {
									e.currentTarget.style.transform = 'translateY(-5px)';
									e.currentTarget.style.boxShadow = '0 12px 30px rgba(0,0,0,0.15)';
								}}
								onMouseLeave={(e) => {
									e.currentTarget.style.transform = 'translateY(0)';
									e.currentTarget.style.boxShadow = '';
								}}
							>
								<div className="card-body p-4">
									{/* Site Badge */}
									<div className="d-flex justify-content-between align-items-start mb-3">
										<span className="badge bg-primary fs-6 px-3 py-2">
											{getSiteIcon(item.site)} {item.site}
										</span>
										{data.best_price && item.site === data.best_price.site && item.product_id === data.best_price.product_id && (
											<span className="badge bg-success fs-6 px-3 py-2">
												🏆 Best Price
											</span>
										)}
									</div>

									{/* Product Info */}
									<h5 className="card-title mb-3">
										<Link 
											to={`/enhanced-product/${item.product_id}?name=${encodeURIComponent(item.product_name)}`}
											className="text-decoration-none text-dark"
										>
											{item.product_name}
										</Link>
									</h5>

									{/* Price */}
									<div className="mb-4">
										<div className="display-6 fw-bold text-primary mb-1">
											₹{item.price.toLocaleString()}
										</div>
										<small className="text-muted">Current price</small>
									</div>

									{/* Actions */}
									<div className="d-grid gap-2">
										<Link 
											to={`/enhanced-product/${item.product_id}?name=${encodeURIComponent(item.product_name)}`}
											className="btn btn-success btn-lg"
											style={{ borderRadius: '10px' }}
										>
											🤖 Smart Analysis & 30-Day Forecast
										</Link>
										<a 
											href={item.url} 
											target="_blank" 
											rel="noopener noreferrer"
											className="btn btn-primary"
											style={{ 
												background: 'linear-gradient(135deg, #667eea, #764ba2)',
												border: 'none',
												borderRadius: '10px'
											}}
										>
											🛒 Buy Now
										</a>
									</div>
								</div>
							</div>
						</div>
					))}
				</div>
			)}


		</div>
	)
}

function getSiteIcon(site: string): string {
	const siteLower = site.toLowerCase()
	if (siteLower.includes('amazon')) return '🛒'
	if (siteLower.includes('flipkart')) return '🛍️'
	if (siteLower.includes('reliance')) return '🏪'
	if (siteLower.includes('croma')) return '📱'
	return '🛒'
}