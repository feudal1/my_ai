# MyTools 分发指南

## 📦 快速开始

### 方法一：自动打包（推荐）

运行 Python 打包脚本，自动生成所有格式的安装包：

```bash
cd e:\code\my_ai\distribution
python build_distribution.py
```

输出目录：`e:\code\my_ai\distribution\output\`

---

## 🎯 三种分发格式

### 1. MSI 安装程序（企业级）
**文件**: `MyTools_1.0.0.msi`

**特点**:
- ✅ Windows 标准安装格式
- ✅ 支持组策略部署
- ✅ 完整的安装/卸载功能
- ✅ 自动注册 SolidWorks 插件
- ✅ 自动配置环境变量

**适用场景**:
- 企业批量部署
- 需要集中管理的环境
- 正式版本发布

**安装方式**:
```bash
# 双击运行
MyTools_1.0.0.msi

# 或命令行静默安装
msiexec /i MyTools_1.0.0.msi /quiet

# 指定安装路径
msiexec /i MyTools_1.0.0.msi INSTALLDIR="C:\MyTools" /quiet
```

**卸载方式**:
```bash
# 控制面板卸载
# 或命令行
msiexec /x {ProductCode} /quiet
```

**依赖**:
- WiX Toolset v3.14+ (仅构建时需要)
- .NET Framework 4.8
- .NET 10.0 (ctools 运行时)

---

### 2. 自解压 EXE（个人用户）
**文件**: `MyTools_1.0.0_setup.exe`

**特点**:
- ✅ 单文件分发
- ✅ 图形化安装向导
- ✅ 无需额外工具
- ✅ 自动解压并安装

**适用场景**:
- 个人用户使用
- 网络分发
- 简单部署

**安装方式**:
```bash
# 双击运行
MyTools_1.0.0_setup.exe

# 或命令行静默安装
MyTools_1.0.0_setup.exe /S
```

**依赖**:
- 7-Zip (构建时需要)
- .NET Framework 4.8
- .NET 10.0

---

### 3. 便携 ZIP 包（免安装）
**文件**: `MyTools_1.0.0_portable.zip`

**特点**:
- ✅ 解压即用
- ✅ 无需安装
- ✅ 不写注册表
- ✅ 可放在 U 盘

**适用场景**:
- 临时使用
- 多版本并存
- 受限环境（无管理员权限）

**使用方式**:
```bash
# 1. 解压到任意位置
# 2. 运行 install.bat（可选，用于注册插件和添加 PATH）
# 3. 或直接在解压目录运行:
.\tools.bat help
.\ptool.exe --help
.\ctool.exe --help
```

**依赖**:
- .NET Framework 4.8
- .NET 10.0

---

## 🛠️ 构建说明

### 前置要求

#### 必需软件:
1. **.NET SDK 10.0** - 编译 C# 项目
2. **Python 3.8+** - 运行打包脚本
3. **Visual Studio 2022** - 编译 C++ 组件（如需要）

#### 可选工具（根据目标格式）:
4. **WiX Toolset v3.14** - 生成 MSI
5. **7-Zip** - 生成 SFX 和 ZIP

### 手动构建步骤

#### 步骤 1: 编译项目
```bash
# 编译 plugin
cd e:\code\my_ai\my_c#\plugin
dotnet build --configuration Release

# 编译 ctools
cd e:\code\my_ai\my_c#\ctools
dotnet build --configuration Release
```

#### 步骤 2: 准备文件
```
distribution/build/
├── plugin_files/        # plugin.dll 及相关文件
├── ctools_files/        # ctool.exe 及相关文件
├── python_tools/        # ptool.exe 及 Python 模块
├── register_plugin.bat  # 插件注册脚本
├── unregister_plugin.bat# 插件卸载脚本
├── tools.bat           # 统一启动脚本
└── install.bat         # 安装脚本
```

#### 步骤 3: 生成 MSI（需要 WiX）
```bash
# 编译 WiX 源
candle.exe -dPluginDir=build\plugin_files ^
           -dCToolsDir=build\ctools_files ^
           -dPythonToolsDir=build\python_tools ^
           -out build\installer.wixobj ^
           installer.wxs

# 链接生成 MSI
light.exe -out output\MyTools_1.0.0.msi build\installer.wixobj
```

#### 步骤 4: 生成 SFX（需要 7-Zip）
```bash
# 压缩文件
"C:\Program Files\7-Zip\7z.exe" a build\temp.7z build\*

# 合并 SFX 模块
copy /b "7zSD.sfx" + sfx_config.txt + build\temp.7z output\MyTools_1.0.0_setup.exe
```

#### 步骤 5: 生成 ZIP
```bash
# 使用 PowerShell 压缩
Compress-Archive -Path build\* -DestinationPath output\MyTools_1.0.0_portable.zip -Force
```

---

## 📋 版本控制

### 版本号设置
修改以下文件中的版本号：

1. `build_distribution.py` - `VERSION = "1.0.0"`
2. `installer.wxs` - `Version="1.0.0"`
3. `README.md` - 本文档中的版本号

### 发布清单
每次发布前检查：

- [ ] 所有测试通过
- [ ] 更新版本号
- [ ] 更新 CHANGELOG.md
- [ ] 生成三种格式安装包
- [ ] 验证安装包功能
- [ ] 更新下载链接

---

## 🔧 自定义配置

### 修改产品名称
编辑文件：
- `installer.wxs`: `Name="MyTools - SolidWorks Plugin and Utilities"`
- `build_distribution.py`: `PRODUCT_NAME = "MyTools"`
- `tools.bat`: 帮助信息中的产品名

### 修改安装路径
MSI 默认安装到：`C:\Program Files\MyTools\`

修改 `installer.wxs`:
```xml
<Directory Id="ProgramFilesFolder">
  <Directory Id="INSTALLFOLDER" Name="YourProductName" />
</Directory>
```

### 修改 GUID
每个组件需要唯一 GUID：

生成新 GUID:
```powershell
[System.Guid]::NewGuid().ToString()
```

替换 `installer.wxs` 中的所有 GUID。

---

## 📊 分发包大小对比

| 格式 | 大小（约） | 解压后 | 安装时间 |
|------|-----------|--------|----------|
| MSI | 50 MB | 150 MB | ~30 秒 |
| SFX | 55 MB | 150 MB | ~20 秒 |
| ZIP | 45 MB | 150 MB | ~5 秒 |

*实际大小取决于包含的文件数量*

---

## 🎓 最佳实践

### 企业部署
1. 使用 MSI + 组策略部署
2. 创建转换文件 (.mst) 自定义安装
3. 使用 WSUS 或 SCCM 分发

示例组策略命令：
```batch
msiexec /i \\server\share\MyTools_1.0.0.msi /quiet /norestart
```

### 网络分发
1. 使用 SFX 格式
2. 提供 SHA256 校验和
3. 附带详细的安装说明

### 开发测试
1. 使用便携 ZIP 格式
2. 快速部署测试环境
3. 避免污染系统注册表

---

## ❓ 常见问题

### Q: 安装时提示"需要管理员权限"
A: MSI 和 SFX 都需要管理员权限来：
- 写入 Program Files 目录
- 注册 COM 组件（SolidWorks 插件）
- 修改系统 PATH 环境变量

解决方案：右键点击安装包，选择"以管理员身份运行"

### Q: SolidWorks 插件无法加载
A: 检查以下步骤：
1. 确认 plugin.dll 已正确注册
2. 运行 `regasm plugin.dll /codebase` 手动注册
3. 在 SolidWorks 中检查：工具 → 插件 → 勾选 MyTools

### Q: 命令行工具无法识别
A: 确保已添加到 PATH：
```bash
# 检查是否在 PATH 中
echo %PATH% | findstr MyTools

# 手动添加（临时）
setx PATH "%PATH%;C:\Program Files\MyTools"
```

### Q: 如何完全卸载？
A: 三种方式：
1. 控制面板 → 程序和功能 → 卸载 MyTools
2. 运行：`msiexec /x {ProductCode}`
3. 手动删除：
   - 删除安装目录
   - 清理注册表项
   - 从 PATH 移除

---

## 📞 技术支持

遇到问题？请提供：
1. 操作系统版本
2. .NET Framework 版本
3. SolidWorks 版本（如适用）
4. 错误日志或截图

---

## 📝 许可证

请在此处添加您的许可证信息。

---

**最后更新**: 2026-03-14  
**版本**: 1.0.0  
**作者**: Your Company
