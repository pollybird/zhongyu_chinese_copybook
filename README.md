# 钟毓汉字字帖生成器（Electron 版）

**中文** | [English](README_EN.md)

生成汉字字帖的桌面应用。输入汉字内容，选择格子类型与生成模式，即可实时预览，并可直接打印、打印预览或导出为 PDF。

当前版本：**2.0.1**（自 2.0.0 起由 PyQt6 重构为 Electron，见 [UPGRADE.md](UPGRADE.md)）

版权所有 (c) 2026 泰州姜堰钟毓信息技术有限公司 · 官网：https://www.tzzhy.cn/

## 功能特性

- **四种格子类型**：米字格、田字格、回宫格、作文纸
- **四种生成模式**：描红、抄写、描红+抄写、纯字帖
- **实时预览**：Canvas 渲染 595×842 页面，PageUp/PageDown 翻页
- **OCR 截图识别**：框选屏幕任意区域，自动识别文字填入内容框，支持中文简体 / 英文 / 中英混合
- **多标签页**：同时编辑多个工程，未保存关闭有提示
- **自定义头部字段**：最多 3 个（如班级、姓名、学号），支持标题与页码
- **工程文件**：`.zyzcb` 格式，与原版 PyQt6 v1.0.0 双向兼容，已注册文件关联（双击打开）
- **打印与打印预览**：无需先导出 PDF，**Ctrl+P** 直接弹出系统打印对话框；打印预览窗口可逐页查看排版、缩放与页码跟随
- **PDF 导出**：A4 多页，描红/网格高清渲染；打印与导出共用同一 A4 渲染管线，效果完全一致
- **中英文界面自动适配**（2.0.1 新增）：应用启动时读取操作系统语言，中文系统显示中文界面，其他语言以英文兜底；`.zyzcb` 工程文件格式不受影响
- **字体选择**：自动获取系统已安装的所有字体，支持自定义字体

## 字体建议

为保证字帖的显示效果和打印质量，**建议用户自行下载安装以下字体**：

- **田英章楷书** — 规范楷书，适合学生临摹
- **方正硬笔书法楷体** — 硬笔书法风格，笔画清晰
- **方正硬笔楷书简体** — 标准硬笔楷书

安装字体后，在应用的「调整设置」→「字体」下拉菜单中即可选择使用。

> 未安装上述字体时，应用会回退到系统默认字体（如楷体、宋体等），但显示效果可能不如专业书法字体。

## 技术栈

- Electron 33 + electron-vite 2 + Vite 5（原生 JavaScript，无前端框架）
- Canvas 2D 排版渲染，tesseract.js 离线 OCR（内置 tessdata_fast 语言数据）
- electron-builder 跨平台打包（Windows NSIS、Linux AppImage/deb/rpm、macOS zip/dmg）

## 开发

```bash
# 安装依赖（国内网络建议先设置镜像）
npm install --registry=https://registry.npmmirror.com
# Electron 二进制下载较慢时：
# export ELECTRON_MIRROR=https://npmmirror.com/mirrors/electron/

# 开发模式
npm run dev

# 构建
npm run build

# 打包当前平台安装包（输出到 dist/）
npm run dist

# 指定平台 / 架构
npx electron-builder --linux AppImage deb rpm   # 可选 --x64 / --arm64
npx electron-builder --win nsis
npx electron-builder --mac zip
```

要求 Node.js 18 及以上。

## 使用说明

1. 在左侧「输入内容」多行文本框输入要生成字帖的汉字内容，或点击**截图识别**框选屏幕文字自动填入
2. 设置字体、字体大小、位置偏移等参数
3. 选择格子类型（米字格 / 田字格 / 回宫格 / 作文纸）与生成模式（描红 / 抄写 / 描红+抄写 / 纯字帖）
4. 可添加自定义头部字段（班级、姓名等）
5. 设置页码格式和位置
6. 保存 / 加载 `.zyzcb` 工程文件
7. 点击**导出PDF**生成字帖文件，或使用**文件菜单 → 打印 / 打印预览**直接打印

### 打印与打印预览

- **文件 → 打印（Ctrl+P）**：按当前工程渲染全部页面后弹出系统打印对话框，选择打印机即可直接打印
- **文件 → 打印预览**：打开独立预览窗口，逐页查看排版效果，支持缩放（适应页宽 / 40%~200%）、页码跟随滚动，也可在窗口中直接点击**打印**
- 打印与 PDF 导出共用同一 A4 渲染管线（192DPI），效果完全一致

### OCR 截图识别

- 点击输入框下方的**截图识别**按钮，选择识别语言（中文简体 / 英文 / 中英混合）
- 屏幕被冻结后拖拽框选要识别的文字区域
- **Enter** 或双击确认，**Esc** 取消；识别结果自动填入输入内容框
- OCR 语言数据已内置，无需联网

### 快捷键

| 快捷键 | 功能 |
|---|---|
| Ctrl+N | 新建工程 |
| Ctrl+O | 打开工程 |
| Ctrl+S | 保存工程 |
| Ctrl+Shift+S | 另存为 |
| Ctrl+P | 打印 |
| Ctrl+F | 导出 PDF |
| PageUp / PageDown | 预览翻页 |
| Alt+F / Alt+E / Alt+H | 打开文件 / 编辑 / 帮助菜单 |

## 目录结构

```
├── src/
│   ├── main/              # 主进程（窗口、菜单、IPC、OCR、打印与 PDF 导出）
│   ├── preload/           # 预加载脚本（contextIsolation 安全桥接）
│   ├── renderer/          # 渲染进程（index.html 主界面、print.html 打印渲染、preview.html 打印预览、sel.html 截图选区）
│   └── shared/            # i18n.js 共用翻译模块（主进程与渲染进程共用）
│       └── src/
│           ├── engine/    # copybook.js 排版引擎、zyzcb-format.js 工程文件读写
│           └── assets/    # 协议文本
├── resources/             # 图标、版权文本、OCR 语言数据（ocr-data）
└── out/                   # 构建产物
```

## 许可证

[Apache-2.0](LICENSE)
