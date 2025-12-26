$WshShell = New-Object -ComObject WScript.Shell
$DesktopPath = [System.Environment]::GetFolderPath('Desktop')

# Usamos un nombre sin tildes para el archivo .lnk internamente si la codificación falla, 
# pero intentaremos el nombre correcto.
$ShortcutName = "Mi Librería Inteligente.lnk"
$Shortcut = $WshShell.CreateShortcut("$DesktopPath\$ShortcutName")

# Ruta absoluta al proyecto
$ProjectRoot = "c:\proyectos_python\MisApps\libreria-inteligente-codex"
$TargetPath = "cmd.exe"
$Arguments = "/c `"$ProjectRoot\start.bat`""

$Shortcut.TargetPath = $TargetPath
$Shortcut.Arguments = $Arguments
$Shortcut.WorkingDirectory = $ProjectRoot
# Cambiamos a icono_L_azul.ico para mejor resolución
$Shortcut.IconLocation = "$ProjectRoot\icono_L_azul.ico"
$Shortcut.Description = "Iniciar Mi Librería Inteligente"
$Shortcut.Save()

Write-Host "Acceso directo actualizado con éxito en el Escritorio."
