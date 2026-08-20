# Get-FreshIdToken.ps1
#
# Google refresh_token으로 새 id_token을 발급받는 스크립트.
# 사용법:
#   1) 아래 $ClientSecret 과 $RefreshToken 값을 채워 넣거나,
#      환경변수(WORKMATE_OAUTH_CLIENT_SECRET, WORKMATE_REFRESH_TOKEN)로 설정
#   2) . .\Get-FreshIdToken.ps1   (dot-source로 불러오기)
#   3) Get-FreshIdToken            (함수 실행 -> id_token 문자열 반환 + 클립보드 복사)

$ClientId = "295781403068-9kr1e17mhm9aeutv75pmh243q7mcg65s.apps.googleusercontent.com"

function Get-FreshIdToken {
    param(
        [string]$ClientSecret = $env:WORKMATE_OAUTH_CLIENT_SECRET,
        [string]$RefreshToken = $env:WORKMATE_REFRESH_TOKEN,
        [switch]$CopyToClipboard = $true
    )

    if (-not $ClientSecret) {
        Write-Error "ClientSecret이 없습니다. -ClientSecret 파라미터로 넘기거나 `$env:WORKMATE_OAUTH_CLIENT_SECRET`을 설정하세요."
        return
    }
    if (-not $RefreshToken) {
        Write-Error "RefreshToken이 없습니다. -RefreshToken 파라미터로 넘기거나 `$env:WORKMATE_REFRESH_TOKEN`을 설정하세요."
        return
    }

    $body = @{
        client_id     = $ClientId
        client_secret = $ClientSecret
        refresh_token = $RefreshToken
        grant_type    = "refresh_token"
    }

    try {
        $response = Invoke-RestMethod -Method Post -Uri "https://oauth2.googleapis.com/token" -Body $body
    }
    catch {
        Write-Error "토큰 갱신 실패: $($_.Exception.Message)"
        if ($_.ErrorDetails.Message) {
            Write-Error $_.ErrorDetails.Message
        }
        return
    }

    if (-not $response.id_token) {
        Write-Error "응답에 id_token이 없습니다. refresh_token이 만료/취소되었을 수 있습니다 (재로그인 필요)."
        Write-Output $response
        return
    }

    Write-Host "새 id_token 발급 완료 (만료까지 약 $($response.expires_in)초)" -ForegroundColor Green

    if ($CopyToClipboard) {
        Set-Clipboard -Value $response.id_token
        Write-Host "클립보드에 복사됨. 바로 붙여넣기(Ctrl+V) 하세요." -ForegroundColor Cyan
    }

    return $response.id_token
}

Write-Host "Get-FreshIdToken 함수가 로드되었습니다. 'Get-FreshIdToken' 실행하면 새 id_token을 받아옵니다." -ForegroundColor Yellow
