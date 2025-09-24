import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Products } from '../api/client'
import { PersonalizedRecommendationResponse } from '../types/recommendations'

type Tracked = { id: number, product_id: string, product_name: string, created_at: string }

type BestDeal = {
	product_name: string
	retailer: string
	current_price: number
	savings_amount: number
	savings_percentage: number
	date: string
}



export default function Dashboard() {
	const [items, setItems] = useState<Tracked[]>([])
	const [bestDeals, setBestDeals] = useState<BestDeal[]>([])
	const [personalizedRecommendations, setPersonalizedRecommendations] = useState<PersonalizedRecommendationResponse | null>(null)
	const [loading, setLoading] = useState(true)
	const [activeTab, setActiveTab] = useState<'basket' | 'deals' | 'smart'>('basket')

	useEffect(() => {
		const loadData = async () => {
			try {
				// Load tracked items if user is logged in
				const token = localStorage.getItem('token')
				if (token) {
					const trackedItems = await Products.tracked()
					setItems(trackedItems)
				}

				// Load best deals (available to all users)
				const dealsResponse = await Products.bestDeals(8)
				setBestDeals(dealsResponse.best_deals || [])

				// Load personalized recommendations if user is logged in
				if (token) {
					try {
						const personalizedResponse = await Products.personalizedRecommendations(10)
						setPersonalizedRecommendations(personalizedResponse)
					} catch (error) {
						console.error('Error loading personalized recommendations:', error)
					}
				}
			} catch (error) {
				console.error('Error loading dashboard data:', error)
			} finally {
				setLoading(false)
			}
		}

		loadData()
	}, [])



	const formatCurrency = (amount: number) => {
		return `₹${amount.toLocaleString('en-IN')}`
	}

	if (loading) {
		return (
			<div className="d-flex justify-content-center py-5">
				<div className="spinner-border text-primary" role="status">
					<span className="visually-hidden">Loading...</span>
				</div>
			</div>
		)
	}

	return (
		<div className="container py-4">
			<div className="row mb-4">
				<div className="col-12">
					<h2 className="mb-3">🏪 Price Intelligence Dashboard</h2>
					<p className="text-muted">Your one-stop destination for smart shopping decisions</p>
				</div>
			</div>

			{/* Navigation Tabs */}
			<ul className="nav nav-tabs mb-4">
				<li className="nav-item">
					<button 
						className={`nav-link ${activeTab === 'basket' ? 'active' : ''}`}
						onClick={() => setActiveTab('basket')}
					>
						🛒 Your Basket {items.length > 0 && `(${items.length})`}
					</button>
				</li>
				<li className="nav-item">
					<button 
						className={`nav-link ${activeTab === 'deals' ? 'active' : ''}`}
						onClick={() => setActiveTab('deals')}
					>
						🔥 Best Deals Today
					</button>
				</li>

				<li className="nav-item">
					<button 
						className={`nav-link ${activeTab === 'smart' ? 'active' : ''}`}
						onClick={() => setActiveTab('smart')}
					>
						🧠 Smart Recommendations
					</button>
				</li>
			</ul>

			{/* Tab Content */}
			{activeTab === 'basket' && (
				<div className="tab-pane fade show active">
					{!localStorage.getItem('token') ? (
						<div className="alert alert-info">
							<h5>🔐 Login Required</h5>
							<p>Please login to view and manage your tracked products.</p>
						</div>
					) : items.length === 0 ? (
						<div className="alert alert-light">
							<h5>📦 Your Basket is Empty</h5>
							<p>Start tracking products to see personalized price alerts and forecasts here.</p>
						</div>
					) : (
						<div className="card">
							<div className="card-header">
								<h5 className="mb-0">📊 Tracked Products</h5>
							</div>
							<div className="card-body p-0">
								<div className="table-responsive">
									<table className="table table-hover mb-0">
										<thead className="table-light">
											<tr>
												<th>Product</th>
												<th>Tracked Since</th>
												<th>Actions</th>
											</tr>
										</thead>
										<tbody>
											{items.map(item => (
												<tr key={item.id}>
													<td>
														<strong>{item.product_name}</strong>
														<br />
														<small className="text-muted">ID: {item.product_id}</small>
													</td>
													<td>{new Date(item.created_at).toLocaleDateString()}</td>
													<td>
														<Link 
															to={`/enhanced-product/${item.product_id}?name=${encodeURIComponent(item.product_name)}`} 
															className="btn btn-sm btn-success"
														>
															🤖 Smart Analysis
														</Link>
													</td>
												</tr>
											))}
										</tbody>
									</table>
								</div>
							</div>
						</div>
					)}
				</div>
			)}

			{activeTab === 'deals' && (
				<div className="tab-pane fade show active">
					<div className="row">
						<div className="col-12 mb-3">
							<div className="alert alert-success">
								<h5>🎯 Today's Best Deals</h5>
								<p className="mb-0">Save big with these current best prices across all retailers!</p>
							</div>
						</div>
						{bestDeals.map((deal, index) => (
							<div key={index} className="col-lg-6 col-xl-4 mb-4">
								<div className="card h-100 border-success">
									<div className="card-body">
										<h6 className="card-title">{deal.product_name}</h6>
										<div className="mb-3">
											<span className="h5 text-success">{formatCurrency(deal.current_price)}</span>
											<div className="text-muted small">at {deal.retailer}</div>
										</div>
										<div className="mb-2">
											<span className="badge bg-success me-2">
												Save {formatCurrency(deal.savings_amount)}
											</span>
											<span className="badge bg-light text-dark">
												{deal.savings_percentage}% off
											</span>
										</div>
										<div className="text-muted small">
											Last updated: {new Date(deal.date).toLocaleDateString()}
										</div>
									</div>
								</div>
							</div>
						))}
					</div>
				</div>
			)}

			{/* Smart Recommendations Tab */}
			{activeTab === 'smart' && (
				<div className="tab-pane fade show active">
					{!localStorage.getItem('token') ? (
						<div className="alert alert-info">
							<h5>🔐 Login Required</h5>
							<p>Please login to view personalized product recommendations based on your activity.</p>
						</div>
					) : !personalizedRecommendations ? (
						<div className="alert alert-light">
							<h5>🤖 Building Your Profile</h5>
							<p>We're analyzing your activity to provide personalized recommendations. Check back after browsing some products!</p>
						</div>
					) : (
						<div>
							<div className="row mb-4">
								<div className="col-12">
									<div className="alert alert-primary">
										<h5>🎯 Personalized for You</h5>
										<p className="mb-1">
											Personalization Score: <strong>{(personalizedRecommendations.personalization_score * 100).toFixed(1)}%</strong>
										</p>
										<p className="mb-0">
											Found {personalizedRecommendations.total_recommendations} smart recommendations based on your activity
										</p>
									</div>
								</div>
							</div>

							<div className="row">
								{personalizedRecommendations.recommendations.map((rec, index) => (
									<div key={rec.product_id} className="col-lg-6 mb-4">
										<div className="card h-100 border-primary">
											<div className="card-body">
												<div className="d-flex justify-content-between align-items-start mb-3">
													<h6 className="card-title mb-0">{rec.product_name}</h6>
													<span className="badge bg-primary">Score: {rec.score.toFixed(1)}</span>
												</div>
												
												<div className="mb-2">
													<span className="badge bg-secondary me-1">{rec.category}</span>
													<span className="badge bg-info me-1">
														{rec.rating}/5 ⭐
													</span>
													<span className={`badge ${rec.price_trend === 'decreasing' ? 'bg-success' : rec.price_trend === 'increasing' ? 'bg-danger' : 'bg-warning'}`}>
														{rec.price_trend === 'decreasing' ? '📉 Decreasing' : rec.price_trend === 'increasing' ? '📈 Increasing' : '📊 Stable'}
													</span>
												</div>

												<div className="row text-center mb-3">
													<div className="col-6">
														<div className="h6 mb-1">{formatCurrency(rec.current_price)}</div>
														<div className="small text-muted">Best Price</div>
														<div className="small text-muted">{rec.best_retailer}</div>
													</div>
													<div className="col-6">
														<div className="h6 mb-1 text-success">Save ₹{rec.potential_savings}</div>
														<div className="small text-muted">Trending Score</div>
														<div className="small text-muted">{rec.trending_score}/10</div>
													</div>
												</div>

												<p className="text-muted small mb-3">{rec.description}</p>

												<div className="mb-3">
													<small className="text-muted d-block mb-1"><strong>Why recommended:</strong></small>
													{rec.reasons.map((reason, idx) => (
														<small key={idx} className="d-block text-muted">• {reason}</small>
													))}
												</div>

												{/* Website Links */}
												<div className="d-grid gap-2">
													<a 
														href={rec.website_url} 
														target="_blank" 
														rel="noopener noreferrer"
														className="btn btn-primary btn-sm"
													>
														🛒 Buy from {rec.best_retailer}
													</a>
													
													{Object.keys(rec.all_retailer_links).length > 1 && (
														<div className="btn-group" role="group">
															{Object.entries(rec.all_retailer_links).map(([retailer, url]) => (
																<a
																	key={retailer}
																	href={url}
																	target="_blank"
																	rel="noopener noreferrer"
																	className={`btn btn-outline-secondary btn-sm ${retailer === rec.best_retailer ? 'active' : ''}`}
																	style={{ fontSize: '0.75rem' }}
																>
																	{retailer}
																</a>
															))}
														</div>
													)}
												</div>
											</div>
										</div>
									</div>
								))}
							</div>
						</div>
					)}
				</div>
			)}

			{/* Quick Stats Summary */}
			<div className="row mt-5">
				<div className="col-12">
					<div className="card bg-light">
						<div className="card-body">
							<div className="row text-center">
								<div className="col-md-4">
									<div className="h4 text-primary">{bestDeals.length}</div>
									<div className="text-muted">Best Deals Available</div>
								</div>
								<div className="col-md-4">
									<div className="h4 text-info">{items.length}</div>
									<div className="text-muted">Tracked Products</div>
								</div>
								{personalizedRecommendations && (
									<div className="col-md-4">
										<div className="h4 text-primary">
											{personalizedRecommendations.total_recommendations}
										</div>
										<div className="text-muted">Smart Recommendations</div>
									</div>
								)}
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	)
} 