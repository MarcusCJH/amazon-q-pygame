.PHONY: help install test lint format clean run dev-install

help:
	@echo "Available commands:"
	@echo "  install     - Install the package"
	@echo "  dev-install - Install in development mode with dev dependencies"
	@echo "  test        - Run tests with coverage"
	@echo "  lint        - Run linting checks"
	@echo "  format      - Format code with black"
	@echo "  clean       - Clean build artifacts"
	@echo "  run         - Run the game"

install:
	pip install -e .

dev-install:
	pip install -e .[dev]

test:
	python scripts/run_tests.py

lint:
	flake8 src tests --max-line-length=88
	black --check src tests

format:
	black src tests

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	python main.py

play:
	python main.py