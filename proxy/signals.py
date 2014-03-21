import django.dispatch

# These are the signals let you handle pre and post for various parts of the Face/Off lifecycle
# The theory here is you can override functionality in ways that the developers never intended

# These signals wrap the "is_allowed" check, which checks if a requests' method is allowed and if an HTTPS check exists
# and passed/failed
pre_is_allowed_check = django.dispatch.Signal(providing_args=["request"])
post_is_allowed_check = django.dispatch.Signal(providing_args=["request", "status", "error"])

# These signals wrap the "healthcheck" calls.
pre_healthcheck = django.dispatch.Signal(providing_args=["request"])
post_healthcheck = django.dispatch.Signal(providing_args=["request", "status", "error"])

# These signals wrap the calls that get the real URL that Face/Off is proxying to
pre_get_real_url_to_call = django.dispatch.Signal(providing_args=["request", "url_to_call"])
post_get_real_url_to_call = django.dispatch.Signal(providing_args=["request", "url_to_call", "web_call"])

# These signals let you react to the beginning and end of the Auth flow
pre_auth_flow = django.dispatch.Signal(providing_args=["request", "custom_headers", "auth"])
post_auth_flow = django.dispatch.Signal(providing_args=["request", "custom_headers", "auth", "status"])

