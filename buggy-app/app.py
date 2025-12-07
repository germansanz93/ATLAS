from flask import Flask, request, jsonify
import logging
import sys
from typing import Tuple, Union, Dict, Any

app = Flask(__name__)

# Configurar logs para que salgan por stdout (importante para K8s)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

@app.route('/')
def hello() -> Tuple[str, int]:
    """
    Maneja las peticiones al endpoint raíz.
    Devuelve un mensaje de éxito simple.
    """
    logging.info("Peticion recibida en root")
    # FIXED BY AIOPS AGENT
    # El endpoint raiz no devuelve un error, por lo que no necesita ser JSON.
    return "Todo bien por aqui!", 200

@app.route('/critical-feature')
def critical() -> Tuple[Dict[str, Any], int]:
    """
    Maneja las peticiones al endpoint de característica crítica.
    Calcula un resultado basado en el ID del usuario y el nivel (tier),
    con validación de entrada robusta y manejo de errores.
    Previene la división por cero y proporciona respuestas JSON.
    """
    logging.info("Iniciando proceso critico...")

    # Validar user_id
    user_id: Union[str, None] = request.args.get('id')
    # FIXED BY AIOPS AGENT
    if not user_id:
        logging.warning("Validation Error: No user_id provided for critical feature.")
        return jsonify({"error": "Missing 'id' parameter."}), 400

    # Validar tier
    tier_str: Union[str, None] = request.args.get('tier')
    # FIXED BY AIOPS AGENT
    if not tier_str:
        logging.warning(f"Validation Error: No 'tier' provided for user_id: {user_id}")
        return jsonify({"error": "Missing 'tier' parameter."}), 400

    try:
        # FIXED BY AIOPS AGENT
        # Validación de entrada: Asegurar que tier sea un entero.
        tier: int = int(tier_str)
    except ValueError:
        logging.warning(f"Validation Error: Invalid 'tier' format '{tier_str}' for user_id: {user_id}")
        # FIXED BY AIOPS AGENT
        # Devolver mensaje de error en formato JSON.
        return jsonify({"error": "Invalid 'tier' format. Must be an integer."}), 400

    # FIXED BY AIOPS AGENT
    # Seguridad y Prevención de Errores: Validar que tier no sea cero antes del cálculo.
    if tier == 0:
        logging.error(f"Logic Error: Attempted division by zero with tier=0 for user_id: {user_id}")
        # FIXED BY AIOPS AGENT
        # Devolver mensaje de error en formato JSON.
        return jsonify({"error": "Tier cannot be zero for this calculation."}), 400

    # Simulamos una lógica compleja - ahora con entradas validadas.
    # FIXED BY AIOPS AGENT
    # El "ERROR INTENCIONAL" original con tier=0 ahora se previene con la validación.
    # No es necesario un try/except genérico para una división simple después de una validación exhaustiva.
    result: float = 100 / tier
    logging.info(f"Critical process completed for user_id: {user_id}, tier: {tier}, result: {result}")
    return jsonify({"user_id": user_id, "tier": tier, "result": result}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
