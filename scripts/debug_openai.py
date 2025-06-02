#!/usr/bin/env python3
"""Debug script to test OpenAI client initialization."""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=== OpenAI Debug Script ===")
print(f"Python version: {sys.version}")
print()

# Check OpenAI library version
try:
    import openai
    print(f"OpenAI library version: {openai.__version__}")
except ImportError:
    print("ERROR: OpenAI library not installed")
    sys.exit(1)

# Check for proxy environment variables
proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy', 'ALL_PROXY', 'all_proxy']
print("\nProxy Environment Variables:")
for var in proxy_vars:
    value = os.environ.get(var)
    if value:
        print(f"  {var}: {value}")

# Check OpenAI API key
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    print(f"\nOpenAI API Key: {'*' * 20}{api_key[-4:]}")
else:
    print("\nERROR: OPENAI_API_KEY not found")

# Try to initialize OpenAI client
print("\nTrying to initialize OpenAI client...")
try:
    from openai import OpenAI
    
    # Simple initialization
    client = OpenAI(api_key=api_key)
    print("SUCCESS: Basic client initialization worked")
    
    # Try a simple API call
    print("\nTesting API connection...")
    try:
        response = client.models.list()
        print(f"SUCCESS: API connection working, found {len(list(response))} models")
    except Exception as e:
        print(f"ERROR: API call failed: {e}")
        
except Exception as e:
    print(f"ERROR: Client initialization failed: {e}")
    print(f"Error type: {type(e).__name__}")
    
    # Try older initialization method if new one fails
    print("\nTrying legacy initialization...")
    try:
        openai.api_key = api_key
        models = openai.Model.list()
        print("SUCCESS: Legacy API initialization worked")
    except Exception as e2:
        print(f"ERROR: Legacy initialization also failed: {e2}")

print("\nDebug complete.") 