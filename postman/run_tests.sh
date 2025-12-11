#!/bin/bash

# FastAPI RAG Application - Postman Test Runner
# This script helps you run the Postman collection tests using Newman CLI

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COLLECTION_FILE="FastAPI_RAG_Application.postman_collection.json"
ENVIRONMENT_FILE="FastAPI_RAG_Environment.postman_environment.json"
DEFAULT_BASE_URL="http://localhost:8000"
DEFAULT_ITERATIONS=1
DEFAULT_DELAY=1000

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Newman is installed
check_newman() {
    if ! command -v newman &> /dev/null; then
        print_error "Newman CLI is not installed!"
        echo "Please install Newman using: npm install -g newman"
        echo "Or visit: https://github.com/postmanlabs/newman"
        exit 1
    fi
    print_success "Newman CLI is installed"
}

# Function to check if files exist
check_files() {
    if [[ ! -f "$COLLECTION_FILE" ]]; then
        print_error "Collection file not found: $COLLECTION_FILE"
        exit 1
    fi
    
    if [[ ! -f "$ENVIRONMENT_FILE" ]]; then
        print_error "Environment file not found: $ENVIRONMENT_FILE"
        exit 1
    fi
    
    print_success "Collection and environment files found"
}

# Function to check if API is running
check_api() {
    local base_url=${1:-$DEFAULT_BASE_URL}
    print_status "Checking if API is running at $base_url..."
    
    if curl -s -f "$base_url/health/simple" > /dev/null 2>&1; then
        print_success "API is running and responding"
        return 0
    else
        print_warning "API is not responding at $base_url"
        print_warning "Make sure your FastAPI application is running:"
        echo "  cd /path/to/llm-chatbot-with-rag"
        echo "  python src/main.py"
        return 1
    fi
}

# Function to run tests
run_tests() {
    local base_url=${1:-$DEFAULT_BASE_URL}
    local iterations=${2:-$DEFAULT_ITERATIONS}
    local delay=${3:-$DEFAULT_DELAY}
    local folder=${4:-""}
    local output_format=${5:-"cli"}
    
    print_status "Running Postman tests..."
    echo "  Base URL: $base_url"
    echo "  Iterations: $iterations"
    echo "  Delay: ${delay}ms"
    echo "  Output: $output_format"
    
    # Build Newman command
    local newman_cmd="newman run \"$COLLECTION_FILE\" -e \"$ENVIRONMENT_FILE\""
    newman_cmd="$newman_cmd --env-var \"base_url=$base_url\""
    newman_cmd="$newman_cmd -n $iterations"
    newman_cmd="$newman_cmd --delay-request $delay"
    
    # Add folder filter if specified
    if [[ -n "$folder" ]]; then
        newman_cmd="$newman_cmd --folder \"$folder\""
        echo "  Folder: $folder"
    fi
    
    # Add output format
    case $output_format in
        "json")
            newman_cmd="$newman_cmd --reporters cli,json --reporter-json-export results.json"
            ;;
        "junit")
            newman_cmd="$newman_cmd --reporters cli,junit --reporter-junit-export test-results.xml"
            ;;
        "html")
            newman_cmd="$newman_cmd --reporters cli,htmlextra --reporter-htmlextra-export test-report.html"
            ;;
        *)
            newman_cmd="$newman_cmd --reporters cli"
            ;;
    esac
    
    echo
    print_status "Executing: $newman_cmd"
    echo
    
    # Run the command
    if eval $newman_cmd; then
        print_success "Tests completed successfully!"
        
        # Show output file info
        case $output_format in
            "json")
                print_status "Results saved to: results.json"
                ;;
            "junit")
                print_status "Results saved to: test-results.xml"
                ;;
            "html")
                print_status "Report saved to: test-report.html"
                ;;
        esac
    else
        print_error "Tests failed!"
        exit 1
    fi
}

# Function to show usage
show_usage() {
    echo "FastAPI RAG Application - Postman Test Runner"
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -u, --url URL          Base URL for API (default: $DEFAULT_BASE_URL)"
    echo "  -n, --iterations N     Number of iterations (default: $DEFAULT_ITERATIONS)"
    echo "  -d, --delay MS         Delay between requests in ms (default: $DEFAULT_DELAY)"
    echo "  -f, --folder NAME      Run only specific folder"
    echo "  -o, --output FORMAT    Output format: cli, json, junit, html (default: cli)"
    echo "  -s, --skip-check       Skip API availability check"
    echo "  -h, --help             Show this help message"
    echo
    echo "Examples:"
    echo "  $0                                    # Run all tests with defaults"
    echo "  $0 -u http://localhost:3000          # Use custom URL"
    echo "  $0 -f \"Health Checks\"                # Run only health check tests"
    echo "  $0 -o json -n 5                      # Run 5 iterations, save JSON results"
    echo "  $0 -u https://api.example.com -o html # Run against remote API, generate HTML report"
    echo
    echo "Available folders:"
    echo "  - Health Checks"
    echo "  - Chat Completion"
    echo "  - Error Scenarios"
    echo "  - Documentation"
}

# Parse command line arguments
BASE_URL="$DEFAULT_BASE_URL"
ITERATIONS="$DEFAULT_ITERATIONS"
DELAY="$DEFAULT_DELAY"
FOLDER=""
OUTPUT_FORMAT="cli"
SKIP_CHECK=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--url)
            BASE_URL="$2"
            shift 2
            ;;
        -n|--iterations)
            ITERATIONS="$2"
            shift 2
            ;;
        -d|--delay)
            DELAY="$2"
            shift 2
            ;;
        -f|--folder)
            FOLDER="$2"
            shift 2
            ;;
        -o|--output)
            OUTPUT_FORMAT="$2"
            shift 2
            ;;
        -s|--skip-check)
            SKIP_CHECK=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    echo "🚀 FastAPI RAG Application - Postman Test Runner"
    echo "=================================================="
    echo
    
    # Check prerequisites
    check_newman
    check_files
    
    # Check API availability (unless skipped)
    if [[ "$SKIP_CHECK" != true ]]; then
        if ! check_api "$BASE_URL"; then
            echo
            read -p "API is not responding. Continue anyway? (y/N): " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                print_status "Exiting..."
                exit 1
            fi
        fi
    fi
    
    echo
    
    # Run tests
    run_tests "$BASE_URL" "$ITERATIONS" "$DELAY" "$FOLDER" "$OUTPUT_FORMAT"
    
    echo
    print_success "All done! 🎉"
}

# Run main function
main "$@"