import React, { useState } from 'react'
import { CopilotChat } from '@copilotkit/react-ui'
import './FloatingChat.css'

interface FloatingChatProps {
  productId?: string
  productName?: string
}

export function FloatingChat({ productId, productName }: FloatingChatProps) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      {/* Enhanced Floating Chat Button */}
      <button
        className="btn position-fixed d-flex align-items-center justify-content-center rounded-circle shadow-lg"
        onClick={() => setIsOpen(!isOpen)}
        style={{
          bottom: '24px',
          right: '24px',
          width: '64px',
          height: '64px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          border: 'none',
          color: 'white',
          fontSize: '28px',
          zIndex: 1050,
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
          animation: isOpen ? 'none' : 'pulse 2s infinite'
        }}
        onMouseEnter={(e) => {
          e.currentTarget.style.transform = 'scale(1.1) rotate(5deg)'
          e.currentTarget.style.boxShadow = '0 8px 25px rgba(102, 126, 234, 0.4)'
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.transform = 'scale(1) rotate(0deg)'
          e.currentTarget.style.boxShadow = '0 4px 15px rgba(0,0,0,0.15)'
        }}
        title={isOpen ? 'Close AI Assistant' : 'Chat with AI Assistant'}
      >
        <span style={{ 
          transition: 'transform 0.2s ease',
          transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)'
        }}>
          {isOpen ? '✕' : '🤖'}
        </span>
      </button>

      {/* Enhanced Chat Panel */}
      {isOpen && (
        <div
          className="position-fixed card border-0 shadow-lg"
          style={{
            bottom: '100px',
            right: '24px',
            width: '380px',
            height: '560px',
            zIndex: 1040,
            borderRadius: '16px',
            overflow: 'hidden',
            background: 'rgba(255, 255, 255, 0.98)',
            backdropFilter: 'blur(10px)',
            animation: 'slideInFromBottom 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
          }}
        >
          {/* Chat Header */}
          <div
            className="card-header border-0 p-0"
            style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white'
            }}
          >
            <div className="d-flex justify-content-between align-items-center p-3">
              <div className="d-flex align-items-center">
                <div 
                  className="rounded-circle d-flex align-items-center justify-content-center me-2"
                  style={{
                    width: '32px',
                    height: '32px',
                    background: 'rgba(255, 255, 255, 0.2)',
                    fontSize: '16px'
                  }}
                >
                  🤖
                </div>
                <div>
                  <div className="fw-bold" style={{ fontSize: '14px' }}>
                    BasketNa AI Assistant
                  </div>
                  <div className="small opacity-75">
                    {productName ? `Helping with: ${productName}` : 'Ready to help you find deals!'}
                  </div>
                </div>
              </div>
              <button
                className="btn btn-sm d-flex align-items-center justify-content-center"
                onClick={() => setIsOpen(false)}
                style={{
                  background: 'rgba(255, 255, 255, 0.2)',
                  border: 'none',
                  color: 'white',
                  width: '28px',
                  height: '28px',
                  borderRadius: '6px',
                  fontSize: '14px',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)'
                }}
                title="Close chat"
              >
                ✕
              </button>
            </div>
          </div>
          
          {/* Chat Content */}
          <div 
            className="card-body p-0 d-flex flex-column"
            style={{ height: 'calc(100% - 70px)' }}
          >
            <div 
              className="flex-grow-1"
              style={{ 
                overflow: 'hidden',
                background: 'linear-gradient(to bottom, #f8f9fa 0%, #ffffff 100%)'
              }}
            >
              <CopilotChat
                instructions={`You are BasketNa's AI shopping assistant helping users find the best deals in India. 
                             ${productName ? `Currently assisting with: "${productName}" (ID: ${productId}).` : ''}
                             
                             Your expertise includes:
                             - Price comparison across Amazon.in, Flipkart, BigBasket
                             - Deal recommendations and timing advice
                             - Product analysis and value assessment
                             - Shopping tips for Indian e-commerce
                             
                             Always be helpful, concise, and focus on actionable insights. Use emojis to make responses engaging.`}
                makeSystemMessage={(message) => 
                  `Context: ${productName ? `User viewing product "${productName}" (${productId})` : 'General shopping assistance'}. ${message}`
                }
                className="h-100"
              />
            </div>
          </div>
        </div>
      )}

      {/* Mobile Overlay & Responsive Adjustments */}
      {isOpen && (
        <>
          {/* Mobile Backdrop */}
          <div
            className="d-lg-none position-fixed w-100 h-100"
            style={{
              top: 0,
              left: 0,
              backgroundColor: 'rgba(0,0,0,0.6)',
              zIndex: 1035,
              backdropFilter: 'blur(4px)'
            }}
            onClick={() => setIsOpen(false)}
          />
          
          {/* Mobile Chat Panel */}
          <div
            className="d-lg-none position-fixed card border-0 shadow-lg"
            style={{
              bottom: '20px',
              left: '20px',
              right: '20px',
              height: '70vh',
              zIndex: 1040,
              borderRadius: '16px',
              overflow: 'hidden',
              background: 'rgba(255, 255, 255, 0.98)',
              backdropFilter: 'blur(10px)',
              animation: 'slideInFromBottom 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
            }}
          >
            {/* Mobile Header */}
            <div
              className="card-header border-0 p-0"
              style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white'
              }}
            >
              <div className="d-flex justify-content-between align-items-center p-3">
                <div className="d-flex align-items-center">
                  <div 
                    className="rounded-circle d-flex align-items-center justify-content-center me-2"
                    style={{
                      width: '36px',
                      height: '36px',
                      background: 'rgba(255, 255, 255, 0.2)',
                      fontSize: '18px'
                    }}
                  >
                    🤖
                  </div>
                  <div>
                    <div className="fw-bold">BasketNa AI Assistant</div>
                    {productName && (
                      <div className="small opacity-75">
                        Helping with: {productName}
                      </div>
                    )}
                  </div>
                </div>
                <button
                  className="btn btn-sm d-flex align-items-center justify-content-center"
                  onClick={() => setIsOpen(false)}
                  style={{
                    background: 'rgba(255, 255, 255, 0.2)',
                    border: 'none',
                    color: 'white',
                    width: '32px',
                    height: '32px',
                    borderRadius: '8px',
                    fontSize: '16px'
                  }}
                >
                  ✕
                </button>
              </div>
            </div>
            
            {/* Mobile Chat Content */}
            <div className="card-body p-0 h-100">
              <CopilotChat
                instructions={`You are BasketNa's AI shopping assistant. ${productName ? `Helping with: "${productName}".` : ''} 
                             Provide concise, mobile-friendly responses with actionable shopping advice for Indian e-commerce.`}
                makeSystemMessage={(message) => 
                  `Mobile context: ${productName ? `Product "${productName}" (${productId})` : 'General assistance'}. ${message}`
                }
                className="h-100"
              />
            </div>
          </div>
        </>
      )}


    </>
  )
}