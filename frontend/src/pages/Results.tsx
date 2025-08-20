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

	useEffect(() => {
		if (!q) return
		axios.get(`/api/search?query=${encodeURIComponent(q)}`).then(r => setData(r.data))
	}, [q])

	if (!q) return <div>Enter a query</div>
	if (!data) return <div>Loading...</div>

	return (
		<div>
			<h2>Results for "{data.query}"</h2>
			{data.items.length === 0 ? <p>No results</p> : (
				<table className="table table-striped">
					<thead>
						<tr>
							<th>Product</th>
							<th>Site</th>
							<th>Price</th>
							<th></th>
						</tr>
					</thead>
					<tbody>
						{data.items.map((it, idx) => (
							<tr key={idx} className={data.best_price && it.site === data.best_price.site && it.product_id === data.best_price.product_id ? 'table-success' : ''}>
								<td><Link to={`/product/${it.product_id}`}>{it.product_name}</Link></td>
								<td>{it.site}</td>
								<td>₹ {it.price.toLocaleString()}</td>
								<td><a href={it.url} target="_blank">View</a></td>
							</tr>
						))}
					</tbody>
				</table>
			)}
		</div>
	)
} 