from collections.abc import AsyncIterator
from pathlib import Path
from typing import TypeVar

from pydantic_ai import Agent, AgentRunResult
from pydantic_ai.capabilities import LocalWorkspace
from pydantic_ai.messages import ModelResponse, TextPart, ToolCallPart, ToolReturnPart
from pydantic_ai.models.function import DeltaToolCall, FunctionModel
from pydantic_ai.models.test import TestModel
from pydantic_ai_harness.playwright import EgressRequest, PlaywrightBrowser

from web_test._run import run_sync
from web_test.automation.coding_agent import (
    GROUNDING_POLICY,
    INSTRUCTIONS,
    AutomationResult,
    build_automation_agent,
)
from web_test.automation.repair_guard import AutomationDeps


T = TypeVar("T")


def _capability(
    agent: Agent[AutomationDeps, AutomationResult], kind: type[T]
) -> T:
    found: list[object] = []
    agent.root_capability.apply(found.append)
    return next(c for c in found if isinstance(c, kind))


def _browser_capability(agent: Agent[AutomationDeps, AutomationResult]) -> PlaywrightBrowser:
    return _capability(agent, PlaywrightBrowser)


def _scripted(*responses: ModelResponse) -> FunctionModel:
    """A model that replays `responses`, for both streamed and non-streamed requests.

    `Coder` streams its model requests, so the model needs a stream function too.
    """
    remaining = list(responses)

    def respond(messages: object, info: object) -> ModelResponse:
        return remaining.pop(0)

    async def stream(messages: object, info: object) -> AsyncIterator[str | dict[int, DeltaToolCall]]:
        for part in remaining.pop(0).parts:
            if isinstance(part, TextPart):
                yield part.content
            elif isinstance(part, ToolCallPart):
                yield {
                    0: DeltaToolCall(
                        name=part.tool_name,
                        json_args=part.args_as_json_str(),
                        tool_call_id=part.tool_call_id or "call_0",
                    )
                }

    return FunctionModel(function=respond, stream_function=stream)


def _tool_returns(result: AgentRunResult[AutomationResult]) -> dict[str, object]:
    return {
        part.tool_name: part.content
        for message in result.all_messages()
        for part in message.parts
        if isinstance(part, ToolReturnPart)
    }


def test_coding_agent_keeps_agent_pytest_traces(tmp_path: Path) -> None:
    agent = build_automation_agent(TestModel(), workspace_dir=tmp_path)

    workspace = _capability(agent, LocalWorkspace)

    assert workspace.env == {"PYTEST_ADDOPTS": "--tracing=retain-on-failure"}


def test_coding_agent_attaches_the_browser_capability(tmp_path: Path) -> None:
    agent = build_automation_agent(TestModel(), workspace_dir=tmp_path)

    browser = _browser_capability(agent)

    assert {"navigate", "snapshot"} <= set(browser.get_toolset().tools)
    assert browser.policy is GROUNDING_POLICY


def test_grounding_policy_blocks_ads_and_allows_the_sut() -> None:
    ad_script = EgressRequest(
        url="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js",
        kind="subresource",
        resource_type="script",
    )
    ad_frame = EgressRequest(url="https://googleads.g.doubleclick.net/pagead/id", kind="subframe")

    assert GROUNDING_POLICY.refuse(ad_script) == "domain in blocked_domains"
    assert GROUNDING_POLICY.refuse(ad_frame) == "domain in blocked_domains"
    assert GROUNDING_POLICY.refuse(EgressRequest(url="https://automationexercise.com/", kind="navigation")) is None


def test_grounding_instructions_name_the_capability_tools() -> None:
    assert "navigate" in INSTRUCTIONS
    assert "snapshot" in INSTRUCTIONS
    assert "playwright-cli" not in INSTRUCTIONS


def test_browser_tools_are_dispatched_through_the_agent(tmp_path: Path) -> None:
    model = _scripted(
        ModelResponse(
            parts=[
                ToolCallPart(tool_name="navigate", args={"url": "https://automationexercise.com"})
            ]
        ),
        ModelResponse(parts=[ToolCallPart(tool_name="snapshot", args={})]),
        ModelResponse(parts=[ToolCallPart(tool_name="final_result", args={"pr_body": None})]),
    )
    agent = build_automation_agent(model, workspace_dir=tmp_path)

    result = run_sync(agent.run("Ground the home page"))

    returns = _tool_returns(result)
    assert "navigate" in returns
    assert "snapshot" in returns


def test_green_run_produces_a_pr_body(tmp_path: Path) -> None:
    body = "## Summary\n\n...\n\n## Evidence\n\n...\n\n## Merge Danger\n\n..."
    model = _scripted(
        ModelResponse(parts=[ToolCallPart(tool_name="load_capability", args={"id": "pr"})]),
        ModelResponse(parts=[ToolCallPart(tool_name="final_result", args={"pr_body": body})]),
    )
    agent = build_automation_agent(model, workspace_dir=tmp_path)

    result = run_sync(agent.run("Automate the approved cases"))

    assert "# Skill: pr" in str(_tool_returns(result)["load_capability"])
    assert result.output.pr_body == body


def test_red_run_produces_no_pr_body(tmp_path: Path) -> None:
    model = _scripted(
        ModelResponse(parts=[ToolCallPart(tool_name="final_result", args={"pr_body": None})]),
    )
    agent = build_automation_agent(model, workspace_dir=tmp_path)

    result = run_sync(agent.run("Automate the approved cases"))

    assert result.output.pr_body is None
