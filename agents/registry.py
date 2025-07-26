import datetime as dt
from typing import List, Dict, Any, Tuple

from pydantic import BaseModel, Field

from agents.main import AsyncSimpleAgent


class Agent(BaseModel):
    agent_id: str = Field(
        ...,
        description="Unique identifier of the model.",
        examples=["user-123"]
    )
    agent_version: int = Field(
        ...,
        description="Version of the agent.",
        examples=[1]
    )
    department_name: str = Field(
        ...,
        description="Department to which the agent belongs.",
        examples=["Engineering", "Marketing"]
    )
    name: str = Field(
        ...,
        description="Username of the user.",
        examples=["example_user"]
    )
    description: str = Field(
        ...,
        description="Description of the agent, if available.",
        examples=["This is an example agent."]
    )
    tags: List[str] = Field(
        default_factory=list,
        description="List of tags associated with the agent.",
        examples=[["tag1", "tag2"]]
    )
    icon_link: str | None = Field(
        None,
        description="Link to the user's icon or avatar, if available.",
        examples=["https://example.com/icon.png"]
    )
    created_at: dt.datetime = Field(
        ...,
        description="Timestamp when the agent was created.",
        examples=[dt.datetime.now()]
    )
    updated_at: dt.datetime = Field(
        ...,
        description="Timestamp when the agent was last updated.",
        examples=[dt.datetime.now()]
    )

class SearchedAgent(BaseModel):
    """
    Represents a searched agent with its details.
    """
    agent_id: str = Field(
        ...,
        description="Unique identifier of the agent.",
        examples=["agent-123"]
    )
    version: int = Field(
        ...,
        description="Version of the agent.",
        examples=[1]
    )
    score: float = Field(
        ...,
        description="Relevance score of the search result.",
        examples=[0.95]
    )
    reason: str = Field(
        ...,
        description="Reason for the relevance score.",
        examples=["Matched query keywords"]
    )

class SearchResult(BaseModel):
    """
    Represents a search result for an agent.
    """
    agents: List[SearchedAgent] = Field(
        ...,
        description="List of agents that match the search criteria.",
        examples=[[{"agent_id": "agent-123", "version": 1, "score": 0.95, "reason": "Matched query keywords"}]]
    )

class AgentRegistry:
    def __init__(
        self,
        agent_cards: List[Dict[str, Any]],
    ) -> None:
        self.agent_cards = [
            Agent(**card) for card in agent_cards
        ]

    async def asearch_by_ai(
        self,
        query: str,
        context: str,
        search_engine: AsyncSimpleAgent
    ) -> Tuple[List[Dict[str, Any]], Exception | None]:
        """
        Search for agents based on the query and context using AI.
        This method uses the agent cards to find relevant agents based on the search criteria.

        Args:
            query (str): The search query.
            context (str): Additional context for the search.
        
        Returns:
            List[Agent]: List of agents matching the search criteria.
        """

        departments = set()
        info = "Available Agents:\n"
        agent_cards = self.agent_cards.copy()
        agent_cards.sort(key=lambda x: x.department_name)

        for agent in self.agent_cards:
            info += f"- {agent.name}: {agent.department_name} (ID: {agent.agent_id}, Version: {agent.agent_version}, Description: {agent.description})\n\n"
            departments.add(agent.department_name)
            
        system_prompt = f"""
## 역할

당신은 유저의 문제를 이해하여 최적의 AI 에이전트를 추천하는 AI 어시스턴트입니다.
유저는 반드시 **특정 기업부서에서 일하는 사람입니다.** 이와 관련된 문제를 회사와 해결함에 있습니다.

## Task
- 유저의 맥락을 고려하여 최적의 AI 에이전트를 추천합니다.
- 추천할 에이전트는 유저의 문제를 해결할 수 있는 에이전트여야 합니다.

## 유저가 처한 맥락
{context}

## 에이전트의 목록
{info}
---
        """
        user_prompt = f"""
{query}
        """

        searched_result, err = await search_engine.aparse(
            messages=[{"role": "system", "content": system_prompt},
                      {"role": "user", "content": user_prompt}],
            deployment_id="gpt-4o",
            response_fmt=SearchResult
        )
        if err or not searched_result:
            return [], err
        
        results = []
        for searched in searched_result.agents:
            for agent in self.agent_cards:
                if agent.agent_id == searched.agent_id and agent.agent_version == searched.version:
                    results.append(
                        {
                            "agent_id": agent.agent_id,
                            "agent_version": agent.agent_version,
                            "department_name": agent.department_name,
                            "name": agent.name,
                            "description": agent.description,
                            "tags": agent.tags,
                            "icon_link": agent.icon_link,
                            "created_at": agent.created_at,
                            "updated_at": agent.updated_at
                        }
                    )

        return results, None
        


        
        

