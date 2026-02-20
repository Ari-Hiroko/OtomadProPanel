# OProPanel: Premiere Pro 音MAD辅助插件

## 说明
这是一系列专为音MAD（YTPMV）制作设计的 Premiere Pro 扩展插件。项目基于 Adobe 官方的 PProPanel 进行二次开发，并结合 Python 脚本，通过处理 MIDI 数据来实现音MAD画面的快速铺轨，提升制作效率。

## 核心工作流
* **数据解析**：通过 Python GUI 读取 MIDI 文件，解析音轨数据并导出为结构化的 JSON 文件。
* **序列生成**：在 Premiere Pro 中，插件读取该 JSON 文件，根据指定素材自动在时间线上进行剪辑与排列。

## 环境依赖
* **宿主软件**：Adobe Premiere Pro (建议版本 2020 及以上)
* **运行环境**：Python 3.x
* *注：运行 Python 脚本可能需要特定的第三方库，请在使用前确保已安装所需依赖。*

## 安装步骤

### 1. 安装扩展
将本项目中的 `OProPanel` 文件夹完整复制到系统的 CEP 扩展目录：
> `C:\Program Files (x86)\Common Files\Adobe\CEP\extensions\`

### 2. 开启开发者调试模式（必做）
由于本插件可能未经过 Adobe 官方签名，直接打开 Premiere 可能会显示扩展无法加载。需要开启调试模式：
1. 打开 Windows 注册表编辑器 (`regedit`)。
2. 导航至 `HKEY_CURRENT_USER\Software\Adobe\CSXS.11`（注：末尾的数字取决于你的 PR 版本，如果是旧版可能是 CSXS.10 或更低，建议将存在的 CSXS 目录都修改）。
3. 新建一个**字符串值** (String Value)，命名为 `PlayerDebugMode`。
4. 双击该键值，将其数据设置为 `1`。

## 使用方法
1. **生成 JSON 数据**：
   在本地运行 `MIDISTGUI.PY`。在弹出的图形界面中输入或选择你的 MIDI 文件，程序会进行处理并输出一个包含排列数据的 JSON 文件。
2. **在 Premiere 中铺轨**：
   * 打开 Premiere Pro，建立目标序列。
   * 在顶部菜单栏中依次点击 **窗口 (Window) -> 扩展 (Extensions) -> OProPanel**，调出插件面板。
   * 在时间线或项目面板中，**选中一个你要作为基础画面的视频/图像素材**。
   * 在 OProPanel 插件面板中操作，读取刚才生成的 JSON 文件，插件将自动完成该素材在时间线上的排列。

## 协议与致谢
* 本项目的 Premiere 插件部分基于 [Adobe PProPanel](https://github.com/Adobe-CEP/Samples/tree/master/PProPanel) 衍生，遵循 Apache License 2.0 协议。
