"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";

interface Recommendation {
	source: string;
	items: {
		product_id: string;
		product_name: string;
		latest_price?: number;
	}[];
}

export default function HomePage() {
	const [query, setQuery] = useState("");
	const [isSearching, setIsSearching] = useState(false);
	console.log("is Searching:", isSearching);
	const [recs, setRecs] = useState<Recommendation | null>(null);

	const router = useRouter();

	const handleSearch = () => {
		if (query.trim()) {
			setIsSearching(true);
			router.push(`/results?q=${encodeURIComponent(query)}`);
			setTimeout(() => setIsSearching(false), 1000);
		}
	};

		const handleKeyPress = (e: React.KeyboardEvent) => {
		if (e.key === 'Enter') {
			handleSearch()
		}
	}

		return (
			<div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-500 to-purple-600 relative overflow-hidden">
				{/* Animated background elements */}
				<div className="absolute -top-1/2 -left-1/2 w-[200%] h-[200%] bg-[radial-gradient(circle,rgba(255,255,255,0.1)_1px,transparent_1px)] bg-[50px_50px] animate-float" />
				<div className="container mx-auto px-4">
					<div className="flex flex-col items-center justify-center min-h-screen">
						{/* Hero Section */}
						<div className="text-center text-white mb-10 w-full">
							<h1 className="text-4xl md:text-5xl font-extrabold mb-6 drop-shadow-lg tracking-tight">
								Find the Best Deals
							</h1>
							<div className="flex flex-col sm:flex-row items-center justify-center gap-3 w-full max-w-xl mx-auto">
								<input
									className="w-full sm:w-auto flex-1 rounded-lg px-5 py-3 text-gray-900 text-lg shadow-lg border border-indigo-200 focus:ring-2 focus:ring-indigo-400 focus:outline-none transition placeholder-gray-400 bg-white/90"
									placeholder="Search for products... e.g., iPhone 14, MacBook Air"
									value={query}
									onChange={e => setQuery(e.target.value)}
									onKeyPress={handleKeyPress}
									style={{ minWidth: 0 }}
								/>
								<button
									className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold text-white text-lg bg-gradient-to-r from-indigo-500 to-purple-600 shadow-lg transition-all ${isSearching ? "opacity-70 scale-95" : "hover:scale-105 hover:shadow-xl"}`}
									onClick={handleSearch}
									disabled={!query.trim() || isSearching}
									type="button"
								>
									{isSearching ? (
										<>
											<span className="inline-block w-5 h-5 mr-2 border-2 border-t-2 border-t-transparent border-indigo-500 rounded-full animate-spin align-middle" />
											Searching...
										</>
									) : (
										<>
											<span role="img" aria-label="search" className="text-xl">🔍</span>
											Search
										</>
									)}
								</button>
							</div>
						{/* Popular searches */}
						<div className="mt-3">
							<p className="text-muted text-sm mb-2">Popular searches:</p>
							<div className="flex flex-wrap gap-2">
								{[
									"iPhone 14",
									"MacBook Air",
									"Samsung Galaxy",
									"Sony Headphones",
								].map((term) => (
									<button
										key={term}
										className="rounded-full text-xs px-3 py-1 border border-indigo-300 text-indigo-700 bg-white hover:bg-indigo-50 transition"
										onClick={() => setQuery(term)}
										type="button"
									>
										{term}
									</button>
								))}
							</div>
						</div>
					</div>

					{/* Features */}
					<div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-10 text-white text-center">
						<div className="p-3 animate-fadeInUp delay-600">
							<div className="mb-3 text-3xl">🛒</div>
							<h5 className="font-semibold">Compare Prices</h5>
							<p className="text-sm">
								Find the best deals across multiple retailers
							</p>
						</div>
						<div className="p-3 animate-fadeInUp delay-800">
							<div className="mb-3 text-3xl">📈</div>
							<h5 className="font-semibold">Price Tracking</h5>
							<p className="text-sm">Monitor price changes and get alerts</p>
						</div>
						<div className="p-3 animate-fadeInUp delay-1000">
							<div className="mb-3 text-3xl">🎯</div>
							<h5 className="font-semibold">Smart Recommendations</h5>
							<p className="text-sm">Discover products you&apos;ll love</p>
						</div>
					</div>

					{/* Recommendations */}
					{recs && recs.items.length > 0 && (
						<div className="mt-10 animate-fadeInUp delay-1200">
							<div className="bg-white/95 backdrop-blur-lg shadow-lg rounded-lg p-6">
								<h4 className="text-center mb-4 font-bold text-lg text-indigo-700">
									❤️ You May Also Like
								</h4>
								<div className="grid grid-cols-1 md:grid-cols-2 gap-4">
									{recs.items.map((it, index) => (
										<a
											key={it.product_id}
											href={`/product/${it.product_id}`}
											className="block no-underline"
											style={{ animationDelay: `${0.1 * index}s` }}
										>
											<div className="bg-white rounded-lg shadow p-4 h-full hover:-translate-y-1 hover:shadow-xl transition-all">
												<h6 className="font-semibold text-gray-900 mb-2">
													{it.product_name}
												</h6>
												{typeof it.latest_price === "number" && (
													<div className="flex items-center">
														<span className="bg-green-100 text-green-700 rounded px-2 py-1 text-sm font-semibold">
															₹{Math.round(it.latest_price).toLocaleString()}
														</span>
													</div>
												)}
											</div>
										</a>
									))}
								</div>
							</div>
						</div>
					)}
				</div>
			</div>
		</div>
	);
}
