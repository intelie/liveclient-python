import vcr

_vcr = vcr.VCR(cassette_library_dir="fixtures/cassettes")


def use_safe_cassete(*args, **kwargs):
    """
    Builds a cassette without sensitive data so we can store it
    """
    required_header_filters = ["authorization"]
    filter_headers = kwargs.get("filter_headers", [])
    for header in required_header_filters:
        if not header in filter_headers:
            filter_headers.append(header)
    kwargs["filter_headers"] = filter_headers

    def before_record_response(original_response):
        original_response["headers"]["Set-Cookie"] = ""
        return original_response

    kwargs["before_record_response"] = before_record_response

    return _vcr.use_cassette(*args, **kwargs)
