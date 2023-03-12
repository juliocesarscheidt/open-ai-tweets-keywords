import nltk
from wordcloud import WordCloud

# download stopwords
nltk.download("stopwords", quiet=True)


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
