# Script to get keywords from tweets using OpenAI and Twitter API

This will search tweets, either based on some query search, or using trending topics, then iterate through these tweets and retrieve keywords from them using OpenAI API. Also it will generate a Word Cloud image with the keywords.

## Runing

```bash
export OPENAI_API_KEY=""
export TWITTER_API_KEY=""
export TWITTER_API_SECRET=""

pip install -r requirements.txt

# using trends topics (default 2 trends)
python main.py
# using 10 trends topics
TWITTER_TRENDS_LIMIT=10 python main.py

# using specific query
python main.py --query "SEARCH_QUERY"
```

```bash
docker image build --tag juliocesarmidia/open-ai-tweets-keywords:latest .

export OPENAI_API_KEY=""
export TWITTER_API_KEY=""
export TWITTER_API_SECRET=""

# using 10 trends topics
docker container run --rm \
  --name open-ai-tweets-keywords \
  --env TWITTER_API_KEY \
  --env TWITTER_API_SECRET \
  --env OPENAI_API_KEY \
  --env TWITTER_TRENDS_LIMIT=10 \
  --volume $PWD/:/usr/src/app/ \
  juliocesarmidia/open-ai-tweets-keywords:latest

# using specific query
docker container run --rm \
  --name open-ai-tweets-keywords \
  --env TWITTER_API_KEY \
  --env TWITTER_API_SECRET \
  --env OPENAI_API_KEY \
  --volume $PWD/:/usr/src/app/ \
  juliocesarmidia/open-ai-tweets-keywords:latest --query "SEARCH_QUERY"
```
