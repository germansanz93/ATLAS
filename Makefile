# Variables
IMAGE_NAME = buggy-app
TAG = v1
APP_DIR = buggy-app

.PHONY: all build load deploy clean tunnel logs infrastructure

# --- Comandos Principales ---

# "make all" construye y despliega todo de una vez
all: build deploy

# 1. Construir la imagen Docker
build:
	@echo "🏗️  Construyendo imagen Docker..."
	docker build -t $(IMAGE_NAME):$(TAG) ./$(APP_DIR)

# 2. (Opcional) Cargar imagen si usas Kind o Minikube
# Si usas Docker Desktop, ignora este paso.
load-kind:
	@echo "🚚 Cargando imagen en Kind..."
	kind load docker-image $(IMAGE_NAME):$(TAG)

load-minikube:
	@echo "🚚 Cargando imagen en Minikube..."
	minikube image load $(IMAGE_NAME):$(TAG)

# 3. Desplegar la app en Kubernetes
deploy:
	@echo "🚀 Desplegando en Kubernetes..."
	kubectl apply -f $(APP_DIR)/k8s-manifest.yaml

# 4. Borrar el despliegue (para reiniciar limpio)
clean:
	@echo "🧹 Limpiando recursos..."
	kubectl delete -f $(APP_DIR)/k8s-manifest.yaml --ignore-not-found=true

# --- Utilidades ---

# Crear el túnel para ver la app (se queda corriendo)
tunnel:
	@echo "🔌 Abriendo túnel en http://localhost:8080 ..."
	kubectl port-forward svc/buggy-app-svc 8080:80

# Ver logs rápidos de los pods
logs:
	kubectl logs -l app=$(IMAGE_NAME) -f

# --- Infraestructura (Loki + Grafana) ---
# Esto lo usaremos en el siguiente paso, pero ya lo dejamos listo.
setup-infra:
	@echo "📦 Instalando Repositorios de Helm..."
	helm repo add grafana https://grafana.github.io/helm-charts
	helm repo update
	@echo "📦 Instalando Loki Stack (Loki, Promtail, Grafana)..."
	helm upgrade --install loki grafana/loki-stack \
		--set grafana.enabled=true \
		--set promtail.enabled=true \
		--set loki.isDefault=true
	@echo "✅ Infraestructura instalada."

get-grafana-pass:
	@echo "🔑 Tu password de Grafana (usuario: admin):"
	@kubectl get secret loki-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo

tunnel-grafana:
	@echo "📊 Abriendo Grafana en http://localhost:3000 ..."
	kubectl port-forward svc/loki-grafana 3000:80