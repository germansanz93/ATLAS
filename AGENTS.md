# Guía de Estilo y Arquitectura para Agentes IA

Eres un ingeniero colaborando en el proyecto ATLAS. Sigue estas reglas estrictas al generar código:

## 1. Estilo de Código
- **Docstrings:** Todas las funciones deben tener un docstring explicativo.
- **Tipado:** Usa Type Hints de Python donde sea posible.
- **Comentarios:** Agrega un comentario que diga `# FIXED BY AIOPS AGENT` justo encima de la corrección.

## 2. Gestión de Errores
- No uses `try/except` genéricos (Exception) si puedes capturar el error específico (ej: ZeroDivisionError).
- Devuelve mensajes de error en formato JSON, no texto plano, si es una API.

## 3. Seguridad
- Valida siempre los inputs antes de procesarlos.