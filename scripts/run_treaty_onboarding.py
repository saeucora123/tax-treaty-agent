from __future__ import annotations

import argparse
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
BACKEND_PATH = REPO_ROOT / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from app.treaty_onboarding import (  # noqa: E402
    PromotionGateError,
    ReviewGateError,
    TreatyOnboardingError,
    run_approve,
    run_compile,
    run_promote,
    run_review,
)


DEFAULT_MANIFEST_PATH = REPO_ROOT / "data" / "onboarding" / "manifests" / "cn-sg.shadow.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the treaty onboarding compiler workflow for shadow rebuilds."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    for command_name in ("compile", "review", "promote"):
        command_parser = subparsers.add_parser(command_name)
        command_parser.add_argument(
            "--manifest",
            type=Path,
            default=DEFAULT_MANIFEST_PATH,
            help="Path to the treaty onboarding manifest JSON.",
        )
    approve_parser = subparsers.add_parser("approve")
    approve_parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST_PATH,
        help="Path to the treaty onboarding manifest JSON.",
    )
    approve_parser.add_argument(
        "--reviewer",
        type=str,
        required=True,
        help="Reviewer name to record in approval.record.json.",
    )
    approve_parser.add_argument(
        "--note",
        type=str,
        default="",
        help="Optional approval note.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        if args.command == "compile":
            report = run_compile(args.manifest)
            print(
                "Compile status: ok "
                f"({report['article_count']} articles, {report['paragraph_count']} paragraphs, "
                f"{report['rule_count']} rules, {report['unresolved_item_count']} unresolved)"
            )
            return 0

        if args.command == "review":
            report = run_review(args.manifest)
            if report["status"] == "pass":
                print(
                    "Review status: "
                    f"{report['status']} (canonical_match={str(report['canonical_match']).lower()}, "
                    f"mismatch_path_count={report['mismatch_path_count']})"
                )
                return 0
            if report["status"] == "ready_for_approval":
                print(
                    "Review status: "
                    f"{report['status']} (unresolved_item_count={report['unresolved_item_count']}, "
                    f"missing_target_articles={len(report['missing_target_articles'])})"
                )
                return 0
            print(f"Review status: {report['status']}", file=sys.stderr)
            return 1

        if args.command == "approve":
            record = run_approve(
                args.manifest,
                reviewer_name=args.reviewer,
                note=args.note,
            )
            print(
                "Approve status: "
                f"{record['status']} (reviewer={record['reviewer_name']})"
            )
            return 0

        record = run_promote(args.manifest)
        print(
            "Promote status: "
            f"{record['status']} (target={record['promotion_target_dataset']})"
        )
        return 0
    except (TreatyOnboardingError, ReviewGateError, PromotionGateError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
