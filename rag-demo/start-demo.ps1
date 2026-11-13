# 一键启动 Demo（后端 + 前端）
# 用法：右键“使用 PowerShell 运行”，或在项目根目录执行：
#   powershell -ExecutionPolicy Bypass -File .\rag-demo\start-demo.ps1

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backend = Join-Path $root "backend"
$frontend = Join-Path $root "..\src-2\src-2"
$envFile = Join-Path $backend ".env"

if (-not (Test-Path $envFile)) {
    Write-Host "未找到 backend\.env，正在从 .env.example 复制..." -ForegroundColor Yellow
    Copy-Item (Join-Path $backend ".env.example") $envFile
}

$hasKey = Select-String -Path $envFile -Pattern '^LLM_API_KEY=\S+' -Quiet
if (-not $hasKey) {
    Write-Host "提示：backend\.env 里还没填 LLM_API_KEY，将进入检索预览模式（界面/引用可演示，回答由检索片段拼接）。" -ForegroundColor Yellow
    Write-Host "填好 Key 后重新运行本脚本即可，后端会自动把索引升级为语义向量。" -ForegroundColor Yellow
}

Write-Host "启动 RAG 后端 http://127.0.0.1:8000 ..." -ForegroundColor Green
Start-Process powershell -WorkingDirectory $backend -ArgumentList @(
    "-NoExit", "-Command", "python -m uvicorn app:app --host 127.0.0.1 --port 8000"
)

Write-Host "启动前端 http://localhost:5173 ..." -ForegroundColor Green
Start-Process powershell -WorkingDirectory $frontend -ArgumentList @(
    "-NoExit", "-Command", "npm run dev"
)

Start-Sleep -Seconds 4
Start-Process "http://localhost:5173/home"

Write-Host ""
Write-Host "两个终端窗口已打开，关闭窗口即停止服务。" -ForegroundColor Cyan
Write-Host "首次使用或修改 API Key 后，请在 backend 目录执行一次：python ingest.py" -ForegroundColor Cyan
