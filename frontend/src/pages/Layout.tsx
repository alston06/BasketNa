import { useEffect, useState } from 'react'
import { Link, Outlet, useNavigate } from 'react-router-dom'
import { Auth } from '../api/client'

export default function Layout() {
	const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
	const [showAuth, setShowAuth] = useState(false)
	const [isLogin, setIsLogin] = useState(true)
	const [email, setEmail] = useState('')
	const [password, setPassword] = useState('')
	const navigate = useNavigate()

	useEffect(() => {
		setToken(localStorage.getItem('token'))
	}, [])

	const onAuth = async () => {
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
			navigate('/dashboard')
		} catch (e) {
			alert('Auth failed')
		}
	}

	const onLogout = () => {
		localStorage.removeItem('token')
		setToken(null)
	}

	return (
		<div>
			<nav className="navbar navbar-expand-lg navbar-light bg-light">
				<div className="container">
					<Link className="navbar-brand" to="/">Basketna</Link>
					<div className="d-flex align-items-center gap-3">
						<ul className="navbar-nav me-auto mb-2 mb-lg-0">
							<li className="nav-item"><Link to="/" className="nav-link">Home</Link></li>
							<li className="nav-item"><Link to="/dashboard" className="nav-link">Dashboard</Link></li>
						</ul>
						{token ? (
							<button className="btn btn-outline-secondary btn-sm" onClick={onLogout}>Logout</button>
						) : (
							<button className="btn btn-primary btn-sm" onClick={() => setShowAuth(true)}>Login / Signup</button>
						)}
					</div>
				</div>
			</nav>
			<main className="container py-4">
				<Outlet />
			</main>
			{showAuth && (
				<div className="position-fixed top-0 start-0 w-100 h-100" style={{ background: 'rgba(0,0,0,.4)' }}>
					<div className="card shadow" style={{ maxWidth: 420, margin: '10vh auto', padding: 16 }}>
						<h5 className="card-title mb-3">{isLogin ? 'Login' : 'Signup'}</h5>
						<div className="mb-2">
							<input className="form-control" placeholder="Email" value={email} onChange={e => setEmail(e.target.value)} />
						</div>
						<div className="mb-3">
							<input type="password" className="form-control" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)} />
						</div>
						<div className="d-flex justify-content-between">
							<button className="btn btn-secondary" onClick={() => setShowAuth(false)}>Cancel</button>
							<div className="d-flex gap-2">
								<button className="btn btn-outline-primary" onClick={() => setIsLogin(!isLogin)}>{isLogin ? 'Switch to Signup' : 'Switch to Login'}</button>
								<button className="btn btn-primary" onClick={onAuth}>{isLogin ? 'Login' : 'Create account'}</button>
							</div>
						</div>
					</div>
				</div>
			)}
		</div>
	)
} 