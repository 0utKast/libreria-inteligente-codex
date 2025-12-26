import os
from PIL import Image
from pathlib import Path

# Configuración
COVERS_DIR = Path("backend/static/covers")
MAX_WIDTH = 400
QUALITY = 80

def optimize_image(file_path):
    try:
        with Image.open(file_path) as img:
            original_size = os.path.getsize(file_path)
            
            # Convertir a RGB si es necesario (para JPEG/PNG)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            # Redimensionar si es más ancho que MAX_WIDTH
            if img.width > MAX_WIDTH:
                ratio = MAX_WIDTH / float(img.width)
                new_height = int(float(img.height) * ratio)
                img = img.resize((MAX_WIDTH, new_height), Image.Resampling.LANCZOS)
            
            # Guardar con compresión
            img.save(file_path, "JPEG", quality=QUALITY, optimize=True)
            new_size = os.path.getsize(file_path)
            
            reduction = (original_size - new_size) / original_size * 100
            print(f"Optimizado: {file_path.name} | {original_size/1024:.1f}KB -> {new_size/1024:.1f}KB ({reduction:.1f}% ahorro)")
            return True
    except Exception as e:
        print(f"Error optimizando {file_path.name}: {e}")
        return False

def main():
    if not COVERS_DIR.exists():
        print(f"No se encontró el directorio: {COVERS_DIR}")
        return

    print(f"Iniciando optimización de portadas en {COVERS_DIR}...")
    count = 0
    optimized = 0
    
    for file in COVERS_DIR.glob("*"):
        if file.suffix.lower() in (".png", ".jpg", ".jpeg"):
            count += 1
            if optimize_image(file):
                optimized += 1
    
    print(f"\nProceso finalizado. {optimized}/{count} imágenes optimizadas.")

if __name__ == "__main__":
    main()
