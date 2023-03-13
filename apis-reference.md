## APIs

```bash
######## Twitter ########
export TWITTER_BEARER_TOKEN=""

# trends
# https://developer.twitter.com/en/docs/twitter-api/v1/trends/trends-for-location/api-reference/get-trends-place

curl --silent --request GET \
  --header "Authorization: Bearer ${TWITTER_BEARER_TOKEN}" \
  --url "https://api.twitter.com/1.1/trends/place.json?id=23424768"

# search tweets
# https://developer.twitter.com/en/docs/twitter-api/v1/tweets/search/api-reference/get-search-tweets

curl --silent --request GET \
  --header "Authorization: Bearer ${TWITTER_BEARER_TOKEN}" \
  --url "https://api.twitter.com/1.1/search/tweets.json?q=coldplay&lang=pt&result_type=recent&count=10"

######## OpenAI ########
export OPENAI_API_KEY=""

# extract keywords with gpt-3.5-turbo
# https://platform.openai.com/docs/api-reference/chat
curl https://api.openai.com/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
  "model": "gpt-3.5-turbo",
  "messages": [
    {"role": "user", "content": "Extract keywords from this text: hello, my name is Julio"}
  ],
  "temperature": 0.5,
  "max_tokens": 60,
  "top_p": 1.0,
  "frequency_penalty": 0.8,
  "presence_penalty": 0.0
}'

# extract keywords with text-davinci-003
# https://platform.openai.com/docs/api-reference/completions
curl --url "https://api.openai.com/v1/completions" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -d '{
  "model": "text-davinci-003",
  "prompt": "Extract keywords from this text: hello, my name is Julio",
  "temperature": 0.5,
  "max_tokens": 60,
  "top_p": 1.0,
  "frequency_penalty": 0.8,
  "presence_penalty": 0.0
}'

```
