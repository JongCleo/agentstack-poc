from pydantic import BaseModel, Field
from typing import Optional, List


class TwitterUser(BaseModel):
    """Represents essential user information for context"""

    id: str
    screen_name: str


class TweetContext(BaseModel):
    """Represents a single tweet in a conversation"""

    id: str
    text: str
    author: TwitterUser
    url: str
    has_media: bool = False
    is_reply: bool = False
    reply_to_id: Optional[str] = None
    is_quote: bool = False
    quote_tweet_id: Optional[str] = None


class TwitterConversation(BaseModel):
    """
    Represents a complete conversation thread. The order of tweets in conversation_tweets
    represents the natural flow of the conversation, with the target_tweet being the
    last tweet that needs a response.
    """

    conversation_tweets: List[TweetContext] = Field(default_factory=list)
    target_tweet: TweetContext

    class Config:
        arbitrary_types_allowed = True
