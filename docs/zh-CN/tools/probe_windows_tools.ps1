# Read-only executable and installed-application discovery.
$taskProjectRoot = Split-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) -Parent
$taskCommands = @('git','pwsh','node','python','uv','ruff','pytest','make','gcc','g++','cl','clang','iverilog','vvp','vivado','matlab','octave','qucs','qucs-s','QucsStudio','openEMS','kicad-cli','eeschema','pcbnew','sfw')
$taskCommandRows = foreach ($taskName in $taskCommands) {
    $taskCommand = Get-Command $taskName -ErrorAction SilentlyContinue
    [pscustomobject]@{ name=$taskName; found=[bool]$taskCommand; path=if ($taskCommand) { $taskCommand.Source } else { $null } }
}
$taskRegistryRoots = @('HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*','HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*','HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*')
$taskApps = @(Get-ItemProperty -Path $taskRegistryRoots -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName -match 'Vivado|Xilinx|MATLAB|Octave|Qucs|openEMS|KiCad|EAGLE|FreeCAD|Microsoft 365|Visual Studio Community|Icarus|MSYS|MinGW|Python|Git$|FTDI|AutoCAD|HFSS|CST' } | Select-Object DisplayName,DisplayVersion,InstallLocation)
$taskVswhere = 'C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe'
$taskVsCpp = if (Test-Path -LiteralPath $taskVswhere) { & $taskVswhere -latest -products '*' -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath } else { $null }
$taskReport = [ordered]@{
    date='2026-10-08'
    commands=@($taskCommandRows)
    installed_apps=$taskApps
    visual_studio_cpp_component_path=$taskVsCpp
    cst_executable_exists=(Test-Path -LiteralPath 'D:\Program Files\CST Studio Suite 2026\CST DESIGN ENVIRONMENT.exe')
    scope='PATH and Windows uninstall registry plus named executable probes; absence is not proof of no portable or unregistered installation.'
}
$taskReport | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $taskProjectRoot 'docs\zh-CN\本机Windows工具.json') -Encoding utf8
Write-Output 'Windows tool inventory saved.'
