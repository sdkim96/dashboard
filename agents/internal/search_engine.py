import abc

class BaseSearchEngine(abc.ABC):

    @abc.abstractmethod
    async def asearch(
        self,
        **kwargs
    ):
        """
        Abstract method for searching agents asynchronously.
        
        Args:
            **kwargs: Keyword arguments for search parameters.
        
        Returns:
            List[mdl.Agent]: List of agents matching the search criteria.
        """
        pass