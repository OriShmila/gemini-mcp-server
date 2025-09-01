import os
import json
import logging
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure logging
logger = logging.getLogger("GeminiMCP")

# Configure Gemini client
if GEMINI_API_KEY:
    # Set up the client
    client = genai.Client(api_key=GEMINI_API_KEY)
else:
    logger.warning("GEMINI_API_KEY not set in environment variables")
    client = None


class WebSearchResult(BaseModel):
    source: str
    publisher: str
    image: str
    title: str
    content: str
    url: str


async def gemini_websearch(
    query: str,
    language: Optional[str] = None,
    extraFieldsProperties: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Search the web using Google grounded search and return normalized results."""
    if not query:
        raise ValueError("query parameter is required")

    if not GEMINI_API_KEY or not client:
        raise ValueError("GEMINI_API_KEY not configured")

    try:
        # Create Google Search grounding tool
        grounding_tool = types.Tool(google_search=types.GoogleSearch())

        # Configure generation settings with grounding
        config = types.GenerateContentConfig(
            tools=[grounding_tool],
            response_schema=list[WebSearchResult],
            response_mime_type="application/json",
        )

        # Construct search prompt for grounded search
        search_prompt = f"""{query}
        Search in web return array 5-7 result with source, publisher, image, title, content, url
        return only array"""

        if language:
            search_prompt += f"\n- Translate result to language: {language}"

        # Make the request with Google Search grounding
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=search_prompt,
            config=config,
        )
        # Parse JSON response
        result_data = json.loads(response.text)
        return {"results": result_data}
    except Exception as e:
        logger.error(f"Error in gemini_websearch: {e}")
        raise ValueError(f"Web search failed: {str(e)}")


async def gemini_call(
    prompt: str,
    args: Optional[Dict[str, Any]] = None,
    outputSchema: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Call Gemini model directly (without grounding) with a prompt and optional args, constraining the response to a provided JSON Schema."""
    if not prompt:
        raise ValueError("prompt parameter is required")

    if not outputSchema:
        raise ValueError("outputSchema parameter is required")

    if not GEMINI_API_KEY or not client:
        raise ValueError("GEMINI_API_KEY not configured")

    try:
        # Construct the full prompt
        full_prompt = prompt

        if args:
            full_prompt += f"\n\nInput data: {json.dumps(args, indent=2)}"

        full_prompt += f"""

Please respond with JSON that strictly adheres to this schema:
{json.dumps(outputSchema, indent=2)}

Your response must be valid JSON that validates against the provided schema. Do not include any text outside the JSON response.
"""

        # Generate response (without grounding)
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=full_prompt,
        )
        response_text = response.text.strip()

        # Try to extract JSON from response
        try:
            # Look for JSON content between ```json and ``` or just parse directly
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                json_content = response_text[start:end].strip()
            elif response_text.startswith("{") or response_text.startswith("["):
                json_content = response_text
            else:
                # Try to find JSON-like content
                import re

                json_match = re.search(r"(\{.*\}|\[.*\])", response_text, re.DOTALL)
                if json_match:
                    json_content = json_match.group(1)
                else:
                    raise ValueError("No valid JSON found in response")

            # Parse the JSON
            output = json.loads(json_content)

            return {"output": output}

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            logger.error(f"Raw response: {response_text}")
            # Return a fallback response
            return {
                "output": {
                    "error": "Failed to parse JSON response",
                    "raw_response": response_text,
                }
            }

    except Exception as e:
        logger.error(f"Error in gemini_call: {e}")
        raise ValueError(f"Gemini call failed: {str(e)}")


# Tool function mapping
TOOL_FUNCTIONS = {
    "gemini_websearch": gemini_websearch,
    "gemini_call": gemini_call,
}
