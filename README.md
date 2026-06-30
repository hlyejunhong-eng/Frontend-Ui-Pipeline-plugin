# Frontend UI Pipeline / 前端 UI 流水线

[![Quick Check](https://github.com/hlyejunhong-eng/Frontend-Ui-Pipeline-plugin/actions/workflows/quick-check.yml/badge.svg)](https://github.com/hlyejunhong-eng/Frontend-Ui-Pipeline-plugin/actions/workflows/quick-check.yml)
[![Release](https://img.shields.io/github/v/release/hlyejunhong-eng/Frontend-Ui-Pipeline-plugin)](https://github.com/hlyejunhong-eng/Frontend-Ui-Pipeline-plugin/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## 简介 / Overview

**中文**

Frontend UI Pipeline 是一个 Codex 插件。它把已有页面、截图、Figma、localhost 地址或本地前端项目拆成三阶段处理：先生成高级定制 UI brief 和预览方案，再生成命名清晰的美术资产和动效规则，最后把审核通过的资产接入真实前端。

**English**

Frontend UI Pipeline is a Codex plugin that turns an existing page, screenshot, Figma screen, localhost URL, or local frontend project into a three-phase delivery flow: a premium UI brief and preview, named production art assets and motion rules, then a real frontend implementation using the approved assets.

## 三个 Skills / Three Skills

| Skill | 中文用途 | English Use |
| --- | --- | --- |
| `$frontend-ui-ideation` | 收集已有页面信息，生成高级定制 UI brief 和预览方案。 | Collect context from an existing app flow and create a premium UI brief plus preview. |
| `$frontend-asset-production` | 根据阶段一文档和预览图生成资产、组件、动效规则，并等待用户审核。 | Generate named art assets, component assets, and motion rules from the Phase 1 brief, then stop for user review. |
| `$frontend-implementation` | 把审核通过的资产接入真实前端；有 API 接 API，没有 API 用 mock。 | Implement the approved assets in the real frontend, using real APIs when available or faithful mocks when not. |

## 安装什么 / What You Install

**中文**

你安装的是 Codex 插件：`frontend-ui-pipeline`。安装后打开 **Codex 应用** 或 **Codex CLI**，新建一个 Codex 线程，然后在底部消息输入框发送页面材料和启动 prompt。

**English**

You are installing the Codex plugin named `frontend-ui-pipeline`. After installation, open the **Codex app** or **Codex CLI**, create a new Codex thread, then paste your page material and start prompt into the message box.

## 安装步骤 / Installation

### 1. 下载插件 / Clone The Plugin

```bash
mkdir -p ~/plugins
git clone https://github.com/hlyejunhong-eng/Frontend-Ui-Pipeline-plugin.git ~/plugins/frontend-ui-pipeline
```

### 2. 注册到 Codex 个人 marketplace / Register It In Your Personal Codex Marketplace

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/install_local_marketplace.py
```

### 3. 在 Codex 中添加插件 / Add The Plugin In Codex

```bash
codex plugin add frontend-ui-pipeline@personal
```

### 4. 新开线程 / Start A New Thread

**中文**

安装后关闭当前线程，重新打开一个新 Codex 线程。新线程才会加载刚安装的三个 skills。

**English**

After installation, close the current thread and create a new Codex thread. The newly installed skills are loaded only in a new thread.

## 更新插件 / Update

```bash
cd ~/plugins/frontend-ui-pipeline
git pull
python3 scripts/install_local_marketplace.py
codex plugin add frontend-ui-pipeline@personal
```

**中文**

更新后同样需要新开一个 Codex 线程。

**English**

After updating, create a new Codex thread again so the latest plugin files are loaded.

## 从哪里开始用 / Where To Start

**中文：Codex 应用**

1. 打开 Codex 应用。
2. 新建一个线程。
3. 选择或确认你的工作目录。
4. 在底部消息输入框粘贴页面材料和启动 prompt。
5. 回车发送。

**English: Codex App**

1. Open the Codex app.
2. Create a new thread.
3. Select or confirm your workspace directory.
4. Paste your page material and start prompt into the bottom message box.
5. Press Enter to send.

**中文：Codex CLI**

1. 在终端进入你的工作目录。
2. 启动 Codex。
3. 在对话输入区粘贴页面材料和启动 prompt。
4. 回车发送。

**English: Codex CLI**

1. Open a terminal in your workspace directory.
2. Start Codex.
3. Paste your page material and start prompt into the conversation input.
4. Press Enter to send.

## 可以给什么输入 / Accepted Inputs

**中文**

你至少给其中一种就能开始：

- 旧页面截图
- 本地项目路径
- 本地运行地址，例如 `http://localhost:3000/dashboard`
- Figma 链接
- 页面功能描述

更好的输入包括：

- 目标用户是谁
- 想把页面做高级的原因
- 品牌颜色、字体、Logo 或参考风格
- 要替换的路由或组件路径
- 是否已有真实 API

**English**

You can start with at least one of these:

- Old screen screenshot
- Local project path
- Local running URL, such as `http://localhost:3000/dashboard`
- Figma link
- Page or flow description

Better inputs include:

- Target users
- Why the page should feel more premium
- Brand colors, fonts, logo, or visual references
- Target route or component path
- Whether real APIs already exist

## 五种启动方式 / Five Start Patterns

### 方式 A：只有截图 / Pattern A: Screenshot Only

```text
Use the Frontend UI Pipeline on this old page screenshot.

Input:
- 我上传了一张旧页面截图。
- I uploaded an old screen screenshot.

Goal:
请把这个页面重做成高端定制 UI，先输出阶段一 brief 和预览图，再进入阶段二资产生产，最后实现可运行前端。如果没有真实项目，就先生成独立可运行 demo。

Redesign this page into a premium custom UI. Start with the Phase 1 brief and preview, then continue to Phase 2 asset production, and finally create a runnable frontend. If there is no real project yet, create a standalone runnable demo first.
```

### 方式 B：有本地项目路径 / Pattern B: Local Project Path

```text
Use the Frontend UI Pipeline on this real frontend route.

Project path:
/Users/<your-name>/path/to/your-frontend-project

Target route or screen:
/dashboard/onboarding

Goal:
请基于当前页面重新设计高端 UI，生成完整组件资产包和动效规则。阶段三请直接在这个项目里实现；如果接口不清楚，先用同结构 mock 数据。

Redesign the current page into a premium UI, generate a complete component asset kit and motion rules, then implement it directly in this project during Phase 3. If APIs are unclear, use same-shape mock data first.
```

### 方式 C：项目已经在 localhost 跑起来 / Pattern C: Running Localhost App

```text
Use the Frontend UI Pipeline on this running local app.

Local URL:
http://localhost:3000/dashboard/onboarding

Project path:
/Users/<your-name>/path/to/your-frontend-project

Goal:
请先审视这个页面，再生成阶段一高端 UI brief 和预览图。阶段二生成完整资产包，阶段三热更替换到真实前端项目。

Inspect this page first, then generate the Phase 1 premium UI brief and preview. In Phase 2, generate the complete asset kit. In Phase 3, hot-replace the real frontend route.
```

### 方式 D：有 Figma 链接 / Pattern D: Figma Link

```text
Use the Frontend UI Pipeline on this Figma screen.

Figma:
<paste Figma link>

Goal:
请基于这个页面重新生成高端定制方向、资产系统和真实前端实现方案。如果不能直接读取 Figma，请告诉我需要补充哪些截图或节点信息。

Create a premium custom direction, asset system, and real frontend implementation plan from this screen. If Figma cannot be read directly, tell me which screenshots or node details you need.
```

### 方式 E：只有页面描述 / Pattern E: Description Only

```text
Use the Frontend UI Pipeline to create a premium frontend flow.

Page description:
这是一个给小商家使用的 AI 文案助手 onboarding 页面。页面需要展示欢迎语、三个设置步骤、品牌语气、网站连接、创建第一条营销内容，以及右侧进度建议。

This is an onboarding page for an AI copywriting assistant used by small business owners. It should show a welcome message, three setup steps, brand voice, website connection, first campaign creation, and right-side progress suggestions.

Goal:
请从阶段一开始，生成高端 UI brief、预览图、阶段二资产包，最后做一个可运行前端 demo。

Start from Phase 1, generate a premium UI brief and preview, then create the Phase 2 asset kit, and finally build a runnable frontend demo.
```

## 通用全流程 Prompt / Full Pipeline Prompt

```text
Use the Frontend UI Pipeline to redesign and implement this app flow.

Input:
- <粘贴旧页面截图、本地项目路径、localhost 地址、Figma 链接或页面描述>
- <Paste an old screenshot, local project path, localhost URL, Figma link, or page description>

Target user:
- <这个页面给谁用>
- <Who this page is for>

Business goal:
- <为什么要把它做高级>
- <Why this page should feel more premium>

Implementation target:
- 如果有真实前端项目，请直接改真实项目。
- 如果没有真实项目，请生成独立可运行 demo。
- 如果有真实 API 就接 API，没有就用同结构 mock 数据。
- If there is a real frontend project, implement directly in it.
- If there is no real project, create a standalone runnable demo.
- If real APIs exist, connect them. Otherwise, use same-shape mock data.

Output requirements:
- Phase 1: 高端 UI brief、桌面/移动预览图、像素级布局/文字/按钮/动效要求。
- Phase 2: 完整基础组件资产包、命名资产、asset manifest、asset handoff，并在最终输出前让我审核资产是否通过。
- Phase 3: 可运行前端、资产接入、接口或 mock、桌面/移动截图和验证命令。
- Phase 1: Premium UI brief, desktop/mobile previews, pixel-level layout/copy/button/motion requirements.
- Phase 2: Complete foundation asset kit, named assets, asset manifest, asset handoff, and an explicit asset review checkpoint before final output.
- Phase 3: Runnable frontend, asset integration, real APIs or mocks, desktop/mobile screenshots, and verification commands.
```

## 单独调用某个 Skill / Run One Skill Only

只做阶段一 / Phase 1 only:

```text
Use $frontend-ui-ideation to redesign this existing app flow into a premium UI brief and preview.
```

只做阶段二 / Phase 2 only:

```text
Use $frontend-asset-production with this phase 1 brief and preview. Generate the real assets, then ask me to review before finalizing.
```

只做阶段三 / Phase 3 only:

```text
Use $frontend-implementation with the approved phase 2 assets. Hot-replace the real frontend route. Connect real APIs if available; otherwise mock it to match the preview.
```

## 阶段输出标准 / Phase Output Standards

### 阶段一：UI Ideation / Phase 1: UI Ideation

**中文**

必须输出：

- `phase1-ui-brief.md`
- 桌面或移动预览图
- 组件、背景、文字、按钮、状态、点击反馈和动效要求
- 给阶段二使用的生成指南
- 完整基础组件资产清单

成功标准：

- 不是只写“现代、简洁、高级”
- 要写清楚布局、像素、层级、状态和动效
- 非设计人员也能读懂下一步要生成什么资产

**English**

Required outputs:

- `phase1-ui-brief.md`
- Desktop or mobile preview image
- Requirements for components, background, copy, buttons, states, click feedback, and motion
- Generation guide for Phase 2
- Complete foundation component asset inventory

Success criteria:

- Does not stop at vague words like "modern", "clean", or "premium"
- Specifies layout, pixels, hierarchy, states, and motion
- Lets a non-designer understand what assets should be generated next

### 阶段二：Asset Production / Phase 2: Asset Production

**中文**

必须输出：

- 背景、插图、遮罩、图标、sprites 或 motion frames
- 完整基础组件资产包
- `asset-manifest.json`
- `phase2-asset-handoff.md`
- 资产预览或审核包

基础组件资产包至少覆盖：

- buttons
- numeric badges
- cards
- combobox
- common icons
- navigation bar
- notice bar
- search bar
- section title
- modal
- transition animation

常用 icon 至少覆盖：

- home
- profile
- page
- scan
- cart
- payment
- chat
- confirm
- close
- back
- forward
- hot
- like
- settings
- help
- info
- wallet
- list
- favorite
- search

阶段二必须停下来让用户审核资产。用户明确说通过后，才能输出最终 handoff。

**English**

Required outputs:

- Backgrounds, illustrations, masks, icons, sprites, or motion frames
- Complete foundation component asset kit
- `asset-manifest.json`
- `phase2-asset-handoff.md`
- Asset preview or review package

The foundation kit should cover at least:

- buttons
- numeric badges
- cards
- combobox
- common icons
- navigation bar
- notice bar
- search bar
- section title
- modal
- transition animation

The common icon set should cover at least:

- home
- profile
- page
- scan
- cart
- payment
- chat
- confirm
- close
- back
- forward
- hot
- like
- settings
- help
- info
- wallet
- list
- favorite
- search

Phase 2 must stop for user asset review. The final handoff should be written only after the user explicitly approves the assets.

### 阶段三：Frontend Implementation / Phase 3: Frontend Implementation

**中文**

必须输出：

- 真实可运行前端代码
- 阶段二资产和基础组件库接入
- 真实 API 接入，或同结构 mock 数据
- hover、focus、pressed、loading、reduced-motion 等状态
- 桌面和移动截图，或说明为什么无法截图
- 验证命令、结果和本地运行方式

**English**

Required outputs:

- Real runnable frontend code
- Imported Phase 2 assets and foundation component kit
- Real API integration, or same-shape mock data
- Hover, focus, pressed, loading, and reduced-motion states
- Desktop and mobile screenshots, or a clear explanation for why screenshots could not be captured
- Verification commands, results, and local run instructions

## 完整运行的最低证据 / Minimum Evidence For A Complete Run

**中文**

一次完整运行至少应该留下：

- `phase1-ui-brief.md`
- Phase 1 预览图或截图
- 已审核通过的资产目录
- 资产审核包
- `phase2-asset-handoff.md`
- 完整 foundation component kit
- common icon set
- 前端代码改动
- 验证命令输出
- 桌面和移动截图

**English**

A complete run should leave at least:

- `phase1-ui-brief.md`
- Phase 1 preview image or screenshot
- Approved asset directory
- Asset review package
- `phase2-asset-handoff.md`
- Complete foundation component kit
- Common icon set
- Frontend code changes
- Verification command output
- Desktop and mobile screenshots

## 本地校验 / Local Check

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/quick_check.py
```

**中文**

它会检查插件 manifest、三个 skills、agent YAML、安装脚本和 README。

**English**

This checks the plugin manifest, three skills, agent YAML files, install script, and README.

## License

MIT
