import os
import json
import logging
from typing import Any, Dict, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

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
        config = types.GenerateContentConfig(tools=[grounding_tool])

        # Construct search prompt for grounded search
        search_prompt = f"""
        Search for information about: "{query}"
        
        Please provide the search results in this exact JSON format:
        {{
            "results": [
                {{
                    "source": "URL or domain identifier",
                    "publisher": "Publisher name or null",
                    "title": "Result title",
                    "description": "Brief description",
                    "image": "Image URL or empty string",
                    "url": "Direct link to result"
                }}
            ]
        }}
        
        Guidelines:
        - Use the grounded search results to provide factual, up-to-date information
        - Include proper source attribution with actual URLs
        - Provide 5-10 relevant, high-quality results
        - Set publisher to null if unknown
        - Use empty string for image if no image available
        - Ensure descriptions are informative but concise
        """

        if language:
            search_prompt += f"\n- Translate result to language: {language}"

        if extraFieldsProperties:
            search_prompt += f"\n- Include these additional fields if possible: {list(extraFieldsProperties.keys())}"

        # Make the request with Google Search grounding
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=search_prompt,
            config=config,
        )

        # Parse JSON response
        try:
            result_data = json.loads(response.text)
            if "results" not in result_data:
                raise ValueError("Invalid response format - missing 'results' field")
            return result_data
        except json.JSONDecodeError:
            # Fallback: create a basic response structure
            return {
                "results": [
                    {
                        "source": "gemini-search",
                        "publisher": "Google Gemini",
                        "title": f"Search results for: {query}",
                        "description": response.text[:200] + "..."
                        if len(response.text) > 200
                        else response.text,
                        "image": "",
                        "url": "",
                    }
                ]
            }

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
