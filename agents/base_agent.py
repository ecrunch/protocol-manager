"""
Base agent class for Protocol Home management.

This module provides the foundational BaseProtocolAgent class that all
specialized agents inherit from.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import os
from langchain.agents import AgentExecutor, create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferWindowMemory
from langchain.tools import BaseTool
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from notion_client.client import NotionClient


class BaseProtocolAgent(ABC):
    """Base class for all Protocol Home management agents."""
    
    def __init__(
        self,
        notion_client: NotionClient,
        openai_api_key: Optional[str] = None,
        model_name: str = "gpt-5-mini",
        temperature: float = 0.1,
        max_iterations: int = 10,
        memory_k: int = 10,
        verbose: bool = False,
    ):
        """
        Initialize the base agent.
        
        Args:
            notion_client: Initialized Notion client instance
            openai_api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model_name: OpenAI model to use (gpt-5-mini, etc.)
            temperature: Temperature for LLM responses (0.0-1.0)
            max_iterations: Maximum iterations for agent execution
            memory_k: Number of conversation turns to remember
            verbose: Whether to enable verbose logging
        """
        self.notion = notion_client
        self.model_name = model_name
        self.temperature = temperature
        self.max_iterations = max_iterations
        self.verbose = verbose
        
        # Initialize OpenAI LLM
        api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OpenAI API key must be provided either as argument or "
                "set in OPENAI_API_KEY environment variable"
            )
            
        self.llm = ChatOpenAI(
            api_key=api_key,
            model=model_name,
            temperature=temperature
        )
        
        # Initialize memory
        self.memory = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=memory_k
        )
        
        # Setup tools and agent
        self.tools = self._setup_tools()
        self.agent_executor = self._create_agent()
        
    @abstractmethod
    def _setup_tools(self) -> List[BaseTool]:
        """
        Setup the tools for this agent.
        
        Each agent subclass must implement this method to define
        the specific tools it needs.
        
        Returns:
            List of LangChain tools for this agent
        """
        pass
        
    @abstractmethod
    def _get_system_prompt(self) -> str:
        """
        Get the system prompt for this agent.
        
        Each agent subclass must implement this method to define
        its specific instructions and behavior.
        
        Returns:
            System prompt string for this agent
        """
        pass
        
    def _create_agent(self) -> AgentExecutor:
        """
        Create the LangChain agent with tools and memory.
        
        Returns:
            Configured AgentExecutor instance
        """
        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages([
            ("system", self._get_system_prompt()),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        # Create the agent
        agent = create_openai_tools_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
        
        # Create and return the agent executor
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            memory=self.memory,
            verbose=self.verbose,
            max_iterations=self.max_iterations,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )
        
    def process(self, user_input: str) -> str:
        """
        Process a user request and return the response.
        
        Args:
            user_input: The user's input/request
            
        Returns:
            Agent's response to the user
        """
        try:
            result = self.agent_executor.invoke({"input": user_input})
            return result.get("output", "I apologize, but I couldn't process your request.")
        except Exception as e:
            error_msg = f"An error occurred while processing your request: {str(e)}"
            if self.verbose:
                print(f"Agent error: {error_msg}")
            return error_msg
            
    async def aprocess(self, user_input: str) -> str:
        """
        Asynchronously process a user request and return the response.
        
        Args:
            user_input: The user's input/request
            
        Returns:
            Agent's response to the user
        """
        try:
            result = await self.agent_executor.ainvoke({"input": user_input})
            return result.get("output", "I apologize, but I couldn't process your request.")
        except Exception as e:
            error_msg = f"An error occurred while processing your request: {str(e)}"
            if self.verbose:
                print(f"Agent error: {error_msg}")
            return error_msg
            
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get the conversation history from memory.
        
        Returns:
            List of conversation messages
        """
        return self.memory.chat_memory.messages
        
    def clear_memory(self) -> None:
        """Clear the conversation memory."""
        self.memory.clear()
        
    def get_tools_info(self) -> List[Dict[str, str]]:
        """
        Get information about available tools.
        
        Returns:
            List of tool information dictionaries
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
            }
            for tool in self.tools
        ]
        
    def set_verbose(self, verbose: bool) -> None:
        """
        Set the verbose mode for the agent.
        
        Args:
            verbose: Whether to enable verbose logging
        """
        self.verbose = verbose
        self.agent_executor.verbose = verbose
