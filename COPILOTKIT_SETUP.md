# BasketNa CopilotKit Integration - Setup Instructions

## Prerequisites

1. **Google Gemini API Key**: Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. **Node.js** (v18 or later) and **Python** (v3.11 or later)

## Backend Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Configuration

Create `.env` file in the `backend/` directory:

```bash
cp .env.example .env
```

Edit `.env` and add your Google Gemini API key:

```env
GOOGLE_API_KEY=your-actual-google-api-key-here
DATABASE_URL=sqlite:///./basketna.db
SECRET_KEY=your-secret-key-here
DEBUG=True
```

### 3. Start Backend Server

```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: http://localhost:8000
CopilotKit endpoint: http://localhost:8000/copilotkit

## Frontend Setup

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Environment Configuration

Create `.env` file in the `frontend/` directory:

```env
VITE_BACKEND_URL=http://localhost:8000/copilotkit
```

### 3. Start Frontend Development Server

```bash
npm run dev
```

The frontend will be available at: http://localhost:5173

## Testing the Integration

### 1. Navigate to a Product Page

Go to: http://localhost:5173/product/P001

### 2. Open AI Assistant

- **Desktop**: Click the "🤖 AI Assistant" button in the top-right
- **Mobile**: Use the floating chat button in the bottom-right corner

### 3. Try These Commands

Ask the AI assistant:

- "What's the current price on Amazon?"
- "Compare prices across all sites"
- "Predict future price trends"
- "When should I buy this product?"
- "Calculate when the price might drop 10%"

## CopilotKit Features

### Available AI Tools

1. **scrape_price**: Get current prices from specific sites
2. **compare_all_sites**: Compare prices across Amazon, Flipkart, BigBasket
3. **predict_price**: AI-powered price forecasting
4. **calculate_drop_timeline**: Predict when prices will drop

### Frontend Actions

1. **trackProduct**: Add products to user's tracking list
2. **getPriceComparison**: Get real-time price comparisons
3. **getPricePrediction**: Get ML-powered price predictions

## Architecture Overview

```
Frontend (React + Vite)
├── CopilotKit Provider (main.tsx)
├── Product Page with AI Chat
├── Floating Chat Component
└── Custom Actions & Hooks

Backend (FastAPI)
├── CopilotKit Integration (/copilotkit)
├── AI Agent with Tools
├── Price Scraping Tools
└── ML Prediction Tools
```

## Troubleshooting

### Common Issues

1. **"Cannot find module @copilotkit"**
   - Run `npm install` in the frontend directory
   - Make sure all dependencies are installed

2. **"Failed to initialize CopilotKit"**
   - Check your `GOOGLE_API_KEY` in backend/.env
   - Ensure the API key is valid and Gemini API is enabled

3. **CORS Errors**
   - Check that frontend and backend URLs match
   - Verify CORS settings in backend/main.py

4. **Chat not responding**
   - Check browser console for errors
   - Verify backend is running and accessible
   - Check CopilotKit endpoint: http://localhost:8000/copilotkit

### Debug Mode

Enable debug logging by setting `DEBUG=True` in backend/.env

## Production Deployment

### Environment Variables

**Backend:**
```env
GOOGLE_API_KEY=your-production-api-key
DATABASE_URL=your-production-database-url
DEBUG=False
```

**Frontend:**
```env
VITE_BACKEND_URL=https://your-domain.com/copilotkit
```

### Docker Deployment

Update `docker-compose.yml` to include the new environment variables and ensure CopilotKit endpoints are properly exposed.

## Next Steps

1. **Real Scraping**: Replace mock data in `price_tools.py` with actual web scraping
2. **Enhanced ML**: Improve price prediction models in the `/ml` directory  
3. **User Analytics**: Track AI assistant usage and user interactions
4. **Rate Limiting**: Add rate limiting for AI tool usage
5. **Caching**: Implement Redis caching for scraped prices

## Support

For issues or questions:
1. Check the console logs (browser & server)
2. Verify all environment variables are set
3. Test the CopilotKit endpoint directly: `curl http://localhost:8000/copilotkit`