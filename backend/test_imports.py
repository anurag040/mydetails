#!/usr/bin/env python3
"""
Test script to check if all required imports are available
"""
import sys
import os

def test_imports():
    """Test if all required packages can be imported"""
    print("🧪 Testing Package Imports...")
    
    # Test basic packages
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
    
    try:
        import openai
        print("✅ OpenAI imported successfully")
    except ImportError as e:
        print(f"❌ OpenAI import failed: {e}")
    
    try:
        import google.generativeai as genai
        print("✅ Google Generative AI imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Google Generative AI import failed: {e}")
        print("💡 Need to install: pip install google-generativeai==0.3.2")
        return False

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("🎯 All imports successful!")
    else:
        print("⚠️ Some imports failed - check package installation")
