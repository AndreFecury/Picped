# =====================================================================
# Picped - sobe o banco + API no Docker e prepara o PC para o celular acessar.
# Uso: dê dois cliques em "subir-picped.bat" (na raiz do projeto).
# =====================================================================
$ErrorActionPreference = 'Continue'
Set-Location (Split-Path $PSScriptRoot -Parent)
$log = Join-Path (Get-Location) 'subir-picped.log'
Start-Transcript -Path $log -Force | Out-Null

function Passo($t) { Write-Host ""; Write-Host "== $t" -ForegroundColor Green }

Passo "1/5 Verificando o Docker"
docker info *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker parado. Abrindo o Docker Desktop..."
    $exe = Join-Path $env:ProgramFiles 'Docker\Docker\Docker Desktop.exe'
    if (Test-Path $exe) { Start-Process $exe }
    for ($i = 0; $i -lt 60; $i++) {
        Start-Sleep -Seconds 3
        docker info *> $null
        if ($LASTEXITCODE -eq 0) { break }
    }
}
docker info *> $null
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: o Docker nao respondeu. Abra o Docker Desktop, espere ficar 'Engine running' e rode de novo." -ForegroundColor Red
    Stop-Transcript | Out-Null; Read-Host "Enter para fechar"; exit 1
}
Write-Host "Docker OK."

Passo "2/5 Conferindo o arquivo .env"
if (-not (Test-Path .env)) { Copy-Item .env.example .env; Write-Host ".env criado a partir do .env.example" }
else { Write-Host ".env OK" }

Passo "3/5 Subindo banco + API (recria o banco com schema + seed + demo)"
$resp = Read-Host "Recriar o banco do zero? Recomendado na 1a vez (S/n)"
if ($resp -ne 'n' -and $resp -ne 'N') { docker compose down -v }
docker compose up -d --build
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO ao subir os containers. Veja as mensagens acima." -ForegroundColor Red
    Stop-Transcript | Out-Null; Read-Host "Enter para fechar"; exit 1
}

Passo "4/5 Esperando a API responder"
$ok = $false
for ($i = 0; $i -lt 40; $i++) {
    try {
        $r = Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 http://localhost:8000/health
        if ($r.StatusCode -eq 200) { $ok = $true; break }
    } catch { }
    Start-Sleep -Seconds 3
}
docker compose ps
if ($ok) { Write-Host "API OK: http://localhost:8000/docs" -ForegroundColor Green; Write-Host "APP no navegador deste PC: http://localhost:8000/app/" -ForegroundColor Green }
else { Write-Host "A API nao respondeu. Logs:" -ForegroundColor Red; docker compose logs --tail 40 api }

Passo "5/5 Liberando a porta 8000 para o celular (Firewall do Windows)"
$regra = Get-NetFirewallRule -DisplayName 'Picped API 8000' -ErrorAction SilentlyContinue
if ($regra) { Write-Host "Regra de firewall ja existe." }
else {
    Write-Host "O Windows vai pedir permissao de administrador para criar a regra (clique em Sim)."
    $cmd = "New-NetFirewallRule -DisplayName 'Picped API 8000' -Direction Inbound -Protocol TCP -LocalPort 8000 -Action Allow -Profile Any | Out-Null"
    try { Start-Process powershell -Verb RunAs -Wait -ArgumentList '-NoProfile', '-Command', $cmd; Write-Host "Regra criada." }
    catch { Write-Host "Regra NAO criada (permissao negada). O celular pode nao conseguir acessar." -ForegroundColor Yellow }
}

Write-Host ""
Write-Host "==============================================================" -ForegroundColor Green
Write-Host " Usar o app neste PC: http://localhost:8000/app/" -ForegroundColor Green
Write-Host " No celular (app Picped > Configurar servidor), use:" -ForegroundColor Green
Get-NetIPAddress -AddressFamily IPv4 |
    Where-Object { $_.IPAddress -notlike '127.*' -and $_.IPAddress -notlike '169.254*' -and $_.InterfaceAlias -notlike 'vEthernet*' } |
    ForEach-Object { Write-Host ("   http://{0}:8000   ({1})" -f $_.IPAddress, $_.InterfaceAlias) }
Write-Host " (o celular precisa estar no MESMO Wi-Fi deste computador)"
Write-Host " Conta demo: ana@picped.dev  /  senha picped123"
Write-Host " Para parar tudo depois: docker compose down"
Write-Host " Para remover a regra do firewall: Remove-NetFirewallRule -DisplayName 'Picped API 8000' (como admin)"
Write-Host "==============================================================" -ForegroundColor Green
Stop-Transcript | Out-Null
Read-Host "Enter para fechar"
