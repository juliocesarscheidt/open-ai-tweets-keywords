import os
import re
import nltk
import openai
import argparse

from requests import request
from wordcloud import WordCloud

# download stopwords
nltk.download("stopwords", quiet=True)

URL_REGEX = r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"
TWITTER_BEARER_TOKEN = os.environ.get("TWITTER_BEARER_TOKEN")
TWITTER_WOEID = int(
    os.environ.get("TWITTER_WOEID", "23424768")
)  # Brazil woeid = 23424768
TWITTER_LANG = os.environ.get("TWITTER_LANG", "pt")
TWITTER_MAX_RESULTS = int(os.environ.get("TWITTER_MAX_RESULTS", "10"))
TWITTER_TRENDS_LIMIT = int(os.environ.get("TWITTER_TRENDS_LIMIT", "10"))
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "text-davinci-003")


def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--query", type=str, required=False, help="Query",
    )
    return parser.parse_args()


def clean_text(text: str):
    if text is None:
        return None
    text = text.strip().lower()
    # replace everything that is not included in the following chars
    text = re.sub(r"[^\w\s!#$%&\(\)\*\+,-—\./:;<=>\?@[\]^_´`\{\}|~]+", "", text)
    text = re.sub(r"\t+", " ", text)
    text = re.sub(r"\n", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def make_request(
    url: str,
    method: str = "GET",
    token: str = None,
    content_type: str = "application/json;charset=UTF-8",
    data=None,
):
    headers = {
        "Content-Type": content_type,
    }
    if token is not None:
        headers.update(
            {"Authorization": token,}
        )
    if content_type.startswith("application/json"):
        response = request(method=method, json=data, url=url, headers=headers)
    else:
        response = request(method=method, data=data, url=url, headers=headers)
    return response.json()


def save_word_cloud_image(keywords_frequencies: dict, filename: str) -> None:
    stopwords = nltk.corpus.stopwords.words("portuguese")
    wordcloud = WordCloud(
        background_color="black",
        stopwords=stopwords,
        min_font_size=10,
        max_words=50,
        width=1024,
        height=768,
        normalize_plurals=False,
    )
    wordcloud.generate_from_frequencies(keywords_frequencies)
    print(f"Saving word cloud image on {filename}")
    wordcloud.to_file(filename)


def retrieve_tweets_from_search(
    search_query, twitter_bearer_token, twitter_max_results, twitter_lang
) -> list:
    # retrieve tweets by query
    query_string = f"lang={twitter_lang}&result_type=recent&count={twitter_max_results}"
    tweets_response = make_request(
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
        text = clean_text(text)
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
    trending_topics_response = make_request(
        f"https://api.twitter.com/1.1/trends/place.json?id={twitter_woeid}",
        "GET",
        f"Bearer {twitter_bearer_token}",
    )
    if trending_topics_response is None or len(trending_topics_response) <= 0:
        pass
    trending_topics = set()
    for trend in trending_topics_response[0]["trends"]:
        trend_name = clean_text(trend["name"])
        trending_topics.add(trend_name)
        if len(trending_topics) >= twitter_trends_limit:
            break
    trending_topics = sorted(trending_topics)
    print(trending_topics)

    return trending_topics


def retrieve_keywords_from_text(text, openai_api_key, openai_model) -> list:
    openai.api_key = openai_api_key  # set key on open ai lib
    responses = openai.Completion.create(
        model=openai_model,
        prompt=text,
        temperature=0.1,  # from 0 to 1
        max_tokens=60,  # up to 4000
        top_p=1,  # from 0 to 1
        frequency_penalty=0.8,  # from 0 to 2
        presence_penalty=0,  # from 0 to 2
    )
    if "choices" not in responses or len(responses["choices"]) <= 0:
        return []
    text = responses["choices"][0]["text"]
    text = re.sub(r"^[0-9].\s?", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[\-]\s?", "", text, flags=re.MULTILINE)
    keywords = text.replace("\n", ",").split(",")
    # remove urls
    keywords = list(map(lambda x: re.sub(URL_REGEX, "", x), keywords))
    keywords = list(map(lambda x: clean_text(x), keywords))
    keywords = list(
        map(lambda x: re.sub(r"keywords:?\s?", "", x, flags=re.IGNORECASE), keywords)
    )
    keywords = list(filter(lambda x: x != "", keywords))

    return keywords


def generate_keywords_frequencies_from_texts(
    texts, openai_api_key, openai_model
) -> dict:
    keywords_list = []
    print(f"Searching keywords with model {openai_model}")
    for text in texts:
        keywords = retrieve_keywords_from_text(
            f"Extract keywords from this text:\n{text}", openai_api_key, openai_model
        )
        print(keywords)
        # add to keywords list
        keywords_list.extend(keywords)

    keywords_frequencies = dict()
    for keyword in keywords_list:
        if keyword in keywords_frequencies:
            keywords_frequencies[keyword] += 1
        else:
            keywords_frequencies[keyword] = 1
    print(keywords_frequencies)

    return keywords_frequencies


if __name__ in "__main__":
    args = get_argument_parser()

    # using specific query
    if args.query is not None:
        search_query = clean_text(args.query)
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
        print(f"Using {TWITTER_TRENDS_LIMIT} trending topics...")
        # retrieve trending topics
        trending_topics = retrieve_trending_topics(
            TWITTER_BEARER_TOKEN, TWITTER_TRENDS_LIMIT, TWITTER_WOEID
        )
        for trend in trending_topics:
            tweets = retrieve_tweets_from_search(
                trend, TWITTER_BEARER_TOKEN, TWITTER_MAX_RESULTS, TWITTER_LANG,
            )
            keywords_frequencies = generate_keywords_frequencies_from_texts(
                tweets, OPENAI_API_KEY, OPENAI_MODEL,
            )
            # save word cloud image
            filename = f"./keywords_{trend.replace(' ', '_')}_{OPENAI_MODEL.replace('-', '_')}.png"
            save_word_cloud_image(keywords_frequencies, filename)
