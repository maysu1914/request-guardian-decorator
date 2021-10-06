import json

from requests import request

PACKAGE_NAME = "RequestGuardian"
METHODS = (
    "POST",
    "PUT",
    "DELETE",
    "PATCH",
)
CORRECT_ANSWERS = ('yes', 'y', 'evet', 'e', 'true')
MESSAGES = {
    'title': "-----------------Request Guardian-----------------",
    'confirmation': "Do you want to proceed %s%s? (Y/N) ",
    'abort_message': "The %s operation is aborted!",
    'preview_data': "CURRENT: %s",
    'data': "REQUEST: %s",
    'target_url': "TARGET URL: %s",
    'method': "METHOD: %s",
    'quick_result': "[%s] %s => %s",
    'successful': "--------------------Successful--------------------",
    'failed': "----------------------Failed----------------------",
}


def request_guardian():
    """
    it gives attention to the data changeable requests (put,post,delete,patch)
    shows the current data info -by get request-
    and wait for confirmation
    :return: decorator func, inner func, Response object
    """

    def decorator(func):
        def inner(*args, **kwargs):
            method = args[0]
            url = args[1]

            preview = kwargs.pop('preview', False)
            forced = kwargs.pop('forced', False)

            if not forced:
                print(MESSAGES['title'])
                print(MESSAGES['target_url'] % url)

            if preview:
                data = kwargs.get('data', None)
                json_data = kwargs.get('json', None)

                print(MESSAGES['method'] % method.upper())
                if method.upper() in ("PUT", "PATCH", "DELETE"):
                    print(MESSAGES['preview_data'] % json.dumps(func('GET', url).json(), indent=4))
                if method.upper() in ("PUT", "PATCH", "POST"):
                    print(MESSAGES['data'] % str(json.dumps(data if data else json_data, indent=4)))

            if not forced and method.upper() in METHODS:
                answer = input(MESSAGES['confirmation'] % (method.upper(), ' with the data above' if preview else ''))
            else:
                answer = 'evet'

            if answer.lower() in CORRECT_ANSWERS:
                response = func(*args, **kwargs)
            else:
                print(MESSAGES['abort_message'] % method.upper())
                response = None

            if not forced:
                if hasattr(response, "ok") and response.ok:
                    print(MESSAGES['successful'])
                else:
                    print(MESSAGES['failed'])
            else:
                print(MESSAGES['quick_result'] % (
                    response.status_code,
                    url,
                    str(response.json() if response.content else None)
                ))

            return response

        return inner

    return decorator


@request_guardian()
def safe_request(*args, **kwargs):
    """
    to run request method under request_guardian decorator
    :param args: args for the request
    :param kwargs: kwargs for the request
    :return: Response of the request
    """
    return request(*args, **kwargs)
