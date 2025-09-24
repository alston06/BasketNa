import { useEffect, useState } from 'react';
import { AITools } from '../api/client';
import { CouponData, Coupon } from '../types/aitools';

interface CouponsWidgetProps {
  productName: string;
  className?: string;
}

export default function CouponsWidget({ productName, className = '' }: CouponsWidgetProps) {
  const [coupons, setCoupons] = useState<CouponData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!productName) return;

    const loadCoupons = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await AITools.getCoupons(productName);
        setCoupons(response.coupon_data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'Failed to load coupons');
        console.error('Error loading coupons:', err);
      } finally {
        setLoading(false);
      }
    };

    loadCoupons();
  }, [productName]);

  const formatCurrency = (amount: number) => {
    return `₹${amount.toLocaleString('en-IN')}`;
  };

  const getCouponIcon = (type: string) => {
    switch (type) {
      case 'percentage_discount': return '🏷️';
      case 'cashback': return '💰';
      case 'shipping': return '🚚';
      case 'bundle': return '📦';
      default: return '🎫';
    }
  };

  const getCouponBadgeColor = (type: string) => {
    switch (type) {
      case 'percentage_discount': return 'bg-primary';
      case 'cashback': return 'bg-success';
      case 'shipping': return 'bg-info';
      case 'bundle': return 'bg-warning text-dark';
      default: return 'bg-secondary';
    }
  };

  if (loading) {
    return (
      <div className={`card ${className}`}>
        <div className="card-header">
          <h5 className="mb-0">🎫 Available Coupons & Deals</h5>
        </div>
        <div className="card-body text-center">
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading coupons...</span>
          </div>
          <p className="mt-2 text-muted">Finding the best deals...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`card ${className}`}>
        <div className="card-header">
          <h5 className="mb-0">🎫 Available Coupons & Deals</h5>
        </div>
        <div className="card-body">
          <div className="alert alert-warning">
            <small>Unable to load coupons: {error}</small>
          </div>
        </div>
      </div>
    );
  }

  if (!coupons || coupons.total_coupons_found === 0) {
    return (
      <div className={`card ${className}`}>
        <div className="card-header">
          <h5 className="mb-0">🎫 Available Coupons & Deals</h5>
        </div>
        <div className="card-body text-center">
          <div className="text-muted">
            <div style={{ fontSize: '2rem' }}>😔</div>
            <p>No active coupons found for this product</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`card ${className}`}>
      <div className="card-header d-flex justify-content-between align-items-center">
        <h5 className="mb-0">🎫 Available Coupons & Deals</h5>
        <span className="badge bg-success">{coupons.total_coupons_found} found</span>
      </div>
      <div className="card-body">
        {/* Best Deal Highlight */}
        {coupons.best_coupon_recommendation && (
          <div className="alert alert-success border-0 mb-3" style={{
            background: 'linear-gradient(135deg, #28a745, #20c997)',
            color: 'white'
          }}>
            <div className="d-flex align-items-center">
              <div className="me-3" style={{ fontSize: '1.5rem' }}>
                {getCouponIcon(coupons.best_coupon_recommendation.type)}
              </div>
              <div className="flex-grow-1">
                <h6 className="mb-1 fw-bold">🏆 Best Deal</h6>
                <div className="fw-bold">{coupons.best_coupon_recommendation.code}</div>
                <div>{coupons.best_coupon_recommendation.description}</div>
                <small>Max savings: {formatCurrency(coupons.max_potential_savings)}</small>
              </div>
            </div>
          </div>
        )}

        {/* All Coupons */}
        <div className="row">
          {coupons.coupons.map((coupon, index) => (
            <div key={index} className="col-md-6 mb-3">
              <div className="card h-100 border-0" style={{ backgroundColor: '#f8f9fa' }}>
                <div className="card-body p-3">
                  <div className="d-flex justify-content-between align-items-start mb-2">
                    <span className={`badge ${getCouponBadgeColor(coupon.type)} fs-6`}>
                      {getCouponIcon(coupon.type)} {coupon.type.replace('_', ' ').toUpperCase()}
                    </span>
                    <div className="text-end">
                      <div className="fw-bold text-primary">{coupon.discount}</div>
                    </div>
                  </div>
                  
                  <div className="mb-2">
                    <div className="fw-bold text-dark mb-1">{coupon.code}</div>
                    <small className="text-muted">{coupon.description}</small>
                  </div>
                  
                  <div className="border-top pt-2 mt-2">
                    <div className="row text-center">
                      <div className="col-6">
                        <small className="text-muted d-block">Min Order</small>
                        <small className="fw-bold">{formatCurrency(coupon.min_order_value)}</small>
                      </div>
                      <div className="col-6">
                        <small className="text-muted d-block">Expires</small>
                        <small className="fw-bold">{coupon.expires_in_days}d</small>
                      </div>
                    </div>
                    
                    {coupon.site_compatibility.length > 0 && (
                      <div className="mt-2">
                        <small className="text-muted d-block">Valid on:</small>
                        <div className="d-flex flex-wrap gap-1">
                          {coupon.site_compatibility.map((site, siteIndex) => (
                            <span key={siteIndex} className="badge bg-light text-dark">
                              {site}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Summary */}
        <div className="alert alert-info border-0 mt-3">
          <small>
            <strong>💡 Tip:</strong> Estimated product price {formatCurrency(coupons.estimated_product_price)}. 
            You could save up to {formatCurrency(coupons.max_potential_savings)} with the best available coupon!
          </small>
        </div>
      </div>
    </div>
  );
}