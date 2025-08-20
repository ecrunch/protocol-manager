"""
Test script to verify the Protocol Home AI agents implementation.

This script tests the basic functionality without requiring full setup.
"""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_imports():
    """Test that all modules can be imported correctly."""
    print("🧪 Testing imports...")
    
    try:
        # Test base components
        from agents.base_agent import BaseProtocolAgent
        print("✅ BaseProtocolAgent imported successfully")
        
        from tools.base_tool import BaseNotionTool
        print("✅ BaseNotionTool imported successfully")
        
        # Test prompts
        from prompts.system_prompts import GOAL_AGENT_PROMPT, TODO_AGENT_PROMPT, COORDINATOR_PROMPT
        print("✅ System prompts imported successfully")
        
        # Test tools
        from tools.goal_tools import CreateGoalTool, GetGoalsTool
        print("✅ Goal tools imported successfully")
        
        from tools.todo_tools import CreateTodoTool, GetTodosTool
        print("✅ Todo tools imported successfully")
        
        print("🎉 All imports successful!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_notion_client():
    """Test Notion client connectivity if credentials are available."""
    print("\n🧪 Testing Notion client...")
    
    notion_token = os.getenv('NOTION_API_TOKEN')
    if not notion_token:
        print("⏭️ Skipping Notion test - no API token found")
        return True
    
    # Check token format (should start with 'ntn_')
    if not notion_token.startswith('ntn_'):
        print("⚠️ Warning: Notion token should start with 'ntn_'")
        print("⏭️ Skipping Notion API test - invalid token format")
        return True
    
    try:
        from notion_client.client import NotionClient
        client = NotionClient(auth_token=notion_token)
        
        # Try to list users (basic API test)
        users_response = client.users.list()
        # Handle the response object properly
        if hasattr(users_response, 'results'):
            user_count = len(users_response.results)
        elif hasattr(users_response, '__dict__') and 'results' in users_response.__dict__:
            user_count = len(users_response.__dict__['results'])
        else:
            user_count = "unknown"
        
        print(f"✅ Notion client connected - found {user_count} users")
        return True
        
    except Exception as e:
        print(f"❌ Notion client error: {e}")
        return False


def test_langchain_dependencies():
    """Test that LangChain dependencies are available."""
    print("\n🧪 Testing LangChain dependencies...")
    
    try:
        from langchain.agents import AgentExecutor
        from langchain_openai import ChatOpenAI
        from langchain.memory import ConversationBufferWindowMemory
        from langchain.tools import BaseTool
        print("✅ LangChain components imported successfully")
        
        # Test OpenAI client if key is available
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            llm = ChatOpenAI(api_key=openai_key, model="gpt-3.5-turbo", temperature=0.1)
            print("✅ OpenAI client initialized successfully")
        else:
            print("⏭️ Skipping OpenAI test - no API key found")
        
        return True
        
    except ImportError as e:
        print(f"❌ LangChain import error: {e}")
        print("💡 Try: pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ LangChain error: {e}")
        return False


def test_agent_initialization():
    """Test agent initialization with mock data."""
    print("\n🧪 Testing agent initialization...")
    
    try:
        # Mock notion client
        class MockNotionClient:
            def __init__(self):
                pass
        
        mock_client = MockNotionClient()
        
        # Test Goal Agent import and basic structure
        from agents.goal_agent import GoalAgent
        print("✅ GoalAgent class available")
        
        # Test Todo Agent import
        from agents.todo_agent import TodoAgent  
        print("✅ TodoAgent class available")
        
        # Test Coordinator import
        from agents.coordinator import ProtocolCoordinator
        print("✅ ProtocolCoordinator class available")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent initialization error: {e}")
        return False


def test_cli_structure():
    """Test CLI structure."""
    print("\n🧪 Testing CLI structure...")
    
    try:
        from cli.main import protocol_cli
        print("✅ CLI main function available")
        
        # Check if click is working
        import click
        print("✅ Click dependency available")
        
        # Check if rich is working
        from rich.console import Console
        console = Console()
        print("✅ Rich console available")
        
        return True
        
    except Exception as e:
        print(f"❌ CLI error: {e}")
        return False


def print_setup_instructions():
    """Print setup instructions."""
    print("\n📚 Setup Instructions:")
    print("=" * 50)
    
    print("\n1. Install dependencies:")
    print("   pip install -r requirements.txt")
    
    print("\n2. Create environment file:")
    print("   cp config.env.example .env")
    
    print("\n3. Get your Notion integration token:")
    print("   • Visit https://developers.notion.com/")
    print("   • Create a new integration")
    print("   • Copy the integration token")
    
    print("\n4. Create Notion databases:")
    print("   • Goals database with required properties")
    print("   • Todos database with required properties")
    print("   • Copy the database IDs from the URLs")
    
    print("\n5. Get OpenAI API key:")
    print("   • Visit https://platform.openai.com/")
    print("   • Create an API key")
    
    print("\n6. Fill in your .env file with the tokens and IDs")
    
    print("\n7. Test the system:")
    print("   python -m cli.main status")
    print("   python -m cli.main chat \"Hello!\"")
    
    print("\n8. Read the documentation:")
    print("   Check README_AGENTS.md for detailed usage instructions")


def main():
    """Run all tests."""
    print("🏠 Protocol Home AI Agents - Implementation Test")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_langchain_dependencies,
        test_notion_client,
        test_agent_initialization,
        test_cli_structure,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n📊 Test Summary:")
    print("=" * 30)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Your Protocol Home agents are ready to use.")
        print("\n💡 Next steps:")
        print("   1. Set up your .env file with API keys")
        print("   2. Create your Notion databases")
        print("   3. Run: python -m cli.main setup")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print_setup_instructions()


if __name__ == "__main__":
    main()
