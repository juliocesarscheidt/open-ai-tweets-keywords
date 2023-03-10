FROM python:3.9-slim

WORKDIR /usr/src/app

COPY requirements.txt .
RUN pip install -r \
    requirements.txt
COPY ./ ./

RUN mkdir -p /root/nltk_data/corpora/
COPY stopwords.zip /root/nltk_data/corpora/stopwords.zip
VOLUME ["/root/nltk_data"]

ENTRYPOINT ["python", "main.py"]
