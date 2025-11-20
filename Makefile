# Variables
IMAGE_NAME = buggy-app
TAG = v1
APP_DIR = buggy-app
FULL_IMAGE = $(IMAGE_NAME):$(TAG)

# Detectar contexto actual de Kubernetes
K8S_CONTEXT := $(shell kubectl config current-context 2>/dev/null)

.PHONY: all build load deploy clean tunnel logs setup-infra help

# --- Ayuda (Por defecto) ---
help: ## Muestra todos los comandos disponibles
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# --- Flujo Principal ---

all: build load deploy ## Construye, carga (si es necesario) y despliega la app
	@echo "🎉 Todo listo! Usa 'make tunnel' para probar la app."

build: ## Construye la imagen Docker de la aplicación
	@echo "🏗️  Construyendo imagen $(FULL_IMAGE)..."
	docker build -t $(FULL_IMAGE) ./$(APP_DIR)

load: ## Detecta el cluster y carga la imagen (Minikube/Kind)
	@echo "🔍 Contexto K8s detectado: $(K8S_CONTEXT)"
	@if echo "$(K8S_CONTEXT)" | grep -q "minikube"; then \
		echo "🚚 Cargando imagen en Minikube..."; \
		minikube image load $(FULL_IMAGE); \
	elif echo "$(K8S_CONTEXT)" | grep -q "kind"; then \
		echo "🚚 Cargando imagen en Kind..."; \
		kind load docker-image $(FULL_IMAGE) --name $$(echo $(K8S_CONTEXT) | sed 's/kind-//'); \
	else \
		echo "⚓ No se requiere carga manual para este contexto (Docker Desktop/Remoto)."; \
	fi

deploy: ## Aplica los manifiestos de K8s
	@echo "🚀 Desplegando en Kubernetes..."
	kubectl apply -f $(APP_DIR)/k8s-manifest.yaml

clean: ## Borra el despliegue de la app del cluster
	@echo "🧹 Limpiando recursos de la app..."
	kubectl delete -f $(APP_DIR)/k8s-manifest.yaml --ignore-not-found=true

# --- Utilidades ---

tunnel: ## Abre un túnel para acceder a la App (http://localhost:8080)
	@echo "🔌 Abriendo túnel en http://localhost:8080 (Ctrl+C para salir)..."
	kubectl port-forward svc/buggy-app-svc 8080:80

logs: ## Muestra los logs de los pods de la app
	kubectl logs -l app=$(IMAGE_NAME) -f

# --- Infraestructura (Loki + Grafana) ---

setup-infra: ## Instala Loki y Grafana usando Helm
	@echo "📦 Configurando repositorios y Stack de Observabilidad..."
	helm repo add grafana https://grafana.github.io/helm-charts
	helm repo update
	helm upgrade --install loki grafana/loki-stack \
		--set grafana.enabled=true \
		--set promtail.enabled=true \
		--set loki.isDefault=true
	@echo "✅ Infraestructura instalada."

grafana-pass: ## Obtiene la contraseña de admin de Grafana
	@echo "🔑 Password de Grafana (User: admin):"
	@kubectl get secret loki-grafana -o jsonpath="{.data.admin-password}" | base64 --decode ; echo

grafana-tunnel: ## Abre un túnel para acceder a Grafana (http://localhost:3000)
	@echo "📊 Abriendo Grafana en http://localhost:3000 (Ctrl+C para salir)..."
	kubectl port-forward svc/loki-grafana 3000:80