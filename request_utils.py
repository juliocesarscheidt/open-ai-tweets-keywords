from requests import request


def do_request(
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
