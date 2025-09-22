import react from '@vitejs/plugin-react-swc'
import { defineConfig } from 'vite'

export default defineConfig({
	plugins: [react()],
	server: {
		port: 5174,
		proxy: {
			'/api': {
				target: 'http://127.0.0.1:8000',
				changeOrigin: true,
				rewrite: (path) => path.replace(/^\/api/, ''),
				configure: (proxy, options) => {
					proxy.on('error', (err, req, res) => {
						console.log('proxy error', err);
					});
					proxy.on('proxyReq', (proxyReq, req, res) => {
						console.log('Sending Request to the Target:', req.method, req.url);
					});
					proxy.on('proxyRes', (proxyRes, req, res) => {
						console.log('Received Response from the Target:', proxyRes.statusCode, req.url);
					});
				},
			}
		}
	}
}) 