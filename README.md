# Script to get keywords from tweets using OpenAI and Twitter API

This will search tweets, either based on some query search, or using trending topics, then iterate through these tweets and retrieve keywords from them using OpenAI API. Also it will generate a Word Cloud image with the keywords.

## Running

```bash
export OPENAI_API_KEY=""
export TWITTER_BEARER_TOKEN=""

pip install -r requirements.txt

# using trending topics (default 2 trends)
python main.py
# using 10 trending topics
TWITTER_TRENDS_LIMIT=10 python main.py

# using other models from OpenAI, either
# text-davinci-003 (GPT-3.5) DEFAULT
# or gpt-3.5-turbo (GPT-3.5)
OPENAI_MODEL=gpt-3.5-turbo TWITTER_TRENDS_LIMIT=10 python main.py

# using specific query with max results (default 10)
TWITTER_MAX_RESULTS=5 python main.py --query "SEARCH_QUERY"
# with gpt-3.5-turbo
OPENAI_MODEL=gpt-3.5-turbo TWITTER_MAX_RESULTS=5 python main.py --query "SEARCH_QUERY"
```

## Running with Docker

```bash
# to build locally, not needed, the image is already on Docker Hub
docker image build --tag juliocesarmidia/open-ai-tweets-keywords:latest .

export OPENAI_API_KEY=""
export TWITTER_BEARER_TOKEN=""

# using 10 trending topics
docker container run --rm \
  --name open-ai-tweets-keywords \
  --env TWITTER_BEARER_TOKEN \
  --env OPENAI_API_KEY \
  --env TWITTER_TRENDS_LIMIT=10 \
  --volume $PWD/:/usr/src/app/ \
  juliocesarmidia/open-ai-tweets-keywords:latest

# using specific query
docker container run --rm \
  --name open-ai-tweets-keywords \
  --env TWITTER_BEARER_TOKEN \
  --env OPENAI_API_KEY \
  --volume $PWD/:/usr/src/app/ \
  juliocesarmidia/open-ai-tweets-keywords:latest --query "SEARCH_QUERY"
```
