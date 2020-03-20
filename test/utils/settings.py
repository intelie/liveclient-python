def create(**kwargs):
    default_settings = {
        "output": {"author": {"id": 1, "name": "__default_name__"}, "room": "__room__"},
        "live": {},
    }
    default_settings.update(kwargs)
    return default_settings
