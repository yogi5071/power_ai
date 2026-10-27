"""
Base Repository
Power AI Copilot
"""

from abc import ABC, abstractmethod


class BaseRepository(ABC):

    @abstractmethod
    def get_by_id(self, id):
        """
        Get single object by id.
        """
        pass