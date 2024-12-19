from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel
from src.twitter.models import TwitterConversation


class FilterTweetOutput(BaseModel):
    """Response from the filterer agent"""

    tweet: TwitterConversation
    selection_reason: str


class DraftResponseOutput(BaseModel):
    """Response from the draft_responses agent"""

    tweet: str
    draft: str
    url: str


@CrewBase
class TweetproposerCrew:
    """tweet_proposer crew"""

    # Agent definitions
    @agent
    def filterer(self) -> Agent:
        return Agent(
            config=self.agents_config["filterer"],
            allow_delegation=False,
            verbose=True,
        )

    @agent
    def responder(self) -> Agent:
        return Agent(
            config=self.agents_config["responder"],
            allow_delegation=False,
            verbose=True,
        )

    @task
    def filter_tweets(self) -> Task:
        return Task(
            config=self.tasks_config["filter_tweet"],
            output_pydantic=FilterTweetOutput,
        )

    @task
    def draft_responses(self) -> Task:
        return Task(
            config=self.tasks_config["draft_response"],
            output_pydantic=DraftResponseOutput,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Test crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
