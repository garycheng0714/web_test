import argparse
import sys

from web_test.planning.review.local import review_case_file
from web_test.planning.review.report import render_report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="review-case", description="Review an existing test-case artifact."
    )
    parser.add_argument("--case", required=True, help="path to the test-case markdown file")
    parser.add_argument("--prd", required=True, help="path to the PRD markdown/text file")
    args = parser.parse_args(argv)

    try:
        record = review_case_file(args.case, args.prd)
    except (OSError, ValueError) as error:
        print(f"failed: {error}", file=sys.stderr)
        return 1

    print(render_report(record))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
