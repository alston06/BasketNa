import 'bootstrap/dist/css/bootstrap.min.css'
import './copilot-styles.css'
import React from 'react'
import ReactDOM from 'react-dom/client'
import { createBrowserRouter, RouterProvider } from 'react-router-dom'
import { CopilotKit } from '@copilotkit/react-core'
import Dashboard from './pages/Dashboard'
import Home from './pages/Home'
import Layout from './pages/Layout'
import Product from './pages/Product'
import Results from './pages/Results'

const router = createBrowserRouter([
	{
		path: '/',
		element: <Layout />,
		children: [
			{ index: true, element: <Home /> },
			{ path: 'results', element: <Results /> },
			{ path: 'product/:productId', element: <Product /> },
			{ path: 'dashboard', element: <Dashboard /> },
		],
	},
])

ReactDOM.createRoot(document.getElementById('root')!).render(
	<React.StrictMode>
		<CopilotKit runtimeUrl={import.meta.env.VITE_BACKEND_URL || "http://localhost:8000/copilotkit"}>
			<RouterProvider router={router} />
		</CopilotKit>
	</React.StrictMode>
) 