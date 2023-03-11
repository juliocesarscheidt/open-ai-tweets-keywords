FROM python:3.9-slim

LABEL maintainer="Julio Cesar <julio@blackdevs.com.br>"
LABEL org.opencontainers.image.source "https://github.com/juliocesarscheidt/open-ai-tweets-keywords"
LABEL org.opencontainers.image.description "Script to get keywords from tweets using OpenAI and Twitter API"
LABEL org.opencontainers.image.licenses "MIT"

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install -r \
    requirements.txt
COPY ./ ./

# in order to avoid downloading stopwords everytime
RUN mkdir -p /root/nltk_data/corpora/
COPY stopwords.zip /root/nltk_data/corpora/stopwords.zip
VOLUME ["/root/nltk_data"]

ENTRYPOINT ["python", "main.py"]
