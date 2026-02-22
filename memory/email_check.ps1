$ErrorActionPreference = 'Stop'

$cfgPath = 'E:\setup\emali.json'
$statePath = 'C:\Users\86178\.openclaw\workspace\memory\email-last-seen.json'

if (!(Test-Path $cfgPath)) { Write-Output 'EMAIL_CHECK_FAIL: config_not_found'; exit 0 }

$raw = Get-Content $cfgPath -Raw
$email = [regex]::Match($raw, '"email"\s*:\s*"([^"]+)"').Groups[1].Value
$pass  = [regex]::Match($raw, '"clientPassword"\s*:\s*"([^"]+)"').Groups[1].Value
if (-not $pass) { $pass = [regex]::Match($raw, '"password"\s*:\s*"([^"]+)"').Groups[1].Value }

$imapHost = [regex]::Match($raw, '"imapServer"\s*:\s*\{[\s\S]*?"host"\s*:\s*"([^"]+)"').Groups[1].Value
if (-not $imapHost) { $imapHost = [regex]::Match($raw, '"imap_server"\s*:\s*"([^"]+)"').Groups[1].Value }

$portS = [regex]::Match($raw, '"imapServer"\s*:\s*\{[\s\S]*?"sslPort"\s*:\s*(\d+)').Groups[1].Value
if (-not $portS) { $portS = [regex]::Match($raw, '"imap_ssl_port"\s*:\s*(\d+)').Groups[1].Value }
$port  = if ($portS) { [int]$portS } else { 993 }

if (-not $email -or -not $pass -or -not $imapHost) { Write-Output 'EMAIL_CHECK_FAIL: config_incomplete'; exit 0 }

function Read-LineSafe($sr) { try { $sr.ReadLine() } catch { $null } }

try {
  $tcp = New-Object System.Net.Sockets.TcpClient($imapHost, $port)
  $ssl = New-Object System.Net.Security.SslStream($tcp.GetStream(), $false, ({ $true }))
  $ssl.AuthenticateAsClient($imapHost)
  $sr = New-Object System.IO.StreamReader($ssl)
  $sw = New-Object System.IO.StreamWriter($ssl)
  $sw.NewLine = "`r`n"
  $sw.AutoFlush = $true

  $null = Read-LineSafe $sr
  $sw.WriteLine("a001 LOGIN $email $pass")
  $login = Read-LineSafe $sr
  if ($login -notmatch 'a001 OK') { Write-Output 'EMAIL_CHECK_FAIL: imap_login_failed'; exit 0 }

  $sw.WriteLine('a002 SELECT INBOX')
  for ($i=0; $i -lt 50; $i++) {
    $l = Read-LineSafe $sr
    if ($null -eq $l) { break }
    if ($l -match '^a002 ') { break }
  }

  $sw.WriteLine('a003 SEARCH ALL')
  $idsLine = ''
  for ($i=0; $i -lt 50; $i++) {
    $l = Read-LineSafe $sr
    if ($null -eq $l) { break }
    if ($l -match '^\* SEARCH') { $idsLine = $l }
    if ($l -match '^a003 ') { break }
  }

  $ids = @()
  if ($idsLine -match '^\* SEARCH\s*(.*)$') {
    $ids = $Matches[1].Trim().Split(' ') | Where-Object { $_ -match '^\d+$' }
  }

  if ($ids.Count -eq 0) { Write-Output 'NO_REPLY'; exit 0 }

  $latest = [int]($ids[-1])
  $lastSeen = 0
  if (Test-Path $statePath) {
    try {
      $st = Get-Content $statePath -Raw | ConvertFrom-Json
      if ($st.lastSeenId) { $lastSeen = [int]$st.lastSeenId }
    } catch { $lastSeen = 0 }
  }

  if ($lastSeen -eq 0) {
    @{ lastSeenId = $latest; updatedAt = (Get-Date).ToString('o') } | ConvertTo-Json | Set-Content $statePath -Encoding UTF8
    Write-Output 'NO_REPLY'
    exit 0
  }

  $newIds = $ids | Where-Object { [int]$_ -gt $lastSeen }
  if ($newIds.Count -eq 0) {
    @{ lastSeenId = $latest; updatedAt = (Get-Date).ToString('o') } | ConvertTo-Json | Set-Content $statePath -Encoding UTF8
    Write-Output 'NO_REPLY'
    exit 0
  }

  $take = $newIds | Select-Object -Last 5
  $items = @()
  foreach ($id in $take) {
    $tag = "a$id"
    $sw.WriteLine("$tag FETCH $id BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)]")
    $from=''; $subject=''; $date=''
    for ($j=0; $j -lt 80; $j++) {
      $l = Read-LineSafe $sr
      if ($null -eq $l) { break }
      if ($l -match '^From:\s*(.*)$') { $from = $Matches[1].Trim() }
      elseif ($l -match '^Subject:\s*(.*)$') { $subject = $Matches[1].Trim() }
      elseif ($l -match '^Date:\s*(.*)$') { $date = $Matches[1].Trim() }
      elseif ($l -match "^$tag ") { break }
    }
    if (-not $subject) { $subject = '(no subject)' }
    if (-not $from) { $from = '(unknown sender)' }
    $urgent = if ($subject -match 'OTP|urgent|immediate|alert|error|fail|code|verify') { 'high' } else { 'normal' }
    $items += "- from: $from ; date: $date ; subject: $subject ; urgency: $urgent"
  }

  @{ lastSeenId = $latest; updatedAt = (Get-Date).ToString('o') } | ConvertTo-Json | Set-Content $statePath -Encoding UTF8

  Write-Output ("NEW_MAIL_COUNT: {0}" -f $newIds.Count)
  $items | ForEach-Object { Write-Output $_ }

  $sw.WriteLine('a999 LOGOUT')
  $tcp.Close()
}
catch {
  Write-Output ('EMAIL_CHECK_FAIL: ' + $_.Exception.Message)
}
