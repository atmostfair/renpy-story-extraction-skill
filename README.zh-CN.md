# Ren'Py 剧情提取 Skill

**建议仓库名称：** `renpy-story-extract-skill`

[English](README.md)

Ren'Py 剧情提取 Skill 是一个面向 Codex 的技能，用于处理 Ren'Py 视觉小说脚本，并准备有顺序、可阅读、可审计的剧情参考材料。这些文本可以作为 NotebookLM、私有知识库、检索增强生成系统、剧情总结、人物分析、本地资料检索、翻译校对、连续性检查，或其他需要剧情资料作为参考的场景的输入材料。

这个仓库是 skill 包和工作流参考，不是传统意义上的独立可执行程序项目。本项目适合个人研究、资料整理和已授权的内容处理。除非你拥有版权或获得明确许可，否则不要公开分发提取出的受版权保护剧情文本。

## 这个项目解决什么问题

Ren'Py 游戏的剧情通常分散在多个 `.rpy` 文件、标签、路线文件、回顾文件、手机消息系统、界面辅助函数和跳转逻辑中。按文件名或字母顺序阅读，往往并不等于真实游戏顺序。

这个仓库提供一套可复用的整理方式，重点保留玩家实际能看到的叙事内容：

- 按剧情顺序拆分的故事文件，而不是未经验证的大段合并文本
- 角色名、旁白和说话人信息
- 对话、内心独白、选项、手机消息和有剧情意义的屏幕文字
- 章节、集数、路线或标签边界
- 记录来源和顺序依据的 manifest
- 对未解析变量、Ren'Py 标签、资源路径和 UI 元数据泄漏的审计检查

## 常见用途

- **上传到 NotebookLM：** 将视觉小说脚本转换为干净的文本源，用于总结、问答、时间线重建、角色分析和主题梳理。
- **构建私有参考语料：** 为本地搜索、笔记系统、RAG 流程或私人助手准备剧情资料。
- **辅助写作和连续性检查：** 对比不同路线，追踪人物弧线，检查伏笔回收和跨章节矛盾。
- **翻译和编辑审校：** 从代码、资源路径、菜单和调试文本中分离玩家可见文本。
- **数据集准备：** 在授权前提下，为模型微调、评测或合成数据生成准备结构化参考材料。

## 重要注意事项

- 尽量使用 `.rpy` 源文件。
- 如果只有 `.rpyc` 编译文件，需要先用 `unrpyc` 等工具反编译，再检查生成的 `.rpy` 文件。
- 不要假设文件名顺序就是剧情顺序。应根据 Ren'Py 的 `label`、`jump`、`call`、路线控制器、章节列表、回放/图库入口和 screen action 判断顺序。
- 默认应保留按剧情单元拆分的输出文件。合并文件可以作为便利版本，但不应替代逐段输出。
- 遵守版权、平台条款和源材料许可证。将文本上传到 AI 工具或用于训练，可能涉及法律和合同限制。

## 推荐仓库结构

```text
renpy-story-extract-skill/
├─ README.md
├─ README.zh-CN.md
├─ SKILL.md
├─ scripts/
│  └─ renpy_story_extract.py
├─ configs/
│  └─ example.project.json
├─ input/
│  └─ .gitkeep
├─ work/
│  └─ .gitkeep
└─ output/
   └─ .gitkeep
```

目录建议：

- `SKILL.md`：Codex skill 的核心说明文件。
- `scripts/`：提取脚本和审计辅助脚本。
- `configs/`：项目级提取计划、说话人映射、顺序规则和包含/排除配置。
- `input/`：临时放置源文件。真实游戏文件通常不建议提交到 git。
- `work/`：扫描结果、跳转图、分析笔记和中间文件。
- `output/`：提取出的剧情文本和 manifest。只提交你有权公开的内容。

## 工作流程

### 1. 准备脚本源文件

先定位 Ren'Py 脚本目录。桌面版通常在 `game/` 下，Android 版可能位于 `assets/x-game/` 之类的路径。

如果已经有 `.rpy` 文件，直接使用它们。如果只有 `.rpyc` 文件，先反编译：

```bash
unrpyc ./game
```

Android 风格的资源目录可以使用：

```bash
unrpyc ./assets
```

反编译后，确认确实生成了可读的 `.rpy` 文件，再继续后续步骤。

### 2. 扫描项目

识别剧情文件、支撑文件、标签、跳转、调用、角色定义、动态名称变量，以及项目自定义的可见文本函数。

如果仓库中包含 `scripts/renpy_story_extract.py`，可以使用类似命令：

```bash
python scripts/renpy_story_extract.py scan \
  --source-dir /path/to/game \
  --output-dir work/my-project-scan
```

扫描结果只是起点。正式提取前，需要人工检查和修正。

### 3. 编写提取配置

在 `configs/` 中为具体项目创建配置。配置应说明：

- 需要提取的有序剧情单元
- 每个单元对应的源文件和 label 范围
- 说话人映射
- 玩家姓名归一化规则
- 内心独白和普通对话的区分方式
- 自定义消息、手机聊天或屏幕文字辅助函数
- 哪些文本应包含，哪些文本应排除

推荐输出命名：

```text
story01_original-title.txt
story02_original-title.txt
story03_original-title.txt
```

如果项目提供章节名、集数名或路线名，优先使用原始标题；否则使用源文件名或 label 名组合。

### 4. 提取有序文本

使用已检查过的配置运行提取：

```bash
python scripts/renpy_story_extract.py extract \
  --source-dir /path/to/game \
  --config configs/my-project.json \
  --output-dir output/my-project
```

推荐输出：

```text
output/my-project/
├─ story01_prologue.txt
├─ story02_chapter-1.txt
├─ story03_chapter-2.txt
├─ story_index.txt
├─ story_manifest.json
└─ speaker_map.txt
```

### 5. 审计输出结果

在上传到 NotebookLM 或用于其他系统前，先检查是否有代码、资源路径或未解析标记泄漏。

常用检查：

```bash
rg -n "audio/|images/|\\.png|\\.jpg|\\.webp|\\.mp3|\\.ogg|\\.webm" output/my-project
rg -n "\\[[^\\]\\n]+\\]" output/my-project
rg -n "\\{[^}\\n]+\\}" output/my-project
rg -n "^extend:|^label |^screen " output/my-project
```

常见需要修正的问题：

- 资源路径被误提取为剧情文本
- `[player_name]` 等 Ren'Py 变量没有被解析
- `{i}`、`{w}`、`{p}`、`{size=...}` 等格式标签残留
- 内心独白被误当成普通对话
- 调试、图库、设置或菜单文本混入剧情

### 6. 将文本作为参考资料使用

用于 NotebookLM 时：

1. 上传有序的 `storyxx_*.txt` 文件。
2. 如果平台支持，也上传 `story_index.txt` 或 `story_manifest.json`。
3. 围绕指定章节、路线、角色或主题提问。
4. 保持按剧情单元拆分，方便平台理解来源顺序和范围。

用于 RAG 或训练流程时：

1. 尽量按剧情单元、label、场景或章节切分，不要只按固定字节数切分。
2. 保存来源元数据，例如文件名、label、说话人、路线和序号。
3. 保留 manifest，方便生成结果追溯到原始剧情单元。
4. 确认你对源内容拥有相应使用权，并符合平台条款。

## 输出文本建议格式

好的提取结果应让读者不懂 Ren'Py 代码也能阅读：

```text
You: I should check the old station before sunset.
You (thought): Something about this place still feels wrong.

[Choice]
- Go to the platform.
- Call Maya first.

Maya: You heard it too, didn't you?
```

应避免这样的输出：

```text
show maya neutral at left with dissolve
audio/bgm/station_theme.ogg
extend: "didn't you?"
mc "[player_name!u], are you listening?"
```

## 法律和伦理使用

这套流程可以处理大量剧情文本，请谨慎使用：

- 只处理你拥有权利或获得许可分析的游戏、mod、脚本或翻译。
- 除非许可证允许，不要公开发布专有剧情文本。
- 除非你拥有必要权利，不要将提取文本用于模型训练、微调或公开数据集。
- 将第三方内容上传到 NotebookLM 等平台前，请先阅读对应平台条款。

## 建议 GitHub Topics

```text
renpy
visual-novel
story-extraction
narrative-analysis
notebooklm
rag
dataset-preparation
localization
```

## 许可证

请根据仓库实际内容选择许可证。

- 如果只包含提取脚本，可以考虑 MIT 或 Apache-2.0 等开源许可证。
- 如果包含文档和示例，可以考虑 CC BY 4.0 等文档友好许可证。
- 除非你拥有相应权利，不要给提取出的剧情文本套用开源许可证。
