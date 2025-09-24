import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Products } from '../api/client'

type Tracked = { id: number, product_id: string, product_name: string, created_at: string }

type BestDeal = {
	product_name: string
	retailer: string
	current_price: number
	savings_amount: number
	savings_percentage: number
	date: string
}

type BuyWaitRecommendation = {
	product_name: string
	current_best_price: number
	current_best_retailer: string
	predicted_best_price: number
	predicted_best_retailer: string
	predicted_best_date: string
	potential_savings: number
	savings_percentage: number
	recommendation: 'BUY_NOW' | 'WAIT' | 'NEUTRAL'
	reason: string
}

export default function Dashboard() {
	const [items, setItems] = useState<Tracked[]>([])
	const [bestDeals, setBestDeals] = useState<BestDeal[]>([])
	const [recommendations, setRecommendations] = useState<BuyWaitRecommendation[]>([])
	const [loading, setLoading] = useState(true)
	const [activeTab, setActiveTab] = useState<'basket' | 'deals' | 'recommendations'>('basket')

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

				// Load buy/wait recommendations
				const recommendationsResponse = await Products.buyWaitRecommendations(30)
				setRecommendations(recommendationsResponse.recommendations?.slice(0, 6) || [])
			} catch (error) {
				console.error('Error loading dashboard data:', error)
			} finally {
				setLoading(false)
			}
		}

		loadData()
	}, [])

	const getRecommendationBadge = (recommendation: string) => {
		switch (recommendation) {
			case 'BUY_NOW':
				return <span className="badge bg-success">Buy Now</span>
			case 'WAIT':
				return <span className="badge bg-warning text-dark">Wait</span>
			default:
				return <span className="badge bg-secondary">Neutral</span>
		}
	}

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
						className={`nav-link ${activeTab === 'recommendations' ? 'active' : ''}`}
						onClick={() => setActiveTab('recommendations')}
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

			{activeTab === 'recommendations' && (
				<div className="tab-pane fade show active">
					<div className="row">
						<div className="col-12 mb-3">
							<div className="alert alert-info">
								<h5>🧠 Smart Buying Recommendations (30-Day Forecast)</h5>
								<p className="mb-0">AI-powered insights to help you decide when to buy or wait for better deals.</p>
							</div>
						</div>
						{recommendations.map((rec, index) => (
							<div key={index} className="col-lg-6 mb-4">
								<div className={`card h-100 ${rec.recommendation === 'BUY_NOW' ? 'border-success' : rec.recommendation === 'WAIT' ? 'border-warning' : 'border-secondary'}`}>
									<div className="card-body">
										<div className="d-flex justify-content-between align-items-start mb-3">
											<h6 className="card-title mb-0">{rec.product_name}</h6>
											{getRecommendationBadge(rec.recommendation)}
										</div>
										
										<div className="row text-center mb-3">
											<div className="col-6">
												<div className="border-end">
													<div className="h6 mb-1">{formatCurrency(rec.current_best_price)}</div>
													<div className="small text-muted">Current Best</div>
													<div className="small text-muted">{rec.current_best_retailer}</div>
												</div>
											</div>
											<div className="col-6">
												<div className="h6 mb-1">{formatCurrency(rec.predicted_best_price)}</div>
												<div className="small text-muted">Predicted Best</div>
												<div className="small text-muted">{rec.predicted_best_retailer}</div>
											</div>
										</div>

										{rec.potential_savings > 0 && (
											<div className="alert alert-warning py-2">
												<small>
													💡 Potential savings: <strong>{formatCurrency(rec.potential_savings)} ({rec.savings_percentage}%)</strong>
													<br />
													Expected on: {new Date(rec.predicted_best_date).toLocaleDateString()}
												</small>
											</div>
										)}

										<div className="text-muted small">
											<strong>Reason:</strong> {rec.reason}
										</div>
									</div>
								</div>
							</div>
						))}
					</div>
				</div>
			)}

			{/* Quick Stats Summary */}
			<div className="row mt-5">
				<div className="col-12">
					<div className="card bg-light">
						<div className="card-body">
							<div className="row text-center">
								<div className="col-md-3">
									<div className="h4 text-primary">{bestDeals.length}</div>
									<div className="text-muted">Best Deals Available</div>
								</div>
								<div className="col-md-3">
									<div className="h4 text-success">
										{recommendations.filter(r => r.recommendation === 'WAIT').length}
									</div>
									<div className="text-muted">Products to Wait For</div>
								</div>
								<div className="col-md-3">
									<div className="h4 text-warning">
										{recommendations.filter(r => r.recommendation === 'BUY_NOW').length}
									</div>
									<div className="text-muted">Buy Now Recommendations</div>
								</div>
								<div className="col-md-3">
									<div className="h4 text-info">{items.length}</div>
									<div className="text-muted">Tracked Products</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	)
} 