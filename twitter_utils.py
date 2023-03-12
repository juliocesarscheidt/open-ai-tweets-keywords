import re

from request_utils import do_request
from text_utils import sanitize_text, URL_REGEX


def retrieve_tweets_from_search(
    search_query, twitter_bearer_token, twitter_max_results, twitter_lang
) -> list:
    # retrieve tweets by query
    query_string = (
        f"lang={twitter_lang}&result_type=recent" f"&count={twitter_max_results}"
    )
    tweets_response = do_request(
        "https://api.twitter.com/1.1/search/tweets.json"
        f"?q={search_query}&{query_string}",
        "GET",
        f"Bearer {twitter_bearer_token}",
    )

    tweets = []
    for tweet in tweets_response["statuses"]:
        # cleaning tweet text
        text = tweet["text"].strip().lower()
        # remove urls
        text = re.sub(URL_REGEX, "", text)
        text = sanitize_text(text)
        # identifying mentions
        mentions = (
            tweet["entities"]["user_mentions"]
            if "entities" in tweet and "user_mentions" in tweet["entities"]
            else None
        )
        if mentions is not None:
            text = re.sub(r"rt\s", "", text, flags=re.IGNORECASE)
            text = re.sub(r"@[a-zA-Z0-9_]+:?\s?", "", text)
        print("Tweet ::", text)
        # add to tweets list
        tweets.append(text)

    return tweets


def retrieve_trending_topics(
    twitter_bearer_token, twitter_trends_limit, twitter_woeid
) -> list:
    trending_topics_response = do_request(
        f"https://api.twitter.com/1.1/trends/place.json?id={twitter_woeid}",
        "GET",
        f"Bearer {twitter_bearer_token}",
    )
    if trending_topics_response is None or len(trending_topics_response) <= 0:
        pass
    trending_topics = set()
    for trend in trending_topics_response[0]["trends"]:
        trend_name = sanitize_text(trend["name"])
        trending_topics.add(trend_name)
        if len(trending_topics) >= twitter_trends_limit:
            break
    trending_topics = sorted(trending_topics)
    print(trending_topics)

    return trending_topics
