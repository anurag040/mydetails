#!/usr/bin/env python3
"""
Simple Gemini API test
"""
import os
import sys

def test_environment():
    """Test environment variables"""
    print("🔧 Environment Check:")
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    print(f"  OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Not Set'}")
    print(f"  GEMINI_API_KEY: {'✅ Set' if gemini_key else '❌ Not Set'}")
    
    return gemini_key is not None

def test_imports():
    """Test required imports"""
    print("\n📦 Testing Imports:")
    
    try:
        import google.generativeai as genai
        print("✅ google.generativeai imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import google.generativeai: {e}")
        return False

def test_gemini_basic():
    """Test basic Gemini functionality"""
    print("\n💎 Testing Gemini Basic:")
    
    try:
        import google.generativeai as genai
        
        # Configure API key
        gemini_key = os.getenv("GEMINI_API_KEY")
        if not gemini_key:
            print("❌ GEMINI_API_KEY not found")
            return False
            
        genai.configure(api_key=gemini_key)
        
        # Create model
        model = genai.GenerativeModel('gemini-pro')
        
        # Generate content
        response = model.generate_content("Say 'Hello from Gemini!' in exactly those words.")
        
        print(f"✅ Gemini Response: {response.text}")
        return True
        
    except Exception as e:
        print(f"❌ Gemini Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Simple Gemini Integration Test")
    print("=" * 40)
    
    # Test environment
    env_ok = test_environment()
    
    # Test imports
    import_ok = test_imports()
    
    # Test Gemini if environment and imports are OK
    if env_ok and import_ok:
        gemini_ok = test_gemini_basic()
        
        if gemini_ok:
            print("\n🎉 All tests passed! Gemini integration is working.")
        else:
            print("\n⚠️ Gemini test failed.")
    else:
        print("\n⚠️ Prerequisites not met. Cannot test Gemini.")
    
    print("\n✨ Test completed!")
