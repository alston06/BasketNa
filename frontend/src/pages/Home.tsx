import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Home() {
	const [query, setQuery] = useState('')
	const navigate = useNavigate()
	return (
		<div className="row justify-content-center">
			<div className="col-md-8">
				<h1 className="mb-4">Compare and track prices in India</h1>
				<div className="input-group input-group-lg">
					<input className="form-control" placeholder="Search a product e.g., iPhone 14" value={query} onChange={e => setQuery(e.target.value)} />
					<button className="btn btn-primary" onClick={() => navigate(`/results?q=${encodeURIComponent(query)}`)}>Search</button>
				</div>
				<p className="text-muted mt-3">Amazon, Flipkart, Reliance Digital, Croma and more</p>
			</div>
		</div>
	)
} 