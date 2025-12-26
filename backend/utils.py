import os
import google.generativeai as genai
from dotenv import load_dotenv
import io
import tempfile
import zipfile
import pathlib
from weasyprint import HTML, CSS
from bs4 import BeautifulSoup

def configure_genai():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("No se encontró la API Key. Asegúrate de que GOOGLE_API_KEY o GEMINI_API_KEY estén configuradas en tu archivo .env")
    genai.configure(api_key=api_key)

def get_gemini_model(model_name: str = "gemini-pro"):
    return genai.GenerativeModel(model_name)

def generate_text_from_prompt(prompt: str, model_name: str = "gemini-pro"):
    """
    Genera texto a partir de un prompt usando el modelo Gemini especificado.
    """
    try:
        model = get_gemini_model(model_name)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error al generar texto: {e}"

def get_file_extension(filename: str) -> str:
    """
    Devuelve la extensión de un archivo en minúsculas.
    Ejemplo: 'libro.PDF' -> '.pdf'
    """
    return os.path.splitext(filename)[1].lower()

def is_allowed_file(filename: str, allowed_extensions: set) -> bool:
    """

    Comprueba si un archivo tiene una extensión permitida.
    """
    return get_file_extension(filename) in allowed_extensions

def convert_epub_bytes_to_pdf_bytes(epub_content: bytes) -> bytes:
    """
    Convierte el contenido de un archivo EPUB (en bytes) a un archivo PDF (en bytes).
    Esta es una función compleja que extrae el contenido del EPUB y lo renderiza.
    """
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # 1. Extraer el EPUB a una carpeta temporal
            with zipfile.ZipFile(io.BytesIO(epub_content), 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # 2. Encontrar el archivo .opf (el "manifiesto" del libro)
            opf_path = next(pathlib.Path(temp_dir).rglob('*.opf'), None)
            if not opf_path:
                raise Exception("No se pudo encontrar el archivo .opf en el EPUB.")
            content_root = opf_path.parent

            # 3. Leer y analizar el manifiesto .opf
            with open(opf_path, 'rb') as f:
                opf_soup = BeautifulSoup(f, 'lxml-xml')

            # 4. Crear una página de portada si se encuentra
            html_docs = []
            cover_meta = opf_soup.find('meta', {'name': 'cover'})
            if cover_meta:
                cover_id = cover_meta.get('content')
                cover_item = opf_soup.find('item', {'id': cover_id})
                if cover_item:
                    cover_href = cover_item.get('href')
                    cover_path = content_root / cover_href
                    if cover_path.exists():
                        cover_html_string = f"<html><body style='text-align: center; margin: 0; padding: 0;'><img src='{cover_path.as_uri()}' style='width: 100%; height: 100%; object-fit: contain;'/></body></html>"
                        html_docs.append(HTML(string=cover_html_string))

            # 5. Encontrar y leer todos los archivos CSS
            stylesheets = []
            css_items = opf_soup.find_all('item', {'media-type': 'text/css'})
            for css_item in css_items:
                css_href = css_item.get('href')
                if css_href:
                    css_path = content_root / css_href
                    if css_path.exists():
                        stylesheets.append(CSS(filename=css_path))

            # 6. Encontrar el orden de lectura (spine) y añadir los capítulos
            spine_ids = [item.get('idref') for item in opf_soup.find('spine').find_all('itemref')]
            html_paths_map = {item['id']: item['href'] for item in opf_soup.find_all('item', {'media-type': 'application/xhtml+xml'})}
            
            for chapter_id in spine_ids:
                href = html_paths_map.get(chapter_id)
                if href:
                    chapter_path = content_root / href
                    if chapter_path.exists():
                        html_docs.append(HTML(filename=chapter_path, encoding='utf-8'))

            if not html_docs:
                raise Exception("No se encontró contenido HTML en el EPUB.")

            # 7. Renderizar y unir todos los documentos
            first_doc = html_docs[0].render(stylesheets=stylesheets)
            all_pages = [p for doc in html_docs[1:] for p in doc.render(stylesheets=stylesheets).pages]
            
            pdf_bytes_io = io.BytesIO()
            first_doc.copy(all_pages).write_pdf(target=pdf_bytes_io)
            return pdf_bytes_io.getvalue()

    except Exception as e:
        # En caso de un error de conversión, lo relanzamos para que el endpoint lo maneje
        raise RuntimeError(f"Error durante la conversión de EPUB a PDF: {e}") from e

def extract_text_from_pdf(file_path: str, max_pages: int = 5) -> str:
    """Extrae texto de las primeras páginas de un PDF usando PyMuPDF (fitz)."""
    import fitz
    try:
        doc = fitz.open(file_path)
        text = ""
        for i in range(min(len(doc), max_pages)):
            text += doc.load_page(i).get_text("text", sort=True) + "\n"
        doc.close()
        return text
    except Exception as e:
        print(f"Error al extraer texto de PDF {file_path}: {e}")
        return ""

def extract_text_from_epub(file_path: str, max_chars: int = 5000) -> str:
    """Extrae texto de un EPUB usando ebooklib."""
    import ebooklib
    from ebooklib import epub
    try:
        book = epub.read_epub(file_path)
        text = ""
        for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            soup = BeautifulSoup(item.get_content(), 'html.parser')
            text += soup.get_text(separator=' ') + "\n"
            if len(text) > max_chars:
                break
        return text
    except Exception as e:
        print(f"Error al extraer texto de EPUB {file_path}: {e}")
        return ""

# Ejemplo de uso (si se ejecuta este script directamente)
if __name__ == '__main__':
    # Para probar, necesitarías un archivo .env en la raíz del proyecto
    # y un archivo epub de ejemplo.
    # configure_genai()
    # print(generate_text_from_prompt("Explica qué es un modelo de lenguaje grande."))
    
    # Crear un epub y pdf de prueba
    if not os.path.exists("temp"):
        os.makedirs("temp")
    
    epub_file = "temp/test.epub"
    pdf_file = "temp/test.pdf"
    
    # Crear un archivo epub falso para la prueba
    with open(epub_file, "w") as f:
        f.write("Este no es un epub real.")
        
    # Esta función ya no existe, el código de abajo fallaría.
    # convert_epub_to_pdf_weasyprint(epub_file, pdf_file)
    
    # Para probar la nueva función:
    # with open("ruta/a/un/epub/real.epub", "rb") as f_epub:
    #     pdf_bytes = convert_epub_bytes_to_pdf_bytes(f_epub.read())
    #     with open(pdf_file, "wb") as f_pdf:
    #         f_pdf.write(pdf_bytes)

    if os.path.exists(pdf_file):
        print(f"Archivo PDF de prueba creado en: {pdf_file}")
        
    # Limpiar
    # os.remove(epub_file)
    # os.remove(pdf_file)
    # os.rmdir("temp")
