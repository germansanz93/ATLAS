from flask import Flask, request
import logging
import sys

app = Flask(__name__)

# Configurar logs para que salgan por stdout (importante para K8s)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

@app.route('/')
def hello():
    logging.info("Peticion recibida en root")
    return "Todo bien por aqui!"

@app.route('/critical-feature')
def critical():
    logging.info("Iniciando proceso critico...")
    # Simulamos una logica compleja
    user_id = request.args.get('id')
    
    if not user_id:
        logging.warning("No user_id provided")
        return "Falta ID", 400

    # Obtener el tier de los argumentos de la solicitud
    tier_str = request.args.get('tier')

    if not tier_str:
        logging.warning("No tier provided")
        return "Falta Tier", 400

    try:
        tier = int(tier_str)
    except ValueError:
        logging.warning(f"Valor de tier invalido: {tier_str}")
        return "Tier invalido. Debe ser un numero entero.", 400

    # Validar que tier no sea cero antes de la division
    if tier == 0:
        logging.warning("Intento de division por cero con tier = 0.")
        return "Operacion no permitida con Tier 0", 400

    try:
        # Calculamos un descuento. Ya hemos validado que tier no es 0.
        result = 100 / tier
        return f"Resultado: {result}"
    except Exception as e:
        # Este bloque ahora solo atraparia errores inesperados, no la division por cero.
        logging.error("Excepcion inesperada en calculo de tier", exc_info=True)
        return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
