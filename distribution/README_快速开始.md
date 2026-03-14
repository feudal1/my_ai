# MyTools 快速使用指南

## 🚀 一键打包

### Windows 用户（最简单）
双击运行：
```
distribution\build-all.bat
```

### 或使用 Python
```bash
cd e:\code\my_ai\distribution
python quick_build.py
```

输出目录：`distribution\output\`

---

## 📦 生成的文件格式

### ✓ 便携版 ZIP (已生成)
**文件**: `MyTools_1.0.0_portable.zip` (~18MB)

**使用方法**:
1. 解压到任意位置
2. 双击 `install.bat`（可选，用于注册插件和添加 PATH）
3. 或直接在解压目录运行命令

**命令行使用**:
```bash
# 查看帮助
tools.bat help

# 使用 Python 工具
ptool.exe --help
ptool.exe pdf merge --files a.pdf b.pdf

# 使用 C# 工具
ctool.exe --help
ctool.exe <command-name>
```

---

## 🎯 如何获取完整安装包

### 方法 1: 安装 WiX Toolset（生成 MSI）
1. 下载：https://wixtoolset.org/
2. 安装后重新运行打包脚本
3. 将生成 `MyTools_1.0.0.msi`

### 方法 2: 安装 7-Zip（生成 SFX）
1. 下载：https://www.7-zip.org/
2. 安装后重新运行打包脚本
3. 将生成 `MyTools_1.0.0_setup.exe`

---

## 📋 分发建议

### 个人使用/小团队
→ 直接分享 **ZIP 包** 即可

### 企业部署
→ 安装 WiX 后生成 **MSI 安装包**

### 网络分发
→ 安装 7-Zip 后生成 **SFX 自解压包**

---

## ✅ 当前可用版本

你现在可以使用：
- ✓ **便携版 ZIP** - 解压即用，无需安装

其他格式需要安装额外工具（可选）

---

## 📞 需要帮助？

查看详细文档：`DISTRIBUTION_README.md`
