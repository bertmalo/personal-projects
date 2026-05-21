.PHONY: help microeconomics install-microeconomics install

MICRO_DIR     := microeconomics-games
MICRO_PORT    ?= 8501

help:
	@echo "Cibles disponibles :"
	@echo "  make install                Installe les dépendances (via uv)"
	@echo "  make install-microeconomics Installe les dépendances du projet Streamlit"
	@echo "  make microeconomics         Lance l'app Streamlit sur http://localhost:$(MICRO_PORT)"

install: install-microeconomics

install-microeconomics:
	cd $(MICRO_DIR) && uv venv && uv pip install -r requirements.txt

microeconomics:
	cd $(MICRO_DIR) && uv run streamlit run app.py --server.port $(MICRO_PORT)
