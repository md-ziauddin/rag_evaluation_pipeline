#!/usr/bin/env bash
# Developer Verification Script: Runs linter, formatter, typecheck, security audit, and test suite.

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Prefer uv run if available, fallback to active python environment binaries
RUNNER="uv run"
if ! command -v uv &> /dev/null; then
    RUNNER=""
fi

echo -e "${GREEN}=== 1/5 Running Ruff Linter ===${NC}"
$RUNNER ruff check .

echo -e "\n${GREEN}=== 2/5 Running Ruff Formatter Check ===${NC}"
$RUNNER ruff format --check .

echo -e "\n${GREEN}=== 3/5 Running Static Type Checker (Mypy) ===${NC}"
$RUNNER mypy src/

echo -e "\n${GREEN}=== 4/5 Running Security Audit (Bandit) ===${NC}"
$RUNNER bandit -r src/ -q

echo -e "\n${GREEN}=== 5/5 Running Automated Tests (Pytest) ===${NC}"
$RUNNER pytest -v

echo -e "\n${GREEN}===========================================${NC}"
echo -e "${GREEN}  ALL QUALITY GATES PASSED SUCCESSFULLY!   ${NC}"
echo -e "${GREEN}===========================================${NC}"
