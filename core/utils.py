def axes_get_username(request, credentials=None):
    # credentials is a dict like {"username": "...", "password": "..."}
    username = (credentials or {}).get("username") or request.POST.get("username") or ""
    return username
