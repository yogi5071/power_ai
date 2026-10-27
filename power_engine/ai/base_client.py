"""
Base AI Client
"""

from abc import ABC, abstractmethod


class BaseClient(ABC):

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate response from AI model.
        """
        pass

    @abstractmethod
    def chat(self, message: str) -> str:
        """
        Chat with AI model.
        """
        pass