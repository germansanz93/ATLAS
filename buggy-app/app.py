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

    # Ahora obtenemos el tier de los parametros de la peticion
    tier_str = request.args.get('tier')
    
    if not tier_str:
        logging.warning(f"No tier provided for user_id: {user_id}")
        return "Falta parametro 'tier'", 400

    try:
        tier = int(tier_str)
        
        # Validamos que el tier no sea cero antes de la division
        if tier == 0:
            logging.warning(f"Attempted division by zero with tier=0 for user_id: {user_id}")
            return "El tier no puede ser cero para esta operación", 400

        result = 100 / tier
        return f"Resultado: {result}"
    except ValueError:
        # Capturamos errores si 'tier' no es un número
        logging.warning(f"Invalid tier value '{tier_str}' provided for user_id: {user_id}")
        return "El tier debe ser un número entero válido", 400
    except Exception as e:
        # Logueamos cualquier otra excepcion critica con stacktrace completo
        logging.error(f"Excepción critica en calculo de tier para user_id: {user_id}", exc_info=True)
        return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)