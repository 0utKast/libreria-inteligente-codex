
import os
import sys
import subprocess
import google.generativeai as genai
from typing import Dict, List

def get_commit_messages(prev_tag, current_tag):
    """Gets commit messages between two tags."""
    try:
        command = f"git log {prev_tag}..{current_tag} --pretty=format:%s"
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit messages: {e}", file=sys.stderr)
        return ""

def _fallback_from_commits(commits: str) -> str:
    """Generate basic Markdown release notes from commit messages without AI."""
    lines = [l.strip("- *\t ") for l in commits.splitlines() if l.strip()]
    buckets: Dict[str, List[str]] = {
        "✨ Nuevas Funcionalidades": [],
        "🐛 Correcciones de Errores": [],
        "🚀 Rendimiento": [],
        "🧹 Mantenimiento": [],
        "📝 Documentación": [],
        "Otros cambios": [],
    }

    for msg in lines:
        low = msg.lower()
        if low.startswith("feat") or "feature" in low:
            buckets["✨ Nuevas Funcionalidades"].append(msg)
        elif low.startswith("fix") or "bug" in low:
            buckets["🐛 Correcciones de Errores"].append(msg)
        elif low.startswith("perf") or "performance" in low:
            buckets["🚀 Rendimiento"].append(msg)
        elif low.startswith(("docs", "doc")):
            buckets["📝 Documentación"].append(msg)
        elif low.startswith(("refactor", "chore", "build", "ci")):
            buckets["🧹 Mantenimiento"].append(msg)
        else:
            buckets["Otros cambios"].append(msg)

    sections = ["## Notas de lanzamiento"]
    for title, items in buckets.items():
        if not items:
            continue
        sections.append(f"\n### {title}")
        sections.extend([f"- {item}" for item in items])

    return "\n".join(sections) if sections else "Sin cambios relevantes."


def generate_release_notes(api_key, commits):
    """Generates release notes from commits using Gemini, with local fallback."""
    if not commits:
        return "No new commits to generate release notes from."

    # Truncate very long commit logs to keep prompt reasonable
    if len(commits) > 8000:
        commits = commits[:8000] + "\n..."

    genai.configure(api_key=api_key)
    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    model = genai.GenerativeModel(model_name)

    prompt = f"""
    Eres un manager de producto experto en comunicación.
    Tu tarea es redactar unas notas de lanzamiento (release notes) claras, atractivas y bien estructuradas para el usuario final.
    Utiliza la siguiente lista de cambios técnicos (mensajes de commit) para generar las notas.

    Instrucciones:
    1.  Analiza la lista de commits.
    2.  Agrupa los cambios en categorías lógicas como '✨ Nuevas Funcionalidades', '🐛 Correcciones de Errores', y '🔧 Mejoras y Mantenimiento'. Si una categoría no tiene cambios, no la incluyas.
    3.  Redacta cada punto de forma clara y orientada al beneficio del usuario, en lugar de describir el cambio técnico.
    4.  El formato de salida debe ser Markdown.
    5.  El tono debe ser profesional pero cercano.

    Lista de commits:
    ---
    {commits}
    ---
    """

    try:
        response = model.generate_content(prompt)
        return response.text or _fallback_from_commits(commits)
    except Exception as e:
        print(f"Error calling Gemini API: {e}", file=sys.stderr)
        return _fallback_from_commits(commits)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_release_notes.py <previous_tag> <current_tag>", file=sys.stderr)
        sys.exit(1)

    gemini_api_key = os.getenv("GEMINI_API_KEY")

    previous_tag = sys.argv[1]
    current_tag = sys.argv[2]

    print(f"Debug: Previous tag: {previous_tag}", file=sys.stderr)
    print(f"Debug: Current tag: {current_tag}", file=sys.stderr)

    commit_messages = get_commit_messages(previous_tag, current_tag)
    print(f"Debug: Commit messages retrieved: {commit_messages}", file=sys.stderr)

    if not commit_messages:
        print("No commits found between the specified tags.", file=sys.stderr)
        print("No commits found between the specified tags.")
        sys.exit(0)

    # If there's no API key, fall back to local generation instead of failing
    if not gemini_api_key:
        print("Warning: GEMINI_API_KEY not set; using local fallback.", file=sys.stderr)
        fallback_notes = _fallback_from_commits(commit_messages)
        print(f"Debug: Fallback release notes generated: {fallback_notes}", file=sys.stderr)
        print(fallback_notes)
        sys.exit(0)

    release_notes = generate_release_notes(gemini_api_key, commit_messages)
    print(f"Debug: Release notes generated: {release_notes}", file=sys.stderr)
    print(release_notes)
