import os
import sys
import argparse


from text_utils import sanitize_text
from twitter_utils import retrieve_trending_topics, retrieve_tweets_from_search
from openai_utils import generate_keywords_frequencies_from_texts, check_valid_models
from word_cloud_utils import save_word_cloud_image


TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN")
TWITTER_WOEID = int(
    os.environ.get("TWITTER_WOEID", "23424768")
)  # Brazil woeid = 23424768
TWITTER_LANG = os.environ.get("TWITTER_LANG", "pt")
TWITTER_MAX_RESULTS = int(os.environ.get("TWITTER_MAX_RESULTS", "10"))
TWITTER_TRENDS_LIMIT = int(os.environ.get("TWITTER_TRENDS_LIMIT", "10"))
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "text-davinci-003")

if not check_valid_models(OPENAI_MODEL):
    sys.exit(1)


def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--query", type=str, required=False, help="Query",
    )
    return parser.parse_args()


if __name__ in "__main__":
    args = get_argument_parser()

    # using specific query
    if args.query is not None:
        search_query = sanitize_text(args.query)
        print(f"Using search query {search_query}...")
        tweets = retrieve_tweets_from_search(
            search_query, TWITTER_BEARER_TOKEN, TWITTER_MAX_RESULTS, TWITTER_LANG,
        )
        keywords_frequencies = generate_keywords_frequencies_from_texts(
            tweets, OPENAI_API_KEY, OPENAI_MODEL,
        )
        # save word cloud image
        filename = f"./keywords_{search_query.replace(' ', '_')}_{OPENAI_MODEL.replace('-', '_')}.png"
        save_word_cloud_image(keywords_frequencies, filename)

    # using trending topics
    else:
        print(f"Finding {TWITTER_TRENDS_LIMIT} trending topics...")
        # retrieve trending topics
        trending_topics = retrieve_trending_topics(
            TWITTER_BEARER_TOKEN, TWITTER_TRENDS_LIMIT, TWITTER_WOEID
        )
        for trend in trending_topics:
            print(f"Using search query {trend}...")
            tweets = retrieve_tweets_from_search(
                trend, TWITTER_BEARER_TOKEN, TWITTER_MAX_RESULTS, TWITTER_LANG,
            )
            keywords_frequencies = generate_keywords_frequencies_from_texts(
                tweets, OPENAI_API_KEY, OPENAI_MODEL,
            )
            # save word cloud image
            filename = f"./keywords_{trend.replace(' ', '_')}_{OPENAI_MODEL.replace('-', '_')}.png"
            save_word_cloud_image(keywords_frequencies, filename)
