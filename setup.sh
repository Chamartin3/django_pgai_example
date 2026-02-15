#!/bin/bash
# =============================================================================
# ⚠️  USE WITH CAUTION ⚠️
# =============================================================================
#
# This script performs DESTRUCTIVE operations on the database including:
#   - Dropping tables (unbuild)
#   - Deleting migration files
#   - Clearing all data
#
# The 'unbuild' and 'rebuild' commands will PERMANENTLY DELETE DATA.
# Use with caution and always backup important data first.
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_header() {
    echo -e "\n${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}🔧 pgai-django Setup Script${NC}"
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

print_danger() {
    echo -e "\n${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${RED}⚠️  DANGER: DESTRUCTIVE OPERATION ⚠️${NC}"
    echo -e "${RED}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}\n"
}

# =============================================================================
# Helper Functions
# =============================================================================

wait_for_db() {
    local max_attempts=30
    local attempt=1

    while [ $attempt -le $max_attempts ]; do
        if docker compose ps db 2>/dev/null | grep -q "(healthy)"; then
            return 0
        fi
        if [ $attempt -eq 1 ]; then
            print_info "Waiting for database to be ready..."
        fi
        sleep 2
        attempt=$((attempt + 1))
    done
    return 1
}

check_services_ready() {
    if ! docker compose ps db 2>/dev/null | grep -q "(healthy)"; then
        print_info "Starting required services..."
        docker compose up -d >/dev/null 2>&1

        if ! wait_for_db; then
            print_error "Database not ready after 60 seconds"
            print_warning "Try: docker compose logs db"
            return 1
        fi
        print_success "Database is ready!"
    fi
    return 0
}

# =============================================================================
# Command Functions
# =============================================================================

cmd_build() {
    local skip_migrations=false
    local skip_migrate=false
    local skip_seed=false
    local model="all"
    local batches=10
    local remaining_args=()

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
        --skip-migrations)
            skip_migrations=true
            shift
            ;;
        --skip-migrate)
            skip_migrate=true
            shift
            ;;
        --skip-seed)
            skip_seed=true
            shift
            ;;
        --model)
            model="$2"
            shift 2
            ;;
        --batches)
            batches="$2"
            shift 2
            ;;
        *)
            remaining_args+=("$1")
            shift
            ;;
        esac
    done

    print_header
    print_info "Building wiki_new sample application..."
    echo ""

    # Check services
    if ! check_services_ready; then
        exit 1
    fi

    # Create migrations
    if [ "$skip_migrations" = false ]; then
        print_info "Creating migrations for wiki_new..."
        ./manage.sh makemigrations wiki_new
        echo ""
    else
        print_warning "Skipping migration generation (--skip-migrations)"
    fi

    # Run migrations
    if [ "$skip_migrate" = false ]; then
        print_info "Running database migrations..."
        ./manage.sh migrate
        echo ""
    else
        print_warning "Skipping migrations (--skip-migrate)"
    fi

    # Seed data
    if [ "$skip_seed" = false ]; then
        print_info "Loading sample Wikipedia data..."
        print_info "Model: $model, Batches: $batches"
        ./manage.sh seed --model "$model" --batches "$batches"
        echo ""
    else
        print_warning "Skipping data seeding (--skip-seed)"
    fi

    print_success "Build complete!"
    echo ""
    print_info "Next steps:"
    echo "  ./manage.sh wiki_new info       # Show model configuration"
    echo "  ./manage.sh wiki_new search     # Perform semantic search"
    echo "  ./setup.sh status               # Check table status"
}

cmd_unbuild() {
    local skip_confirm=false

    # Parse arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
        -y | --yes)
            skip_confirm=true
            shift
            ;;
        *)
            shift
            ;;
        esac
    done

    print_danger
    print_warning "This will PERMANENTLY DELETE the following:"
    echo ""
    echo "  Database:"
    echo "    - Full database reset (docker volume removed)"
    echo ""
    echo "  Migration Files:"
    echo "    - wiki_new/migrations/0*.py (all numbered migrations)"
    echo ""
    print_warning "⚠️  This action cannot be undone!"
    echo ""

    if [ "$skip_confirm" = false ]; then
        read -p "Type 'yes' to proceed with deletion: " -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
            print_info "Operation cancelled"
            exit 0
        fi
    fi

    print_info "Proceeding with unbuild..."
    echo ""

    # Stop services and remove database volume
    print_info "Stopping services and removing database volume..."
    docker compose down -v 2>/dev/null || true
    print_success "Database volume removed"
    echo ""

    # Delete migration files
    print_info "Deleting migration files..."
    if [ -d "wiki_new/migrations" ]; then
        local count=0
        for f in wiki_new/migrations/0*.py; do
            [ -f "$f" ] || continue
            rm -f "$f"
            count=$((count + 1))
        done
        if [ $count -gt 0 ]; then
            print_success "Deleted $count migration file(s)"
        else
            print_warning "No migration files to delete"
        fi
    else
        print_warning "Migrations directory not found"
    fi
    echo ""

    print_success "Unbuild complete!"
    print_info "The database has been fully reset."
    print_info "Run './setup.sh build' to rebuild from scratch."
}

cmd_rebuild() {
    local build_args=()

    # Parse arguments and filter out confirmation flags
    while [[ $# -gt 0 ]]; do
        case $1 in
        -y | --yes)
            # Pass through to unbuild
            build_args+=("$1")
            shift
            ;;
        *)
            build_args+=("$1")
            shift
            ;;
        esac
    done

    print_header
    print_warning "This will DESTROY all existing wiki_new data and rebuild from scratch."
    echo ""

    # Run unbuild with -y flag
    cmd_unbuild -y
    echo ""

    # Run build with remaining args
    cmd_build "${build_args[@]}"
}

cmd_status() {
    print_header
    print_info "Checking wiki_new database status..."
    echo ""

    # Check services
    if ! check_services_ready; then
        exit 1
    fi

    # Query database for table information
    print_info "Database tables and row counts:"
    echo ""

    ./manage.sh dbshell <<'EOF'
SELECT
    schemaname || '.' || tablename as table_name,
    n_live_tup as row_count
FROM pg_stat_user_tables
WHERE schemaname = 'public'
AND tablename LIKE 'wiki_new_%'
ORDER BY tablename;
EOF

    echo ""
    print_success "Status check complete!"
}

cmd_help() {
    print_header
    echo -e "${GREEN}Usage:${NC} ./setup.sh [COMMAND] [OPTIONS]"
    echo ""
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}Available Commands${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  ${MAGENTA}build${NC}                   Create migrations, run them, and seed data"
    echo -e "    Options:"
    echo -e "      --skip-migrations     Skip migration generation"
    echo -e "      --skip-migrate        Skip running migrations"
    echo -e "      --skip-seed           Skip data loading"
    echo -e "      --model MODEL         Model to use: minilm, snowflake, or all (default: all)"
    echo -e "      --batches N           Number of batches to load (default: 10)"
    echo ""
    echo -e "  ${MAGENTA}unbuild${NC}                 ${RED}DESTRUCTIVE:${NC} Full database reset"
    echo -e "    Options:"
    echo -e "      --yes, -y             Skip confirmation prompt (USE WITH CAUTION!)"
    echo -e "    Actions:"
    echo -e "      - Stops all services"
    echo -e "      - Removes database volume (full reset)"
    echo -e "      - Deletes wiki_new/migrations/0*.py"
    echo ""
    echo -e "  ${MAGENTA}rebuild${NC}                 Clean unbuild + build sequence"
    echo -e "    Runs: unbuild -y, then build with passed options"
    echo -e "    Options: (same as build command)"
    echo -e "      --skip-migrations     Skip migration generation"
    echo -e "      --skip-migrate        Skip running migrations"
    echo -e "      --skip-seed           Skip data loading"
    echo -e "      --model MODEL         Model to use: minilm, snowflake, or all"
    echo -e "      --batches N           Number of batches to load"
    echo ""
    echo -e "  ${MAGENTA}status${NC}                  Show database tables and row counts"
    echo ""
    echo -e "  ${MAGENTA}help${NC}                    Show this help message"
    echo ""
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}⚠️  Warnings${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "  ${RED}• The 'unbuild' and 'rebuild' commands will PERMANENTLY DELETE DATA.${NC}"
    echo -e "  ${RED}• Always backup important data before using these commands.${NC}"
    echo -e "  ${RED}• The default behavior requires explicit confirmation for unbuild.${NC}"
    echo ""
    echo -e "${GREEN}Examples:${NC}"
    echo ""
    echo -e "  ${CYAN}# Building${NC}"
    echo -e "  ./setup.sh build                        # Full build with all models"
    echo -e "  ./setup.sh build --model minilm         # Build with only MiniLM model"
    echo -e "  ./setup.sh build --skip-seed            # Build without loading data"
    echo -e "  ./setup.sh build --batches 5            # Load only 5 batches"
    echo ""
    echo -e "  ${CYAN}# Destructive Operations (USE WITH CAUTION!)${NC}"
    echo -e "  ./setup.sh unbuild                      # Prompt for confirmation"
    echo -e "  ./setup.sh unbuild --yes                # Skip confirmation (DANGEROUS)"
    echo -e "  ./setup.sh rebuild                      # Clean slate rebuild"
    echo -e "  ./setup.sh rebuild --skip-seed          # Rebuild without loading data"
    echo ""
    echo -e "  ${CYAN}# Status${NC}"
    echo -e "  ./setup.sh status                       # Show table row counts"
    echo ""
}

# =============================================================================
# Main Command Handling
# =============================================================================

# Check if docker-compose is available
if ! command -v docker &>/dev/null; then
    print_error "Docker is not installed or not in PATH"
    exit 1
fi

if ! docker compose version &>/dev/null; then
    print_error "Docker Compose is not available"
    exit 1
fi

# Check if manage.sh is available
if [ ! -f "./manage.sh" ]; then
    print_error "manage.sh not found in current directory"
    print_info "Make sure you're running this script from the project root"
    exit 1
fi

# Main command dispatcher
case "${1:-help}" in
"build")
    shift
    cmd_build "$@"
    ;;
"unbuild")
    shift
    cmd_unbuild "$@"
    ;;
"rebuild")
    shift
    cmd_rebuild "$@"
    ;;
"status")
    cmd_status
    ;;
"help" | "-h" | "--help" | "")
    cmd_help
    ;;
*)
    print_error "Unknown command: $1"
    echo ""
    cmd_help
    exit 1
    ;;
esac
