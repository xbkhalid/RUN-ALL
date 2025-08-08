# Create virtual environment if not exists
if (-not (Test-Path ".\venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

Write-Host "Activating virtual environment..."
. .\venv\Scripts\Activate.ps1

Write-Host "Upgrading pip and installing requirements..."
pip install --upgrade pip
pip install -r requirements.txt

# Remove old Qdrant container if exists
$qdrantName = "qdrant"
$containerExists = docker ps -a --filter name=$qdrantName --format "{{.Names}}"
if ($containerExists -eq $qdrantName) {
    Write-Host "Removing old Qdrant container..."
    docker rm -f $qdrantName
}

# Run Qdrant in Docker
Write-Host "Starting Qdrant container..."
docker run -d --name qdrant -p 6333:6333 qdrant/qdrant

# Wait for Qdrant to be ready
Write-Host "Waiting for Qdrant to start..."
Start-Sleep -Seconds 5

# Generate Embeddings
Write-Host "Generating embeddings..."
python scripts/generate_embeddings.py

# Upload data to Qdrant
Write-Host "Uploading data to Qdrant..."
python scripts/upload_to_qdrant.py

# Start FastAPI server
Write-Host "Starting FastAPI server..."
Start-Process cmd.exe "/k uvicorn app.main:app --reload"

# Wait for FastAPI server to be available, then open browser
$maxTries = 30
$waitSeconds = 1
$url = "http://127.0.0.1:8000/docs"
for ($i = 1; $i -le $maxTries; $i++) {
    try {
        $resp = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 2
        if ($resp.StatusCode -eq 200) {
            Write-Host "Server is up, opening browser!"
            Start-Process $url
            break
        }
    } catch {
        Start-Sleep -Seconds $waitSeconds
    }
    if ($i -eq $maxTries) {
        Write-Host "Server did not start in time. Please check manually."
    }
}

Write-Host "All done! Press Enter to exit."
Read-Host
