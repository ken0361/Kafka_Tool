@echo off
REM Check if Docker is installed

docker --version >nul 2>&1
if %ERRORLEVEL% equ 0 (
    set docker_installed=Y
    echo Docker is installed.
) else (
    set docker_installed=N
    echo Docker is not installed.
)


if /I "%docker_installed%"=="Y" (
    REM Build the Docker image
    echo Building Docker image...
    docker image build -t kafka-tool:test ./
    echo Docker image built successfully.

    REM Run the Docker container in a new window
    echo Running Docker container...
    start cmd /c "docker run -p 8080:5000 kafka-tool:test"
    echo Docker container is running.

    REM Open the web page
    echo Opening web page...
    start http://localhost:8080/templates/
    echo Web page opened.

    REM Pause to keep the terminal open
    pause
) else (
    echo Please install Docker and try again.
    pause
)