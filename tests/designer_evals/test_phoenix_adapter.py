from datetime import UTC, datetime
from types import SimpleNamespace

from opentelemetry import trace as otel_trace

from evals.designer.designer_eval import phoenix
from evals.designer.designer_eval.annotations import AnnotationSpec
from evals.designer.designer_eval.units import UnitKind, UnitSpec


class _FakeSpans:
    def __init__(self, responses: list[list[dict]]):
        self.responses = responses
        self.calls: list[dict] = []

    def get_spans(self, **kwargs):
        self.calls.append(kwargs)
        return self.responses.pop(0)


class _FakeClient:
    def __init__(self, responses: list[list[dict]]):
        self.spans = _FakeSpans(responses)


def test_find_agent_span_returns_the_latest_span(monkeypatch):
    older = {"start_time": 1, "context": {"trace_id": "1", "span_id": "1"}}
    newer = {"start_time": 2, "context": {"trace_id": "2", "span_id": "2"}}
    client = _FakeClient([[older, newer]])
    monkeypatch.setattr(phoenix.time, "sleep", lambda _: None)

    span = phoenix.find_agent_span(client, "project", datetime.now(UTC))

    assert span == newer
    assert len(client.spans.calls) == 1


def test_find_agent_span_retries_until_the_agent_span_appears(monkeypatch):
    span = {"start_time": 1, "context": {"trace_id": "1", "span_id": "1"}}
    client = _FakeClient([[], [span]])
    monkeypatch.setattr(phoenix.time, "sleep", lambda _: None)

    result = phoenix.find_agent_span(client, "project", datetime.now(UTC))

    assert result == span
    assert len(client.spans.calls) == 2


def test_find_agent_span_gives_up_after_ten_attempts(monkeypatch):
    client = _FakeClient([[] for _ in range(10)])
    monkeypatch.setattr(phoenix.time, "sleep", lambda _: None)

    result = phoenix.find_agent_span(client, "project", datetime.now(UTC))

    assert result is None
    assert len(client.spans.calls) == 10


def test_fetch_usage_sums_the_trace_spans():
    client = _FakeClient(
        [
            [
                {
                    "attributes": {
                        "llm.token_count.prompt": 10,
                        "llm.token_count.completion": 2,
                        "llm.token_count.total": 12,
                    }
                },
                {
                    "attributes": {
                        "llm.token_count.prompt": 5,
                        "llm.token_count.completion": 3,
                        "llm.token_count.total": 8,
                    }
                },
            ]
        ]
    )

    usage = phoenix.fetch_usage(client, "project", "trace-1")

    assert usage == {"prompt": 15, "completion": 5, "total": 20, "cache_read": 0}
    assert client.spans.calls == [
        {"project_identifier": "project", "trace_ids": ["trace-1"], "limit": 100}
    ]


class _FakeSpan:
    def __init__(self, span_id: int, trace_id: int = int("0" * 31 + "1", 16)):
        self._context = SimpleNamespace(span_id=span_id, trace_id=trace_id)

    def get_span_context(self):
        return self._context

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class _FakeTracer:
    def __init__(self):
        self.calls: list[tuple[str, object, dict[str, str]]] = []
        self._next_span_id = 0xABC

    def start_as_current_span(self, name: str, *, context, attributes):
        self.calls.append((name, context, attributes))
        span = _FakeSpan(self._next_span_id)
        self._next_span_id += 1
        return span


class _FakeProvider:
    def __init__(self):
        self.flushed = False

    def force_flush(self):
        self.flushed = True


def test_create_units_uses_the_agent_span_as_parent(monkeypatch):
    tracer = _FakeTracer()
    monkeypatch.setattr("opentelemetry.trace.get_tracer", lambda _: tracer)
    provider = _FakeProvider()
    spec = UnitSpec(
        kind=UnitKind.CLAIM,
        target_id="FR-1<-case-1",
        name="claim FR-1 <- case-1",
        attributes={"claim.requirement_id": "FR-1"},
    )
    agent_span = {
        "context": {
            "trace_id": "0" * 31 + "1",
            "span_id": "0" * 15 + "1",
        }
    }

    units = phoenix.create_units(provider, agent_span, [spec])

    assert provider.flushed is True
    assert [unit.span_id for unit in units] == ["0000000000000abc"]
    assert units[0].kind == UnitKind.CLAIM
    assert units[0].attributes is spec.attributes
    assert len(tracer.calls) == 1
    name, context, attributes = tracer.calls[0]
    assert name == spec.name
    assert attributes is spec.attributes
    parent = otel_trace.get_current_span(context).get_span_context()
    assert parent.trace_id == int("0" * 31 + "1", 16)
    assert parent.span_id == int("0" * 15 + "1", 16)


def test_create_units_nests_claims_under_their_requirement_span(monkeypatch):
    tracer = _FakeTracer()
    monkeypatch.setattr("opentelemetry.trace.get_tracer", lambda _: tracer)
    provider = _FakeProvider()
    specs = [
        UnitSpec(
            kind=UnitKind.REQUIREMENT,
            target_id="FR-1",
            name="requirement FR-1",
            attributes={"requirement.id": "FR-1"},
        ),
        UnitSpec(
            kind=UnitKind.CLAIM,
            target_id="case-1-functional->FR-1",
            name="claim case-1-functional -> FR-1",
            attributes={"claim.requirement_id": "FR-1"},
            parent_target_id="FR-1",
        ),
    ]
    agent_span = {
        "context": {
            "trace_id": "0" * 31 + "1",
            "span_id": "0" * 15 + "1",
        }
    }

    units = phoenix.create_units(provider, agent_span, specs)

    assert units[0].parent_span_id == "0" * 15 + "1"
    assert units[1].parent_span_id == units[0].span_id
    claim_parent = otel_trace.get_current_span(tracer.calls[1][1]).get_span_context()
    assert claim_parent.span_id == int(units[0].span_id, 16)


def test_instrument_designer_passes_the_version_and_provider(monkeypatch):
    captured = {}

    class _Provider:
        def __init__(self):
            self.tracers = []

        def get_tracer(self, *args):
            self.tracers.append(args)
            return object()

    monkeypatch.setattr(
        "pydantic_ai.Agent.instrument_all",
        lambda settings: captured.setdefault("settings", settings),
    )
    provider = _Provider()

    phoenix.instrument_designer(provider, version=5)

    settings = captured["settings"]
    assert settings.version == 5
    assert provider.tracers


class _FakeAnnotationFactory:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class _FakeLogSpans:
    def __init__(self):
        self.calls: list[dict] = []

    def log_span_annotations(self, **kwargs):
        self.calls.append(kwargs)


class _FakeLogClient:
    def __init__(self):
        self.spans = _FakeLogSpans()


def test_log_code_annotations_builds_the_phoenix_payload():
    client = _FakeLogClient()
    annotation = AnnotationSpec(
        name="requirement_exists",
        span_id="span-1",
        label="valid",
        score=1.0,
        metadata={"claim_id": "FR-1<-case-1"},
    )

    phoenix.log_code_annotations(client, [annotation], factory=_FakeAnnotationFactory)

    call = client.spans.calls[0]
    payload = call["span_annotations"][0]
    assert isinstance(payload, _FakeAnnotationFactory)
    assert payload.kwargs == {
        "name": "requirement_exists",
        "annotator_kind": "CODE",
        "span_id": "span-1",
        "result": {"label": "valid", "score": 1.0},
        "metadata": {"claim_id": "FR-1<-case-1"},
    }
    assert call["sync"] is True


def test_log_code_annotations_skips_an_empty_payload():
    client = _FakeLogClient()

    def fail(**kwargs):
        raise AssertionError("factory should not be called")

    phoenix.log_code_annotations(client, [], factory=fail)

    assert client.spans.calls == []
