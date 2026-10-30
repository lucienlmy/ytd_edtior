<div align="center">

# YTD 纹理编辑器

**面向 GTA V / FiveM `.ytd` 纹理字典的桌面图像编辑器。**

打开一个 `.ytd`，在其纹理上绘制、添加文字和图片，保存出一个全新的、合法的
`.ytd`，可直接放进 FiveM 资源中使用。

[English](README.md) | **简体中文**

[![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-41CD52?logo=qt&logoColor=white)](https://doc.qt.io/qtforpython/)
[![NumPy](https://img.shields.io/badge/codecs-NumPy-013243?logo=numpy&logoColor=white)](https://numpy.org/)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey)](#安装)
[![License](https://img.shields.io/badge/license-MIT-green)](../LICENSE)

</div>


<img width="1586" height="1008" alt="image" src="https://github.com/user-attachments/assets/0d2dc64c-7de2-4454-9105-8db4ee6a6d55" />


```
打开 .ytd  ->  选中纹理  ->  绘制 / 加文字 / 放图片  ->  另存为 YTD
```

---

## 目录

- [为什么需要它](#为什么需要它)
- [功能特性](#功能特性)
- [安装](#安装)
- [运行](#运行)
- [工作流程](#工作流程)
- [上传图片](#上传图片)
- [快捷键](#快捷键)
- [支持的纹理格式](#支持的纹理格式)
- [YTD 支持是如何实现的](#ytd-支持是如何实现的)
- [已知限制](#已知限制)
- [故障排查](#故障排查)
- [项目结构](#项目结构)
- [无界面调用 core](#无界面调用-core)
- [参与贡献](#参与贡献)
- [致谢](#致谢)
- [许可证](#许可证)

---

## 为什么需要它

以往修改 `.ytd` 里的一张纹理，需要三个工具来回折腾：用一个工具导出 DDS，
用另一个工具编辑，再用第三个工具导回，然后祈祷这个字典还能在游戏里正常加载。

本工具把这些全部收进一个窗口，而且——关键在于——**不需要重建资源**。只有你
真正改动过的像素字节会被写回；每个名字、哈希、指针以及未改动的纹理都按字节
原样保留。详见 [YTD 支持是如何实现的](#ytd-支持是如何实现的)。

---

## 功能特性

### YTD 相关
- 读取字典中的每张纹理：名称、尺寸、格式、mip 层数
- **按字节原样**保留名称、哈希、结构和未编辑的纹理
- 写出合法的新 `.ytd`，并且**在落盘前先重新解析一遍结果**
- 除非你明确要求，否则绝不覆盖原始文件
- 单张纹理可导出为 PNG，或带着原始表面字节导出为 DDS

### 画布
- 按原始分辨率编辑 — 缩放 2%–6400%，平移、适配窗口、复位
- 最近邻放大，放大后 texel 依然锐利不糊
- 完整的 alpha 支持，并带透明棋盘格底
- 40 级撤销 / 重做

### 工具
- **画笔** — 大小、颜色、不透明度、可选平滑。每一笔先画在独立图层上，
  松开时一次性合成，所以同一笔里重叠的线段不会叠成一团更深的色块。
- **橡皮** — 擦成真正的透明
- **文字** — 任意已安装字体、字号、颜色、粗体/斜体；可移动、可修改、可删除，
  只在你确认时才烘焙进纹理
- **上传图片** — 把图片作为浮动层放进来：拖动移动，拖角缩放，可精确填写
  宽高 / 位置 / 不透明度，并可锁定比例
- **矩形 / 椭圆 / 直线** — 填充或描边
- **取色器**
- 清空、旋转、翻转、调整尺寸、裁切、用图片替换纹理
- 任何时候都能把某张纹理还原为初始状态

---

## 安装

需要 **Python 3.11 或更新版本**（开发与测试基于 3.12）。

```bash
git clone https://github.com/0xFL1n7/ytd_edtior.git
pip install -r requirements.txt
```

| 依赖包 | 版本 | 用途 |
|---|---|---|
| `PySide6` | >= 6.6 | Qt 6 图形界面 |
| `numpy` | >= 1.24 | 纹理编码 / 解码 |
| `Pillow` | >= 10.0 | PNG/JPG 导入导出与 BC7 解码 |

> [!NOTE]
> BC7 解码的硬性下限是 Pillow **9.4+**；固定到 10.0 是为了留出足够余量。

如果缺少依赖，程序会明确告诉你是哪一个、为什么需要，而不是抛一个裸的
`ImportError` 就退出。

<details>
<summary><b>使用虚拟环境（推荐）</b></summary>

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```
</details>

---

## 运行

```bash
cd ytd_edtior
python main.py
```

或者在上一级目录运行：

```bash
python -m ytd_edtior.main
```

> [!NOTE]
> 仓库目录名是 `ytd_edtior`（上游笔误）。入口按目录实际名称导入包，所以你把
> 它改成 `ytd_editor` 也能正常启动 —— 只需把 `-m` 以及下面的库导入路径换成
> 新名字即可。

也可以直接带上文件路径：

```bash
python main.py path/to/vehicle.ytd
```

---

## 工作流程

1. **打开 YTD**（`Ctrl+O`），选一个 `.ytd`。
2. 左侧列表会填入字典中的所有纹理 —— 缩略图、名称、尺寸和格式。点击即可载入。
3. 开始编辑：
   - **画笔**（`B`）— 大小、颜色、不透明度
   - **橡皮**（`E`）— 擦成真正的透明
   - **文字**（`T`）— 点击放置，拖动移动，在右侧面板调参，
     最后用 **应用文字** 烘焙进纹理
   - **矩形** / **椭圆** / **直线**，填充或描边
   - **取色**（`I`）— 从纹理中取一个颜色
   - **上传图片** — 见 [上传图片](#上传图片)
4. 纹理之间随意切换 —— 修改按纹理各自保存，改过的会在列表里标一个小圆点。
5. **另存为 YTD**（`Ctrl+Shift+S`）。每张改过的纹理都会按其原始格式重新编码、
   原位修补，结果在写盘之前会先重新解析并校验一遍。

输出默认名为 `<name>_edited.ytd`。**原始文件绝不会被覆盖**，除非你有意选中
它的准确路径 —— 而且即便那样，也会先弹一个明确的确认框。

---

## 上传图片

右侧面板里的 **上传图片...** 会把图片作为*浮动层*放到画布上 —— 在你确认之前
不会写入纹理任何东西。浮动期间你可以：

- **拖动**它到纹理上的任意位置
- **拖动任意右下角手柄**缩放
- 直接填写精确的 **宽 / 高 / X / Y**
- 设置它的**不透明度**
- 切换 **锁定宽高比**（默认开启）— 以宽驱动高，图片永不变形；取消后可自由拉伸
- 点 **填充纹理** 铺满整张，或 **原始尺寸** 恢复图片自身的像素尺寸

然后 **应用图片** 烘焙进纹理（可撤销），或 **放弃** 直接丢弃、一个像素都不改。
`Ctrl+Enter` 应用，`Delete` 放弃。

图片会居中放入，并缩小到能完整落在纹理内 —— 从不放大 —— 所以一张过大的照片
会以可用尺寸进来，而不是盖住全部内容。

> [!TIP]
> 这与 Texture 区域里的 **用图片替换...** 不同，后者会立刻把图片拉伸铺满整张
> 纹理。

---

## 快捷键

| 按键 | 动作 |
|---|---|
| `Ctrl+O` | 打开 YTD |
| `Ctrl+Shift+S` | 另存为 YTD |
| `Ctrl+Z` / `Ctrl+Y` | 撤销 / 重做 |
| `B` `E` `T` `R` `L` `N` `I` | 画笔、橡皮、文字、矩形、椭圆、直线、取色 |
| `Ctrl+ +` / `Ctrl+ -` | 放大 / 缩小 |
| `Ctrl+0` / `Ctrl+1` | 适配窗口 / 100% |
| 滚轮 | 以光标位置缩放 |
| 中键拖动，或按住 `Space` | 平移 |
| `Ctrl+Enter` | 应用浮动的文字或图片 |
| `Delete` | 放弃浮动的文字或图片 |

---

## 支持的纹理格式

| 格式 | 读取 | 写入 | 说明 |
|---|:---:|:---:|---|
| DXT1 (BC1) | ✅ | ✅ | 保留 1 位 punch-through alpha |
| DXT3 (BC2) | ✅ | ✅ | 显式 4 位 alpha |
| DXT5 (BC3) | ✅ | ✅ | GTA V 中最常见的格式 |
| ATI1 (BC4) | ✅ | ✅ | 单通道 |
| ATI2 (BC5) | ✅ | ✅ | 双通道，法线贴图 |
| BC7 | ✅ | ✅ | 以 mode 6 编码，alpha 保持满精度 |
| A8R8G8B8 | ✅ | ✅ | 无损 |
| X8R8G8B8 | ✅ | ✅ | 按该格式语义强制 alpha 不透明 |
| A8B8G8R8 | ✅ | ✅ | 无损 |
| A1R5G5B5 | ✅ | ✅ | 1 位 alpha |
| L8 | ✅ | ✅ | 亮度 |
| A8 | ✅ | ✅ | 仅 alpha |

不支持的格式会在列表中以橙色标出并附上原因，禁止编辑，并且会**原样复制**到
输出文件中。

---

## YTD 支持是如何实现的

这是本项目最核心的设计决定，值得展开说明。

### 原地修补，而非重建

`.ytd` 是一个 **RSC7 资源**：16 字节头部，后接一段原始 DEFLATE 流。解压后得
到两个内存段 —— 存放结构体、名称和指针的 *system* 段，以及存放原始像素数据的
*graphics* 段。头部的两个 flag 字以页数编码每段的大小。

多数 YTD 工具在保存时会**重建**整个资源：重新排布页面、重算 flag、重新生成
每个结构体。这正是问题所在 —— 这样产出的文件在查看器里能打开，进游戏却各种
异常。

本编辑器反其道而行：它**直接在解压后的段内修补像素字节，绝不动布局**，因此
可以保证：

- 每个纹理名称、哈希、指针都与 Rockstar 写入时完全一致
- 你没有编辑过的纹理**按字节原样**保留
- 页面布局 —— 因而也包括 RSC7 头部 flag —— 天然保持合法

代价是：改过的纹理必须重新编码成*完全相同的字节数*——相同尺寸、相同格式、
相同 mip 层数。编辑器会强制这一约束，界面也是围绕“让纹理保持原始尺寸”来设计的。

### 格式处理

纹理以无头部的裸 D3D9 表面存储，各级 mip 首尾相接，没有偏移表 —— 游戏会根据
宽 / 高 / 格式 / 层数重算布局，本编辑器用的是同一套算法。

块压缩编解码（BC1–BC5）直接用 NumPy 实现，而 **BC7 采用 mode 6 编码** ——
即单子集、完整 RGBA 的那一种，也是不做昂贵的 partition 搜索就能可靠编码的唯一
BC7 模式，并且 alpha 为满精度。所以 BC7 纹理**仍然是 BC7**；不会被偷偷降级成
DXT5。

mip 链是根据你的编辑**重新生成**的，而不是沿用原始 mip。这一点在游戏中很重要：
引擎在远处会采样低层 mip，若保留旧 mip，改过的纹理在你走远时会明显“弹回”成
原图。

### 为什么不调用外部工具

[CodeWalker](https://github.com/dexyfex/CodeWalker) 是事实上的参考实现，但它是
C#/.NET，只能靠外部进程调用。PyPI 上有 `texfury` 和 `fivefury`，但它们附带
仅支持 Windows 的原生 DLL。自研的纯 Python 实现不需要安装任何外部二进制，
Python 能跑的地方就能跑，而且 —— 最重要的 —— 它让保存路径可以做成字节修补，
而不是重建。

### 已用真实文件验证

- 解析 **238 个真实的 FiveM `.ytd` 文件**（小地图切片与地图替换资源）
- 解码结果与 Pillow 独立的 DXT5 解码器交叉核对 —— **逐位一致**
- 完整的 保存 → 重新打开 → 解码 往返验证，并确认未改动的纹理字节完全相同
- DXT1 的 punch-through alpha 与 BC7 的 alpha 均验证为精确无误

---

## 已知限制

在你依赖本工具之前值得先了解：

- **纹理必须保持原始尺寸才能写回。** 这是原地修补固有的约束。旋转非正方形
  纹理，或在不勾选 *“保持原始纹理尺寸”* 的情况下调整尺寸 / 裁切，都会让该纹理
  无法导出 —— 事前会有警告，保存时也会明确报告，而不是写出一个坏文件。
- **不能新增、删除或重命名纹理。** 本工具编辑的是已有字典中的像素，不是从零
  制作字典。
- **块压缩是有损的。** 重新保存 BC 纹理会重新压缩一次，因此反复
  打开/编辑/保存会逐步劣化画质，这与任何 DDS 流程一样。尽量基于原始文件编辑。
- **RSC8（Red Dead Redemption 2）** 资源会被识别并明确拒绝。Gen9 的 GTA V
  字典使用不同的结构体大小，目前不支持。
- 仍打包在 `.rpf` 内的文件需要先解包（OpenIV 或 CodeWalker）。

---

## 故障排查

<details>
<summary><b>“Not a valid GTA V resource file: missing 'RSC7' magic.”</b></summary>

该文件不是资源文件、已损坏，或仍被封在 `.rpf` 里。请先用 OpenIV 或
CodeWalker 解包。
</details>

<details>
<summary><b>“No readable textures were found in this .ytd.”</b></summary>

字典解析成功，但没有一张纹理结构可被解读。请带上该文件提 issue —— 解析器
有一个在结构体内扫描已知格式码的兜底逻辑，所以这种情况本应很罕见。
</details>

<details>
<summary><b>列表里有些纹理是橙色的</b></summary>

它们使用了无法解码的格式。这些纹理会原样保留到输出中，只是不能编辑。
</details>

<details>
<summary><b>“Texture must stay WxH to be written back into the .ytd”</b></summary>

你改动了画布尺寸。撤销（`Ctrl+Z`）或点 **还原**，然后在勾选
*“保持原始纹理尺寸”* 的情况下重做该操作。
</details>

<details>
<summary><b>保存超大纹理很慢</b></summary>

一张 3072×3072 的 BC3 纹理重新编码需要几秒。那是块压缩器在实打实地算，
不是卡死了。
</details>

---

## 项目结构

```
ytd_edtior/
├── main.py                  程序入口 + 依赖检查
├── requirements.txt
├── README.md                英文版说明
├── README_zh-CN.md          中文版说明
├── core/                    不导入 Qt - 可作为无界面库使用
│   ├── rsc7.py              RSC7 容器：头部、flag、deflate、指针
│   ├── ytd_handler.py       字典解析 + 原地像素修补
│   ├── texture_handler.py   BC1-BC7 与无压缩编解码、mip 链
│   └── export_handler.py    保存调度、PNG/DDS 导出、图片导入
├── gui/                     不含任何 YTD 格式知识
│   ├── main_window.py       窗口、停靠面板、状态栏、全部接线
│   ├── canvas.py            缩放/平移/画笔/橡皮/文字/图片/图形/撤销
│   ├── toolbar.py           顶部工具栏
│   ├── texture_sidebar.py   左侧带缩略图的纹理列表
│   ├── tool_panel.py        右侧工具参数面板
│   └── style.py             深色主题
└── assets/
```

所有与 YTD 格式相关的逻辑都在代码里就地注释 —— `core/rsc7.py`、
`core/ytd_handler.py` 和 `core/texture_handler.py` 的模块 docstring 逐字段
记录了磁盘上的结构。

---

## 无界面调用 core

`core/` 不依赖 Qt，因此当作批处理库来用完全没问题：

```python
from ytd_edtior.core.ytd_handler import YtdFile
from ytd_edtior.core.export_handler import save_ytd_as

ytd = YtdFile.open("vehicle.ytd")
for t in ytd.textures:
    print(t.describe())          # 名称、尺寸、格式、mip 层数

tex = ytd.textures[0]
img = ytd.decode(tex)            # (h, w, 4) uint8 RGBA numpy 数组
img[0:64, 0:64] = [255, 0, 0, 255]

save_ytd_as(ytd, {tex.index: img}, "vehicle_edited.ytd")
```

---

## 参与贡献

欢迎提 issue 和 pull request。尤其有价值的是：

- 解析失败的 `.ytd` 文件（方便的话请附上文件）
- Gen9 / RDR2 字典支持
- 更好的 BC7 编码器 —— 目前只有 mode 6

请保持现有的分层约束：**`core/` 里不导入 Qt，`gui/` 里不含 YTD 格式知识。**

---

## 致谢

- [CodeWalker](https://github.com/dexyfex/CodeWalker)（dexyfex 作品）——
  RSC7 容器与 `grcTexturePC` 结构布局的参考依据
- [Pillow](https://python-pillow.org/) —— BC7 解码与图像读写
- [GTAMods Wiki](https://gtamods.com/wiki/Texture_archive) —— 格式背景资料

与 Rockstar Games、Take-Two Interactive 以及 FiveM / Cfx.re 项目无任何关联、
背书或从属关系。GTA V 是 Take-Two Interactive Software, Inc. 的商标。

---
https://discord.gg/a9zq8qKvH5
discord : _1n7
## 许可证

基于 [MIT License](../LICENSE) 发布。
