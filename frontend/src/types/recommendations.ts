export interface PersonalizedRecommendation {
  product_id: string
  product_name: string
  category: string
  current_price: number
  best_retailer: string
  description: string
  score: number
  reasons: string[]
  rating: number
  trending_score: number
  price_trend: 'stable' | 'decreasing' | 'increasing'
  potential_savings: number
  website_url: string
  all_retailer_links: Record<string, string>
}

export interface PersonalizedRecommendationResponse {
  status: string
  user_id?: number
  session_id?: string
  personalization_score: number
  total_recommendations: number
  generated_at: string
  recommendations: PersonalizedRecommendation[]
}

export interface CategoryRecommendationResponse {
  status: string
  category: string
  total_found: number
  total_recommendations: number
  recommendations: Array<{
    product_id: string
    product_name: string
    category: string
    current_price: number
    best_retailer: string
    rating: number
    trending_score: number
    price_trend: string
    potential_savings: number
    score: number
    website_url: string
    all_retailer_links: Record<string, string>
  }>
}

export interface TrendingRecommendationResponse {
  status: string
  total_trending: number
  total_recommendations: number
  trending_recommendations: Array<{
    product_id: string
    product_name: string
    category: string
    current_price: number
    best_retailer: string
    rating: number
    trending_score: number
    price_trend: string
    potential_savings: number
    description: string
    website_url: string
    all_retailer_links: Record<string, string>
  }>
}