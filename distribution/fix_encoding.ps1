# UTF-8 with BOM 编码转换脚本
# 用于修复批处理文件的乱码问题

$files = @(
    'tools.bat',
    'register_plugin.bat',
    'unregister_plugin.bat'
)

Write-Host "正在转换批处理文件为 UTF-8 with BOM 编码..." -ForegroundColor Cyan

foreach ($file in $files) {
    $filePath = Join-Path $PSScriptRoot $file
    if (Test-Path $filePath) {
        # 读取文件内容
        $content = Get-Content $filePath -Raw
        
        # 以 UTF-8 with BOM 格式保存
        $utf8BOM = New-Object System.Text.UTF8Encoding $true
        [System.IO.File]::WriteAllText($filePath, $content, $utf8BOM)
        
        Write-Host "✓ 已转换：$file" -ForegroundColor Green
    } else {
        Write-Host "✗ 文件不存在：$file" -ForegroundColor Red
    }
}

Write-Host "`n 所有文件转换完成！" -ForegroundColor Green
Write-Host "请重新运行安装程序以应用更改。" -ForegroundColor Yellow
