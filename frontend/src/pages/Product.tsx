import { useCopilotReadable } from "@copilotkit/react-core";
import { CopilotSidebar } from "@copilotkit/react-ui";
import axios from "axios";
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
import { useParams } from "react-router-dom";
import { Products } from "../api/client";
import { useTrackingActions } from "../hooks/useCopilotActions";

ChartJS.register(
	CategoryScale,
	LinearScale,
	PointElement,
	LineElement,
	Tooltip,
	Legend,
);

type FP = { date: string; price: number; lower: number; upper: number };

type ForecastResponse = {
	product_id: string;
	product_name: string;
	history: FP[];
	forecast: FP[];
	great_deal: boolean;
	great_deal_reason: string;
};

export default function Product() {
	const { productId } = useParams();
	const [data, setData] = useState<ForecastResponse | null>(null);
	const [showCopilot, setShowCopilot] = useState(false);

	// Initialize CopilotKit actions
	useTrackingActions(productId);

	// Provide context to CopilotKit
	useCopilotReadable({
		description:
			"Current product information including pricing history and forecasts",
		value: {
			productId,
			productName: data?.product_name || "Loading...",
			currentPrices: data
				? {
						history: data.history,
						forecast: data.forecast,
						greatDeal: data.great_deal,
						greatDealReason: data.great_deal_reason,
					}
				: null,
		},
	});

	useEffect(() => {
		if (!productId) return;
		axios
			.get(`/api/forecast/${productId}`)
			.then((r) => setData(r.data))
			.catch(() => setData(null));
	}, [productId]);

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

	if (!productId) return <div>Missing product</div>;
	if (!data) return <div>Loading...</div>;

	const labels = [
		...data.history.map((h) => h.date),
		...data.forecast.map((f) => f.date),
	];
	const histLen = data.history.length;
	const prices = [
		...data.history.map((h) => h.price),
		...data.forecast.map((f) => f.price),
	];
	const lower = [
		...data.history.map((h) => h.lower),
		...data.forecast.map((f) => f.lower),
	];
	const upper = [
		...data.history.map((h) => h.upper),
		...data.forecast.map((f) => f.upper),
	];

	return (
		<div className="container-fluid">
			<div className="row">
				{/* Main Product Content */}
				<div className={`col-12`}>
					<div className="container py-4">
						<div className="d-flex justify-content-between align-items-center mb-4">
							<h2 className="mb-0">{data.product_name}</h2>
							<div className="d-flex gap-2">
								<button
									type="button"
									className="btn btn-outline-primary d-none d-md-flex align-items-center gap-2"
									onClick={() => setShowCopilot(!showCopilot)}
								>
									🤖 AI Assistant
									{showCopilot ? " (Close)" : " (Open)"}
								</button>
							</div>
						</div>

						{data.great_deal && (
							<div className="alert alert-success d-flex align-items-center">
								<strong>🎉 Great Deal!</strong>
								<span className="ms-2">{data.great_deal_reason}</span>
							</div>
						)}

						<div className="mb-4">
							<button className="btn btn-primary" onClick={track}>
								📊 Track This Product
							</button>
						</div>

						<div className="card shadow-sm">
							<div className="card-header">
								<h5 className="mb-0">📈 Price History & Forecast</h5>
							</div>
							<div className="card-body">
								<Line
									data={{
										labels,
										datasets: [
											{
												label: "Price",
												data: prices,
												borderColor: "rgba(13,110,253,1)",
												backgroundColor: "rgba(13,110,253,0.2)",
											},
											{
												label: "Lower",
												data: lower,
												borderColor: "rgba(220,53,69,0.6)",
												borderDash: [5, 5],
											},
											{
												label: "Upper",
												data: upper,
												borderColor: "rgba(25,135,84,0.6)",
												borderDash: [5, 5],
											},
										],
									}}
								/>
							</div>
						</div>
					</div>
				</div>

				{/* Desktop CopilotKit Sidebar */}
				{showCopilot && (
						<CopilotSidebar
							instructions="You are a helpful AI assistant for BasketNa, a price comparison platform. Help users understand price trends, find the best deals, and make informed purchasing decisions. You have access to tools that can scrape current prices from Amazon.in, Flipkart.com, and BigBasket.com, and predict future price trends. Always use Indian Rupees (₹) when discussing prices."
							defaultOpen={true}
							clickOutsideToClose={false}
							labels={{
								title: "BasketNa AI Assistant",
								placeholder: "Ask me about price trends, deals, and more...",
							}}
						/>
				)}
			</div>
		</div>
	);
}
