.PHONY: help install run test lint format clean docs coverage all

help:
	@echo "Music Recommendation System - Available Commands"
	@echo ""
	@echo "  make install       Install dependencies"
	@echo "  make run           Run the CLI application"
	@echo "  make api           Run the Flask API server"
	@echo "  make test          Run all tests"
	@echo "  make coverage      Generate test coverage report"
	@echo "  make lint          Run linting checks"
	@echo "  make format        Format code with black"
	@echo "  make docs          Show documentation"
	@echo "  make clean         Remove build artifacts"
	@echo "  make all           Install, format, lint, and test"
	@echo ""

install:
	pip install -r requirements.txt

run:
	cd src && python main.py

api:
	cd src && python -m api.app

test:
	pytest tests/ -v

coverage:
	pytest tests/ --cov=src --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	flake8 src/ tests/

format:
	black src/ tests/

docs:
	@echo "📚 Available Documentation:"
	@echo ""
	@echo "  QUICKSTART.md           - 5-minute quick start guide"
	@echo "  IMPLEMENTATION_GUIDE.md - Detailed feature documentation"
	@echo "  README.md               - Project overview"
	@echo ""
	@echo "Open these files in your editor for more information."

all: clean install format lint test
	@echo "✅ All tasks completed!"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	@echo "✅ Cleaned up build artifacts"
