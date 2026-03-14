# 安装程序修复说明

## 修复的问题

### 1. plugin.dll 查找失败问题
**问题描述**: 安装时提示"错误：未找到 plugin.dll"

**原因**: 
- `register_plugin.bat` 和 `unregister_plugin.bat` 脚本只在脚本同级目录查找 `plugin.dll`
- 实际文件在 `plugin_files` 子目录中

**解决方案**:
修改了两个脚本，使其能够在多个位置查找 plugin.dll：
- `plugin_files\plugin.dll` (便携版/ZIP 结构)
- `plugin.dll` (MSI 安装后的扁平结构)

**修改的文件**:
- `distribution/register_plugin.bat`
- `distribution/unregister_plugin.bat`

### 2. PATH 环境变量截断警告
**问题描述**: 
```
WARNING: The data being saved is truncated to 1024 characters.
```

**原因**: 
- Windows 环境变量 PATH 有 1024 字符限制
- 使用 `%LOCALAPPDATA%\MyTools` 路径较长（约 30+ 字符）
- 当系统 PATH 已经很长时，添加新路径可能超出限制

**解决方案**:
1. 优化了 `install.bat` 中的 PATH 处理逻辑
2. 添加了 PATH 长度检测，接近限制时给出警告
3. 建议用户使用更短的安装路径（如 `C:\MyTools`）
4. 改进了错误处理，失败时给出明确提示

**修改的文件**:
- `distribution/build_distribution.py` 中的 `create_install_bat()` 函数

### 3. 插件注册权限问题
**问题描述**: 插件注册需要管理员权限，但普通用户运行时无法注册

**解决方案**:
- 在 `install.bat` 中添加错误提示
- 告知用户如需注册插件，需以管理员身份重新运行脚本
- 即使注册失败，也不影响其他功能的使用

## 测试方法

### 测试修复后的安装程序

1. **构建分发包**:
   ```bash
   cd distribution
   python build_distribution.py
   ```

2. **测试便携版**:
   ```powershell
   # 解压到测试目录
   Expand-Archive -Path "output\MyTools_1.0.0_portable.zip" -DestinationPath "test_install"
   
   # 运行安装（建议以管理员身份）
   cd test_install
   .\install.bat
   ```

3. **验证安装**:
   - 检查文件是否复制到 `%LOCALAPPDATA%\MyTools`
   - 检查 PATH 环境变量是否添加
   - 打开新命令行窗口，运行 `tools help`

### 预期输出

成功的安装应该显示：
```
============================================
MyTools 安装程序
============================================

正在安装到：C:\Users\xxx\AppData\Local\MyTools

复制文件...
30 File(s) copied

注册 SolidWorks 插件...
插件注册成功  [或：注意：插件注册失败，可能需要以管理员身份运行此脚本]

添加到系统 PATH...
已添加到系统 PATH

============================================
安装完成！
============================================

请重新打开命令提示符窗口，然后运行:
  tools help

注意：如需注册 SolidWorks 插件，请以管理员身份重新运行此脚本
```

## 使用建议

### 推荐安装方式

1. **企业部署**: 使用 MSI 安装程序（需要 WiX Toolset）
   ```bash
   # 生成 MSI
   msiexec /i MyTools_1.0.0.msi /quiet
   ```

2. **个人用户**: 使用自解压 EXE（需要 7-Zip）
   ```bash
   # 生成 SFX
   # 双击运行生成的 .exe 文件
   ```

3. **便携使用**: 直接解压 ZIP
   ```bash
   # 解压到任意位置
   Expand-Archive MyTools_1.0.0_portable.zip -DestinationPath C:\MyTools
   # 手动添加到 PATH
   ```

### 最短路径安装

为避免 PATH 长度警告，建议使用较短的安装路径：

```batch
:: 修改 install.bat 第 12 行
set INSTALL_DIR=C:\MyTools
```

而不是默认的：
```batch
set INSTALL_DIR=%LOCALAPPDATA%\MyTools
```

## 技术细节

### register_plugin.bat 的查找逻辑

```batch
:: 优先查找 plugin_files 子目录（便携版结构）
if exist "%SCRIPT_DIR%plugin_files\plugin.dll" (
    set PLUGIN_DLL=%SCRIPT_DIR%plugin_files\plugin.dll
) 
:: 回退到同级目录（MSI 安装结构）
else if exist "%SCRIPT_DIR%plugin.dll" (
    set PLUGIN_DLL=%SCRIPT_DIR%plugin.dll
) 
:: 报错
else (
    echo 错误：未找到 plugin.dll
    exit /b 1
)
```

### PATH 长度检测

```batch
:: 动态检测 PATH 长度
for /L %%i in (1000,1,2048) do (
    if "!NEWPATH:~%%i,1!"=="" (
        if %%i lss 1024 (
            echo WARNING: PATH 环境变量接近长度限制
        )
        goto :check_done
    )
)
```

## 已知限制

1. **MSI 生成**: 需要安装 WiX Toolset v3.14+
2. **SFX 生成**: 需要 7-Zip 和 7zSD.sfx 模块
3. **插件注册**: 需要管理员权限
4. **PATH 长度**: Windows 限制为 1024 字符

## 后续改进建议

1. 提供自定义安装路径选项
2. 创建单独的快捷方式来设置临时 PATH
3. 考虑使用 PowerShell 脚本替代批处理以获得更好的错误处理
4. 添加卸载时的 PATH 清理逻辑

## 相关文件清单

### 源文件（需要时修改）
- `distribution/register_plugin.bat` - 插件注册脚本
- `distribution/unregister_plugin.bat` - 插件注销脚本
- `distribution/tools.bat` - 命令行工具入口
- `distribution/build_distribution.py` - 打包构建脚本

### 生成的文件（自动创建）
- `distribution/build/install.bat` - 安装脚本（由 Python 生成）
- `distribution/output/MyTools_1.0.0_portable.zip` - 便携版

---

**最后更新**: 2026-03-14  
**版本**: 1.0.0
