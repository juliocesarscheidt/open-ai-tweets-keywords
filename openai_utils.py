import re
import openai

from text_utils import sanitize_text, URL_REGEX

VALID_MODELS = ["text-davinci-003", "gpt-3.5-turbo"]


def check_valid_models(model) -> bool:
    valid = model in VALID_MODELS
    if not valid:
        print("Invalid model, please select either", " or ".join(VALID_MODELS))
    return valid


def chat_completion(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": f"Extract keywords from this text:\n{text}"}
        ],
    )
    if "choices" not in response or len(response["choices"]) <= 0:
        return None
    return response["choices"][0]["message"]["content"]


def completion(text):
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=f"Extract keywords from this text:\n{text}",
        temperature=0.1,  # from 0 to 1
        max_tokens=60,  # up to 4000
        top_p=1,  # from 0 to 1
        frequency_penalty=0.8,  # from 0 to 2
        presence_penalty=0,  # from 0 to 2
    )
    if "choices" not in response or len(response["choices"]) <= 0:
        return None
    return response["choices"][0]["text"]


def retrieve_keywords_from_text(text, openai_api_key, openai_model) -> list:
    openai.api_key = openai_api_key  # set key on open ai lib
    if openai_model == "gpt-3.5-turbo":
        text = chat_completion(text)
    elif openai_model == "text-davinci-003":
        text = completion(text)

    print("Text", text)

    if text is None:
        return []
    text = re.sub(r"^[0-9].\s?", "", text, flags=re.MULTILINE)
    text = re.sub(r"^[\-]\s?", "", text, flags=re.MULTILINE)
    keywords = text.replace("\n", ",").split(",")
    # remove urls
    keywords = list(map(lambda x: re.sub(URL_REGEX, "", x), keywords))
    keywords = list(map(lambda x: sanitize_text(x), keywords))
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
        keywords = retrieve_keywords_from_text(text, openai_api_key, openai_model)
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
