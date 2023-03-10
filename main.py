import os
import re
import nltk
import openai
import argparse
import unicodedata
import matplotlib.pyplot as plt
from requests import request
from base64 import b64encode
from wordcloud import WordCloud


# download stopwords
# nltk.download('stopwords')
TWITTER_API_KEY = os.environ.get("TWITTER_API_KEY")
TWITTER_API_SECRET = os.environ.get("TWITTER_API_SECRET")
TWITTER_BASIC_TOKEN = b64encode(
    f"{TWITTER_API_KEY}:{TWITTER_API_SECRET}".encode("utf-8")
).decode("utf-8")
# https://gist.github.com/tedyblood/5bb5a9f78314cc1f478b3dd7cde790b9#file-woeid-L4919
# Brazil woeid = 23424768
TWITTER_WOEID = int(os.environ.get("TWITTER_WOEID", "23424768"))
# it must be between 10 and 100
TWITTER_MAX_RESULTS = int(os.environ.get("TWITTER_MAX_RESULTS", "10"))
TWITTER_TRENDS_LIMIT = int(os.environ.get("TWITTER_TRENDS_LIMIT", "1"))
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
# set key on open ai lib
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "text-davinci-003")
openai.api_key = OPENAI_API_KEY
URL_REGEX = r"((http|https)\:\/\/)?[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"


def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--query", type=str, required=False, help="Query",
    )
    return parser.parse_args()


def clean_text(text):
    if text is None:
        return None
    text = str(text).strip().lower()
    # NFKD: Normalization Form: Compatibility (K) Decomposition
    # text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\n", " ", text)
    text = re.sub(r"[!#$%&\'()*+/:;<=>?\[\\\]^`{|}~]+", "", text)
    return text


def make_request(
    url,
    method="GET",
    token=None,
    data=None,
    content_type="application/json;charset=UTF-8",
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


def save_word_cloud_image(keywords, search_query):
    stopwords = nltk.corpus.stopwords.words("portuguese")
    wordcloud = WordCloud(
        background_color="black", stopwords=stopwords, min_font_size=10
    ).generate(keywords)
    plt.figure(figsize=(15, 15), facecolor=None)
    plt.imshow(wordcloud, interpolation="bilinear")
    plt.axis("off")
    plt.imshow(wordcloud)
    wordcloud.to_file(f"./keywords_{search_query.replace(' ', '_')}.png")


def get_keywords_from_text(text):
    responses = openai.Completion.create(
        model=OPENAI_MODEL,
        prompt=text,
        temperature=0.1,  # from 0 to 1
        max_tokens=20,  # up to 4000
        top_p=1,  # from 0 to 1
        frequency_penalty=1,  # from 0 to 2
        presence_penalty=0,  # from 0 to 2
    )
    keywords = (
        responses["choices"][0]["text"].replace("\n", ",")
        if "choices" in responses and len(responses["choices"]) > 0
        else ""
    )
    keywords = list(map(lambda x: clean_text(x.strip()), keywords.split(",")))
    keywords = list(
        map(lambda x: re.sub(r"keywords:?\s?", "", x, flags=re.IGNORECASE), keywords)
    )
    keywords = list(map(lambda x: re.sub(r"^[\-]\s?", "", x), keywords))
    keywords = list(map(lambda x: re.sub(r"^[0-9].\s", "", x), keywords))
    keywords = list(map(lambda x: re.sub(r'"', "", x), keywords))
    keywords = list(filter(lambda x: x != "", keywords))
    return keywords


def retrieve_keywords(search_query, twitter_access_token):
    # retrieve tweets by query
    query_string = "lang=pt&result_type=recent" f"&count={TWITTER_MAX_RESULTS}"
    tweets_response = make_request(
        "https://api.twitter.com/1.1/search/tweets.json"
        f"?q={search_query}&{query_string}",
        "GET",
        f"Bearer {twitter_access_token}",
    )

    keywords_list = []
    for tweet in tweets_response["statuses"]:
        # cleaning tweet text
        text = tweet["text"].strip()
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
            text = re.sub(r"@[a-zA-Z0-9_]+:?\s", "", text)

        print("Tweet ::", text)
        keywords = get_keywords_from_text(f"Extract keywords from this text:\n{text}")
        print(keywords)

        # add to keywords list
        keywords_list.extend(keywords)
        print()

    keywords_list = sorted(keywords_list)
    keywords_list = " ".join(keywords_list).strip()
    print(keywords_list)

    # save word cloud image
    save_word_cloud_image(keywords_list, search_query)


if __name__ in "__main__":
    args = get_argument_parser()

    # retrieve access token
    twitter_token_response = make_request(
        "https://api.twitter.com/oauth2/token",
        "POST",
        f"Basic {TWITTER_BASIC_TOKEN}",
        {"grant_type": "client_credentials"},
        "application/x-www-form-urlencoded",
    )
    twitter_access_token = twitter_token_response["access_token"]

    if args.query is not None:
        print(f"Using search query {args.query}")
        retrieve_keywords(args.query, twitter_access_token)

    else:
        print(f"Using {TWITTER_TRENDS_LIMIT} trending topics")
        # retrieve trends
        trending_topics_response = make_request(
            "https://api.twitter.com/1.1/trends/place.json" f"?id={TWITTER_WOEID}",
            "GET",
            f"Bearer {twitter_access_token}",
        )
        if trending_topics_response is None or len(trending_topics_response) <= 0:
            pass
        trending_topics = set()
        for trend in trending_topics_response[0]["trends"]:
            trend_name = clean_text(trend["name"])
            trending_topics.add(trend_name)
            if len(trending_topics) >= TWITTER_TRENDS_LIMIT:
                break
        trending_topics = sorted(trending_topics)
        print(trending_topics)

        for trend in trending_topics:
            retrieve_keywords(trend, twitter_access_token)
