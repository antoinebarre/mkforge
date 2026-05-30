#!/usr/bin/env bash
set -uo pipefail

G='\033[32m'
R='\033[31m'
B='\033[1m'
N='\033[0m'
SEP='━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━'
MODE="${1:-local}"

PASS=0
FAIL=0
FAIL_NAMES=()

cleanup() {
    mkdir -p work
    find work -mindepth 1 ! -name .gitkeep -exec rm -rf {} +
}

detail_for() {
    local name=$1 log=$2
    case "$name" in
        format | format-check)
            tail -n 1 "$log" 2>/dev/null || true
            ;;
        ruff)
            grep -E 'All checks passed|Found [0-9]+ errors?' "$log" | tail -n 1 || true
            ;;
        flake8)
            local count
            count=$(grep -E '^[^:]+:[0-9]+:[0-9]+:' "$log" 2>/dev/null | wc -l | tr -d ' ')
            [ "${count:-0}" -eq 0 ] && echo "No issues" || echo "${count} violation(s)"
            ;;
        docstrings)
            tail -n 1 "$log" 2>/dev/null || true
            ;;
        typecheck)
            grep -E '^Success:|^Found [0-9]+ errors?' "$log" | tail -n 1 || true
            ;;
        metrics)
            grep -E '^Code metrics (passed|failed)' "$log" | head -n 1 || true
            ;;
        security-code)
            grep -E 'No issues identified|Issue: ' "$log" | tail -n 1 | sed 's/^[[:space:]]*//' || true
            ;;
        security-deps)
            grep -E '^No known vulnerabilities found|^Found [0-9]+ known vulnerabilities' "$log" | tail -n 1 || true
            ;;
        tests)
            local passed coverage
            passed=$(grep -oE '[0-9]+ passed' "$log" | tail -n 1 || true)
            coverage=$(awk '/^TOTAL/{print $NF}' "$log" | tail -n 1 || true)
            printf "%s%s" "${passed:-tests failed}" "${coverage:+ · coverage $coverage}"
            ;;
    esac
}

run() {
    local name=$1 log=$2
    shift 2
    printf " %-16s  " "$name"
    if "$@" >"$log" 2>&1; then
        printf "${G}✔ pass${N}"
        PASS=$((PASS + 1))
    else
        printf "${R}✘ FAIL${N}"
        FAIL=$((FAIL + 1))
        FAIL_NAMES+=("$name")
    fi
    local detail
    detail=$(detail_for "$name" "$log")
    [ -n "$detail" ] && printf "  %s" "$detail"
    printf "\n"
}

print_failures() {
    if [ "${#FAIL_NAMES[@]}" -eq 0 ]; then
        return
    fi
    for name in "${FAIL_NAMES[@]}"; do
        local log="work/${name}.log"
        printf "\n%s\n-- %s details --\n" "$SEP" "$name"
        [ -f "$log" ] && cat "$log"
    done
}

cleanup
mkdir -p work

printf "\n${B}Running %s checks${N}\n\n" "$MODE"
printf "${B}%s${N}\n" "$SEP"
printf "${B} %-16s  %-10s  %s${N}\n" "Check" "Status" "Details"
printf "${B}%s${N}\n" "$SEP"

if [ "$MODE" = "--ci" ]; then
    run format-check work/format-check.log uv run ruff format --check src tests scripts
else
    run format work/format.log uv run ruff format src tests scripts
fi
run ruff work/ruff.log uv run ruff check src tests scripts
run flake8 work/flake8.log uv run flake8 src tests scripts
run docstrings work/docstrings.log uv run python scripts/check_docstrings.py
run typecheck work/typecheck.log uv run mypy src tests scripts
run metrics work/metrics.log uv run python scripts/code_metrics.py
run security-code work/security-code.log uv run bandit -c pyproject.toml -r src scripts
run security-deps work/security-deps.log bash scripts/security_deps.sh
run tests work/tests.log uv run pytest

print_failures

TOTAL=$((PASS + FAIL))
printf "\n${B}%s${N}\n" "$SEP"
if [ "$FAIL" -eq 0 ]; then
    printf " ${G}${B}All %d checks passed.${N}\n\n" "$TOTAL"
else
    printf " ${R}${B}%d of %d checks failed.${N}\n\n" "$FAIL" "$TOTAL"
fi

cleanup
exit "$FAIL"
