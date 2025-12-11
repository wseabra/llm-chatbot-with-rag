@echo off
REM FastAPI RAG Application - Postman Test Runner (Windows)
REM This script helps you run the Postman collection tests using Newman CLI

setlocal enabledelayedexpansion

REM Configuration
set COLLECTION_FILE=FastAPI_RAG_Application.postman_collection.json
set ENVIRONMENT_FILE=FastAPI_RAG_Environment.postman_environment.json
set DEFAULT_BASE_URL=http://localhost:8000
set DEFAULT_ITERATIONS=1
set DEFAULT_DELAY=1000

REM Default values
set BASE_URL=%DEFAULT_BASE_URL%
set ITERATIONS=%DEFAULT_ITERATIONS%
set DELAY=%DEFAULT_DELAY%
set FOLDER=
set OUTPUT_FORMAT=cli
set SKIP_CHECK=false

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :check_newman
if "%~1"=="-u" (
    set BASE_URL=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--url" (
    set BASE_URL=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-n" (
    set ITERATIONS=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--iterations" (
    set ITERATIONS=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-d" (
    set DELAY=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--delay" (
    set DELAY=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-f" (
    set FOLDER=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--folder" (
    set FOLDER=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-o" (
    set OUTPUT_FORMAT=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--output" (
    set OUTPUT_FORMAT=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-s" (
    set SKIP_CHECK=true
    shift
    goto :parse_args
)
if "%~1"=="--skip-check" (
    set SKIP_CHECK=true
    shift
    goto :parse_args
)
if "%~1"=="-h" goto :show_usage
if "%~1"=="--help" goto :show_usage
echo [ERROR] Unknown option: %~1
goto :show_usage

:check_newman
echo 🚀 FastAPI RAG Application - Postman Test Runner
echo ==================================================
echo.

REM Check if Newman is installed
newman --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Newman CLI is not installed!
    echo Please install Newman using: npm install -g newman
    echo Or visit: https://github.com/postmanlabs/newman
    exit /b 1
)
echo [SUCCESS] Newman CLI is installed

REM Check if files exist
if not exist "%COLLECTION_FILE%" (
    echo [ERROR] Collection file not found: %COLLECTION_FILE%
    exit /b 1
)
if not exist "%ENVIRONMENT_FILE%" (
    echo [ERROR] Environment file not found: %ENVIRONMENT_FILE%
    exit /b 1
)
echo [SUCCESS] Collection and environment files found

REM Check API availability (unless skipped)
if "%SKIP_CHECK%"=="false" (
    echo [INFO] Checking if API is running at %BASE_URL%...
    curl -s -f "%BASE_URL%/health/simple" >nul 2>&1
    if errorlevel 1 (
        echo [WARNING] API is not responding at %BASE_URL%
        echo [WARNING] Make sure your FastAPI application is running:
        echo   cd /path/to/llm-chatbot-with-rag
        echo   python src/main.py
        echo.
        set /p continue="API is not responding. Continue anyway? (y/N): "
        if /i not "!continue!"=="y" (
            echo [INFO] Exiting...
            exit /b 1
        )
    ) else (
        echo [SUCCESS] API is running and responding
    )
)

echo.

REM Run tests
echo [INFO] Running Postman tests...
echo   Base URL: %BASE_URL%
echo   Iterations: %ITERATIONS%
echo   Delay: %DELAY%ms
echo   Output: %OUTPUT_FORMAT%

REM Build Newman command
set NEWMAN_CMD=newman run "%COLLECTION_FILE%" -e "%ENVIRONMENT_FILE%" --env-var "base_url=%BASE_URL%" -n %ITERATIONS% --delay-request %DELAY%

REM Add folder filter if specified
if not "%FOLDER%"=="" (
    set NEWMAN_CMD=%NEWMAN_CMD% --folder "%FOLDER%"
    echo   Folder: %FOLDER%
)

REM Add output format
if "%OUTPUT_FORMAT%"=="json" (
    set NEWMAN_CMD=%NEWMAN_CMD% --reporters cli,json --reporter-json-export results.json
) else if "%OUTPUT_FORMAT%"=="junit" (
    set NEWMAN_CMD=%NEWMAN_CMD% --reporters cli,junit --reporter-junit-export test-results.xml
) else if "%OUTPUT_FORMAT%"=="html" (
    set NEWMAN_CMD=%NEWMAN_CMD% --reporters cli,htmlextra --reporter-htmlextra-export test-report.html
) else (
    set NEWMAN_CMD=%NEWMAN_CMD% --reporters cli
)

echo.
echo [INFO] Executing: %NEWMAN_CMD%
echo.

REM Run the command
%NEWMAN_CMD%
if errorlevel 1 (
    echo [ERROR] Tests failed!
    exit /b 1
)

echo [SUCCESS] Tests completed successfully!

REM Show output file info
if "%OUTPUT_FORMAT%"=="json" (
    echo [INFO] Results saved to: results.json
) else if "%OUTPUT_FORMAT%"=="junit" (
    echo [INFO] Results saved to: test-results.xml
) else if "%OUTPUT_FORMAT%"=="html" (
    echo [INFO] Report saved to: test-report.html
)

echo.
echo [SUCCESS] All done! 🎉
goto :eof

:show_usage
echo FastAPI RAG Application - Postman Test Runner
echo.
echo Usage: %~nx0 [OPTIONS]
echo.
echo Options:
echo   -u, --url URL          Base URL for API (default: %DEFAULT_BASE_URL%)
echo   -n, --iterations N     Number of iterations (default: %DEFAULT_ITERATIONS%)
echo   -d, --delay MS         Delay between requests in ms (default: %DEFAULT_DELAY%)
echo   -f, --folder NAME      Run only specific folder
echo   -o, --output FORMAT    Output format: cli, json, junit, html (default: cli)
echo   -s, --skip-check       Skip API availability check
echo   -h, --help             Show this help message
echo.
echo Examples:
echo   %~nx0                                    # Run all tests with defaults
echo   %~nx0 -u http://localhost:3000          # Use custom URL
echo   %~nx0 -f "Health Checks"                # Run only health check tests
echo   %~nx0 -o json -n 5                      # Run 5 iterations, save JSON results
echo   %~nx0 -u https://api.example.com -o html # Run against remote API, generate HTML report
echo.
echo Available folders:
echo   - Health Checks
echo   - Chat Completion
echo   - Error Scenarios
echo   - Documentation
exit /b 0