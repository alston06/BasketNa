import { useEffect, useState } from 'react';
import { AITools } from '../api/client';
import { ComprehensiveAnalysis } from '../types/aitools';
import CouponsWidget from './CouponsWidget';
import ReviewsWidget from './ReviewsWidget';

interface AIAnalysisWidgetProps {
  productName: string;
  className?: string;
  showIndividualComponents?: boolean;
}

export default function AIAnalysisWidget({ 
  productName, 
  className = '', 
  showIndividualComponents = false 
}: AIAnalysisWidgetProps) {
  const [analysis, setAnalysis] = useState<ComprehensiveAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!productName) return;

    const loadAnalysis = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await AITools.getComprehensiveAnalysis(productName);
        setAnalysis(response.comprehensive_analysis);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load AI analysis');
        console.error('Error loading AI analysis:', err);
      } finally {
        setLoading(false);
      }
    };

    loadAnalysis();
  }, [productName]);

  // If we want to show individual components when comprehensive fails
  if (showIndividualComponents || error) {
    return (
      <div className={className}>
        {error && (
          <div className="alert alert-warning mb-3">
            <small>
              <strong>⚠️ Note:</strong> Comprehensive AI analysis unavailable. 
              Showing individual tool results instead.
            </small>
          </div>
        )}
        <div className="row">
          <div className="col-lg-6 mb-4">
            <CouponsWidget productName={productName} />
          </div>
          <div className="col-lg-6 mb-4">
            <ReviewsWidget productName={productName} />
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className={`card ${className}`}>
        <div className="card-header">
          <h5 className="mb-0">🤖 AI-Powered Product Analysis</h5>
        </div>
        <div className="card-body text-center py-5">
          <div className="mb-3">
            <div className="spinner-border text-primary" style={{ width: '3rem', height: '3rem' }} role="status">
              <span className="visually-hidden">Running AI analysis...</span>
            </div>
          </div>
          <h6>AI is analyzing "{productName}"</h6>
          <p className="text-muted">
            Finding coupons, analyzing reviews, and generating insights...
          </p>
          <div className="mt-3">
            <div className="progress" style={{ height: '8px' }}>
              <div 
                className="progress-bar progress-bar-striped progress-bar-animated bg-primary" 
                style={{ width: '75%' }}
              ></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!analysis) {
    return (
      <div className={`card ${className}`}>
        <div className="card-header">
          <h5 className="mb-0">🤖 AI-Powered Product Analysis</h5>
        </div>
        <div className="card-body text-center">
          <div className="text-muted">
            <div style={{ fontSize: '3rem' }}>🤖</div>
            <h6>AI Analysis Unavailable</h6>
            <p>Unable to perform comprehensive product analysis at this time.</p>
          </div>
        </div>
      </div>
    );
  }

  const formatCurrency = (amount: number) => {
    return `₹${amount.toLocaleString('en-IN')}`;
  };

  return (
    <div className={className}>
      {/* Analysis Header */}
      <div className="card mb-4 border-0 shadow-sm">
        <div className="card-body" style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white'
        }}>
          <div className="row align-items-center">
            <div className="col-md-8">
              <h4 className="mb-2">🤖 AI-Powered Product Analysis</h4>
              <p className="mb-0">
                Complete analysis for <strong>{analysis.product_name}</strong>
              </p>
            </div>
            <div className="col-md-4 text-md-end">
              <div className="d-flex justify-content-md-end gap-2">
                <span className="badge bg-light text-dark fs-6 px-3 py-2">
                  🎫 {analysis.coupons.total_coupons_found} Coupons
                </span>
                <span className="badge bg-light text-dark fs-6 px-3 py-2">
                  📝 {analysis.reviews.total_reviews_analyzed} Reviews
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Quick Insights Summary */}
      <div className="row mb-4">
        <div className="col-md-3 mb-3">
          <div className="card h-100 text-center border-success">
            <div className="card-body">
              <div className="h2 text-success mb-2">💰</div>
              <h6 className="card-title">Max Savings</h6>
              <div className="h5 text-success">
                {formatCurrency(analysis.coupons.max_potential_savings)}
              </div>
              <small className="text-muted">with best coupon</small>
            </div>
          </div>
        </div>
        
        <div className="col-md-3 mb-3">
          <div className="card h-100 text-center border-primary">
            <div className="card-body">
              <div className="h2 text-primary mb-2">⭐</div>
              <h6 className="card-title">Customer Rating</h6>
              <div className="h5 text-primary">
                {analysis.reviews.average_rating ? `${analysis.reviews.average_rating}/5` : 'N/A'}
              </div>
              <small className="text-muted">average rating</small>
            </div>
          </div>
        </div>
        
        <div className="col-md-3 mb-3">
          <div className="card h-100 text-center border-warning">
            <div className="card-body">
              <div className="h2 text-warning mb-2">😊</div>
              <h6 className="card-title">Positive Sentiment</h6>
              <div className="h5 text-warning">
                {analysis.reviews.sentiment_breakdown.positive}%
              </div>
              <small className="text-muted">customer satisfaction</small>
            </div>
          </div>
        </div>
        
        <div className="col-md-3 mb-3">
          <div className="card h-100 text-center border-info">
            <div className="card-body">
              <div className="h2 text-info mb-2">🏪</div>
              <h6 className="card-title">Sites Analyzed</h6>
              <div className="h5 text-info">
                {analysis.reviews.sites_analyzed.length}
              </div>
              <small className="text-muted">e-commerce platforms</small>
            </div>
          </div>
        </div>
      </div>

      {/* Best Deal Alert */}
      {analysis.coupons.best_coupon_recommendation && analysis.coupons.max_potential_savings > 500 && (
        <div className="alert alert-success border-0 mb-4" style={{
          background: 'linear-gradient(135deg, #28a745, #20c997)',
          color: 'white'
        }}>
          <div className="row align-items-center">
            <div className="col-md-8">
              <h5 className="mb-1">🎉 Excellent Deal Found!</h5>
              <p className="mb-0">
                Use coupon <strong>{analysis.coupons.best_coupon_recommendation.code}</strong> to save up to{' '}
                <strong>{formatCurrency(analysis.coupons.max_potential_savings)}</strong>
              </p>
            </div>
            <div className="col-md-4 text-md-end">
              <div className="h4 mb-0">💰 {formatCurrency(analysis.coupons.max_potential_savings)}</div>
              <small>Maximum Savings</small>
            </div>
          </div>
        </div>
      )}

      {/* AI Insights */}
      {analysis.reviews.insights.length > 0 && (
        <div className="card mb-4">
          <div className="card-header">
            <h6 className="mb-0">🧠 AI-Generated Insights</h6>
          </div>
          <div className="card-body">
            <div className="row">
              {analysis.reviews.insights.map((insight, index) => (
                <div key={index} className="col-md-6 mb-2">
                  <div className="d-flex align-items-start">
                    <div className="me-2 text-primary">💡</div>
                    <small>{insight}</small>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Detailed Analysis Tabs */}
      <div className="row">
        <div className="col-lg-6 mb-4">
          <div className="card h-100">
            <div className="card-header">
              <h6 className="mb-0">🎫 Available Coupons & Deals</h6>
            </div>
            <div className="card-body">
              {analysis.coupons.coupons.slice(0, 3).map((coupon, index) => (
                <div key={index} className="border rounded p-3 mb-3 bg-light">
                  <div className="d-flex justify-content-between align-items-start mb-2">
                    <div className="fw-bold">{coupon.code}</div>
                    <span className="badge bg-primary">{coupon.discount}</span>
                  </div>
                  <div className="small text-muted mb-2">{coupon.description}</div>
                  <div className="small">
                    <span className="me-3">Min: {formatCurrency(coupon.min_order_value)}</span>
                    <span>Expires: {coupon.expires_in_days}d</span>
                  </div>
                </div>
              ))}
              {analysis.coupons.total_coupons_found > 3 && (
                <div className="text-center">
                  <small className="text-muted">
                    +{analysis.coupons.total_coupons_found - 3} more coupons available
                  </small>
                </div>
              )}
            </div>
          </div>
        </div>
        
        <div className="col-lg-6 mb-4">
          <div className="card h-100">
            <div className="card-header">
              <h6 className="mb-0">📝 Customer Feedback Summary</h6>
            </div>
            <div className="card-body">
              {/* Sentiment Progress */}
              <div className="mb-3">
                <div className="progress" style={{ height: '20px' }}>
                  <div 
                    className="progress-bar bg-success" 
                    style={{ width: `${analysis.reviews.sentiment_breakdown.positive}%` }}
                  >
                    {analysis.reviews.sentiment_breakdown.positive}%
                  </div>
                  <div 
                    className="progress-bar bg-warning" 
                    style={{ width: `${analysis.reviews.sentiment_breakdown.neutral}%` }}
                  >
                    {analysis.reviews.sentiment_breakdown.neutral}%
                  </div>
                  <div 
                    className="progress-bar bg-danger" 
                    style={{ width: `${analysis.reviews.sentiment_breakdown.negative}%` }}
                  >
                    {analysis.reviews.sentiment_breakdown.negative}%
                  </div>
                </div>
                <div className="d-flex justify-content-between mt-1">
                  <small className="text-success">Positive</small>
                  <small className="text-warning">Neutral</small>
                  <small className="text-danger">Negative</small>
                </div>
              </div>
              
              {/* Key Points */}
              {analysis.reviews.key_positives.length > 0 && (
                <div className="mb-3">
                  <h6 className="small text-success mb-2">👍 Key Positives</h6>
                  <div className="d-flex flex-wrap gap-1">
                    {analysis.reviews.key_positives.slice(0, 4).map((positive, index) => (
                      <span key={index} className="badge bg-success small">
                        {positive}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {analysis.reviews.key_negatives.length > 0 && (
                <div className="mb-3">
                  <h6 className="small text-danger mb-2">👎 Key Concerns</h6>
                  <div className="d-flex flex-wrap gap-1">
                    {analysis.reviews.key_negatives.slice(0, 4).map((negative, index) => (
                      <span key={index} className="badge bg-danger small">
                        {negative}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Summary */}
              <div className="alert alert-light border-0 mb-0">
                <small className="text-muted">
                  <strong>Summary:</strong> {analysis.reviews.summary_text}
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Analysis Footer */}
      <div className="card border-0 bg-light">
        <div className="card-body text-center py-3">
          <small className="text-muted">
            <strong>🤖 AI Analysis Complete</strong> • 
            Processed {analysis.reviews.total_reviews_analyzed} reviews • 
            Found {analysis.coupons.total_coupons_found} active coupons • 
            Analysis generated in real-time
          </small>
        </div>
      </div>
    </div>
  );
}