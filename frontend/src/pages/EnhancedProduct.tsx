import { useCopilotReadable } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import {
	CategoryScale,
	Chart as ChartJS,
	Legend,
	LinearScale,
	LineElement,
	PointElement,
	Tooltip,
} from "chart.js";
import { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import { useParams, useSearchParams } from "react-router-dom";
import { Products } from "../api/client";
import { useTrackingActions } from "../hooks/useCopilotActions";
import AIAnalysisWidget from "../components/AIAnalysisWidget";

ChartJS.register(
	CategoryScale,
	LinearScale,
	PointElement,
	LineElement,
	Tooltip,
	Legend,
);

type EnhancedForecast = {
	product_name: string
	retailer_filter?: string
	forecast_period: string
	current_market_price: number
	forecast_summary: {
		best_predicted_price: number
		worst_predicted_price: number
		average_predicted_price: number
		best_deal_date: string
		potential_savings: number
		potential_savings_pct: number
		price_trend: 'INCREASING' | 'DECREASING' | 'STABLE'
		buying_advice: string
	}
	daily_forecasts: Array<{
		date: string
		day_of_week: string
		days_ahead: number
		predicted_price: number
		confidence_score: number
		price_range: {
			lower: number
			upper: number
			margin_pct: number
		}
		market_insights: {
			vs_current_price: number
			vs_historical_avg: number
			market_event?: string
			weekend_effect: boolean
		}
	}>
	model_metadata: {
		forecast_method: string
		confidence_method: string
		data_points_used: number
		generated_at: string
	}
}

type CompetitiveAnalysis = {
	product_name: string
	analysis_date: string
	retailer_analysis: Record<string, {
		current_price: number
		forecast_avg: number
		forecast_min: number
		forecast_max: number
		expected_change_pct: number
	}>
	market_summary: {
		current_best_deal: {
			retailer: string
			price: number
		}
		forecast_best_deal: {
			retailer: string
			price: number
		}
		total_retailers: number
	}
}

export default function EnhancedProduct() {
	const { productId } = useParams();
	const [searchParams] = useSearchParams();
	const productName = searchParams.get('name') || productId || '';
	
	// Auto-generate a product name from productId if name param is missing
	const displayProductName = productName || (productId ? productId.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : '');
	
	const [enhancedForecast, setEnhancedForecast] = useState<EnhancedForecast | null>(null);
	const [competitiveAnalysis, setCompetitiveAnalysis] = useState<CompetitiveAnalysis | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [showCopilot, setShowCopilot] = useState(false);
	const [selectedRetailer, setSelectedRetailer] = useState<string>('');

	// Initialize CopilotKit actions
	useTrackingActions(productId);

	// Provide context to CopilotKit
	useCopilotReadable({
		description: "Enhanced product information with 30-day forecasts and competitive analysis",
		value: {
			productId,
			productName: displayProductName,
			enhancedForecast,
			competitiveAnalysis,
			currentMarketPrice: enhancedForecast?.current_market_price,
			buyingAdvice: enhancedForecast?.forecast_summary.buying_advice,
			bestDealDate: enhancedForecast?.forecast_summary.best_deal_date,
			potentialSavings: enhancedForecast?.forecast_summary.potential_savings,
		},
	});

	useEffect(() => {
		if (!displayProductName) return;
		
		const loadData = async () => {
			setLoading(true);
			setError(null);
			
			try {
				// Load enhanced forecast
				const forecastResponse = await Products.enhancedForecast(displayProductName, selectedRetailer);
				setEnhancedForecast(forecastResponse.enhanced_forecast);

				// Load competitive analysis
				const competitiveResponse = await Products.competitiveAnalysis(displayProductName);
				setCompetitiveAnalysis(competitiveResponse.competitive_analysis);
			} catch (err: any) {
				setError(err.response?.data?.detail || 'Failed to load product data');
				console.error('Error loading product data:', err);
			} finally {
				setLoading(false);
			}
		};

		loadData();
	}, [displayProductName, selectedRetailer]);

	const track = async () => {
		if (!productId) return;
		const token = localStorage.getItem("token");
		if (!token) {
			alert("Please login to track products");
			return;
		}
		try {
			await Products.track(productId);
			alert("Tracking added to your basket");
		} catch (e) {
			alert("Failed to track (maybe already tracked?)");
		}
	};

	const formatCurrency = (amount: number) => {
		return `₹${amount.toLocaleString('en-IN')}`;
	};

	const getTrendIcon = (trend: string) => {
		switch (trend) {
			case 'INCREASING': return '📈';
			case 'DECREASING': return '📉';
			default: return '➡️';
		}
	};

	const getTrendColor = (trend: string) => {
		switch (trend) {
			case 'INCREASING': return 'text-danger';
			case 'DECREASING': return 'text-success';
			default: return 'text-secondary';
		}
	};

	if (!displayProductName) {
		return (
			<div className="container py-4">
				<div className="alert alert-warning">
					<h5>Missing Product Information</h5>
					<p>Please provide a product name in the URL parameters.</p>
				</div>
			</div>
		);
	}

	if (loading) {
		return (
			<div className="container py-4">
				<div className="d-flex justify-content-center">
					<div className="spinner-border text-primary" role="status">
						<span className="visually-hidden">Loading enhanced forecast...</span>
					</div>
				</div>
			</div>
		);
	}

	if (error) {
		return (
			<div className="container py-4">
				<div className="alert alert-danger">
					<h5>Error Loading Product Data</h5>
					<p>{error}</p>
				</div>
			</div>
		);
	}

	if (!enhancedForecast) {
		return (
			<div className="container py-4">
				<div className="alert alert-info">
					<h5>No Forecast Data Available</h5>
					<p>Enhanced forecast data is not available for this product.</p>
				</div>
			</div>
		);
	}

	// Prepare chart data
	const chartLabels = enhancedForecast.daily_forecasts.map(f => {
		const date = new Date(f.date);
		return `${date.getDate()}/${date.getMonth() + 1}`;
	});

	const chartData = {
		labels: chartLabels,
		datasets: [
			{
				label: 'Predicted Price',
				data: enhancedForecast.daily_forecasts.map(f => f.predicted_price),
				borderColor: 'rgba(13,110,253,1)',
				backgroundColor: 'rgba(13,110,253,0.1)',
				fill: false,
				tension: 0.4,
			},
			{
				label: 'Lower Bound',
				data: enhancedForecast.daily_forecasts.map(f => f.price_range.lower),
				borderColor: 'rgba(220,53,69,0.6)',
				backgroundColor: 'rgba(220,53,69,0.05)',
				borderDash: [5, 5],
				fill: '+1',
			},
			{
				label: 'Upper Bound',
				data: enhancedForecast.daily_forecasts.map(f => f.price_range.upper),
				borderColor: 'rgba(25,135,84,0.6)',
				backgroundColor: 'rgba(25,135,84,0.05)',
				borderDash: [5, 5],
				fill: false,
			},
		],
	};

	const chartOptions = {
		responsive: true,
		plugins: {
			legend: {
				position: 'top' as const,
			},
			tooltip: {
				callbacks: {
					label: function(context: any) {
						return `${context.dataset.label}: ${formatCurrency(context.parsed.y)}`;
					},
				},
			},
		},
		scales: {
			y: {
				beginAtZero: false,
				ticks: {
					callback: function(value: any) {
						return formatCurrency(value);
					},
				},
			},
		},
	};

	return (
		<div className="container-fluid">
			<div className="row">
				<div className="col-12">
					<div className="container py-4">
						{/* Header */}
						<div className="d-flex justify-content-between align-items-center mb-4">
							<div>
								<h2 className="mb-1">{enhancedForecast.product_name}</h2>
								<p className="text-muted mb-0">30-Day Enhanced Price Forecast</p>
							</div>
							<div className="d-flex gap-2">
								<button
									type="button"
									className="btn btn-outline-primary"
									onClick={() => setShowCopilot(!showCopilot)}
								>
									🤖 AI Assistant {showCopilot ? '(Close)' : '(Open)'}
								</button>
							</div>
						</div>

						{/* Price Summary Cards */}
						<div className="row mb-4">
							<div className="col-md-3 mb-3">
								<div className="card text-center">
									<div className="card-body">
										<h5 className="card-title text-primary">Current Price</h5>
										<div className="h4">{formatCurrency(enhancedForecast.current_market_price)}</div>
									</div>
								</div>
							</div>
							<div className="col-md-3 mb-3">
								<div className="card text-center">
									<div className="card-body">
										<h5 className="card-title text-success">Best Deal Expected</h5>
										<div className="h4">{formatCurrency(enhancedForecast.forecast_summary.best_predicted_price)}</div>
										<small className="text-muted">{enhancedForecast.forecast_summary.best_deal_date}</small>
									</div>
								</div>
							</div>
							<div className="col-md-3 mb-3">
								<div className="card text-center">
									<div className="card-body">
										<h5 className="card-title text-warning">Potential Savings</h5>
										<div className="h4">{formatCurrency(enhancedForecast.forecast_summary.potential_savings)}</div>
										<small className="text-muted">{enhancedForecast.forecast_summary.potential_savings_pct}%</small>
									</div>
								</div>
							</div>
							<div className="col-md-3 mb-3">
								<div className="card text-center">
									<div className="card-body">
										<h5 className="card-title">Price Trend</h5>
										<div className={`h4 ${getTrendColor(enhancedForecast.forecast_summary.price_trend)}`}>
											{getTrendIcon(enhancedForecast.forecast_summary.price_trend)} {enhancedForecast.forecast_summary.price_trend}
										</div>
									</div>
								</div>
							</div>
						</div>

						{/* Buying Advice Alert */}
						<div className={`alert ${enhancedForecast.forecast_summary.price_trend === 'DECREASING' ? 'alert-warning' : enhancedForecast.forecast_summary.price_trend === 'INCREASING' ? 'alert-danger' : 'alert-info'} mb-4`}>
							<h5>🧠 Smart Buying Advice</h5>
							<p className="mb-0">{enhancedForecast.forecast_summary.buying_advice}</p>
						</div>

						{/* Action Buttons */}
						<div className="mb-4">
							<button className="btn btn-primary me-2" onClick={track}>
								📊 Track This Product
							</button>
							{enhancedForecast.forecast_summary.potential_savings > 1000 && (
								<span className="badge bg-success ms-2 p-2">
									💡 High Savings Potential: {formatCurrency(enhancedForecast.forecast_summary.potential_savings)}
								</span>
							)}
						</div>

						{/* Retailer Filter */}
						{competitiveAnalysis && (
							<div className="mb-4">
								<label className="form-label">Filter by Retailer (Optional):</label>
								<select 
									className="form-select w-auto d-inline-block ms-2"
									value={selectedRetailer}
									onChange={(e) => setSelectedRetailer(e.target.value)}
								>
									<option value="">All Retailers</option>
									{Object.keys(competitiveAnalysis.retailer_analysis).map(retailer => (
										<option key={retailer} value={retailer}>{retailer}</option>
									))}
								</select>
							</div>
						)}

						{/* Price Forecast Chart */}
						<div className="card mb-4">
							<div className="card-header">
								<h5 className="mb-0">📈 30-Day Price Forecast</h5>
								<small className="text-muted">
									Generated using {enhancedForecast.model_metadata.forecast_method}
								</small>
							</div>
							<div className="card-body">
								<Line data={chartData} options={chartOptions} />
							</div>
						</div>

						{/* Competitive Analysis */}
						{competitiveAnalysis && (
							<div className="card mb-4">
								<div className="card-header">
									<h5 className="mb-0">🏪 Competitive Analysis</h5>
									<small className="text-muted">Current vs Forecast prices across retailers</small>
								</div>
								<div className="card-body">
									<div className="row">
										{Object.entries(competitiveAnalysis.retailer_analysis).map(([retailer, data]) => (
											<div key={retailer} className="col-lg-6 col-xl-4 mb-3">
												<div className="card h-100">
													<div className="card-body">
														<h6 className="card-title">{retailer}</h6>
														<div className="row text-center">
															<div className="col-6">
																<div className="border-end">
																	<div className="h6 mb-1">{formatCurrency(data.current_price)}</div>
																	<div className="small text-muted">Current</div>
																</div>
															</div>
															<div className="col-6">
																<div className="h6 mb-1">{formatCurrency(data.forecast_min)}</div>
																<div className="small text-muted">Best Forecast</div>
															</div>
														</div>
														<div className="mt-2">
															<span className={`badge ${data.expected_change_pct < 0 ? 'bg-success' : data.expected_change_pct > 0 ? 'bg-danger' : 'bg-secondary'}`}>
																{data.expected_change_pct > 0 ? '+' : ''}{data.expected_change_pct}% expected
															</span>
														</div>
													</div>
												</div>
											</div>
										))}
									</div>
								</div>
							</div>
						)}

						{/* AI-Powered Analysis */}
						<AIAnalysisWidget 
							productName={enhancedForecast.product_name} 
							className="mb-4"
						/>

						{/* Forecast Details Table */}
						<div className="card">
							<div className="card-header">
								<h5 className="mb-0">📅 Detailed Daily Forecast (Next 10 Days)</h5>
							</div>
							<div className="card-body p-0">
								<div className="table-responsive">
									<table className="table table-hover mb-0">
										<thead className="table-light">
											<tr>
												<th>Date</th>
												<th>Day</th>
												<th>Predicted Price</th>
												<th>Confidence</th>
												<th>Price Range</th>
												<th>vs Current</th>
												<th>Market Event</th>
											</tr>
										</thead>
										<tbody>
											{enhancedForecast.daily_forecasts.slice(0, 10).map((forecast, index) => (
												<tr key={index}>
													<td>{new Date(forecast.date).toLocaleDateString()}</td>
													<td>
														<span className={`badge ${forecast.market_insights.weekend_effect ? 'bg-warning text-dark' : 'bg-light text-dark'}`}>
															{forecast.day_of_week}
														</span>
													</td>
													<td className="fw-bold">{formatCurrency(forecast.predicted_price)}</td>
													<td>
														<div className="d-flex align-items-center">
															<div className="progress me-2" style={{width: '60px', height: '8px'}}>
																<div 
																	className="progress-bar bg-success" 
																	style={{width: `${forecast.confidence_score * 100}%`}}
																></div>
															</div>
															<small>{(forecast.confidence_score * 100).toFixed(0)}%</small>
														</div>
													</td>
													<td>
														<small className="text-muted">
															{formatCurrency(forecast.price_range.lower)} - {formatCurrency(forecast.price_range.upper)}
														</small>
													</td>
													<td>
														<span className={`badge ${forecast.market_insights.vs_current_price < 0 ? 'bg-success' : forecast.market_insights.vs_current_price > 0 ? 'bg-danger' : 'bg-secondary'}`}>
															{forecast.market_insights.vs_current_price > 0 ? '+' : ''}{forecast.market_insights.vs_current_price}%
														</span>
													</td>
													<td>
														{forecast.market_insights.market_event ? (
															<small className="text-info">{forecast.market_insights.market_event}</small>
														) : (
															<small className="text-muted">None</small>
														)}
													</td>
												</tr>
											))}
										</tbody>
									</table>
								</div>
							</div>
						</div>
					</div>
				</div>

				{/* CopilotKit Sidebar */}
				{showCopilot && (
					<CopilotSidebar
						instructions={`You are a helpful AI assistant for BasketNa's enhanced price forecasting system. Help users understand the 30-day price predictions, competitive analysis, and make smart buying decisions. 

Current product: ${displayProductName}
Current price: ${formatCurrency(enhancedForecast.current_market_price)}
Best predicted price: ${formatCurrency(enhancedForecast.forecast_summary.best_predicted_price)} on ${enhancedForecast.forecast_summary.best_deal_date}
Buying advice: ${enhancedForecast.forecast_summary.buying_advice}

Always use Indian Rupees (₹) when discussing prices and provide actionable insights based on the forecast data.`}
						defaultOpen={true}
						clickOutsideToClose={false}
						labels={{
							title: "BasketNa AI Assistant",
							placeholder: "Ask me about price trends, forecasts, and buying advice...",
						}}
					/>
				)}
			</div>
		</div>
	);
}