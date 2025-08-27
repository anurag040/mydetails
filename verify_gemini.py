#!/usr/bin/env python3
"""
Verify Gemini API integration
Run this script to test if your GEMINI_API_KEY is working
"""
import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

def load_env_file():
    """Load environment variables from .env file"""
    env_file = Path(__file__).parent / "backend" / ".env"
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

def main():
    print("🧪 Gemini API Verification")
    print("=" * 50)
    
    # Load .env file
    load_env_file()
    
    # Check environment
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        print("❌ GEMINI_API_KEY not found")
        print("💡 Make sure it's set in backend/.env file")
        return False
    
    print(f"✅ GEMINI_API_KEY found (length: {len(gemini_key)})")
    
    # Test import
    try:
        import google.generativeai as genai
        print("✅ google.generativeai imported successfully")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        print("💡 Run: pip install google-generativeai==0.3.2")
        return False
    
    # Test API
    try:
        print("🔄 Testing Gemini API connection...")
        genai.configure(api_key=gemini_key)
        model = genai.GenerativeModel('gemini-pro')
        
        response = model.generate_content("Reply with exactly: 'Gemini is working!'")
        
        print(f"✅ Success! Response: {response.text}")
        
        # Test unified LLM service
        print("\n🔄 Testing Unified LLM Service...")
        from app.services.unified_llm_service import UnifiedLLMService, LLMModel
        
        llm_service = UnifiedLLMService()
        model_info = llm_service.get_model_info()
        
        print(f"Available models: {model_info['available_models']}")
        print(f"Gemini available: {model_info['providers']['gemini']['available']}")
        
        if llm_service.is_model_available(LLMModel.GEMINI_PRO):
            print("✅ Unified LLM Service can use Gemini")
            return True
        else:
            print("❌ Unified LLM Service cannot use Gemini")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 Gemini integration is fully working!")
        print("You can now use Gemini models in your application.")
    else:
        print("\n⚠️ Gemini integration needs attention.")
        print("Check the errors above and fix them.")
    
    input("\nPress Enter to exit...")
