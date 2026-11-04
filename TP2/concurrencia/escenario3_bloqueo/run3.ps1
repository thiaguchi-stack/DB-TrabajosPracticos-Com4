param(
    [string]$Db = 'foodstore_tp2',
    [string]$DbUser = 'postgres',
    [string]$DbHost = 'localhost'
)
# Orquestador Escenario 3 - Espera por bloqueo con SELECT ... FOR UPDATE
# Uso:  $env:PGPASSWORD="..." ; .\run3.ps1
$ErrorActionPreference = 'Stop'
$dir = $PSScriptRoot
if (-not $env:PGPASSWORD) {
    throw 'Defini la variable de entorno PGPASSWORD antes de ejecutar el escenario.'
}
Remove-Item (Join-Path $dir 'salida_A.txt'),(Join-Path $dir 'salida_B.txt') -ErrorAction SilentlyContinue
$qA = '"' + (Join-Path $dir 'sA.sql') + '"'
$qB = '"' + (Join-Path $dir 'sB.sql') + '"'
Write-Host '>>> t0: A bloquea fila 1 y duerme 5s'
$pA = Start-Process psql -ArgumentList @('-U',$DbUser,'-h',$DbHost,'-d',$Db,'-X','-f',$qA) -NoNewWindow -PassThru -RedirectStandardOutput (Join-Path $dir 'salida_A.txt') -RedirectStandardError (Join-Path $dir 'err_A.txt')
Start-Sleep -Seconds 2
Write-Host '>>> t+2s: B intenta FOR UPDATE sobre la misma fila'
$pB = Start-Process psql -ArgumentList @('-U',$DbUser,'-h',$DbHost,'-d',$Db,'-X','-f',$qB) -NoNewWindow -PassThru -RedirectStandardOutput (Join-Path $dir 'salida_B.txt') -RedirectStandardError (Join-Path $dir 'err_B.txt')
$pA.WaitForExit(); $pB.WaitForExit()
Write-Host '=== SESION A ==='; Get-Content (Join-Path $dir 'salida_A.txt')
Write-Host '=== SESION B (timestamps muestran la espera) ==='; Get-Content (Join-Path $dir 'salida_B.txt')
