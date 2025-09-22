import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Products } from '../api/client'

export default function Home() {
	const [query, setQuery] = useState('')
	const [isSearching, setIsSearching] = useState(false)
	const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null
	const [recs, setRecs] = useState<{ source: string, items: { product_id: string, product_name: string, latest_price?: number }[] } | null>(null)
	const navigate = useNavigate()

	useEffect(() => {
		if (token) {
			Products.recommend({ limit: 5 }).then(setRecs).catch(() => setRecs(null))
		} else {
			setRecs(null)
		}
	}, [token])

	const handleSearch = () => {
		if (query.trim()) {
			setIsSearching(true)
			navigate(`/results?q=${encodeURIComponent(query)}`)
			setTimeout(() => setIsSearching(false), 1000)
		}
	}

	const handleKeyPress = (e: React.KeyboardEvent) => {
		if (e.key === 'Enter') {
			handleSearch()
		}
	}

	return (
		<div className="min-vh-100 d-flex align-items-center" style={{
			background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
			position: 'relative',
			overflow: 'hidden'
		}}>
			{/* Animated background elements */}
			<div style={{
				position: 'absolute',
				top: '-50%',
				left: '-50%',
				width: '200%',
				height: '200%',
				background: 'radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px)',
				backgroundSize: '50px 50px',
				animation: 'float 20s infinite linear'
			}} />
			
			<div className="container">
				<div className="row justify-content-center">
					<div className="col-lg-8 col-xl-6">
						{/* Hero Section */}
						<div className="text-center text-white mb-5">
							<h1 className="display-4 fw-bold mb-4" style={{
								textShadow: '2px 2px 4px rgba(0,0,0,0.3)',
								animation: 'fadeInUp 1s ease-out'
							}}>
								Find the Best Deals
							</h1>
							<p className="lead mb-4" style={{
								animation: 'fadeInUp 1s ease-out 0.2s both',
								textShadow: '1px 1px 2px rgba(0,0,0,0.3)'
							}}>
								Compare prices across India's top retailers and never overpay again
							</p>
						</div>

						{/* Search Section */}
						<div className="card shadow-lg border-0" style={{
							animation: 'fadeInUp 1s ease-out 0.4s both',
							background: 'rgba(255,255,255,0.95)',
							backdropFilter: 'blur(10px)'
						}}>
							<div className="card-body p-4">
								<div className="input-group input-group-lg">
									<input 
										className="form-control border-0 shadow-sm" 
										placeholder="Search for products... e.g., iPhone 14, MacBook Air" 
										value={query} 
										onChange={e => setQuery(e.target.value)}
										onKeyPress={handleKeyPress}
										style={{ fontSize: '1.1rem' }}
									/>
									<button 
										className={`btn btn-primary px-4 ${isSearching ? 'btn-loading' : ''}`}
										onClick={handleSearch}
										disabled={!query.trim() || isSearching}
										style={{
											background: 'linear-gradient(45deg, #667eea, #764ba2)',
											border: 'none',
											fontWeight: '600',
											transition: 'all 0.3s ease'
										}}
									>
										{isSearching ? (
											<>
												<span className="spinner-border spinner-border-sm me-2" role="status" />
												Searching...
											</>
										) : (
											<>
												🔍 Search
											</>
										)}
									</button>
								</div>
								
								{/* Popular searches */}
								<div className="mt-3">
									<p className="text-muted small mb-2">Popular searches:</p>
									<div className="d-flex flex-wrap gap-2">
										{['iPhone 14', 'MacBook Air', 'Samsung Galaxy', 'Sony Headphones'].map(term => (
											<button
												key={term}
												className="btn btn-outline-secondary btn-sm"
												onClick={() => setQuery(term)}
												style={{
													borderRadius: '20px',
													fontSize: '0.85rem',
													transition: 'all 0.2s ease'
												}}
											>
												{term}
											</button>
										))}
									</div>
								</div>
							</div>
						</div>

						{/* Features */}
						<div className="row mt-5 text-white text-center">
							<div className="col-md-4 mb-4" style={{ animation: 'fadeInUp 1s ease-out 0.6s both' }}>
								<div className="p-3">
									<div className="mb-3" style={{ fontSize: '2.5rem' }}>🛒</div>
									<h5>Compare Prices</h5>
									<p className="small">Find the best deals across multiple retailers</p>
								</div>
							</div>
							<div className="col-md-4 mb-4" style={{ animation: 'fadeInUp 1s ease-out 0.8s both' }}>
								<div className="p-3">
									<div className="mb-3" style={{ fontSize: '2.5rem' }}>📈</div>
									<h5>Price Tracking</h5>
									<p className="small">Monitor price changes and get alerts</p>
								</div>
							</div>
							<div className="col-md-4 mb-4" style={{ animation: 'fadeInUp 1s ease-out 1s both' }}>
								<div className="p-3">
									<div className="mb-3" style={{ fontSize: '2.5rem' }}>🎯</div>
									<h5>Smart Recommendations</h5>
									<p className="small">Discover products you'll love</p>
								</div>
							</div>
						</div>

						{/* Recommendations */}
						{recs && recs.items.length > 0 && (
							<div className="mt-5" style={{ animation: 'fadeInUp 1s ease-out 1.2s both' }}>
								<div className="card shadow-lg border-0" style={{
									background: 'rgba(255,255,255,0.95)',
									backdropFilter: 'blur(10px)'
								}}>
									<div className="card-body">
										<h4 className="text-center mb-4">
											❤️ You May Also Like
										</h4>
										<div className="row">
											{recs.items.map((it, index) => (
												<div key={it.product_id} className="col-md-6 mb-3">
													<a 
														href={`/product/${it.product_id}`}
														className="text-decoration-none"
														style={{
															animation: `fadeInUp 0.6s ease-out ${0.1 * index}s both`
														}}
													>
														<div className="card h-100 border-0 shadow-sm recommendation-card">
															<div className="card-body p-3">
																<h6 className="card-title text-dark mb-2">{it.product_name}</h6>
																{typeof it.latest_price === 'number' && (
																	<div className="d-flex align-items-center">
																		<span className="badge bg-success fs-6">
																			₹{Math.round(it.latest_price).toLocaleString()}
																		</span>
																	</div>
																)}
															</div>
														</div>
													</a>
												</div>
											))}
										</div>
									</div>
								</div>
							</div>
						)}
					</div>
				</div>
			</div>

			<style jsx>{`
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

				@keyframes float {
					0% { transform: translate(-50%, -50%) rotate(0deg); }
					100% { transform: translate(-50%, -50%) rotate(360deg); }
				}

				.btn-loading {
					opacity: 0.7;
					transform: scale(0.98);
				}

				.recommendation-card {
					transition: all 0.3s ease;
					cursor: pointer;
				}

				.recommendation-card:hover {
					transform: translateY(-5px);
					box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
				}

				.btn-outline-secondary:hover {
					background: linear-gradient(45deg, #667eea, #764ba2);
					border-color: transparent;
					color: white;
				}

				.form-control:focus {
					box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
					border-color: #667eea;
				}
			`}</style>
		</div>
	)
}