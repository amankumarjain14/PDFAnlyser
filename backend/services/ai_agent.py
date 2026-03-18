import os
import json
import httpx
from openai import AsyncOpenAI
from typing import Callable, Awaitable

SYSTEM_PROMPT = """You are an expert document analyst and researcher. Your purpose is to deeply analyze PDF content, extract key information, and enhance it with up-to-date web research using the google_search function tool. Always cite your sources and provide comprehensive, well-structured output.

When you use google_search, incorporate the results into the document naturally."""

ANALYSIS_PROMPT_TEMPLATE = """Analyze the following PDF content and provide a comprehensive enhanced version:

{content}

Your analysis must include:
1. EXECUTIVE SUMMARY: Key points and main takeaways (3-5 bullet points)
2. DETAILED INSIGHTS: Deep analysis of the content with context and implications
3. SECTION-WISE BREAKDOWN: Organize content into logical sections with clear headings
4. DATA EXTRACTION: Identify and highlight all tables, numbers, statistics, and important facts
5. WEB RESEARCH ENHANCEMENT: Use the google_search tool to find and incorporate:
   - Updated information on key topics mentioned
   - Missing context or background information
   - Supporting data, statistics, and references
   - Recent developments or changes related to the content
6. REFERENCES: List all sources used for enhancement

Format the output as a well-structured document with:
- Clear headings (use ## for main sections, ### for subsections)
- Bullet points for lists
- Tables in markdown format where applicable
- Proper paragraphs with good readability

Make the enhanced document comprehensive, accurate, and professionally formatted."""


async def google_search(query: str, serpapi_key: str) -> str:
    """Call SerpAPI to perform a Google search."""
    if not serpapi_key:
        return "Web search unavailable (no SerpAPI key configured)."
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                "https://serpapi.com/search",
                params={"q": query, "api_key": serpapi_key, "gl": "us", "hl": "en", "num": 5},
            )
            data = resp.json()
            results = data.get("organic_results", [])
            if not results:
                return "No results found."
            snippets = []
            for r in results[:5]:
                title = r.get("title", "")
                snippet = r.get("snippet", "")
                link = r.get("link", "")
                snippets.append(f"**{title}**\n{snippet}\nSource: {link}")
            return "\n\n".join(snippets)
    except Exception as e:
        return f"Search failed: {str(e)}"


async def analyze_pdf_content(
    content: str,
    openai_api_key: str,
    model: str,
    serpapi_key: str,
    progress_callback: Callable[[str], Awaitable[None]] = None,
) -> str:
    """
    Run the AI analysis agent with optional web search tool.
    Returns the enhanced markdown content.
    """
    client = AsyncOpenAI(api_key=openai_api_key)

    tools = [
        {
            "type": "function",
            "function": {
                "name": "google_search",
                "description": "Search Google for up-to-date information, statistics, and references to enhance document analysis.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query to look up",
                        }
                    },
                    "required": ["query"],
                },
            },
        }
    ]

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": ANALYSIS_PROMPT_TEMPLATE.format(content=content[:12000])},
    ]

    max_iterations = 15
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools if serpapi_key else None,
            tool_choice="auto" if serpapi_key else None,
        )

        choice = response.choices[0]
        message = choice.message
        messages.append(message)

        # If no tool calls, we have our final answer
        if not message.tool_calls:
            return message.content or ""

        # Process each tool call
        for tool_call in message.tool_calls:
            if tool_call.function.name == "google_search":
                args = json.loads(tool_call.function.arguments)
                query = args.get("query", "")
                if progress_callback:
                    await progress_callback(f"Searching: {query}")
                search_result = await google_search(query, serpapi_key)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": search_result,
                    }
                )

    # Safety fallback – return last assistant message content
    for msg in reversed(messages):
        if hasattr(msg, "role") and msg.role == "assistant" and msg.content:
            return msg.content
        if isinstance(msg, dict) and msg.get("role") == "assistant" and msg.get("content"):
            return msg["content"]
    return "Analysis could not be completed."


async def chat_with_pdf(
    content: str,
    chat_history: list,
    openai_api_key: str,
    model: str,
) -> str:
    """
    Handle a follow-up chat message using the PDF content as context.
    """
    client = AsyncOpenAI(api_key=openai_api_key)

    system_msg = f"You are an assistant helping a user understand a PDF document. Here is the content of the PDF for your reference:\n\n{content[:15000]}"
    
    messages = [{"role": "system", "content": system_msg}]
    
    # Add chat history (convert from schemas if needed)
    for msg in chat_history:
        messages.append({"role": msg.role, "content": msg.content})

    response = await client.chat.completions.create(
        model=model,
        messages=messages,
    )

    return response.choices[0].message.content or "Internal AI error."
