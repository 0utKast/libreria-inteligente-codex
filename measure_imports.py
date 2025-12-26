import time

start = time.time()
import fitz
print(f"fitz: {time.time() - start:.4f}s")

start = time.time()
import ebooklib
from ebooklib import epub
print(f"ebooklib: {time.time() - start:.4f}s")

start = time.time()
from weasyprint import HTML, CSS
print(f"weasyprint: {time.time() - start:.4f}s")

start = time.time()
import chromadb
print(f"chromadb: {time.time() - start:.4f}s")

start = time.time()
import google.generativeai as genai
print(f"genai: {time.time() - start:.4f}s")
