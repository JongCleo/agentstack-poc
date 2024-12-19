#!/usr/bin/env python
import sys
from crew import TweetproposerCrew
import agentops
import asyncio

import logging

from src.twitter.utils import fetch_tweets

logger = logging.getLogger(__name__)

agentops.init(default_tags=["crewai", "agentstack"])


def run():
    """
    Run the crew.
    """

    user_interests = """
    Applied AI consulting for agentic AI, RAG (retrieval augmented generation) 
    and any developments in the space including research papers, fundraising, and 
    any other relevant information.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    tweets = loop.run_until_complete(fetch_tweets())

    inputs = []

    for tweet in tweets:
        inputs.append(
            {
                "conversation_context": tweet.model_dump(),
                "user_interests": user_interests,
            }
        )

    TweetproposerCrew().crew().kickoff_for_each(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {}
    try:
        TweetproposerCrew().crew().train(
            n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")


def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        TweetproposerCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {}
    try:
        TweetproposerCrew().crew().test(
            n_iterations=int(sys.argv[1]), openai_model_name=sys.argv[2], inputs=inputs
        )

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    run()
