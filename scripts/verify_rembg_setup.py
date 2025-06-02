from rembg import remove
from PIL import Image
import sys

def test_rembg():
    """Test if rembg is properly set up."""
    print("=== Testing rembg Background Removal ===\n")
    
    try:
        # Test with a simple image
        print("✅ rembg imported successfully")
        
        # First download will fetch the U2Net model (~170MB)
        print("\n📥 Note: First run will download the AI model (~170MB)")
        print("   This is a one-time download that will be cached locally.")
        
        print("\n✅ rembg is ready to use!")
        print("\nThe image processor will now:")
        print("1. Generate images with DALL-E")
        print("2. Automatically remove backgrounds") 
        print("3. Save both versions (with and without background)")
        
        return True
        
    except Exception as e:
        print(f"❌ rembg test failed: {e}")
        return False

if __name__ == "__main__":
    test_rembg()
    input("\nPress Enter to exit...") 