
interface ChatWelcomeProps {
  productName?: string
}

export function ChatWelcome({ productName }: ChatWelcomeProps) {
  return (
    <div className="p-4 text-center">
      <div 
        className="mx-auto mb-3 d-flex align-items-center justify-content-center rounded-circle shadow"
        style={{
          width: 60,
          height: 60,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          fontSize: 28,
          color: 'white',
        }}
      >
        🛒
      </div>
      <h5 className="fw-bold text-primary mb-2">
        Welcome to <span className="text-gradient">BasketNa AI!</span>
      </h5>
      <p className="text-muted small mb-4">
        {productName 
          ? `I'm here to help you with "${productName}". Ask me about prices, deals, and the best time to buy!`
          : 'I\'m your AI shopping assistant! Ask me about prices, deals, comparisons, and shopping advice for Indian e-commerce.'
        }
      </p>
      <div className="row g-2 justify-content-center">
        <div className="col-12 col-md-10 col-lg-8">
          <div className="card border-0 bg-light shadow-sm">
            <div className="card-body p-3">
              <h6 className="card-title mb-2 text-secondary small fw-semibold">
                💡 Try asking me:
              </h6>
              <ul className="list-group list-group-flush mb-0 small text-muted">
                <li className="list-group-item bg-light border-0 ps-0">• "Compare iPhone prices across sites"</li>
                <li className="list-group-item bg-light border-0 ps-0">• "When should I buy this product?"</li>
                <li className="list-group-item bg-light border-0 ps-0">• "Find me deals on laptops"</li>
                <li className="list-group-item bg-light border-0 ps-0">• "Is this price good?"</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}