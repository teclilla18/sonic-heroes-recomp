# Notification hook (optional, Windows): pops a desktop notification when
# Claude Code is waiting for you. Wired up in .claude/settings.local.json.
$text = 'Claude Code needs your input'
try {
    $in = [Console]::In.ReadToEnd() | ConvertFrom-Json
    if ($in.message) { $text = $in.message }
} catch { }
Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing
$n = New-Object System.Windows.Forms.NotifyIcon
$n.Icon = [System.Drawing.SystemIcons]::Information
$n.Visible = $true
$n.ShowBalloonTip(5000, 'Claude Code - Sonic Heroes', $text, 'Info')
Start-Sleep -Seconds 4
$n.Dispose()
