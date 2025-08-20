import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Products } from '../api/client'

type Tracked = { id: number, product_id: string, product_name: string, created_at: string }

export default function Dashboard() {
	const [items, setItems] = useState<Tracked[]>([])
	const [loading, setLoading] = useState(true)

	useEffect(() => {
		const token = localStorage.getItem('token')
		if (!token) { setLoading(false); return }
		Products.tracked().then(setItems).finally(() => setLoading(false))
	}, [])

	if (!localStorage.getItem('token')) return <div>Please login to view your basket.</div>
	if (loading) return <div>Loading...</div>

	return (
		<div>
			<h2>Your Basket</h2>
			{items.length === 0 ? <p>No tracked items yet.</p> : (
				<table className="table">
					<thead>
						<tr>
							<th>Product</th>
							<th>Added</th>
						</tr>
					</thead>
					<tbody>
						{items.map(it => (
							<tr key={it.id}>
								<td><Link to={`/product/${it.product_id}`}>{it.product_name}</Link></td>
								<td>{new Date(it.created_at).toLocaleString()}</td>
							</tr>
						))}
					</tbody>
				</table>
			)}
		</div>
	)
} 