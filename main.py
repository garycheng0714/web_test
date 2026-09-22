import subprocess

from pydantic_ai import Agent

agent = Agent(
    "google:gemini-2.5-flash-lite",
    name="web_test_agent",
    instructions=(
        "You drive a real browser through the `playwright_cli` tool. "
        "Call it with an argv list, e.g. ['open', 'https://example.com']. "
        "Use 'open <url>' to navigate. To read the page contents, call "
        "['--raw', 'snapshot']. Report findings concisely."
    ),
)


@agent.tool_plain
def playwright_cli(args: list[str]) -> str:
    """Run a playwright-cli command and return its stdout/stderr.

    Pass argv as a list, e.g. ["open", "https://example.com"] or ["--raw", "snapshot"].
    """
    try:
        proc = subprocess.run(
            ["playwright-cli", *args],
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return "playwright-cli timed out after 120s"
    output = (proc.stdout + proc.stderr).strip()
    return output[:8000] or f"(exit {proc.returncode})"


def main() -> None:
    try:
        result = agent.run_sync(
            "Go to https://automationexercise.com/ and report the page title and URL."
        )
        print(result.output)
    finally:
        subprocess.run(["playwright-cli", "close"], capture_output=True)


if __name__ == "__main__":
    main()
