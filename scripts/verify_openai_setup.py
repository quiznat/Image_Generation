import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_openai_setup():
    """Test if OpenAI is properly configured."""
    print("=== Testing OpenAI Setup ===\n")
    
    # Check API key from .env file
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-api-key-here":
        print("❌ OPENAI_API_KEY not found in .env file or not set properly!")
        print("   Please add your API key to the .env file:")
        print("   OPENAI_API_KEY=your-actual-api-key")
        return False
    
    print("✅ API key found in .env file")
    
    # Test connection
    try:
        client = OpenAI(api_key=api_key)
        
        # Simple test with chat completion
        print("🔄 Testing API connection...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": "Say 'API working'"}],
            max_tokens=10
        )
        
        if response.choices[0].message.content:
            print("✅ API connection successful!")
            print(f"   Response: {response.choices[0].message.content}")
        
        # Test DALL-E availability
        print("\n🔄 Testing DALL-E 3...")
        try:
            response = client.images.generate(
                model="dall-e-3",
                prompt="A simple test image of a red circle",
                size="1024x1024",
                quality="standard",
                n=1
            )
            if response.data:
                print("✅ DALL-E 3 is available!")
        except Exception as e:
            print(f"⚠️ DALL-E 3 test failed: {e}")
            print("   (This might be due to rate limits or API plan)")
        
        print("\n✅ Setup test complete! You're ready to process images.")
        return True
        
    except Exception as e:
        print(f"❌ API connection failed: {e}")
        return False

if __name__ == "__main__":
    test_openai_setup()
    input("\nPress Enter to exit...") 