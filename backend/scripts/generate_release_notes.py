
import os
import sys
import subprocess
import google.generativeai as genai

def get_commit_messages(prev_tag, current_tag):
    """Gets commit messages between two tags."""
    try:
        command = f"git log {prev_tag}..{current_tag} --pretty=format:%s"
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error getting commit messages: {e}", file=sys.stderr)
        return ""

def generate_release_notes(api_key, commits):
    """Generates release notes from commits using Gemini."""
    if not commits:
        return "No new commits to generate release notes from."

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')

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
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}", file=sys.stderr)
        return "Error generating release notes."

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python generate_release_notes.py <previous_tag> <current_tag>", file=sys.stderr)
        sys.exit(1)

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("Error: GEMINI_API_KEY environment variable not set.", file=sys.stderr)
        sys.exit(1)

    previous_tag = sys.argv[1]
    current_tag = sys.argv[2]

    commit_messages = get_commit_messages(previous_tag, current_tag)
    if commit_messages:
        release_notes = generate_release_notes(gemini_api_key, commit_messages)
        print(release_notes)
    else:
        print("No commits found between the specified tags.")

