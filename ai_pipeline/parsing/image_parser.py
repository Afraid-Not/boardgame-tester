"""이미지 규칙서를 텍스트로 변환한 뒤 구조화된 게임 JSON으로 파싱."""

import base64
from openai import OpenAI

from ai_pipeline.parsing.prompts.economic_board import IMAGE_PARSE_PROMPT
from ai_pipeline.parsing.text_parser import parse_rules_text


def parse_rules_image(
    image_data: bytes,
    media_type: str,
    api_key: str,
    rag_references: list[dict] | None = None,
    model: str = "gpt-4o",
) -> dict:
    """
    이미지 규칙서를 파싱하여 구조화된 게임 JSON을 반환.

    1단계: GPT-4o Vision으로 이미지에서 규칙 텍스트 추출
    2단계: 추출된 텍스트를 text_parser로 구조화

    Args:
        image_data: 이미지 바이너리 데이터
        media_type: MIME type (image/png, image/jpeg, etc.)
        api_key: OpenAI API key
        rag_references: RAG 유사 게임 레퍼런스
        model: 사용할 OpenAI 모델

    Returns:
        파싱된 게임 구조 dict
    """
    # 1단계: 이미지 → 텍스트
    rules_text = _extract_text_from_image(image_data, media_type, api_key, model)

    # 2단계: 텍스트 → 구조화된 JSON
    return parse_rules_text(
        rules_text=rules_text,
        api_key=api_key,
        rag_references=rag_references,
        model=model,
    )


def extract_text_only(
    image_data: bytes,
    media_type: str,
    api_key: str,
    model: str = "gpt-4o",
) -> str:
    """이미지에서 규칙 텍스트만 추출 (구조화하지 않음)."""
    return _extract_text_from_image(image_data, media_type, api_key, model)


def _extract_text_from_image(
    image_data: bytes,
    media_type: str,
    api_key: str,
    model: str,
) -> str:
    """OpenAI Vision API로 이미지에서 텍스트 추출."""
    client = OpenAI(api_key=api_key)

    image_b64 = base64.b64encode(image_data).decode("utf-8")

    response = client.chat.completions.create(
        model=model,
        max_tokens=4096,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{media_type};base64,{image_b64}",
                        },
                    },
                    {
                        "type": "text",
                        "text": IMAGE_PARSE_PROMPT,
                    },
                ],
            }
        ],
    )

    return response.choices[0].message.content
