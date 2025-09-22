import React, { useState } from 'react'
import { CopilotChat } from '@copilotkit/react-ui'

interface FloatingChatProps {
  productId?: string
  productName?: string
}

export function FloatingChat({ productId, productName }: FloatingChatProps) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <>
      {/* Floating Chat Button */}
      <button
        className="floating-chat-button"
        onClick={() => setIsOpen(!isOpen)}
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, #667eea, #764ba2)',
          border: 'none',
          color: 'white',
          fontSize: '24px',
          cursor: 'pointer',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          zIndex: 1000,
          transition: 'all 0.3s ease',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.transform = 'scale(1.1)'
          e.currentTarget.style.boxShadow = '0 6px 20px rgba(0,0,0,0.25)'
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.transform = 'scale(1)'
          e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)'
        }}
      >
        {isOpen ? '✕' : '🤖'}
      </button>

      {/* Chat Panel */}
      {isOpen && (
        <div
          className="floating-chat-panel"
          style={{
            position: 'fixed',
            bottom: '90px',
            right: '20px',
            width: '350px',
            height: '500px',
            backgroundColor: 'white',
            borderRadius: '12px',
            boxShadow: '0 8px 32px rgba(0,0,0,0.12)',
            zIndex: 1000,
            overflow: 'hidden',
            border: '1px solid #e0e0e0'
          }}
        >
          <div
            style={{
              background: 'linear-gradient(135deg, #667eea, #764ba2)',
              color: 'white',
              padding: '12px 16px',
              fontSize: '14px',
              fontWeight: '600'
            }}
          >
            <div className="d-flex justify-content-between align-items-center">
              <span>🛒 BasketNa AI Assistant</span>
              <button
                onClick={() => setIsOpen(false)}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'white',
                  cursor: 'pointer',
                  fontSize: '16px'
                }}
              >
                ✕
              </button>
            </div>
            {productName && (
              <div style={{ fontSize: '12px', opacity: 0.9, marginTop: '4px' }}>
                Helping with: {productName}
              </div>
            )}
          </div>
          
          <div style={{ height: 'calc(100% - 60px)', overflow: 'hidden' }}>
            <CopilotChat
              instructions={`You are helping the user with product "${productName}" (ID: ${productId}). 
                           Focus on price analysis, deal recommendations, and purchase timing advice for this specific product.
                           Always provide actionable insights for Indian e-commerce platforms.`}
              makeSystemMessage={(message) => 
                `Current context: User is viewing product "${productName}" (${productId}). ${message}`
              }
            />
          </div>
        </div>
      )}

      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="d-md-none"
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0,0,0,0.5)',
            zIndex: 999
          }}
          onClick={() => setIsOpen(false)}
        />
      )}


    </>
  )
}