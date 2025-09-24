import { CopilotKit } from '@copilotkit/react-core';
import "@copilotkit/react-ui/styles.css";
import 'bootstrap/dist/css/bootstrap.min.css';
import React from 'react';
import ReactDOM from 'react-dom/client';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import EnhancedProduct from './pages/EnhancedProduct';
import Home from './pages/Home';
import Layout from './pages/Layout';
import Results from './pages/Results';

const router = createBrowserRouter([
	{
		path: '/',
		element: <Layout />,
		children: [
			{ index: true, element: <Home /> },
			{ path: 'results', element: <Results /> },
			{ path: 'product/:productId', element: <EnhancedProduct /> },
			{ path: 'enhanced-product/:productId', element: <EnhancedProduct /> },
			{ path: 'dashboard', element: <Dashboard /> },
		],
	},
])

ReactDOM.createRoot(document.getElementById('root')!).render(
	<React.StrictMode>
		<CopilotKit runtimeUrl={"http://localhost:4000/copilotkit"} agent="my_agent">
			<RouterProvider router={router} />
		</CopilotKit>
	</React.StrictMode>
) 