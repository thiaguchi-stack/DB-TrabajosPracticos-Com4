# ============================================================================
# Orquestador Escenario 1 - Lectura no repetible (READ COMMITTED)
# Lanza SESION A (sA_rc.sql) y SESION B (sB1.sql) en paralelo con psql.
# Uso:  $env:PGPASSWORD="..." ; .\run1.ps1
# ============================================================================
param(
    [string]$Db = 'foodstore_tp2',
    [string]$DbUser = 'postgres',
    [string]$DbHost = 'localhost'
)
$ErrorActionPreference = 'Stop'
$dir = $PSScriptRoot
if (-not $env:PGPASSWORD) {
    throw 'Defini la variable de entorno PGPASSWORD antes de ejecutar el escenario.'
}

& psql -U $DbUser -h $DbHost -d $Db -X -v ON_ERROR_STOP=1 -c "UPDATE producto SET precio = 800.00 WHERE id = 2;" | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'No se pudo restaurar el precio base del producto 2.' }

Remove-Item (Join-Path $dir 'salida_A_rc.txt'), (Join-Path $dir 'salida_B.txt'), (Join-Path $dir 'err_A.txt'), (Join-Path $dir 'err_B.txt') -ErrorAction SilentlyContinue

$qA = '"' + (Join-Path $dir 'sA_rc.sql') + '"'
$qB = '"' + (Join-Path $dir 'sB1.sql') + '"'

Write-Host '=== LANZANDO SESION A (READ COMMITTED) ==='
$procA = Start-Process -FilePath 'psql' -ArgumentList @('-U',$DbUser,'-h',$DbHost,'-d',$Db,'-X','-f',$qA) `
    -NoNewWindow -PassThru `
    -RedirectStandardOutput (Join-Path $dir 'salida_A_rc.txt') -RedirectStandardError (Join-Path $dir 'err_A.txt')

Start-Sleep -Seconds 2
Write-Host '=== LANZANDO SESION B (actualiza precio 800 -> 850 y COMMIT) ==='
$procB = Start-Process -FilePath 'psql' -ArgumentList @('-U',$DbUser,'-h',$DbHost,'-d',$Db,'-X','-f',$qB) `
    -NoNewWindow -PassThru `
    -RedirectStandardOutput (Join-Path $dir 'salida_B.txt') -RedirectStandardError (Join-Path $dir 'err_B.txt')

$procA.WaitForExit()
$procB.WaitForExit()

Write-Host ''
Write-Host '================ SALIDA SESION A (READ COMMITTED) ================'
Get-Content (Join-Path $dir 'salida_A_rc.txt')
Write-Host ''
Write-Host '================ SALIDA SESION B ================'
Get-Content (Join-Path $dir 'salida_B.txt')
