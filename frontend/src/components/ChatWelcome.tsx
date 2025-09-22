import React from 'react'

interface ChatWelcomeProps {
  productName?: string
}

export function ChatWelcome({ productName }: ChatWelcomeProps) {
  return (
    <div className="p-4 text-center">
      <div 
        className="mx-auto mb-3 d-flex align-items-center justify-content-center rounded-circle"
        style={{
          width: '60px',
          height: '60px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          fontSize: '24px'
        }}
      >
        🛒
      </div>
      
      <h5 className="fw-bold text-primary mb-2">
        Welcome to BasketNa AI! 
      </h5>
      
      <p className="text-muted small mb-4">
        {productName 
          ? `I'm here to help you with "${productName}". Ask me about prices, deals, and the best time to buy!`
          : 'I\'m your AI shopping assistant! Ask me about prices, deals, comparisons, and shopping advice for Indian e-commerce.'
        }
      </p>
      
      <div className="row g-2 text-start">
        <div className="col-12">
          <div className="card border-0 bg-light">
            <div className="card-body p-3">
              <h6 className="card-title mb-2" style={{ fontSize: '14px' }}>
                💡 Try asking me:
              </h6>
              <ul className="list-unstyled mb-0 small text-muted">
                <li className="mb-1">• "Compare iPhone prices across sites"</li>
                <li className="mb-1">• "When should I buy this product?"</li>
                <li className="mb-1">• "Find me deals on laptops"</li>
                <li className="mb-1">• "Is this price good?"</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}