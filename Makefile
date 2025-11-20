# --- Variables ---
IMAGE_NAME = buggy-app
TAG = v1
APP_DIR = buggy-app
FULL_IMAGE = $(IMAGE_NAME):$(TAG)
K8S_CONTEXT := $(shell kubectl config current-context 2>/dev/null)

.PHONY: all setup-infra build load deploy wait-resources info connect clean help

# --- COMANDO MAESTRO ---
all: setup-infra build load deploy wait-resources info ## 🚀 Instala TODO y muestra credenciales
	@echo "✅ Instalación completa. Ejecuta 'make connect' para abrir la conexión."

# --- Pasos Individuales ---

setup-infra:
	@echo "📦 [1/5] Instalando Stack de Observabilidad (Loki/Grafana)..."
	@helm repo add grafana https://grafana.github.io/helm-charts > /dev/null 2>&1
	@helm repo update > /dev/null 2>&1
	@helm upgrade --install loki grafana/loki-stack \
		--set grafana.enabled=true \
		--set promtail.enabled=true \
		--set loki.isDefault=true > /dev/null 2>&1 || echo "⚠️  Loki ya estaba instalado o warning ignorado."

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
	@echo "🚀 [4/5] Desplegando aplicaciones en K8s..."
	@kubectl apply -f $(APP_DIR)/k8s-manifest.yaml > /dev/null 2>&1

wait-resources:
	@echo "⏳ [5/5] Esperando a que los servicios estén listos (puede tardar unos segundos)..."
	@# Esperamos a que el pod de la app esté running
	@kubectl wait --for=condition=ready pod -l app=$(IMAGE_NAME) --timeout=120s > /dev/null 2>&1
	@# Esperamos a que el secreto de grafana exista
	@echo "   ...esperando secreto de Grafana..."
	@until kubectl get secret loki-grafana > /dev/null 2>&1; do sleep 2; done

info:
	$(eval GRAFANA_PASS := $(shell kubectl get secret loki-grafana -o jsonpath="{.data.admin-password}" | base64 --decode))
	@echo ""
	@echo "============================================================"
	@echo "🎉  ENTORNO LISTO PARA LA DEMO"
	@echo "============================================================"
	@echo "📱 App Buggy:     http://localhost:8080"
	@echo "📊 Grafana:       http://localhost:3000"
	@echo "👤 User Grafana:  admin"
	@echo "🔑 Pass Grafana:  $(GRAFANA_PASS)"
	@echo "============================================================"
	@echo "👉  AHORA: Ejecuta 'make connect' en esta terminal para abrir el acceso."
	@echo "============================================================"

# --- Utilidades ---

connect: ## Abre los túneles para App y Grafana simultáneamente
	@echo "🔌 Abriendo túneles... (Presiona Ctrl+C para detener)"
	@echo "   - App: http://localhost:8080"
	@echo "   - Grafana: http://localhost:3000"
	@(trap 'kill 0' SIGINT; \
	kubectl port-forward svc/buggy-app-svc 8080:80 > /dev/null 2>&1 & \
	kubectl port-forward svc/loki-grafana 3000:80 > /dev/null 2>&1 & \
	wait)

logs: ## Ver logs de la app
	kubectl logs -l app=$(IMAGE_NAME) -f

clean: ## 🛑 BORRADO TOTAL (App + Infra + Datos)
	@echo "🧹 Iniciando limpieza profunda..."
	@# 1. Borrar la App
	@kubectl delete -f $(APP_DIR)/k8s-manifest.yaml --ignore-not-found=true > /dev/null 2>&1
	@echo "   - App eliminada."
	
	@# 2. Desinstalar Helm Chart
	@helm uninstall loki --ignore-not-found=true > /dev/null 2>&1
	@echo "   - Helm release desinstalada."
	
	@# 3. Borrar Secretos específicos que a veces quedan
	@kubectl delete secret loki-grafana --ignore-not-found=true > /dev/null 2>&1
	@kubectl delete secret sh.helm.release.v1.loki.v1 --ignore-not-found=true > /dev/null 2>&1
	@echo "   - Secretos eliminados."

	@# 4. Borrar PVCs (Discos persistentes) - ESTO ES LO QUE FALTABA
	@# Buscamos cualquier PVC que tenga la etiqueta de release=loki
	@kubectl delete pvc -l release=loki --ignore-not-found=true > /dev/null 2>&1
	@kubectl delete pvc -l app=loki --ignore-not-found=true > /dev/null 2>&1
	@echo "   - Datos persistentes (PVCs) eliminados."
	
	@echo "✨ Cluster limpioa."

help: ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'