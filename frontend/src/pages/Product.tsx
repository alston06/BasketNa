import axios from 'axios'
import {
    CategoryScale,
    Chart as ChartJS,
    Legend,
    LinearScale,
    LineElement,
    PointElement,
    Tooltip
} from 'chart.js'
import { useEffect, useState } from 'react'
import { Line } from 'react-chartjs-2'
import { useParams } from 'react-router-dom'
import { Products } from '../api/client'

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend)

type FP = { date: string, price: number, lower: number, upper: number }

type ForecastResponse = {
	product_id: string
	product_name: string
	history: FP[]
	forecast: FP[]
	great_deal: boolean
	great_deal_reason: string
}

export default function Product() {
	const { productId } = useParams()
	const [data, setData] = useState<ForecastResponse | null>(null)

	useEffect(() => {
		if (!productId) return
		axios.get(`/api/forecast/${productId}`).then(r => setData(r.data)).catch(() => setData(null))
	}, [productId])

	const track = async () => {
		if (!productId) return
		const token = localStorage.getItem('token')
		if (!token) {
			alert('Please login to track products')
			return
		}
		try {
			await Products.track(productId)
			alert('Tracking added to your basket')
		} catch (e) {
			alert('Failed to track (maybe already tracked?)')
		}
	}

	if (!productId) return <div>Missing product</div>
	if (!data) return <div>Loading...</div>

	const labels = [...data.history.map(h => h.date), ...data.forecast.map(f => f.date)]
	const histLen = data.history.length
	const prices = [...data.history.map(h => h.price), ...data.forecast.map(f => f.price)]
	const lower = [...data.history.map(h => h.lower), ...data.forecast.map(f => f.lower)]
	const upper = [...data.history.map(h => h.upper), ...data.forecast.map(f => f.upper)]

	return (
		<div>
			<h2>{data.product_name}</h2>
			{data.great_deal && <div className="alert alert-success">Great Deal! {data.great_deal_reason}</div>}
			<div className="mb-3">
				<button className="btn btn-outline-primary" onClick={track}>Track</button>
			</div>
			<Line data={{
				labels,
				datasets: [
					{ label: 'Price', data: prices, borderColor: 'rgba(13,110,253,1)', backgroundColor: 'rgba(13,110,253,0.2)' },
					{ label: 'Lower', data: lower, borderColor: 'rgba(220,53,69,0.6)', borderDash: [5,5] },
					{ label: 'Upper', data: upper, borderColor: 'rgba(25,135,84,0.6)', borderDash: [5,5] },
				]
			}} />
		</div>
	)
} 