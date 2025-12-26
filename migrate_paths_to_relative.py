import sqlite3
import os
from pathlib import Path

def migrate():
    db_path = Path("library.db").resolve()
    if not db_path.exists():
        print(f"No se encontró la base de datos en {db_path}")
        return

    print(f"Normalizando rutas en {db_path} mediante reconstrucción de tabla...")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. Obtener todos los datos actuales
        cursor.execute("SELECT id, title, author, category, cover_image_url, file_path FROM books")
        rows = cursor.fetchall()
        
        normalized_data = []
        seen_paths = set()

        for row in rows:
            book_id, title, author, category, cover_url, file_path = row
            
            # Normalizar file_path
            filename = os.path.basename(file_path)
            new_file_path = f"books/{filename}"
            
            # Manejar colisiones
            if new_file_path in seen_paths:
                name, ext = os.path.splitext(filename)
                counter = 1
                while f"books/{name}_{counter}{ext}" in seen_paths:
                    counter += 1
                new_file_path = f"books/{name}_{counter}{ext}"
                print(f"Colisión corregida: {filename} -> {new_file_path}")
            
            seen_paths.add(new_file_path)

            # Normalizar cover_url
            if cover_url:
                cover_filename = os.path.basename(cover_url.split('?')[0])
                new_cover_url = f"static/covers/{cover_filename}"
            else:
                new_cover_url = cover_url
            
            # Guardamos todo excepto el ID (que se autoincrementará o lo preservaremos si es necesario)
            # Para mayor fidelidad, preservaremos el ID
            normalized_data.append((book_id, title, author, category, new_cover_url, new_file_path))

        # 2. Reconstruir la tabla
        cursor.execute("BEGIN TRANSACTION")
        
        # Primero borramos todo
        cursor.execute("DELETE FROM books")
        
        # Luego insertamos los nuevos
        cursor.executemany("""
            INSERT INTO books (id, title, author, category, cover_image_url, file_path)
            VALUES (?, ?, ?, ?, ?, ?)
        """, normalized_data)
        
        conn.commit()
        print(f"Migración completada con éxito. {len(normalized_data)} libros procesados.")

    except Exception as e:
        conn.rollback()
        print(f"Error fatal durante la migración: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()
