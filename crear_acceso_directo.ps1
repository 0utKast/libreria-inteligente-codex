$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath('Desktop')

# Caracter 'í' en Unicode para evitar problemas de codificación del script
$iConTilde = [char]0xED
$ShortcutName = "Mi Librer$($iConTilde)a Inteligente.lnk"
$ShortcutPath = Join-Path $DesktopPath $ShortcutName

# Eliminar versiones previas con fallos de codificación (buscando el patrón 'Ã')
Get-ChildItem $DesktopPath -Filter "Mi Librer*.lnk" | Where-Object { $_.Name -match "Ã" -or $_.Name -match " -a" } | Remove-Item -ErrorAction SilentlyContinue

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)

# Ruta absoluta al proyecto
$ProjectRoot = "c:\proyectos_python\MisApps\libreria-inteligente-codex"
$TargetPath = "cmd.exe"
$Arguments = "/c `"$ProjectRoot\start.bat`""

$Shortcut.TargetPath = $TargetPath
$Shortcut.Arguments = $Arguments
$Shortcut.WorkingDirectory = $ProjectRoot
$Shortcut.IconLocation = "$ProjectRoot\icono_L_azul.ico"
$Shortcut.Description = "Iniciar Mi Librería Inteligente"
$Shortcut.Save()

Write-Host "Acceso directo '$ShortcutName' corregido y versiones anteriores eliminadas."
