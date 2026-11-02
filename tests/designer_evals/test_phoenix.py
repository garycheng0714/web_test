from designer_eval.phoenix import base_url, endpoint, sum_usage


def test_endpoint_uses_the_default_phoenix_endpoint(monkeypatch):
    monkeypatch.delenv("PHOENIX_COLLECTOR_ENDPOINT", raising=False)

    assert endpoint() == "http://127.0.0.1:6006/v1/traces"


def test_endpoint_accepts_a_base_url_or_a_full_traces_url():
    assert endpoint("http://phoenix:4318") == "http://phoenix:4318/v1/traces"
    assert endpoint("http://phoenix:4318/") == "http://phoenix:4318/v1/traces"
    assert endpoint("http://phoenix:4318/v1/traces") == "http://phoenix:4318/v1/traces"


def test_endpoint_reads_the_environment(monkeypatch):
    monkeypatch.setenv("PHOENIX_COLLECTOR_ENDPOINT", "http://collector:6006")

    assert endpoint() == "http://collector:6006/v1/traces"


def test_base_url_strips_the_traces_suffix():
    assert base_url("http://phoenix:4318/v1/traces") == "http://phoenix:4318"
    assert base_url("http://phoenix:4318") == "http://phoenix:4318"


def test_sum_usage_adds_llm_token_counts():
    spans = [
        {
            "attributes": {
                "llm.token_count.prompt": 10,
                "llm.token_count.completion": 2,
                "llm.token_count.total": 12,
                "llm.token_count.prompt_details.cache_read": 7,
            }
        },
        {
            "attributes": {
                "llm.token_count.prompt": 20,
                "llm.token_count.completion": 3,
                "llm.token_count.total": 23,
            }
        },
    ]

    assert sum_usage(spans) == {
        "prompt": 30,
        "completion": 5,
        "total": 35,
        "cache_read": 7,
    }
