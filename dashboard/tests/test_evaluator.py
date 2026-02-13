"""Tests for the HumaneBench evaluator."""

import json
from unittest.mock import MagicMock, patch

import pytest

from humanebench.evaluator import (
    NEUTRAL_FALLBACK,
    _parse_eval_json,
    _strip_fences,
    evaluate,
)
from humanebench.models import EvaluationResult, Principle


VALID_JSON = {
    "principles": [
        {"name": "respect_attention", "score": 1.0},
        {"name": "meaningful_choices", "score": 0.5},
        {"name": "enhance_capabilities", "score": -0.5, "rationale": "Gives fish, not a rod."},
        {"name": "dignity_safety", "score": 1.0},
        {"name": "healthy_relationships", "score": 0.5},
        {"name": "longterm_wellbeing", "score": 0.5},
        {"name": "transparency_honesty", "score": -1.0, "rationale": "Fabricated statistics."},
        {"name": "equity_inclusion", "score": 1.0},
    ],
    "globalViolations": ["factual error detected"],
    "confidence": 0.9,
}


# --- _strip_fences ---

def test_strip_fences_no_fences():
    raw = '{"foo": "bar"}'
    assert _strip_fences(raw) == '{"foo": "bar"}'


def test_strip_fences_markdown_json():
    raw = '```json\n{"foo": "bar"}\n```'
    assert _strip_fences(raw) == '{"foo": "bar"}'


def test_strip_fences_plain_backticks():
    raw = '```\n{"foo": "bar"}\n```'
    assert _strip_fences(raw) == '{"foo": "bar"}'


def test_strip_fences_with_whitespace():
    raw = '  ```json\n  {"foo": "bar"}\n  ```  '
    assert _strip_fences(raw) == '{"foo": "bar"}'


# --- _parse_eval_json ---

def test_parse_valid_json():
    raw = json.dumps(VALID_JSON)
    result = _parse_eval_json(raw)
    assert isinstance(result, EvaluationResult)
    assert len(result.principles) == 8
    assert result.confidence == 0.9
    assert result.globalViolations == ["factual error detected"]


def test_parse_json_with_markdown_fences():
    raw = f"```json\n{json.dumps(VALID_JSON)}\n```"
    result = _parse_eval_json(raw)
    assert len(result.principles) == 8


def test_parse_rationale_only_on_negative():
    raw = json.dumps(VALID_JSON)
    result = _parse_eval_json(raw)
    for p in result.principles:
        if p.score >= 0:
            assert p.rationale is None or p.score < 0 or p.rationale is None


def test_parse_malformed_json_raises():
    with pytest.raises(json.JSONDecodeError):
        _parse_eval_json("not valid json")


def test_parse_score_clamping():
    data = {
        "principles": [{"name": "respect_attention", "score": 0.8}],
        "globalViolations": [],
        "confidence": 0.7,
    }
    result = _parse_eval_json(json.dumps(data))
    assert result.principles[0].score == 1.0


def test_parse_negative_score_clamping():
    data = {
        "principles": [{"name": "dignity_safety", "score": -0.8}],
        "globalViolations": [],
        "confidence": 0.7,
    }
    result = _parse_eval_json(json.dumps(data))
    assert result.principles[0].score == -1.0


# --- evaluate (mocked) ---

def _make_mock_response(json_data: dict) -> MagicMock:
    content = json.dumps(json_data)
    choice = MagicMock()
    choice.message.content = content
    response = MagicMock()
    response.choices = [choice]
    return response


@patch("humanebench.evaluator.litellm.completion")
def test_evaluate_success(mock_completion):
    mock_completion.return_value = _make_mock_response(VALID_JSON)
    result = evaluate("Hello", "Hi there!")
    assert isinstance(result, EvaluationResult)
    assert len(result.principles) == 8
    mock_completion.assert_called_once()


@patch("humanebench.evaluator.litellm.completion")
def test_evaluate_retries_on_bad_json(mock_completion):
    bad_choice = MagicMock()
    bad_choice.message.content = "not json"
    bad_response = MagicMock()
    bad_response.choices = [bad_choice]

    good_response = _make_mock_response(VALID_JSON)

    mock_completion.side_effect = [bad_response, good_response]
    result = evaluate("Hello", "Hi!")
    assert isinstance(result, EvaluationResult)
    assert mock_completion.call_count == 2


@patch("humanebench.evaluator.litellm.completion")
def test_evaluate_fallback_on_double_failure(mock_completion):
    bad_choice = MagicMock()
    bad_choice.message.content = "definitely not json {{{"
    bad_response = MagicMock()
    bad_response.choices = [bad_choice]

    mock_completion.side_effect = [bad_response, bad_response]
    result = evaluate("Hello", "Hi!")
    assert result.confidence == 0.0
    assert len(result.principles) == len(list(Principle))
    for p in result.principles:
        assert p.score == 0.5


@patch("humanebench.evaluator.litellm.completion")
def test_evaluate_fallback_on_exception(mock_completion):
    mock_completion.side_effect = Exception("Network error")
    result = evaluate("Hello", "Hi!")
    assert result is NEUTRAL_FALLBACK


@patch("humanebench.evaluator.litellm.completion")
def test_evaluate_with_history(mock_completion):
    mock_completion.return_value = _make_mock_response(VALID_JSON)
    history = [
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello!"},
    ]
    result = evaluate("Follow-up question", "Here's my answer.", history=history)
    assert isinstance(result, EvaluationResult)
    # Verify history was included in the prompt
    call_args = mock_completion.call_args
    messages = call_args[1]["messages"] if "messages" in call_args[1] else call_args[0][1]
    assert any("CONVERSATION HISTORY" in str(m) for m in messages)


@patch("humanebench.evaluator.litellm.completion")
def test_evaluate_temperature_zero(mock_completion):
    mock_completion.return_value = _make_mock_response(VALID_JSON)
    evaluate("test", "response")
    call_kwargs = mock_completion.call_args[1]
    assert call_kwargs.get("temperature") == 0
