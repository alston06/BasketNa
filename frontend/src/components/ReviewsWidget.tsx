import { useEffect, useState } from 'react';
import { AITools } from '../api/client';
import { ReviewAnalysis, SampleReview } from '../types/aitools';

interface ReviewsWidgetProps {
  productName: string;
  className?: string;
  site?: 'all' | 'amazon' | 'flipkart';
}

export default function ReviewsWidget({ productName, className = '', site = 'all' }: ReviewsWidgetProps) {
  const [reviews, setReviews] = useState<ReviewAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedSite, setSelectedSite] = useState<'all' | 'amazon' | 'flipkart'>(site);

  useEffect(() => {
    if (!productName) return;

    const loadReviews = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await AITools.getReviews(productName, selectedSite);
        setReviews(response.review_analysis);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load reviews');
        console.error('Error loading reviews:', err);
      } finally {
        setLoading(false);
      }
    };

    loadReviews();
  }, [productName, selectedSite]);

  const getSentimentColor = (percentage: number) => {
    if (percentage >= 70) return 'text-success';
    if (percentage >= 50) return 'text-warning';
    return 'text-danger';
  };

  const getSentimentIcon = (sentiment: string) => {
    const sentimentLower = sentiment.toLowerCase();
    if (sentimentLower.includes('pos')) return '😊';
    if (sentimentLower.includes('neg')) return '😞';
    return '😐';
  };

  const renderStars = (rating: number | null) => {
    if (!rating) return <span className="text-muted">N/A</span>;
    
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const emptyStars = 5 - fullStars - (hasHalfStar ? 1 : 0);

    return (
      <span className="text-warning">
        {'★'.repeat(fullStars)}
        {hasHalfStar && '☆'}
        {'☆'.repeat(emptyStars)}
        <span className="text-dark ms-1">({rating}/5)</span>
      </span>
    );
  };

  if (loading) {
    return (
      <div className={`card ${className}`}>
        <div className="card-header">
          <h5 className="mb-0">📝 Customer Reviews & Sentiment</h5>
        </div>
        <div className="card-body text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Analyzing reviews...</span>
          </div>
          <p className="mt-2 text-muted">AI is analyzing customer feedback...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`card ${className}`}>
        <div className="card-header">
          <h5 className="mb-0">📝 Customer Reviews & Sentiment</h5>
        </div>
        <div className="card-body">
          <div className="alert alert-warning">
            <small>Unable to load reviews: {error}</small>
          </div>
        </div>
      </div>
    );
  }

  if (!reviews) {
    return (
      <div className={`card ${className}`}>
        <div className="card-header">
          <h5 className="mb-0">📝 Customer Reviews & Sentiment</h5>
        </div>
        <div className="card-body text-center">
          <div className="text-muted">
            <div style={{ fontSize: '2rem' }}>📝</div>
            <p>No reviews found for analysis</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`card ${className}`}>
      <div className="card-header">
        <div className="d-flex justify-content-between align-items-center">
          <h5 className="mb-0">📝 Customer Reviews & Sentiment</h5>
          <div className="d-flex align-items-center gap-2">
            <select 
              className="form-select form-select-sm"
              value={selectedSite}
              onChange={(e) => setSelectedSite(e.target.value as 'all' | 'amazon' | 'flipkart')}
              style={{ width: 'auto' }}
            >
              <option value="all">All Sites</option>
              <option value="amazon">Amazon</option>
              <option value="flipkart">Flipkart</option>
            </select>
            <span className="badge bg-primary">{reviews.total_reviews_analyzed} reviews</span>
          </div>
        </div>
      </div>
      
      <div className="card-body">
        {/* Overall Rating & Sentiment */}
        <div className="row mb-4">
          <div className="col-md-6">
            <div className="text-center p-3 bg-light rounded">
              <h6 className="text-muted mb-2">Overall Rating</h6>
              <div className="h4 mb-0">
                {renderStars(reviews.average_rating)}
              </div>
            </div>
          </div>
          <div className="col-md-6">
            <div className="text-center p-3 bg-light rounded">
              <h6 className="text-muted mb-2">Customer Sentiment</h6>
              <div className={`h4 mb-0 ${getSentimentColor(reviews.sentiment_breakdown.positive)}`}>
                😊 {reviews.sentiment_breakdown.positive}% Positive
              </div>
            </div>
          </div>
        </div>

        {/* Sentiment Breakdown */}
        <div className="mb-4">
          <h6>Sentiment Breakdown</h6>
          <div className="progress mb-2" style={{ height: '25px' }}>
            <div 
              className="progress-bar bg-success" 
              style={{ width: `${reviews.sentiment_breakdown.positive}%` }}
            >
              {reviews.sentiment_breakdown.positive}% Positive
            </div>
            <div 
              className="progress-bar bg-warning" 
              style={{ width: `${reviews.sentiment_breakdown.neutral}%` }}
            >
              {reviews.sentiment_breakdown.neutral}% Neutral
            </div>
            <div 
              className="progress-bar bg-danger" 
              style={{ width: `${reviews.sentiment_breakdown.negative}%` }}
            >
              {reviews.sentiment_breakdown.negative}% Negative
            </div>
          </div>
        </div>

        {/* Key Points */}
        <div className="row mb-4">
          {reviews.key_positives.length > 0 && (
            <div className="col-md-6">
              <div className="card border-success">
                <div className="card-body">
                  <h6 className="card-title text-success">👍 Key Positives</h6>
                  <div className="d-flex flex-wrap gap-1">
                    {reviews.key_positives.map((positive, index) => (
                      <span key={index} className="badge bg-success">
                        {positive}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {reviews.key_negatives.length > 0 && (
            <div className="col-md-6">
              <div className="card border-danger">
                <div className="card-body">
                  <h6 className="card-title text-danger">👎 Key Concerns</h6>
                  <div className="d-flex flex-wrap gap-1">
                    {reviews.key_negatives.map((negative, index) => (
                      <span key={index} className="badge bg-danger">
                        {negative}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Insights */}
        {reviews.insights.length > 0 && (
          <div className="mb-4">
            <h6>💡 AI Insights</h6>
            <div className="list-group list-group-flush">
              {reviews.insights.map((insight, index) => (
                <div key={index} className="list-group-item border-0 px-0">
                  <small>• {insight}</small>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Sample Reviews */}
        {reviews.sample_reviews.length > 0 && (
          <div className="mb-4">
            <h6>📄 Sample Customer Reviews</h6>
            <div className="row">
              {reviews.sample_reviews.map((review, index) => (
                <div key={index} className="col-md-6 mb-3">
                  <div className="card border-0 bg-light">
                    <div className="card-body p-3">
                      <div className="d-flex justify-content-between align-items-start mb-2">
                        <span className="badge bg-secondary">{review.source}</span>
                        <span className="fs-5">
                          {getSentimentIcon(review.sentiment)}
                        </span>
                      </div>
                      <p className="card-text small mb-0">
                        "{review.text}"
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Summary */}
        <div className="alert alert-info border-0">
          <h6 className="alert-heading">🧠 AI Summary</h6>
          <p className="mb-0 small">{reviews.summary_text}</p>
          <hr />
          <div className="row text-center">
            <div className="col-md-4">
              <small className="text-muted">Sites Analyzed</small>
              <div className="fw-bold">{reviews.sites_analyzed.join(', ')}</div>
            </div>
            <div className="col-md-4">
              <small className="text-muted">Reviews Processed</small>
              <div className="fw-bold">{reviews.total_reviews_analyzed}</div>
            </div>
            <div className="col-md-4">
              <small className="text-muted">Analysis Time</small>
              <div className="fw-bold">Real-time</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}