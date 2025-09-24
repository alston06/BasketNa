// Types for AI Agent Tools responses

export interface CouponData {
  product_name: string;
  total_coupons_found: number;
  coupons: Coupon[];
  estimated_product_price: number;
  max_potential_savings: number;
  best_coupon_recommendation: Coupon;
  search_timestamp: string;
  currency: string;
}

export interface Coupon {
  code: string;
  discount: string;
  description: string;
  type: 'percentage_discount' | 'cashback' | 'shipping' | 'bundle';
  min_order_value: number;
  expires_in_days: number;
  terms: string;
  site_compatibility: string[];
}

export interface ReviewAnalysis {
  product_name: string;
  sites_analyzed: string[];
  total_reviews_analyzed: number;
  average_rating: number | null;
  sentiment_breakdown: {
    positive: number;
    negative: number;
    neutral: number;
  };
  key_positives: string[];
  key_negatives: string[];
  insights: string[];
  sample_reviews: SampleReview[];
  summary_text: string;
  analysis_timestamp: string;
}

export interface SampleReview {
  text: string;
  sentiment: string;
  source: string;
}

export interface ComprehensiveAnalysis {
  product_name: string;
  coupons: CouponData;
  reviews: ReviewAnalysis;
  analysis_complete: boolean;
}

export interface AIToolsResponse<T> {
  status: 'success' | 'error';
  coupon_data?: CouponData;
  review_analysis?: ReviewAnalysis;
  comprehensive_analysis?: ComprehensiveAnalysis;
}

export interface AIToolsHealth {
  status: 'healthy' | 'unavailable';
  tools_available: boolean;
  available_endpoints: string[];
  message: string;
}