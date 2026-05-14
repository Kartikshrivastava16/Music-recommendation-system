.PHONY: help install venv run test lint format clean

help:
	@echo "Music Recommendation System - Available Commands"
	@echo ""
	@echo "  make install       Install dependencies"
	@echo "  make venv          Create virtual environment"
	@echo "  make run           Run the application"
	@echo "  make api           Run the API server"
	@echo "  make test          Run tests"
	@echo "  make lint          Run linting checks"
	@echo "  make format        Format code with black"
	@echo "  make clean         Remove build artifacts"
	@echo ""

venv:
	python -m venv venv

install:
	pip install -r requirements.txt

run:
	python src/main.py

api:
	python src/api/app.py

test:
	pytest tests/ -v

lint:
	flake8 src/ tests/

format:
	black src/ tests/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
