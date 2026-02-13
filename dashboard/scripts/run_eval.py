#!/usr/bin/env python3
"""CLI to evaluate conversations from a JSONL file or direct prompt/response."""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from humanebench.evaluator import evaluate


def print_result(result, user_prompt: str = "", ai_response: str = "") -> None:
    if user_prompt:
        print(f"\nUser: {user_prompt[:100]}{'...' if len(user_prompt) > 100 else ''}")
    if ai_response:
        print(f"AI:   {ai_response[:100]}{'...' if len(ai_response) > 100 else ''}")

    print("\nScores:")
    for p in result.principles:
        icon = "✓" if p.score > 0 else "✗"
        bar = "█" * int(abs(p.score) * 4)
        print(f"  {icon} {p.name.value:<25} {p.score:+.1f} {bar}")
        if p.rationale:
            print(f"    └─ {p.rationale}")

    overall = sum(p.score for p in result.principles) / len(result.principles)
    print(f"\nOverall: {overall:+.3f}  |  Confidence: {result.confidence:.2f}")

    if result.globalViolations:
        print(f"Global violations: {', '.join(result.globalViolations)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="HumaneBench CLI evaluator")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", "-i", help="JSONL file with {user_prompt, ai_response} objects")
    group.add_argument("--prompt", "-p", help="User prompt (use with --response)")
    parser.add_argument("--response", "-r", help="AI response (use with --prompt)")
    parser.add_argument("--json-output", action="store_true", help="Output raw JSON")
    args = parser.parse_args()

    if args.prompt:
        if not args.response:
            parser.error("--response is required when using --prompt")
        result = evaluate(args.prompt, args.response)
        if args.json_output:
            print(result.model_dump_json(indent=2))
        else:
            print_result(result, args.prompt, args.response)

    elif args.input:
        path = Path(args.input)
        if not path.exists():
            print(f"Error: file not found: {path}", file=sys.stderr)
            sys.exit(1)

        with open(path) as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    conv = json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"Line {line_num}: JSON parse error: {e}", file=sys.stderr)
                    continue

                user_prompt = conv.get("user_prompt", "")
                ai_response = conv.get("ai_response", "")
                history = conv.get("history")

                if not user_prompt or not ai_response:
                    print(f"Line {line_num}: missing user_prompt or ai_response", file=sys.stderr)
                    continue

                print(f"\n{'='*60}")
                print(f"Conversation {line_num}")
                result = evaluate(user_prompt, ai_response, history)

                if args.json_output:
                    output = result.model_dump()
                    output["user_prompt"] = user_prompt
                    output["ai_response"] = ai_response
                    print(json.dumps(output, indent=2))
                else:
                    print_result(result, user_prompt, ai_response)


if __name__ == "__main__":
    main()
