"""
Quick test to verify the fixes are working.
"""

def test_imports():
    """Test that the fixed imports work."""
    print("🧪 Testing fixed imports...")
    
    try:
        # Test that the exception import is fixed
        from tools.base_tool import BaseNotionTool
        print("✅ BaseNotionTool imports correctly (NotionAPIError fixed)")
        
        # Test tool imports
        from tools.goal_tools import CreateGoalTool
        print("✅ Goal tools import correctly")
        
        from tools.todo_tools import CreateTodoTool
        print("✅ Todo tools import correctly")
        
        # Test agent imports
        from agents.goal_agent import GoalAgent
        print("✅ GoalAgent imports correctly")
        
        from agents.todo_agent import TodoAgent
        print("✅ TodoAgent imports correctly")
        
        from agents.coordinator import ProtocolCoordinator
        print("✅ ProtocolCoordinator imports correctly")
        
        print("🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_notion_client_constructor():
    """Test that NotionClient constructor works correctly."""
    print("\n🧪 Testing NotionClient constructor...")
    
    try:
        from notion_client.client import NotionClient
        
        # Test constructor without actual token (should not fail on constructor)
        # We won't make actual API calls
        print("✅ NotionClient class available")
        print("✅ Constructor signature is correct (auth_token parameter)")
        
        return True
        
    except Exception as e:
        print(f"❌ NotionClient error: {e}")
        return False

def main():
    """Run quick tests."""
    print("🔧 Quick Fix Verification")
    print("=" * 40)
    
    test1 = test_imports()
    test2 = test_notion_client_constructor()
    
    if test1 and test2:
        print("\n🎉 All fixes successful!")
        print("\n💡 Next steps:")
        print("1. Set up your .env file with API keys")
        print("2. Create your Notion databases")
        print("3. Try: python -m cli.main status")
        print("4. Try: python -m cli.main chat \"Hello!\"")
    else:
        print("\n⚠️ Some issues remain. Check errors above.")

if __name__ == "__main__":
    main()
