#!/usr/bin/env python3
"""
Test script to verify Google Gemini integration with CopilotKit
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_gemini_connection():
    """Test basic Gemini API connection"""
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key or api_key == "your_actual_google_api_key_here":
            print("❌ GOOGLE_API_KEY not set in .env file")
            print("Please set your Google Gemini API key in backend/.env")
            print("Get it from: https://makersuite.google.com/app/apikey")
            return False
        
        # Initialize Gemini model
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            google_api_key=api_key,
            temperature=0.7
        )
        
        # Test with a simple message
        response = llm.invoke("Hello! Can you confirm you're working? Just say 'Yes, Gemini is working!'")
        print("✅ Gemini API connection successful!")
        print(f"Response: {response.content}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini API connection failed: {e}")
        return False

def test_copilotkit_import():
    """Test CopilotKit imports"""
    try:
        from copilotkit import CopilotKitSDK, Action
        from copilotkit.integrations.fastapi import add_fastapi_endpoint
        print("✅ CopilotKit imports successful!")
        return True
    except Exception as e:
        print(f"❌ CopilotKit import failed: {e}")
        return False

def main():
    print("🧪 Testing Google Gemini integration with CopilotKit...")
    print("=" * 50)
    
    # Test CopilotKit imports
    copilotkit_ok = test_copilotkit_import()
    
    # Test Gemini connection
    gemini_ok = test_gemini_connection()
    
    print("\n" + "=" * 50)
    if copilotkit_ok and gemini_ok:
        print("🎉 All tests passed! Your setup is ready.")
        print("You can now start your server with:")
        print("uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()