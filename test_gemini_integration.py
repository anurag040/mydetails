#!/usr/bin/env python3
"""
Test script to verify Gemini integration with the unified LLM service
"""
import sys
import os
import asyncio

# Add the backend directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.unified_llm_service import UnifiedLLMService, LLMModel

async def test_gemini_integration():
    """Test Gemini integration with the unified LLM service"""
    print("🧪 Testing Gemini Integration...")
    
    # Initialize the unified LLM service
    llm_service = UnifiedLLMService()
    
    # Test 1: Check available models
    print("\n📋 Available Models:")
    available_models = llm_service.get_available_models()
    for provider, info in available_models["providers"].items():
        status = "✅ Available" if info["available"] else "❌ Not Available"
        print(f"  {provider.upper()}: {status}")
        if info["available"]:
            for model in info["models"]:
                print(f"    - {model}")
    
    # Test 2: Test OpenAI (should work with existing setup)
    print("\n🤖 Testing OpenAI GPT-4o-mini:")
    try:
        openai_response = await llm_service.generate_completion(
            prompt="Explain what statistical correlation means in 2 sentences.",
            model=LLMModel.GPT_4O_MINI,
            max_tokens=100,
            temperature=0.3
        )
        print(f"✅ OpenAI Response: {openai_response[:100]}...")
    except Exception as e:
        print(f"❌ OpenAI Error: {str(e)}")
    
    # Test 3: Test Gemini (requires GEMINI_API_KEY)
    print("\n💎 Testing Gemini Pro:")
    try:
        gemini_response = await llm_service.generate_completion(
            prompt="Explain what statistical correlation means in 2 sentences.",
            model=LLMModel.GEMINI_PRO,
            max_tokens=100,
            temperature=0.3
        )
        print(f"✅ Gemini Response: {gemini_response[:100]}...")
    except Exception as e:
        print(f"❌ Gemini Error: {str(e)}")
        if "API key" in str(e).lower():
            print("💡 Hint: Set GEMINI_API_KEY environment variable to test Gemini")
    
    # Test 4: Test model fallback
    print("\n🔄 Testing Model Fallback:")
    try:
        fallback_response = await llm_service.generate_completion(
            prompt="What is machine learning?",
            model="invalid-model",  # This should fallback
            max_tokens=50,
            temperature=0.3
        )
        print(f"✅ Fallback Response: {fallback_response[:100]}...")
    except Exception as e:
        print(f"❌ Fallback Error: {str(e)}")

if __name__ == "__main__":
    # Check environment variables
    print("🔧 Environment Check:")
    openai_key = os.getenv("OPENAI_API_KEY")
    gemini_key = os.getenv("GEMINI_API_KEY")
    
    print(f"  OPENAI_API_KEY: {'✅ Set' if openai_key else '❌ Not Set'}")
    print(f"  GEMINI_API_KEY: {'✅ Set' if gemini_key else '❌ Not Set'}")
    
    if not openai_key and not gemini_key:
        print("\n⚠️  Warning: No API keys found. Set OPENAI_API_KEY or GEMINI_API_KEY to test.")
    
    # Run the test
    asyncio.run(test_gemini_integration())
    
    print("\n🎯 Integration test completed!")
