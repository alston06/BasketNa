import { useEffect, useState } from 'react'
import { Link, Outlet, useNavigate } from 'react-router-dom'
import { Auth } from '../api/client'

export default function Layout() {
	const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
	const [showAuth, setShowAuth] = useState(false)
	const [isLogin, setIsLogin] = useState(true)
	const [email, setEmail] = useState('')
	const [password, setPassword] = useState('')
	const [isLoading, setIsLoading] = useState(false)
	const navigate = useNavigate()

	useEffect(() => {
		setToken(localStorage.getItem('token'))
	}, [])

	const onAuth = async () => {
		if (!email.trim() || !password.trim()) {
			alert('Please fill in all fields')
			return
		}
		
		setIsLoading(true)
		try {
			if (isLogin) {
				const res = await Auth.login(email, password)
				localStorage.setItem('token', res.access_token)
				setToken(res.access_token)
			} else {
				await Auth.signup(email, password)
				const res = await Auth.login(email, password)
				localStorage.setItem('token', res.access_token)
				setToken(res.access_token)
			}
			setShowAuth(false)
			setEmail('')
			setPassword('')
			navigate('/dashboard')
		} catch (e) {
			alert('Authentication failed. Please check your credentials.')
		} finally {
			setIsLoading(false)
		}
	}

	const onLogout = () => {
		localStorage.removeItem('token')
		setToken(null)
		navigate('/')
	}

	return (
		<div className="min-vh-100" style={{ background: '#f8f9fa' }}>
			{/* Enhanced Navigation */}
			<nav className="navbar navbar-expand-lg navbar-light shadow-sm" style={{
				background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
				backdropFilter: 'blur(10px)'
			}}>
				<div className="container">
					<Link className="navbar-brand text-white fw-bold fs-3" to="/" style={{
						textShadow: '2px 2px 4px rgba(0,0,0,0.3)'
					}}>
						🛒 Basketna
					</Link>
					
					<button className="navbar-toggler border-0" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
						<span className="navbar-toggler-icon"></span>
					</button>
					
					<div className="collapse navbar-collapse" id="navbarNav">
						<ul className="navbar-nav me-auto mb-2 mb-lg-0">
							<li className="nav-item">
								<Link to="/" className="nav-link text-white fw-semibold">
									🏠 Home
								</Link>
							</li>
							<li className="nav-item">
								<Link to="/dashboard" className="nav-link text-white fw-semibold">
									📊 Dashboard
								</Link>
							</li>
						</ul>
						
						<div className="d-flex align-items-center gap-3">
							{token ? (
								<div className="d-flex align-items-center gap-3">
									<span className="text-white small">
										👤 Welcome back!
									</span>
									<button 
										className="btn btn-outline-light btn-sm px-3" 
										onClick={onLogout}
										style={{
											borderRadius: '20px',
											fontWeight: '600',
											transition: 'all 0.3s ease'
										}}
									>
										🚪 Logout
									</button>
								</div>
							) : (
								<button 
									className="btn btn-light btn-sm px-4" 
									onClick={() => setShowAuth(true)}
									style={{
										borderRadius: '20px',
										fontWeight: '600',
										background: 'rgba(255,255,255,0.9)',
										transition: 'all 0.3s ease'
									}}
								>
									🔐 Login / Signup
								</button>
							)}
						</div>
					</div>
				</div>
			</nav>

			{/* Main Content */}
			<main>
				<Outlet />
			</main>

			{/* Enhanced Auth Modal */}
			{showAuth && (
				<div 
					className="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center" 
					style={{ 
						background: 'rgba(0,0,0,0.6)',
						backdropFilter: 'blur(5px)',
						zIndex: 1050
					}}
					onClick={() => setShowAuth(false)}
				>
					<div 
						className="card shadow-lg border-0" 
						style={{ 
							maxWidth: 420, 
							width: '90%',
							background: 'rgba(255,255,255,0.95)',
							backdropFilter: 'blur(10px)'
						}}
						onClick={(e) => e.stopPropagation()}
					>
						<div className="card-body p-4">
							<div className="text-center mb-4">
								<div style={{
									width: '60px',
									height: '60px',
									background: 'linear-gradient(135deg, #667eea, #764ba2)',
									borderRadius: '50%',
									display: 'flex',
									alignItems: 'center',
									justifyContent: 'center',
									margin: '0 auto',
									fontSize: '1.5rem',
									color: 'white'
								}}>
									{isLogin ? '🔐' : '👤'}
								</div>
								<h4 className="mt-3 mb-1 fw-bold">
									{isLogin ? 'Welcome Back!' : 'Join Basketna'}
								</h4>
								<p className="text-muted small">
									{isLogin ? 'Sign in to track your favorite products' : 'Create an account to get started'}
								</p>
							</div>

							<div className="mb-3">
								<label className="form-label small fw-semibold">Email Address</label>
								<input 
									className="form-control form-control-lg border-0 shadow-sm" 
									placeholder="Enter your email" 
									value={email} 
									onChange={e => setEmail(e.target.value)}
									style={{ borderRadius: '10px' }}
								/>
							</div>
							
							<div className="mb-4">
								<label className="form-label small fw-semibold">Password</label>
								<input 
									type="password" 
									className="form-control form-control-lg border-0 shadow-sm" 
									placeholder="Enter your password" 
									value={password} 
									onChange={e => setPassword(e.target.value)}
									style={{ borderRadius: '10px' }}
								/>
							</div>

							<div className="d-grid gap-2">
								<button 
									className={`btn btn-primary btn-lg ${isLoading ? 'btn-loading' : ''}`}
									onClick={onAuth}
									disabled={isLoading}
									style={{
										background: 'linear-gradient(135deg, #667eea, #764ba2)',
										border: 'none',
										borderRadius: '10px',
										fontWeight: '600'
									}}
								>
									{isLoading ? (
										<>
											<span className="spinner-border spinner-border-sm me-2" role="status" />
											{isLogin ? 'Signing in...' : 'Creating account...'}
										</>
									) : (
										isLogin ? '🔑 Sign In' : '✨ Create Account'
									)}
								</button>
								
								<button 
									className="btn btn-outline-secondary" 
									onClick={() => setIsLogin(!isLogin)}
									style={{ borderRadius: '10px' }}
								>
									{isLogin ? 'Don\'t have an account? Sign up' : 'Already have an account? Sign in'}
								</button>
								
								<button 
									className="btn btn-link text-muted" 
									onClick={() => setShowAuth(false)}
								>
									Cancel
								</button>
							</div>
						</div>
					</div>
				</div>
			)}

			{/* Footer */}
			<footer className="mt-5 py-4" style={{
				background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
				color: 'white'
			}}>
				<div className="container">
					<div className="row text-center">
						<div className="col-md-6 mb-3">
							<h5 className="fw-bold">🛒 Basketna</h5>
							<p className="small mb-0">Find the best deals across India's top retailers</p>
						</div>
						<div className="col-md-6 mb-3">
							<h6 className="fw-semibold">Features</h6>
							<div className="small">
								<div>📊 Price Tracking</div>
								<div>🔍 Smart Search</div>
								<div>❤️ Recommendations</div>
							</div>
						</div>
					</div>
					<hr className="my-3" style={{ borderColor: 'rgba(255,255,255,0.3)' }} />
					<div className="text-center small">
						© 2024 Basketna. Made with ❤️ for smart shoppers.
					</div>
				</div>
			</footer>

			<style>{`
				.btn-loading {
					opacity: 0.7;
					transform: scale(0.98);
				}

				.nav-link:hover {
					transform: translateY(-1px);
					transition: all 0.2s ease;
				}

				.form-control:focus {
					box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25) !important;
					border-color: #667eea !important;
				}

				.card {
					animation: fadeInUp 0.3s ease-out;
				}

				@keyframes fadeInUp {
					from {
						opacity: 0;
						transform: translateY(20px);
					}
					to {
						opacity: 1;
						transform: translateY(0);
					}
				}
			`}</style>
		</div>
	)
}