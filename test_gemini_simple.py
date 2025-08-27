#!/usr/bin/env python3
"""
Test Gemini API with environment variables
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('backend/.env')

def main():
    print("🧪 Testing Gemini API Integration")
    print("=" * 40)
    
    # Check if API key is loaded
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("❌ GEMINI_API_KEY not found in environment")
        return
    
    print("✅ GEMINI_API_KEY found in environment")
    
    # Test import
    try:
        import google.generativeai as genai
        print("✅ google.generativeai imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import google.generativeai: {e}")
        print("💡 Install with: pip install google-generativeai==0.3.2")
        return
    
    # Test API connection
    try:
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-pro')
        
        print("🔄 Testing Gemini API...")
        response = model.generate_content("Say 'Hello from Gemini API!' and nothing else.")
        
        print(f"✅ Gemini Response: {response.text}")
        print("🎉 Gemini integration is working perfectly!")
        
    except Exception as e:
        print(f"❌ Gemini API Error: {str(e)}")
        if "API_KEY" in str(e):
            print("💡 Check if your GEMINI_API_KEY is valid")
        elif "quota" in str(e).lower():
            print("💡 API quota exceeded - check your Gemini API usage")
        else:
            print("💡 Check your internet connection and API key")

if __name__ == "__main__":
    main()
