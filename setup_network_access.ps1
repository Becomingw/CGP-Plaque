# WSL网络访问配置脚本
# 在Windows PowerShell中以管理员身份运行此脚本

Write-Host "=== WSL网络访问配置 ===" -ForegroundColor Green

# 获取WSL IP地址
$wslIP = "172.19.220.112"  # 从之前的检查中获取
$port1 = 5001
$port2 = 5002

Write-Host "WSL IP地址: $wslIP" -ForegroundColor Yellow
Write-Host "应用端口: $port1, $port2" -ForegroundColor Yellow

# 1. 配置端口转发
Write-Host "`n1. 配置端口转发..." -ForegroundColor Cyan
try {
    # 删除可能存在的旧规则
    netsh interface portproxy delete v4tov4 listenport=$port1 2>$null
    netsh interface portproxy delete v4tov4 listenport=$port2 2>$null
    
    # 添加新的端口转发规则
    netsh interface portproxy add v4tov4 listenport=$port1 listenaddress=0.0.0.0 connectport=$port1 connectaddress=$wslIP
    netsh interface portproxy add v4tov4 listenport=$port2 listenaddress=0.0.0.0 connectport=$port2 connectaddress=$wslIP
    
    Write-Host "✓ 端口转发配置成功 (端口 $port1 和 $port2)" -ForegroundColor Green
} catch {
    Write-Host "✗ 端口转发配置失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 2. 配置Windows防火墙
Write-Host "`n2. 配置Windows防火墙..." -ForegroundColor Cyan
try {
    # 添加入站规则
    New-NetFirewallRule -DisplayName "AHA_LLM_App_$port1" -Direction Inbound -Protocol TCP -LocalPort $port1 -Action Allow -Profile Any 2>$null
    New-NetFirewallRule -DisplayName "AHA_LLM_App_$port2" -Direction Inbound -Protocol TCP -LocalPort $port2 -Action Allow -Profile Any 2>$null
    Write-Host "✓ 防火墙规则添加成功 (端口 $port1 和 $port2)" -ForegroundColor Green
} catch {
    Write-Host "✗ 防火墙规则添加失败: $($_.Exception.Message)" -ForegroundColor Red
}

# 3. 显示当前配置
Write-Host "`n3. 当前端口转发配置:" -ForegroundColor Cyan
netsh interface portproxy show all

Write-Host "`n4. 当前防火墙规则:" -ForegroundColor Cyan
Get-NetFirewallRule -DisplayName "AHA_LLM_App_*" | Select-Object DisplayName, Direction, Action, Protocol, LocalPort

# 5. 获取Windows主机IP地址
Write-Host "`n5. 网络访问信息:" -ForegroundColor Cyan
$hostIPs = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.*" } | Select-Object -ExpandProperty IPAddress

Write-Host "局域网访问地址:" -ForegroundColor Yellow
foreach ($ip in $hostIPs) {
    Write-Host "  端口 $port1`: http://$ip`:$port1" -ForegroundColor White
    Write-Host "  端口 $port2`: http://$ip`:$port2" -ForegroundColor White
}

Write-Host "`n外网访问需要:" -ForegroundColor Yellow
Write-Host "  1. 路由器端口转发 (外网端口 -> Windows主机IP:$port1 和 $port2)" -ForegroundColor White
Write-Host "  2. 动态DNS服务 (如果IP是动态的)" -ForegroundColor White

Write-Host "`n=== 配置完成 ===" -ForegroundColor Green
Write-Host "请确保WSL中的应用正在运行: python run_production.py" -ForegroundColor Yellow
