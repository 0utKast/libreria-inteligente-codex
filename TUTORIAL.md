# Tutorial: Automatización de Flujos de Trabajo con GitHub Actions y Gemini

En este tutorial, exploraremos cómo hemos transformado nuestro proceso de desarrollo utilizando una combinación de **GitHub Actions** y la potencia de la **IA de Google Gemini**. Aprenderás qué son las GitHub Actions, cómo se integran con servicios de IA como Gemini y analizaremos paso a paso cada una de las automatizaciones que hemos implementado en este repositorio.

## 1. ¿Qué es GitHub Actions?

Imagina que tienes un asistente robótico personal para tu repositorio de código. Cada vez que ocurre algo (como subir código, crear una tarea o abrir un Pull Request), este asistente puede realizar una serie de tareas por ti de forma automática. Eso es, en esencia, **GitHub Actions**.

Es una plataforma de **Integración Continua y Entrega Continua (CI/CD)** que te permite automatizar tus flujos de trabajo de software. Estos flujos de trabajo se definen en ficheros de texto (con formato YAML) que viven dentro de tu repositorio, en la carpeta `.github/workflows`.

## 2. ¿Cómo se Integra Gemini en GitHub Actions?

Para que nuestro "asistente" pueda usar los superpoderes de Gemini, necesita una forma de autenticarse con la API de Google. Esto se logra mediante una **API Key** (una clave secreta).

Sin embargo, es una **muy mala práctica** escribir esta clave secreta directamente en los ficheros de workflow, ya que cualquiera podría verla. La solución es usar los **Secretos de GitHub**.

El proceso es el siguiente:
1.  Obtienes tu API Key de Google AI Studio.
2.  En tu repositorio de GitHub, vas a `Settings > Secrets and variables > Actions`.
3.  Creas un nuevo "secret" llamado `GEMINI_API_KEY` y pegas tu clave allí.
4.  En nuestros ficheros de workflow, accedemos a esta clave de forma segura usando la sintaxis `${{ secrets.GEMINI_API_KEY }}`. GitHub se encarga de pasarla al entorno de ejecución sin exponerla.

## 3. Análisis de Nuestras Acciones Automatizadas

A continuación, se detalla cada uno de los workflows que hemos configurado.

### 3.1. Revisión Automática de Pull Requests (`pr-review.yml`)

*   **Propósito:** Utiliza a Gemini para actuar como un revisor de código automático. Analiza los cambios en un Pull Request y publica un comentario con sugerencias, mejoras y posibles errores.
*   **Disparador (Trigger):** Se ejecuta cada vez que se abre o se actualiza un **Pull Request**.
*   **Funcionamiento:**
    1.  El workflow se activa cuando se abre un PR.
    2.  Obtiene los cambios exactos (el "diff") del PR usando la herramienta de línea de comandos de GitHub (`gh`).
    3.  Envía este "diff" al script `backend/scripts/review_pr.py`.
    4.  Este script, a su vez, envía el diff a la API de Gemini con un prompt que le pide actuar como un revisor de código experto.
    5.  La respuesta de Gemini (la revisión del código) se captura.
    6.  Finalmente, el workflow publica la respuesta de Gemini como un comentario en el Pull Request para que los desarrolladores la vean.

### 3.2. Clasificación Automática de Issues (`issue_triage.yml`)

*   **Propósito:** Ayuda a gestionar y organizar las nuevas "issues" (tareas, bugs, etc.) que se crean. Gemini lee el título y la descripción de la issue y le asigna automáticamente etiquetas de tipo (`bug`, `feature`, `docs`) y de prioridad (`low`, `medium`, `high`).
*   **Disparador (Trigger):** Se ejecuta cada vez que se **crea o reabre una Issue**.
*   **Funcionamiento:**
    1.  Cuando un usuario crea una nueva issue, el workflow se inicia.
    2.  Extrae el título y el cuerpo de la issue.
    3.  Llama al script `backend/scripts/classify_issue.py`, pasándole el título y el cuerpo.
    4.  El script pide a Gemini que analice el texto y devuelva una etiqueta y una prioridad en formato JSON.
    5.  El workflow recibe esta respuesta y utiliza la herramienta `gh` para añadir las etiquetas correspondientes (`bug`, `priority: high`, etc.) a la issue.

### 3.3. Generación Automática de Documentación (`documentation.yml`)

*   **Propósito:** Mantiene el fichero principal de documentación del proyecto (`DOCUMENTACION_PROYECTO.md`) siempre actualizado.
*   **Disparador (Trigger):** Se ejecuta cada vez que se hace un **push (una subida de código) a la rama `main`**.
*   **Funcionamiento:**
    1.  Tras una actualización en la rama `main`, el workflow se pone en marcha.
    2.  Ejecuta el script `backend/scripts/generate_docs.py`.
    3.  Este script analiza la estructura actual del proyecto y utiliza Gemini para generar una descripción actualizada y completa del mismo en formato Markdown.
    4.  El script sobreescribe el fichero `DOCUMENTACION_PROYECTO.md` con el nuevo contenido.
    5.  Finalmente, el workflow crea un nuevo commit con el fichero actualizado y lo sube al repositorio automáticamente, bajo el nombre del autor "Gemini Bot".

### 3.4. Borrador Automático de Notas de Release (`release-drafter.yml`)

*   **Propósito:** Simplifica el proceso de creación de nuevas versiones (releases). Automáticamente redacta un borrador de las "release notes" (notas de la versión) basado en los cambios realizados desde la última versión.
*   **Disparador (Trigger):** Se ejecuta cuando se crea un nuevo **tag** (etiqueta de versión, ej. `v1.2.0`) o manualmente.
*   **Funcionamiento:**
    1.  Al crear un tag, el workflow se activa.
    2.  Identifica el tag anterior para saber desde qué punto debe recopilar los cambios.
    3.  Ejecuta el script `backend/scripts/generate_release_notes.py`, que recopila los commits entre los dos tags.
    4.  Envía esta lista de cambios a Gemini y le pide que genere un resumen amigable para las notas de la versión.
    5.  Utiliza una action pre-hecha (`actions/create-release`) para crear un **borrador** de una nueva release en GitHub, rellenando el cuerpo con las notas generadas por Gemini.

### 3.5. Linter de Calidad de Código (`linter.yml`)

*   **Propósito:** Asegura que todo el código nuevo que se añade al proyecto sigue unos estándares de calidad y estilo. No usa Gemini, pero es una pieza clave de la automatización.
*   **Disparador (Trigger):** Se ejecuta en cada **Pull Request** que modifica código en las carpetas `backend/` o `frontend/`.
*   **Funcionamiento:**
    1.  El workflow tiene dos trabajos (jobs) que se ejecutan en paralelo: uno para el backend (Python) y otro para el frontend (JavaScript).
    2.  **Backend:** Instala las dependencias de Python y ejecuta la herramienta `ruff`, un linter extremadamente rápido que busca errores y problemas de estilo en el código Python.
    3.  **Frontend:** Instala las dependencias de Node.js y ejecuta `npm run lint`, que normalmente invoca a `ESLint` para revisar el código JavaScript/React.
    4.  Si cualquiera de estos linters encuentra un error, el workflow falla y GitHub lo marca con una `X` roja en el Pull Request, impidiendo que se pueda mergear código de mala calidad.

## 4. ¿Cómo Reutilizar Estas Acciones en Otros Proyectos?

Una de las preguntas más importantes es: ¿puedo usar todo este trabajo en mis otros proyectos? La respuesta es un rotundo **sí**. La reutilización es uno de los pilares de GitHub Actions.

No necesitas empezar de cero. La estrategia recomendada es copiar los workflows y los scripts a tu nuevo proyecto y adaptarlos. A continuación te explicamos el nivel de esfuerzo que requiere cada uno.

### Guía de Reutilización por Workflow

*   **Linter de Código (`linter.yml`)**
    *   **Nivel de Reutilización:** Muy Alto.
    *   **Adaptación:** Solo necesitas cambiar las rutas de las carpetas (`backend/`, `frontend/`) si tu nuevo proyecto tiene una estructura diferente.

*   **Borrador de Releases (`release-drafter.yml`)**
    *   **Nivel de Reutilización:** Muy Alto.
    *   **Adaptación:** El workflow funciona para cualquier proyecto que use tags de Git. Solo te recomendamos ajustar el prompt dentro del script `generate_release_notes.py` para que el tono de las notas de release coincida con tu nuevo proyecto.

*   **Clasificación de Issues (`issue_triage.yml`)**
    *   **Nivel de Reutilización:** Alto.
    *   **Adaptación:** La lógica es reutilizable, pero necesitarás ajustar el "cerebro" (el prompt de Gemini en `classify_issue.py`) para que use las etiquetas (`bug`, `mejora`, etc.) y prioridades que tengan sentido en tu nuevo proyecto.

*   **Revisión de Pull Requests (`pr-review.yml`)**
    *   **Nivel de Reutilización:** Medio-Alto.
    *   **Adaptación:** El prompt en `review_pr.py` es clave. Deberás modificarlo para que Gemini se comporte como un experto en las tecnologías de tu nuevo proyecto (por ejemplo, Go y Vue.js en lugar de Python y React).

*   **Generación de Documentación (`documentation.yml`)**
    *   **Nivel de Reutilización:** Medio.
    *   **Adaptación:** Este es el más específico. Necesitarás reescribir partes del script `generate_docs.py` para que entienda la arquitectura de tu nuevo proyecto y crear un prompt completamente nuevo para que la documentación generada sea coherente y útil.

### Conclusión: La Regla de Oro es "Copiar y Adaptar"

Como puedes ver, la estructura base de los workflows (leer secretos, ejecutar scripts, interactuar con la API de GitHub) ya está resuelta. **Nunca empieces desde cero.** Copia los ficheros `.github/workflows` y la carpeta `backend/scripts` en tu nuevo proyecto y sigue esta guía para adaptarlos. Ahorrarás una enorme cantidad de tiempo y esfuerzo.