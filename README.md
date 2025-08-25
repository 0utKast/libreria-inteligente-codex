# 📚 Mi Librería Inteligente

Mi Librería Inteligente es una aplicación web que utiliza la IA multimodal de Google Gemini para analizar y catalogar automáticamente tu colección de libros digitales (PDF y EPUB). Simplemente sube un libro, y la aplicación extraerá su portada, título, autor y le asignará una categoría, guardándolo todo en una base de datos local para que puedas explorar tu biblioteca fácilmente.

## ✨ Características Principales

- **Subida Sencilla:** Arrastra y suelta o selecciona archivos PDF y EPUB para añadir a tu biblioteca.
- **Subida Múltiple:** Sube varios libros a la vez y observa el progreso de cada uno de forma individual.
- **Análisis Inteligente con IA:** Utiliza Google Gemini para extraer metadatos clave (título, autor, categoría) de tus libros, incluso si no están presentes en el archivo, y encuentra la portada.
- **Lectura Integrada:** Lee tus libros (PDF y EPUB) directamente dentro de la aplicación, sin necesidad de software externo. Los PDF se abren en una nueva pestaña para una mejor experiencia.
- **Conversor EPUB a PDF:** Convierte tus archivos EPUB a formato PDF directamente desde la aplicación. El PDF resultante se abre automáticamente en una nueva pestaña.
- **Charla sobre libros con la IA (RAG):** Sube cualquier libro (PDF o EPUB) y mantén una conversación interactiva con la IA sobre su contenido. La IA priorizará la información del libro, pero también puede usar su conocimiento general para responder preguntas más amplias sobre el autor o temas relacionados.
- **Catalogación Automática:** Guarda los libros y sus metadatos en una base de datos local.
- **Biblioteca Visual:** Explora todos tus libros en una vista de galería intuitiva.
- **Filtros por Categoría:** Filtra tu biblioteca por las categorías asignadas por la IA.
- **Buscador Integrado:** Busca libros instantáneamente por título, autor o categoría.
- **Gestión Completa:** Elimina libros individuales o categorías enteras con un solo clic.
- **Acceso Directo:** Abre los archivos originales de tus libros directamente desde la aplicación.
- **Diseño Responsivo:** La interfaz de usuario se adapta automáticamente a diferentes tamaños de pantalla, permitiendo una experiencia fluida tanto en ordenadores de escritorio como en dispositivos móviles (teléfonos y tablets).

## 🛠️ Tecnologías Utilizadas

- **Backend:** Python, FastAPI, SQLAlchemy, Alembic
- **Frontend:** React (JavaScript)
- **IA:** Google Gemini Pro
- **Base de Datos:** SQLite
- **Manejo de Libros:** PyMuPDF (para PDF), EbookLib (para EPUB)

## Building and Running

This is a small change for the documentation PR example.

Testing release drafter action.

Sigue estos pasos para ejecutar el proyecto en tu máquina local.

### Prerrequisitos

- [Python 3.9+](https://www.python.org/downloads/)
- [Node.js y npm](https://nodejs.org/en/)
- Una clave de API de **Google Gemini**. Puedes obtenerla en [Google AI Studio](https://aistudio.google.com/app/apikey).

### Dependencias Adicionales (Para la Conversión EPUB a PDF)

La herramienta de conversión de EPUB a PDF requiere la instalación de **GTK3**. Si no instalas esta dependencia, el resto de la aplicación funcionará correctamente, pero la herramienta de conversión mostrará un error al intentar convertir.

Sigue las instrucciones para tu sistema operativo:

- **Windows:**
  1. Descarga e instala **MSYS2** desde [su web oficial](https://www.msys2.org/).
  2. Abre la terminal de MSYS2 (no la de Windows) y actualiza el sistema:
     ```bash
     pacman -Syu
     ```
  3. Cierra la terminal y vuelve a abrirla. Actualiza de nuevo:
     ```bash
     pacman -Su
     ```
  4. Instala GTK3:
     ```bash
     pacman -S mingw-w64-x86_64-gtk3
     ```
  5. Añade la carpeta `bin` de MSYS2 a tu **PATH** de Windows. Normalmente se encuentra en `C:\msys64\mingw64\bin`.

- **macOS (usando [Homebrew](https://brew.sh/)):**
  ```bash
  brew install pango
  ```

- **Linux (Debian/Ubuntu):**
  ```bash
  sudo apt-get install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0
  ```

### 1. Clonar el Repositorio

```bash
git clone https://github.com/TU_USUARIO/TU_REPOSITORIO.git
cd TU_REPOSITORIO
```

### 2. Configurar el Backend

```bash
# Navega al directorio del backend
cd backend

# Crea y activa un entorno virtual
python -m venv .venv
# En Windows:
.venv\Scripts\activate
# En macOS/Linux:
# source .venv/bin/activate

# Instala las dependencias de Python
pip install -r requirements.txt

# Crea la base de datos inicial
alembic upgrade head
```

### 3. Configurar las Variables de Entorno

En la raíz del proyecto, crea un archivo llamado `.env` y añade tu clave de API de Gemini. Puedes usar el archivo `.env.example` como plantilla.

**.env**
```
GEMINI_API_KEY="TU_API_KEY_DE_GEMINI_AQUI"
```

### 4. Configurar el Frontend

```bash
# Desde la raíz del proyecto, navega al directorio del frontend
cd frontend

# Instala las dependencias de Node.js
npm install
```

### 5. ¡Ejecutar la Aplicación!

Necesitarás dos terminales abiertas.

- **En la Terminal 1 (para el Backend):**
  ```bash
  # Desde la carpeta 'backend' y con el entorno virtual activado
  uvicorn main:app --reload --port 8001 --host 0.0.0.0
  ```

- **En la Terminal 2 (para el Frontend):**
  ```bash
  # Desde la carpeta 'frontend'
  npm start
  ```

¡Abre tu navegador en `http://localhost:3000` y empieza a construir tu librería inteligente!

**Acceso desde Dispositivos Móviles:**
Para acceder a la aplicación desde un dispositivo móvil en la misma red, asegúrate de que el servidor backend se inicie con `--host 0.0.0.0` (como se muestra arriba). Luego, en tu dispositivo móvil, abre el navegador y navega a `http://<TU_IP_LOCAL>:3000`, donde `<TU_IP_LOCAL>` es la dirección IP de tu ordenador en la red local (por ejemplo, `http://192.168.1.100:3000`).

## 🧭 Variante “Codex”: nuevo repositorio limpio

Esta variante incorpora mejoras de seguridad, CI estable sin llamadas a IA, CORS configurable y RAG persistente. Recomendado publicarla en un nuevo repositorio para no mezclar con el historial anterior.

### 1) Crear repositorio vacío en GitHub
- Crea `libreria-inteligente-codex` en GitHub (sin README inicial).

### 2) Preparar carpeta y publicar
```
cp -R <ruta_proyecto> ../libreria-inteligente-codex
cd ../libreria-inteligente-codex
rm -rf .git library.db backend/.venv frontend/node_modules temp_books static/covers || true
git init
git add .
git commit -m "feat: variante Codex con CI-safe AI, CORS y RAG persistente"
git branch -M main
git remote add origin https://github.com/<tu_usuario>/libreria-inteligente-codex.git
git push -u origin main
```

### 3) Configurar secrets del repositorio
- En GitHub → Settings → Secrets and variables → Actions:
  - `GEMINI_API_KEY`: tu clave de Google Gemini.

### 4) Variables de entorno y configuración
- En la raíz, crea `.env` (puedes copiar de `.env.example`):
  - `GEMINI_API_KEY`: clave IA.
  - `ALLOW_ORIGINS`: CSV de orígenes exactos (ej. `http://localhost:3000`).
  - `FRONTEND_PORTS`: CSV de puertos del frontend (por defecto `3000,5173,8080`).
  - `ALLOW_ORIGIN_REGEX`: regex opcional de orígenes. Por defecto habilita HTTP y HTTPS para `localhost`, `127.0.0.1` y rangos privados (10.x, 192.168.x, 172.16–31) en los puertos de `FRONTEND_PORTS`. Esto permite acceder desde cualquier dispositivo de tu red sin fijar IPs.
  - `CHROMA_PATH`: ruta para persistir el índice (por defecto `./rag_index`).
  - Opcional: `DISABLE_AI=1` en CI/tests.
- Frontend (CRA) usa `REACT_APP_API_URL`:
  - Linux/macOS: `export REACT_APP_API_URL="http://<tu-ip>:8001"`
  - Windows PowerShell: `$env:REACT_APP_API_URL="http://<tu-ip>:8001"`

### 5) Ejecutar localmente
- Backend: `cd backend && python -m venv .venv && (activar) && pip install -r requirements.txt && uvicorn main:app --reload --port 8001 --host 0.0.0.0`
- Frontend: `cd frontend && npm install && npm start`

### 6) Notas de CI de la variante
- Los tests en CI se ejecutan con `DISABLE_AI=1` para evitar llamadas reales a Gemini.
- La generación automática de tests ignora archivos de test existentes y no sobreescribe.

## 🔎 RAG: indexado, consulta y limpieza

- Indexar libro existente (usa el ID de BD como `book_id` en RAG):
  - `POST /rag/index/{book_id}?force=false` → procesa el `file_path` del libro y genera/actualiza su índice.
  - Usa `force=true` para reindexar (borra y vuelve a indexar).
- Consultar:
  - `POST /rag/query/` con body `{ "query": "...", "book_id": "<id>" }`.
- Limpieza automática:
  - Al borrar un libro (`DELETE /books/{id}`) o una categoría (`DELETE /categories/{name}`), el backend elimina también los vectores de RAG asociados.

- Estado RAG por libro:
  - `GET /rag/status/{book_id}` → devuelve `{ indexed: boolean, vector_count: number }`.

- (Re)indexación por lotes:
  - `POST /rag/reindex/category/{category_name}?force=true|false` → procesa todos los libros de una categoría.
  - `POST /rag/reindex/all?force=true|false` → procesa todos los libros de la biblioteca.

### Estimar coste/tokens antes de indexar

- Por libro: `GET /rag/estimate/book/{book_id}?per1k=<coste_por_1000>`
- Por categoría: `GET /rag/estimate/category/{category_name}?per1k=<coste_por_1000>`
- Total biblioteca: `GET /rag/estimate/all?per1k=<coste_por_1000>`

Devuelve tokens totales estimados, número de chunks (tamaño base 1000 tokens) y coste estimado (`tokens/1000 * per1k`).
Nota: el conteo usa `tiktoken` como aproximación a los tokens de Gemini, por lo que es una estimación.

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.
