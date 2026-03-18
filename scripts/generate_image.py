"""
Content Claw - Image Generator

Takes an image spec (JSON from agent prompts) and generates an image using DALL-E.
Saves the image to the specified output path.

Usage:
    uv run generate_image.py <spec-json-file> <output-path>
    uv run generate_image.py --prompt "description" <output-path>

Environment:
    OPENAI_API_KEY - Required. Set in .env file.
"""

import json
import os
import sys
from pathlib import Path


def spec_to_prompt(spec: dict) -> str:
    """Convert an image spec JSON (from agent prompts) into a DALL-E prompt."""
    parts = []

    # Diagram type
    diagram_type = spec.get("diagram_type")
    layout = spec.get("style", {}).get("layout", "")
    sub_type = diagram_type or layout

    # Title and description
    title = spec.get("title", spec.get("headline", ""))
    if title:
        parts.append(f'Title: "{title}"')

    subtitle = spec.get("subtitle", spec.get("subheadline", spec.get("description", "")))
    if subtitle:
        parts.append(f"Subtitle: {subtitle}")

    # Content sections
    sections = spec.get("sections", [])
    if sections:
        section_text = []
        for s in sections:
            heading = s.get("heading", "")
            content = s.get("content", "")
            section_text.append(f"- {heading}: {content}")
        parts.append("Content:\n" + "\n".join(section_text))

    # Details (for posters)
    details = spec.get("details", [])
    if details:
        parts.append("Details: " + ", ".join(details))

    # Components (for diagrams)
    components = spec.get("components", [])
    if components:
        comp_text = []
        for c in components:
            comp_text.append(f"- {c.get('label', '')}: {c.get('description', '')}")
        parts.append("Components:\n" + "\n".join(comp_text))

    # Connections (for diagrams)
    connections = spec.get("connections", [])
    if connections:
        conn_text = []
        for c in connections:
            conn_text.append(f"- {c.get('from', '')} -> {c.get('to', '')}: {c.get('label', '')}")
        parts.append("Connections:\n" + "\n".join(conn_text))

    # Style guidance
    style = spec.get("style", {})
    tone = style.get("tone", "professional")
    primary_color = style.get("primary_color")
    accent_color = style.get("accent_color")

    style_parts = [f"{tone} style"]
    if primary_color:
        style_parts.append(f"primary color {primary_color}")
    if accent_color:
        style_parts.append(f"accent color {accent_color}")

    # CTA (for posters)
    cta = spec.get("call_to_action")
    if cta:
        parts.append(f"Call to action: {cta}")

    # Build the full prompt
    content_description = "\n".join(parts)

    if diagram_type:
        prompt = (
            f"Create a clean, modern {diagram_type} diagram for social media. "
            f"{', '.join(style_parts)}. "
            f"Clear labels, readable at small sizes, white or light background. "
            f"\n\n{content_description}"
        )
    elif "poster" in sub_type or "banner" in sub_type:
        prompt = (
            f"Create a modern event poster for social media. "
            f"{', '.join(style_parts)}. "
            f"Bold typography, clean layout, eye-catching. "
            f"\n\n{content_description}"
        )
    else:
        # Default: infographic
        prompt = (
            f"Create a clean, modern infographic for social media. "
            f"{', '.join(style_parts)}. "
            f"Clear visual hierarchy, readable at small sizes, {layout or 'vertical'} layout. "
            f"\n\n{content_description}"
        )

    return prompt


def generate_image(prompt: str, output_path: str, size: str = "1024x1024") -> dict:
    """Generate an image using DALL-E and save to output_path."""
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"error": "OPENAI_API_KEY not set. Add it to your .env file."}

    client = OpenAI(api_key=api_key)

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size=size,
        quality="standard",
    )

    image_url = response.data[0].url
    revised_prompt = response.data[0].revised_prompt

    # Download the image
    import httpx

    img_resp = httpx.get(image_url, timeout=60)
    img_resp.raise_for_status()

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(img_resp.content)

    return {
        "output_path": output_path,
        "size": size,
        "revised_prompt": revised_prompt,
        "bytes": len(img_resp.content),
    }


def main():
    if len(sys.argv) < 3:
        print(
            json.dumps({"error": "Usage: generate_image.py <spec.json|--prompt 'text'> <output.png>"}),
            file=sys.stderr,
        )
        sys.exit(1)

    # Load .env if present
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

    if sys.argv[1] == "--prompt":
        prompt = sys.argv[2]
        output_path = sys.argv[3]
    else:
        spec_path = sys.argv[1]
        output_path = sys.argv[2]
        with open(spec_path) as f:
            spec = json.load(f)
        prompt = spec_to_prompt(spec)

    try:
        result = generate_image(prompt, output_path)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == "__main__":
    main()
