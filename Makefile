.PHONY: test clean build help

# Default target
help:
	@echo "Available targets:"
	@echo "  test          - Run all tests"
	@echo "  build         - Build the collection"
	@echo "  clean         - Clean build artifacts"
	@echo "  lint          - Run ruff checks"
	@echo "  format        - Format code"

# Build the collection
build:
	ansible-galaxy collection build

# Clean build artifacts
clean:
	rm -f *.tar.gz
	rm -rf tests/__pycache__/

# Run linting
lint:
	uv run ruff check .
	uv run ruff format --check .

# Format code
format:
	uv run ruff format .

# Run tests
test:
	cd tests && python3 run_tests.py
