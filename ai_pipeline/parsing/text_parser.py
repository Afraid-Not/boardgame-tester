"""텍스트 규칙서를 구조화된 게임 JSON으로 파싱."""

import json
from openai import OpenAI

from ai_pipeline.parsing.prompts.economic_board import (
    SYSTEM_PROMPT,
    PARSE_PROMPT_TEMPLATE,
    RAG_CONTEXT_TEMPLATE,
    EXAMPLE_OUTPUT,
)


def parse_rules_text(
    rules_text: str,
    api_key: str,
    rag_references: list[dict] | None = None,
    model: str = "gpt-4o",
) -> dict:
    """
    규칙서 텍스트를 파싱하여 구조화된 게임 JSON을 반환.

    Args:
        rules_text: 규칙서 원문 텍스트
        api_key: OpenAI API key
        rag_references: RAG로 검색된 유사 게임 레퍼런스 목록
        model: 사용할 OpenAI 모델

    Returns:
        파싱된 게임 구조 dict
    """
    client = OpenAI(api_key=api_key)

    # RAG 컨텍스트 구성
    rag_context = ""
    if rag_references:
        ref_texts = []
        for ref in rag_references:
            ref_texts.append(
                f"**{ref['name']}**: {ref.get('rules_summary', 'N/A')}"
            )
        rag_context = RAG_CONTEXT_TEMPLATE.format(references="\n\n".join(ref_texts))

    # 프롬프트 구성
    user_prompt = PARSE_PROMPT_TEMPLATE.format(
        rag_context=rag_context,
        rules_text=rules_text,
        example=EXAMPLE_OUTPUT,
    )

    # OpenAI API 호출
    response = client.chat.completions.create(
        model=model,
        max_tokens=8192,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    # 응답에서 JSON 추출
    raw_text = response.choices[0].message.content.strip()
    return _extract_json(raw_text)


def _extract_json(text: str) -> dict:
    """응답 텍스트에서 JSON을 추출. 마크다운 코드블록도 처리."""
    if "```" in text:
        start = text.find("```")
        content_start = text.find("\n", start) + 1
        end = text.find("```", content_start)
        if end != -1:
            text = text[content_start:end].strip()

    return json.loads(text)
