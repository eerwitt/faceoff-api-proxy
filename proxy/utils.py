import hmac
import importlib
import datetime
import os
import logging

logger = logging.getLogger(__name__)


def load_class_from_name(full_name):
    clazz_name = full_name.split(".")[-1]
    module_name = ".".join(full_name.split(".")[:-1])
    actual_module = importlib.import_module(module_name)
    return getattr(actual_module, clazz_name)


def init_classes_with_params_from_dict(class_dictionary):
    results = []
    for entity in class_dictionary.keys():
        try:
            cls = load_class_from_name(entity)
            inited_cls = cls(**class_dictionary.get(entity, {}))
            results.append(inited_cls)
        except Exception as e:
            logger.exception("Class '%s' for %s failed at initializing" % (class_dictionary, class_dictionary.get(entity, {})))

    return results


def get_all_http_request_headers(request, custom_headers=None):
    pure_header = dict()
    for header in request.META.keys():
        if header.startswith("HTTP"):
            # this one header totally messes with web server vhosts.  You almost NEVER want to pass it
            if not header == "HTTP_HOST":
                pure_header[header.replace("HTTP_","").replace("_","-")] = request.META.get(header)
        if header.startswith("CONTENT"):
            if header != "CONTENT_LENGTH":  # let's not override this one since we might be changing it
                pure_header[header.replace("_", "-")] = request.META.get(header)

    if custom_headers:
        final_dict = pure_header.copy()
        final_dict.update(custom_headers)
        return final_dict
    else:
        return pure_header


def get_content_request_headers_only(request, custom_headers=None):
    pure_header = dict()

    for header in request.META.keys():
        if header.startswith("CONTENT"):
            pure_header[header.replace("_", "-")] = request.META.get(header)

    if custom_headers:
        final_dict = pure_header.copy()
        final_dict.update(custom_headers)
        return final_dict
    else:
        return pure_header

hop_headers = set("""
    connection keep-alive proxy-authenticate proxy-authorization
    te trailers transfer-encoding upgrade
    """.split())


def str2bool(string):
    return string.lower() in ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly']

dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None

# this method is probably really slow?
def parse_basic_auth(full_url):
    if "@" not in full_url:
        return {"url": full_url}
    http_https = full_url.split("/")[0]
    full_url = full_url.replace(http_https + "//", "")
    (login_password, url) = full_url.split("@")
    (login, password) = login_password.split(":")
    return {
        "url": http_https + "//" + url,
        "login": login,
        "password": password
    }


def convert_variable_to_env_setting(variable):
    if variable is None:
        return variable
    if variable.startswith("$"):
        env_setting = os.environ.get(variable[1:], None)
        if env_setting is not None:
            return env_setting
    return variable


def application_hasher(app, string):
    magic_string = app.id+":"+app.client_secret+":"+string
    return hmac.new(magic_string.encode('utf-8')).hexdigest()


# from http://stackoverflow.com/questions/4581789/how-do-i-get-user-ip-address-in-django
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[-1].strip() # there might be multiple IPs if this comes from multiple proxies
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
