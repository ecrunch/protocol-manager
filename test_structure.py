"""
Simple test to verify the package structure is correct.
Run this file to check if the basic imports work.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing basic imports...")
    
    # Test core imports
    from notion_client import NotionClient
    print("✅ NotionClient import successful")
    
    from notion_client.exceptions import NotionAPIError, NotionAuthError
    print("✅ Exceptions import successful")
    
    from notion_client.utils import create_rich_text, create_paragraph_block
    print("✅ Utils import successful")
    
    print("\n🎉 All imports successful! The Notion client is properly structured.")
    print("\nNext steps:")
    print("1. Install dependencies: requests, pydantic, python-dotenv")
    print("2. Set up your .env file with NOTION_API_TOKEN")
    print("3. Run the examples/basic_usage.py script")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Some modules may be missing or incorrectly structured.")

except Exception as e:
    print(f"❌ Unexpected error: {e}")
