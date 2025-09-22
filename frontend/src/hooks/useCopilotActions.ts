import { useCopilotAction } from '@copilotkit/react-core'
import { Products } from '../api/client'

export function useTrackingActions(productId?: string) {
  useCopilotAction({
    name: "trackProduct",
    description: "Track a product for price changes and get notifications when the price drops",
    parameters: [
      {
        name: "productId",
        type: "string",
        description: "The ID of the product to track",
        required: true,
      },
    ],
    handler: async ({ productId: trackProductId }) => {
      try {
        const token = localStorage.getItem('token')
        if (!token) {
          return {
            success: false,
            message: "Please log in to track products"
          }
        }
        
        await Products.track(trackProductId || productId || '')
        return {
          success: true,
          message: `Successfully added ${trackProductId} to your tracking list!`
        }
      } catch (error) {
        return {
          success: false,
          message: "Failed to track product. It may already be in your tracking list."
        }
      }
    },
  })

  useCopilotAction({
    name: "getPriceComparison",
    description: "Get current price comparison across different e-commerce sites for a product",
    parameters: [
      {
        name: "productName",
        type: "string",
        description: "Name of the product to compare prices for",
        required: true,
      },
    ],
    handler: async ({ productName }) => {
      // This would call your backend's price scraping functionality
      // For now, return mock data
      return {
        productName,
        prices: [
          { site: "Amazon.in", price: "₹499", url: "https://amazon.in" },
          { site: "Flipkart.com", price: "₹520", url: "https://flipkart.com" },
          { site: "BigBasket.com", price: "₹485", url: "https://bigbasket.com" }
        ],
        bestDeal: { site: "BigBasket.com", price: "₹485", savings: "₹14" }
      }
    },
  })

  useCopilotAction({
    name: "getPricePrediction",
    description: "Get AI-powered price predictions for a product based on historical data",
    parameters: [
      {
        name: "productId",
        type: "string",
        description: "The ID of the product to get predictions for",
        required: true,
      },
    ],
    handler: async ({ productId: predictionProductId }) => {
      // This would call your ML prediction endpoint
      const currentPrice = 499
      return {
        productId: predictionProductId,
        currentPrice: `₹${currentPrice}`,
        predictions: [
          { 
            timeframe: "Next 7 days", 
            predictedPrice: `₹${Math.round(currentPrice * 0.95)}`,
            confidence: "85%",
            change: "-5%"
          },
          { 
            timeframe: "Next 14 days", 
            predictedPrice: `₹${Math.round(currentPrice * 0.92)}`,
            confidence: "80%", 
            change: "-8%"
          },
          { 
            timeframe: "Next 30 days", 
            predictedPrice: `₹${Math.round(currentPrice * 0.88)}`,
            confidence: "75%",
            change: "-12%"
          }
        ],
        recommendation: "Price is expected to drop in the next 2 weeks. Consider waiting for a better deal."
      }
    },
  })
}