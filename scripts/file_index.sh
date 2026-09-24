#!/usr/bin/env bash
# file_index.sh - Generate and search a file index for the SignSpeakPH repository
#
# Purpose: Create a searchable index of all files to avoid repeated filesystem scanning
# Usage:
#   ./file_index.sh --build    # Build/update the file index
#   ./file_index.sh --search "pattern"  # Search the index for files matching pattern
#   ./file_index.sh --help     # Show this help
#
# The index is saved as .file_index in the repository root.

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
INDEX_FILE="$REPO_ROOT/.file_index"

show_help() {
    echo "file_index.sh - Generate and search a file index for the SignSpeakPH repository"
    echo ""
    echo "Purpose: Create a searchable index of all files to avoid repeated filesystem scanning"
    echo ""
    echo "Usage:"
    echo "  ./file_index.sh --build    # Build/update the file index"
    echo "  ./file_index.sh --search \"pattern\"  # Search the index for files matching pattern"
    echo "  ./file_index.sh --help     # Show this help"
    echo ""
    echo "The index is saved as .file_index in the repository root."
}

build_index() {
    echo "Building file index..."
    # Using find as the bash equivalent of dir /s /b
    # -type f: only files (not directories)
    # Sort for consistent output
    find "$REPO_ROOT" -type f | sort > "$INDEX_FILE"
    echo "Index built: $(wc -l < "$INDEX_FILE") files indexed"
}

search_index() {
    local pattern="$1"
    if [[ ! -f "$INDEX_FILE" ]]; then
        echo "Error: Index file not found. Run '$0 --build' first."
        exit 1
    fi

    if [[ -z "$pattern" ]]; then
        echo "Error: Please provide a search pattern"
        echo "Usage: $0 --search \"pattern\""
        exit 1
    fi

    grep -i "$pattern" "$INDEX_FILE"
}

# Main script logic
if [[ $# -eq 0 ]]; then
    show_help
    exit 0
fi

case "$1" in
    --build|-b)
        build_index
        ;;
    --search|-s)
        if [[ -z "$2" ]]; then
            echo "Error: Please provide a search pattern"
            echo "Usage: $0 --search \"pattern\""
            exit 1
        fi
        search_index "$2"
        ;;
    --help|-h)
        show_help
        ;;
    *)
        echo "Error: Unknown option '$1'"
        echo "Usage: $0 {--build|--search \"pattern\"|--help}"
        exit 1
        ;;
esac