.PHONY: help portfolio portfolio-build portfolio-serve microeconomics install-portfolio install-microeconomics install

PORTFOLIO_DIR := portfolio
MICRO_DIR     := microeconomics-games
PORTFOLIO_PORT ?= 8000
MICRO_PORT     ?= 8501

help:
	@echo "Cibles disponibles :"
	@echo "  make install                Installe les dépendances des deux projets (via uv)"
	@echo "  make install-portfolio      Installe les dépendances du portfolio"
	@echo "  make install-microeconomics Installe les dépendances du projet Streamlit"
	@echo "  make portfolio              Génère et sert le portfolio sur http://localhost:$(PORTFOLIO_PORT)"
	@echo "  make portfolio-build        Régénère uniquement les fichiers HTML du portfolio"
	@echo "  make portfolio-serve        Sert le portfolio sans le régénérer"
	@echo "  make microeconomics         Lance l'app Streamlit sur http://localhost:$(MICRO_PORT)"

install: install-portfolio install-microeconomics

install-portfolio:
	cd $(PORTFOLIO_DIR) && uv venv && uv pip install -r requirements.txt

install-microeconomics:
	cd $(MICRO_DIR) && uv venv && uv pip install -r requirements.txt

portfolio-build:
	cd $(PORTFOLIO_DIR) && uv run python generate_portfolio.py

portfolio-serve:
	cd $(PORTFOLIO_DIR) && uv run python -m http.server $(PORTFOLIO_PORT)

portfolio: portfolio-build portfolio-serve

microeconomics:
	cd $(MICRO_DIR) && uv run streamlit run app.py --server.port $(MICRO_PORT)
