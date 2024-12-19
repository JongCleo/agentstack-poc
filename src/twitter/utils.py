import os
from logging import getLogger
from twikit import Client as TwikitClient
from src.twitter.models import TwitterConversation, TweetContext, TwitterUser

from typing import Optional, List

logger = getLogger(__name__)

client = TwikitClient("en-US")


async def fetch_tweets() -> List[TwitterConversation]:
    """Fetch tweets and build conversation threads"""

    await client.login(
        auth_info_1=os.getenv("TWITTER_USERNAME"),
        auth_info_2=os.getenv("TWITTER_EMAIL"),
        password=os.getenv("TWITTER_PASSWORD"),
    )
    logger.info("Successfully logged in to Twitter")

    tweets = await client.search_tweet("query", "Latest")

    MAX_RESULTS = 5
    result_count = 0
    results: List[TwitterConversation] = []

    while result_count < MAX_RESULTS:
        for tweet in tweets:
            # Skip result if it has media because we don't support it yet
            if tweet.media:
                logger.debug(
                    f"Skipping tweet {tweet.id} because it has video or picture"
                )
                continue

            try:
                conversation = await _get_conversation_context(tweet)
                # Skip result if it has media
                if any(tweet.has_media for tweet in conversation.conversation_tweets):
                    logger.debug(f"Skipping tweet {tweet.id} because it has media")
                    continue

                results.append(conversation)
                logger.debug(
                    f"Added conversation thread {conversation.model_dump()} to results"
                )
                result_count += 1
                if result_count >= MAX_RESULTS:
                    break
            except Exception as e:
                logger.error(f"Error processing tweet {tweet.id}: {e}")
                continue

        next_page = await tweets.next()
        if not next_page or len(next_page) == 0:
            break
        tweets = next_page

    logger.info(f"Found {len(results)} relevant conversations")
    return results


async def _get_conversation_context(tweet) -> TwitterConversation:
    """
    Recursively build conversation context by traversing reply-to chains first,
    then quote chains. The traversal order determines the conversation flow,
    with the input tweet being the last one in the chain.
    """
    conversation_tweets = []
    seen_tweet_ids = set()  # Prevent circular references

    async def traverse_context(current_tweet, depth=0, max_depth=3):
        """
        Depth-first traversal of the conversation tree.
        Prioritizes reply-to chains over quote chains.
        """
        if depth >= max_depth or not current_tweet:
            logger.debug(f"Reached max depth ({depth}) or empty tweet")
            return

        tweet_context = await _extract_tweet_data(current_tweet)
        if not tweet_context or current_tweet.id in seen_tweet_ids:
            return

        seen_tweet_ids.add(current_tweet.id)

        # First traverse reply-to chain
        if current_tweet.in_reply_to:
            try:
                reply_to_tweet = await client.get_tweet_by_id(current_tweet.in_reply_to)
                logger.debug(f"Found reply chain for tweet {current_tweet.id}")
                await traverse_context(reply_to_tweet, depth + 1)
            except Exception as e:
                logger.warning(
                    f"Failed to fetch reply context for tweet {current_tweet.id}: {e}"
                )

        # Then handle quote chain
        if current_tweet.quote:
            try:
                await traverse_context(current_tweet.quote, depth + 1)
            except Exception as e:
                logger.warning(f"Failed to fetch quote context: {e}")

        # Add tweet to conversation after traversing its context
        # This ensures chronological order based on conversation flow
        conversation_tweets.append(tweet_context)

    # Start traversal from the target tweet
    target_tweet_context = await _extract_tweet_data(tweet)

    await traverse_context(tweet)

    # Reverse the list to get the conversation in chronological order
    conversation_tweets.reverse()

    return TwitterConversation(
        conversation_tweets=conversation_tweets, target_tweet=target_tweet_context
    )


async def _extract_tweet_data(tweet) -> Optional[TweetContext]:
    """Process a single tweet into our TweetContext model"""

    author = TwitterUser(
        id=tweet.user.id,
        screen_name=tweet.user.screen_name,
    )

    return TweetContext(
        id=tweet.id,
        text=tweet.text,
        author=author,
        has_media=bool(tweet.media),
        url=f"https://x.com/{author.screen_name}/status/{tweet.id}",
        is_reply=bool(tweet.in_reply_to),
        reply_to_id=tweet.in_reply_to,
        is_quote=tweet.is_quote_status,
        quote_tweet_id=tweet.quote.id if tweet.quote else None,
    )
