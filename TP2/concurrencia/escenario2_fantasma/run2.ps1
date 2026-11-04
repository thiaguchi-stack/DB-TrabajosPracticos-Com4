param(
    [string]$sA,
    [string]$Db = 'foodstore_tp2',
    [string]$DbUser = 'postgres',
    [string]$DbHost = 'localhost'
)
# Orquestador generico escenario 2: $sA = sA_rc.sql o sA_rr.sql
# Usa un nombre de salida propio por script para no pisar la evidencia.
# Uso:  $env:PGPASSWORD="..." ; .\run2.ps1 -sA sA_rc.sql
$ErrorActionPreference = 'Stop'
$dir = $PSScriptRoot
if (-not $env:PGPASSWORD) {
    throw 'Defini la variable de entorno PGPASSWORD antes de ejecutar el escenario.'
}
if (-not $sA) {
    throw 'Indica el script de la sesion A con -sA sA_rc.sql o -sA sA_rr.sql.'
}
& psql -U $DbUser -h $DbHost -d $Db -X -v ON_ERROR_STOP=1 -c "DELETE FROM producto WHERE categoria_id = 1 AND nombre = 'Fugazzeta';" | Out-Null
if ($LASTEXITCODE -ne 0) { throw 'No se pudo limpiar la pizza de prueba del escenario 2.' }
$tag = ($sA -replace '^sA_','' -replace '\.sql$','')
$outA = Join-Path $dir ("salida_A_{0}.txt" -f $tag)
Remove-Item $outA,(Join-Path $dir 'salida_B.txt') -ErrorAction SilentlyContinue
$qA = '"' + (Join-Path $dir $sA) + '"'
$qB = '"' + (Join-Path $dir 'sB2.sql') + '"'
$pA = Start-Process psql -ArgumentList @('-U',$DbUser,'-h',$DbHost,'-d',$Db,'-X','-f',$qA) -NoNewWindow -PassThru -RedirectStandardOutput $outA -RedirectStandardError (Join-Path $dir 'err_A.txt')
Start-Sleep -Seconds 2
$pB = Start-Process psql -ArgumentList @('-U',$DbUser,'-h',$DbHost,'-d',$Db,'-X','-f',$qB) -NoNewWindow -PassThru -RedirectStandardOutput (Join-Path $dir 'salida_B.txt') -RedirectStandardError (Join-Path $dir 'err_B.txt')
$pA.WaitForExit(); $pB.WaitForExit()
Write-Host "=== SESION A ($sA) ==="; Get-Content $outA
Write-Host '=== SESION B ==='; Get-Content (Join-Path $dir 'salida_B.txt')
