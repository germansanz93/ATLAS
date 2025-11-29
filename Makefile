# --- Configuración de Shell (Evita error de trap) ---
SHELL := /bin/bash

# --- Variables ---
IMAGE_NAME = buggy-app
TAG = v1
APP_DIR = buggy-app
N8N_DIR = n8n
FULL_IMAGE = $(IMAGE_NAME):$(TAG)
K8S_CONTEXT := $(shell kubectl config current-context 2>/dev/null)

.PHONY: all setup-infra secrets build load deploy wait-resources info connect clean help

# --- COMANDO MAESTRO ---
all: setup-infra secrets build load deploy wait-resources info ## 🚀 Instala TODO
	@echo "✅ Instalación completa. Ejecuta 'make connect' para abrir la conexión."

# --- Pasos Individuales ---

setup-infra:
	@echo "📦 [1/5] Instalando Stack de Observabilidad (Loki/Grafana)..."
	@if [ ! -f grafana-values.yaml ]; then echo "❌ Faltan grafana-values.yaml"; exit 1; fi
	@helm repo add grafana https://grafana.github.io/helm-charts > /dev/null 2>&1
	@helm repo update > /dev/null 2>&1
	@# Aquí inyectamos la configuración automática
	@helm upgrade --install loki grafana/loki-stack \
		--set promtail.enabled=true \
		--set loki.isDefault=false \
		-f grafana-values.yaml > /dev/null 2>&1 || echo "⚠️  Warning ignorado."
secrets:
	@echo "PwD [2/6] Generando Configuración y Secretos..."
	@if [ ! -f .env ]; then echo "❌ ERROR: No existe el archivo .env"; exit 1; fi
	@# 1. Secretos (.env)
	@kubectl create secret generic n8n-secrets --from-env-file=.env --dry-run=client -o yaml | kubectl apply -f - > /dev/null 2>&1
	@# 2. ConfigMap (Workflow JSON)
	@kubectl create configmap n8n-import-data --from-file=$(N8N_DIR)/workflow.json --dry-run=client -o yaml | kubectl apply -f - > /dev/null 2>&1

build:
	@echo "🏗️  [2/5] Construyendo imagen Docker..."
	@docker build -t $(FULL_IMAGE) ./$(APP_DIR) > /dev/null 2>&1

load:
	@echo "🚚 [3/5] Verificando destino de la imagen ($(K8S_CONTEXT))..."
	@if echo "$(K8S_CONTEXT)" | grep -q "minikube"; then \
		minikube image load $(FULL_IMAGE); \
	elif echo "$(K8S_CONTEXT)" | grep -q "kind"; then \
		kind load docker-image $(FULL_IMAGE) --name $$(echo $(K8S_CONTEXT) | sed 's/kind-//'); \
	fi

deploy:
	@echo "🚀 [4/5] Desplegando App y n8n..."
	@kubectl apply -f $(APP_DIR)/k8s-manifest.yaml > /dev/null 2>&1
	@# Aquí es donde fallaba antes: ahora sí incluimos n8n
	@kubectl apply -f $(N8N_DIR)/n8n-manifest.yaml > /dev/null 2>&1

wait-resources:
	@echo "⏳ [5/5] Esperando a que los servicios estén listos..."
	@# Esperar App Buggy
	@echo "   ...esperando buggy-app..."
	@kubectl wait --for=condition=ready pod -l app=$(IMAGE_NAME) --timeout=120s > /dev/null 2>&1
	@# Esperar n8n (puede tardar en bajar la imagen)
	@echo "   ...esperando n8n (esto puede tardar la primera vez)..."
	@kubectl wait --for=condition=ready pod -l app=n8n --timeout=300s > /dev/null 2>&1
	@# Esperar Secret Grafana
	@echo "   ...esperando secreto de Grafana..."
	@until kubectl get secret loki-grafana > /dev/null 2>&1; do sleep 2; done

info:
	$(eval GRAFANA_PASS := $(shell kubectl get secret loki-grafana -o jsonpath="{.data.admin-password}" | base64 --decode))
	@echo ""
	@echo "============================================================"
	@echo "🎉  ENTORNO AIOPS LISTO"
	@echo "============================================================"
	@echo "📱 Buggy App:     http://localhost:8080"
	@echo "🧠 n8n Workflow:  http://localhost:5678"
	@echo "📊 Grafana:       http://localhost:3000"
	@echo "   User: admin / Pass: $(GRAFANA_PASS)"
	@echo "============================================================"
	@echo "👉  Ejecuta 'make connect' para empezar."

# --- Utilidades ---

connect: ## Abre los 3 túneles simultáneamente
	@echo "🔌 Abriendo túneles... (Presiona Ctrl+C para detener)"
	@echo "   - App:     http://localhost:8080"
	@echo "   - Grafana: http://localhost:3000"
	@echo "   - n8n:     http://localhost:5678"
	@(trap 'kill 0' INT; \
	kubectl port-forward svc/buggy-app-svc 8080:80 > /dev/null 2>&1 & \
	kubectl port-forward svc/loki-grafana 3000:80 > /dev/null 2>&1 & \
	kubectl port-forward svc/n8n-svc 5678:80 > /dev/null 2>&1 & \
	wait)

logs: ## Ver logs de la app
	kubectl logs -l app=$(IMAGE_NAME) -f

clean: ## 🛑 BORRADO TOTAL
	@echo "🧹 Iniciando limpieza profunda..."
	@kubectl delete -f $(APP_DIR)/k8s-manifest.yaml --ignore-not-found=true > /dev/null 2>&1
	@kubectl delete -f $(N8N_DIR)/n8n-manifest.yaml --ignore-not-found=true > /dev/null 2>&1
	@helm uninstall loki --ignore-not-found=true > /dev/null 2>&1
	@kubectl delete secret loki-grafana --ignore-not-found=true > /dev/null 2>&1
	@kubectl delete secret sh.helm.release.v1.loki.v1 --ignore-not-found=true > /dev/null 2>&1
	@kubectl delete pvc -l release=loki --ignore-not-found=true > /dev/null 2>&1
	@kubectl delete pvc n8n-pvc --ignore-not-found=true > /dev/null 2>&1
	@echo "✨ Cluster limpio."

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'