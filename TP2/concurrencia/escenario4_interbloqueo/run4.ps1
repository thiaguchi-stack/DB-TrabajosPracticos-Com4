param(
    [string]$Db = 'foodstore_tp2',
    [string]$DbUser = 'postgres',
    [string]$DbHost = 'localhost'
)
# Orquestador Escenario 4 - Interbloqueo real con orden cruzado de bloqueos.
# Uso:  $env:PGPASSWORD="..." ; .\run4.ps1
$ErrorActionPreference = 'Stop'
$dir = $PSScriptRoot
if (-not $env:PGPASSWORD) {
    throw 'Defini la variable de entorno PGPASSWORD antes de ejecutar el escenario.'
}
& psql -U $DbUser -h $DbHost -d $Db -X -v ON_ERROR_STOP=1 -c "UPDATE sync_deadlock SET aviso = FALSE WHERE id = 1;" | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'No se pudo reiniciar sync_deadlock. Ejecuta TP2/sql/00_seed_minimo.sql.' }
Remove-Item (Join-Path $dir 'salida_A.txt'),(Join-Path $dir 'salida_B.txt'),(Join-Path $dir 'err_A.txt'),(Join-Path $dir 'err_B.txt') -ErrorAction SilentlyContinue
$qA = '"' + (Join-Path $dir 'sA.sql') + '"'
$qB = '"' + (Join-Path $dir 'sB.sql') + '"'
$pA = Start-Process psql -ArgumentList @('-U',$DbUser,'-h',$DbHost,'-d',$Db,'-X','-f',$qA) -NoNewWindow -PassThru -RedirectStandardOutput (Join-Path $dir 'salida_A.txt') -RedirectStandardError (Join-Path $dir 'err_A.txt')
Start-Sleep -Seconds 1
$pB = Start-Process psql -ArgumentList @('-U',$DbUser,'-h',$DbHost,'-d',$Db,'-X','-f',$qB) -NoNewWindow -PassThru -RedirectStandardOutput (Join-Path $dir 'salida_B.txt') -RedirectStandardError (Join-Path $dir 'err_B.txt')
$pA.WaitForExit(); $pB.WaitForExit()

# La evidencia del error 40P01 (deadlock) llega por stderr; se anexa a la salida
# para que quede versionada junto al resto de la evidencia.
Get-Content (Join-Path $dir 'err_A.txt') -ErrorAction SilentlyContinue | Add-Content (Join-Path $dir 'salida_A.txt')
Get-Content (Join-Path $dir 'err_B.txt') -ErrorAction SilentlyContinue | Add-Content (Join-Path $dir 'salida_B.txt')

Write-Host '=== SESION A ==='; Get-Content (Join-Path $dir 'salida_A.txt')
Write-Host '=== SESION B ==='; Get-Content (Join-Path $dir 'salida_B.txt')
