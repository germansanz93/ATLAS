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

    # Obtener el valor de 'tier' de los argumentos de la peticion
    tier_str = request.args.get('tier')

    if not tier_str:
        logging.warning("No tier provided")
        return "Falta el parametro 'tier'", 400

    try:
        tier = int(tier_str) # Convertir 'tier' a entero
        
        if tier == 0:
            logging.warning(f"Intento de division por cero para user_id={user_id} con tier={tier_str}")
            return "El parametro 'tier' no puede ser cero", 400

        result = 100 / tier
        logging.info(f"Calculo de tier exitoso para user_id={user_id}, tier={tier}: {result}")
        return f"Resultado: {result}"
    except ValueError:
        logging.warning(f"Valor invalido para 'tier': {tier_str}")
        return "El parametro 'tier' debe ser un numero entero valido", 400
    except Exception as e:
        # Logueamos el error con stacktrace completo
        logging.error(f"Excepcion critica en calculo de tier para user_id={user_id}, tier_str={tier_str}", exc_info=True)
        return "Internal Server Error", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
