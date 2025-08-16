"""
Basic tests for the Notion Python client.

This module contains basic unit tests to verify core functionality
of the Notion client without requiring API access.
"""

import pytest
from unittest.mock import Mock, patch

from notion_client import NotionClient
from notion_client.auth import IntegrationAuth, OAuthAuth
from notion_client.exceptions import NotionAuthError, NotionAPIError
from notion_client.utils import (
    create_rich_text,
    create_page_parent,
    create_paragraph_block,
    validate_notion_id,
    validate_email,
    validate_url,
)


class TestNotionClient:
    """Test cases for the main NotionClient class."""
    
    def test_client_initialization_with_token(self):
        """Test client initialization with integration token."""
        client = NotionClient(auth_token="secret_test_token", auto_load_env=False)
        
        assert client is not None
        assert isinstance(client.auth, IntegrationAuth)
        assert client.auth.token == "secret_test_token"
    
    def test_client_initialization_without_auth_raises_error(self):
        """Test that client raises error when no auth is provided."""
        with pytest.raises(NotionAuthError):
            NotionClient(auto_load_env=False)
    
    def test_client_from_token_class_method(self):
        """Test creating client using from_token class method."""
        client = NotionClient.from_token("secret_test_token")
        
        assert client is not None
        assert isinstance(client.auth, IntegrationAuth)
    
    def test_client_endpoints_are_accessible(self):
        """Test that all endpoint properties are accessible."""
        client = NotionClient(auth_token="secret_test_token", auto_load_env=False)
        
        # Test that endpoints are accessible (lazy loaded)
        assert client.pages is not None
        assert client.blocks is not None
        assert client.databases is not None
        assert client.users is not None
        assert client.search is not None
    
    def test_client_context_manager(self):
        """Test that client works as context manager."""
        with NotionClient(auth_token="secret_test_token", auto_load_env=False) as client:
            assert client is not None
        
        # Client should be closed after context exit
        # (We can't easily test this without mocking)


class TestAuthentication:
    """Test cases for authentication classes."""
    
    def test_integration_auth_initialization(self):
        """Test IntegrationAuth initialization."""
        auth = IntegrationAuth("secret_test_token")
        
        assert auth.token == "secret_test_token"
        assert auth.is_valid()
    
    def test_integration_auth_empty_token_raises_error(self):
        """Test that empty token raises error."""
        with pytest.raises(NotionAuthError):
            IntegrationAuth("")
    
    def test_integration_auth_headers(self):
        """Test that IntegrationAuth provides correct headers."""
        auth = IntegrationAuth("secret_test_token")
        headers = auth.get_headers()
        
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer secret_test_token"
        assert headers["Content-Type"] == "application/json"
    
    def test_oauth_auth_initialization(self):
        """Test OAuthAuth initialization."""
        auth = OAuthAuth(
            client_id="test_client_id",
            client_secret="test_client_secret",
            redirect_uri="https://example.com/callback"
        )
        
        assert auth.client_id == "test_client_id"
        assert auth.client_secret == "test_client_secret"
        assert auth.redirect_uri == "https://example.com/callback"
    
    def test_oauth_auth_missing_params_raises_error(self):
        """Test that missing OAuth params raise error."""
        with pytest.raises(NotionAuthError):
            OAuthAuth(
                client_id="test_id",
                client_secret="",  # Missing secret
                redirect_uri="https://example.com/callback"
            )


class TestUtilities:
    """Test cases for utility functions."""
    
    def test_create_rich_text(self):
        """Test rich text creation."""
        rich_text = create_rich_text("Hello World", bold=True, color="blue")
        
        assert rich_text["type"] == "text"
        assert rich_text["text"]["content"] == "Hello World"
        assert rich_text["annotations"]["bold"] is True
        assert rich_text["annotations"]["color"] == "blue"
        assert rich_text["plain_text"] == "Hello World"
    
    def test_create_rich_text_with_link(self):
        """Test rich text creation with link."""
        rich_text = create_rich_text(
            "Click here", 
            url="https://example.com"
        )
        
        assert rich_text["text"]["link"]["url"] == "https://example.com"
        assert rich_text["href"] == "https://example.com"
    
    def test_create_page_parent(self):
        """Test page parent creation."""
        parent = create_page_parent("12345678901234567890123456789012")
        
        assert parent["type"] == "page_id"
        assert parent["page_id"] == "12345678901234567890123456789012"
    
    def test_create_paragraph_block(self):
        """Test paragraph block creation."""
        block = create_paragraph_block("Test paragraph", bold=True)
        
        assert block["type"] == "paragraph"
        assert block["paragraph"]["rich_text"][0]["text"]["content"] == "Test paragraph"
        assert block["paragraph"]["rich_text"][0]["annotations"]["bold"] is True
    
    def test_validate_notion_id_valid(self):
        """Test Notion ID validation with valid IDs."""
        # 32 character hex string
        valid_id = "12345678901234567890123456789012"
        assert validate_notion_id(valid_id) is True
        
        # With dashes (UUID format)
        valid_id_with_dashes = "12345678-9012-3456-7890-123456789012"
        assert validate_notion_id(valid_id_with_dashes) is True
    
    def test_validate_notion_id_invalid(self):
        """Test Notion ID validation with invalid IDs."""
        # Too short
        assert validate_notion_id("12345") is False
        
        # Too long
        assert validate_notion_id("123456789012345678901234567890123") is False
        
        # Non-hex characters
        assert validate_notion_id("1234567890123456789012345678901g") is False
        
        # Empty string
        assert validate_notion_id("") is False
        
        # None
        assert validate_notion_id(None) is False
    
    def test_validate_email_valid(self):
        """Test email validation with valid emails."""
        assert validate_email("test@example.com") is True
        assert validate_email("user.name+tag@domain.co.uk") is True
    
    def test_validate_email_invalid(self):
        """Test email validation with invalid emails."""
        assert validate_email("invalid-email") is False
        assert validate_email("@example.com") is False
        assert validate_email("test@") is False
        assert validate_email("") is False
        assert validate_email(None) is False
    
    def test_validate_url_valid(self):
        """Test URL validation with valid URLs."""
        assert validate_url("https://example.com") is True
        assert validate_url("http://test.co.uk/path") is True
        assert validate_url("https://subdomain.example.com/path?param=value") is True
    
    def test_validate_url_invalid(self):
        """Test URL validation with invalid URLs."""
        assert validate_url("not-a-url") is False
        assert validate_url("ftp://example.com") is False  # Only http/https typically
        assert validate_url("") is False
        assert validate_url(None) is False


class TestExceptions:
    """Test cases for custom exceptions."""
    
    def test_notion_api_error(self):
        """Test NotionAPIError creation."""
        error = NotionAPIError("Test error", status_code=400)
        
        assert str(error) == "Test error"
        assert error.status_code == 400
        assert error.message == "Test error"
    
    def test_notion_auth_error(self):
        """Test NotionAuthError creation."""
        error = NotionAuthError("Authentication failed")
        
        assert str(error) == "Authentication failed"
        assert error.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__])
