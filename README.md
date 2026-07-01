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

### 5. 安装诊断 / Install Doctor

**中文**

如果你不确定插件有没有装好，运行：

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/diagnose_install.py
```

它会检查插件 manifest、三个 skills、个人 marketplace 条目、Codex 已安装缓存，并打印下一句可以直接发给 Codex 的启动 prompt。

**English**

If you are not sure whether the plugin is installed correctly, run:

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/diagnose_install.py
```

It checks the plugin manifest, three skills, personal marketplace entry, installed Codex cache, and prints a ready-to-send start prompt.

## 首次运行检查清单 / First Run Checklist

**中文**

1. 确认已经运行：`codex plugin add frontend-ui-pipeline@personal`。
2. 打开 Codex 应用或 Codex CLI。
3. 新建一个线程；如果三个 skills 没出现，再新开一个线程。
4. 在底部消息输入框粘贴旧页面截图、本地项目路径、localhost 地址、Figma 链接或页面描述。
5. 发送包含 `$frontend-ui-ideation` 的启动 prompt。

**English**

1. Confirm that you ran: `codex plugin add frontend-ui-pipeline@personal`.
2. Open the Codex app or Codex CLI.
3. Create a new thread; if the three skills do not appear, create another new thread.
4. Paste an old screenshot, local project path, localhost URL, Figma link, or page description into the bottom message box.
5. Send a start prompt that includes `$frontend-ui-ideation`.

## 更新插件 / Update

```bash
cd ~/plugins/frontend-ui-pipeline
git pull
python3 scripts/install_local_marketplace.py
codex plugin add frontend-ui-pipeline@personal
python3 scripts/diagnose_install.py
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
- Phase 1: 三个独立视觉方向、选中的视觉目标、高端 UI brief、桌面/移动预览图、像素级布局/文字/按钮/动效要求。
- Phase 2: 先做主屏封面级资产，再扩展完整基础组件资产包、命名资产、asset manifest、asset handoff，并在最终输出前让我审核资产是否通过。
- Phase 3: 可运行前端、资产接入、接口或 mock、桌面/移动截图、design QA 和验证命令。
- Phase 1: Three independent visual directions, a selected visual target, premium UI brief, desktop/mobile previews, pixel-level layout/copy/button/motion requirements.
- Phase 2: Primary selected-screen assets first, then the complete foundation asset kit, named assets, asset manifest, asset handoff, and an explicit asset review checkpoint before final output.
- Phase 3: Runnable frontend, asset integration, real APIs or mocks, desktop/mobile screenshots, design QA, and verification commands.
```

## Demo 模式和生产模式 / Demo Mode And Production Mode

**中文**

- `production`：默认模式。阶段二必须等用户明确审核通过，阶段三才可以热替换真实应用。
- `demo`：适合自媒体、销售演示或方向验证。可以先生成独立可运行预览，但必须标记为非最终产物；没有用户审核通过前，不要改真实应用代码。

**English**

- `production`: Default mode. Phase 2 must wait for explicit user approval before Phase 3 hot-replaces the real app.
- `demo`: Useful for social posts, sales demos, or direction validation. It may create a standalone runnable preview first, but it must be labeled non-final; do not modify the real app before user approval.

Demo artifacts such as `phase3-demo*/index.html`, `README.md`, and `phase3-demo-evidence.md` are indexed by the pipeline runbook so non-expert users can find and open the preview without digging through folders.

## 质量门禁 / Quality Gates

**中文**

这个插件的目标不是“写一段审美提示词”，而是把高质量前端设计拆成可验证步骤：

- 阶段一先锁定 design brief：目标页面、视觉来源、交互等级和目标尺寸。
- 阶段一必须使用真实参考：截图、localhost、Figma、品牌资产、Storybook、tokens 或组件引用；不能只靠文件名猜风格。
- 阶段一生成三个独立视觉方向，每个方向单独一张图，选中后才能进入阶段二。
- 阶段二必须生成 asset-assembled primary screen preview，也就是用真实 Phase 2 assets 拼一次主屏；不能把 Phase 1 preview screenshot 复制过来冒充资产证明。
- 阶段二审核包必须说明 visual diff / assembly diff 的结果；如果差异来自“资产拼装图不是最终前端截图”，要写清楚并把 Phase 3 screenshot QA 作为最终像素门禁。
- 阶段三必须在真实前端里跑起来、截图、做 visual diff，并生成 `design-qa.md`。

**English**

This plugin is not just a prompt for taste. It turns frontend design quality into verifiable gates:

- Phase 1 locks the design brief: target surface, visual source, interactivity level, and target dimensions.
- Phase 1 must use real references: screenshots, localhost, Figma, brand assets, Storybook, tokens, or component references; do not infer style from filenames alone.
- Phase 1 generates three independent visual directions, each as its own image, before selecting one for Phase 2.
- Phase 2 must create an asset-assembled primary screen preview from real Phase 2 assets; do not copy the Phase 1 preview screenshot as asset proof.
- Phase 2 review must explain the visual diff / assembly diff result; when the difference exists because the assembly is not the final app screenshot, keep Phase 3 screenshot QA as the final pixel gate.
- Phase 3 must run the real frontend, capture screenshots, run visual diff, and generate `design-qa.md`.

## uni-app / HBuilderX 项目 / uni-app And HBuilderX Projects

**中文**

如果项目里有 `pages.json`、`manifest.json`、`uni_modules`，它通常是 uni-app 项目。很多这类项目没有 `npm run dev`。阶段三应该优先：

- 保留 `rpx`、`view`、`text`、`scroll-view` 等 uni-app 写法。
- 把资产放到 `static/frontend-ui-pipeline/`。
- 保留现有 `api`、`uniCloud.callFunction` 和页面方法。
- 如果 CLI 跑不起来，先给出 HBuilderX 运行说明和独立预览截图，不要假装已经完成像素级验证。

**English**

If the project contains `pages.json`, `manifest.json`, and `uni_modules`, it is usually a uni-app project. Many such projects do not have `npm run dev`. Phase 3 should:

- Preserve uni-app primitives such as `rpx`, `view`, `text`, and `scroll-view`.
- Put assets under `static/frontend-ui-pipeline/`.
- Preserve existing `api`, `uniCloud.callFunction`, and page methods.
- If the CLI cannot run it, provide HBuilderX run instructions and standalone preview screenshots instead of claiming pixel-perfect verification.

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
- 已锁定的 design brief：目标页面、视觉来源、交互等级和目标尺寸
- 三个独立视觉方向预览图
- 选中的视觉目标
- `phase1-visual-excellence-gate.md`
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
- Locked design brief: target surface, visual source, interactivity level, and target dimensions
- Three independent visual direction previews
- Selected visual target
- `phase1-visual-excellence-gate.md`
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

- 主屏封面级资产集
- 用真实资产拼出来的主屏预览：`primary-screen-asset-assembly.png` 或等价 HTML/PNG
- visual diff / assembly diff 报告和已知差异说明
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

- Primary selected-screen asset set
- Asset-assembled primary screen preview such as `primary-screen-asset-assembly.png` or equivalent HTML/PNG
- Visual diff / assembly diff report and known deviation notes
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
- `design-qa.md`，且最终交付前必须是 `final result: passed`
- 验证命令、结果和本地运行方式

**English**

Required outputs:

- Real runnable frontend code
- Imported Phase 2 assets and foundation component kit
- Real API integration, or same-shape mock data
- Hover, focus, pressed, loading, and reduced-motion states
- Desktop and mobile screenshots, or a clear explanation for why screenshots could not be captured
- `design-qa.md`, with `final result: passed` before final handoff
- Verification commands, results, and local run instructions

## 完整运行的最低证据 / Minimum Evidence For A Complete Run

**中文**

一次完整运行至少应该留下：

- `phase1-ui-brief.md`
- 三个 Phase 1 视觉方向和选中的预览图
- `phase1-visual-excellence-gate.md`
- 已审核通过的资产目录
- 资产审核包
- 真实资产拼装主屏预览
- visual diff / assembly diff 记录
- `phase2-asset-handoff.md`
- 完整 foundation component kit
- common icon set
- 阶段三实现补丁计划
- 前端代码改动
- 验证命令输出
- `design-qa.md`
- 桌面和移动截图

**English**

A complete run should leave at least:

- `phase1-ui-brief.md`
- Three Phase 1 visual directions and the selected preview
- `phase1-visual-excellence-gate.md`
- Approved asset directory
- Asset review package
- Primary screen preview assembled from real generated assets
- Visual diff / assembly diff evidence
- `phase2-asset-handoff.md`
- Complete foundation component kit
- Common icon set
- Phase 3 implementation patch plan
- Frontend code changes
- Verification command output
- `design-qa.md`
- Desktop and mobile screenshots

## 流水线运行索引生成器 / Pipeline Runbook Generator

**中文**

每跑完一个阶段，建议生成一次运行索引。它会扫描当前运行目录，告诉普通用户现在卡在哪一步、下一句应该发给 Codex 什么、阶段二是否还在等审核、哪些文件可以用于交付或自媒体展示。

如果运行目录里有 `phase3-demo*/index.html`、`README.md` 或 `phase3-demo-evidence.md`，索引也会把这些 demo 入口列出来。

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/generate_pipeline_runbook.py \
  --run-root ./frontend-ui-pipeline-run \
  --project "my-app" \
  --target "/dashboard"
```

**English**

After each phase, generate a runbook. It scans the current run folder and tells a non-expert user what is done, what to send to Codex next, whether Phase 2 is still waiting for approval, and which files are useful for handoff or social proof.

If the run folder contains `phase3-demo*/index.html`, `README.md`, or `phase3-demo-evidence.md`, the runbook also lists those standalone demo entrypoints.

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/generate_pipeline_runbook.py \
  --run-root ./frontend-ui-pipeline-run \
  --project "my-app" \
  --target "/dashboard"
```

## 流水线完成度审计 / Pipeline Completion Audit Generator

**中文**

完成度审计会按目标逐条检查证据：插件是否易安装、阶段一是否有 Phase 2 生成指南、阶段二是否覆盖完整基础组件和 20 个 icons、阶段三是否只有 demo 还是已经有真实截图和 Design QA、自媒体材料是否存在。它会诚实输出 `complete`、`blocked-on-asset-approval`、`in-progress` 或 `incomplete`。

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/generate_pipeline_completion_audit.py \
  --run-root ./frontend-ui-pipeline-run \
  --repo-root ~/plugins/frontend-ui-pipeline \
  --project "my-app" \
  --target "/dashboard"
```

**English**

The completion audit checks evidence requirement by requirement: installability, Phase 1 Phase 2 guide, Phase 2 foundation coverage and 20 icons, Phase 3 demo versus production screenshots and Design QA, and social proof material. It honestly reports `complete`, `blocked-on-asset-approval`, `in-progress`, or `incomplete`.

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/generate_pipeline_completion_audit.py \
  --run-root ./frontend-ui-pipeline-run \
  --repo-root ~/plugins/frontend-ui-pipeline \
  --project "my-app" \
  --target "/dashboard"
```

## 本地校验 / Local Check

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/quick_check.py
```

**中文**

它会检查插件 manifest、三个 skills、agent YAML、安装脚本、README、流水线运行索引生成器、流水线完成度审计生成器、阶段一视觉卓越门、阶段一 brief 验收器、阶段二 manifest 工具、阶段二资产提示包生成器、阶段二资产审核包生成器、阶段二最终交接文档生成器、阶段三目标项目检查器、阶段三截图 QA 计划生成器、阶段三实现补丁计划生成器、阶段三 design QA 门、视觉产物检查器、视觉差异对比器，以及仓库是否误跟踪了 `examples/`、`launch-kit/`、`docs/`、`PROMPTS.md` 等非插件内容。

如果你是普通使用者，不需要跑完整 CI，可以优先运行安装诊断：

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/diagnose_install.py
```

**English**

This checks the plugin manifest, three skills, agent YAML files, install script, README, pipeline runbook generator, pipeline completion audit generator, Phase 1 visual excellence gate, Phase 1 brief validator, Phase 2 manifest tools, Phase 2 asset prompt pack generator, Phase 2 asset review packet generator, Phase 2 final handoff generator, Phase 3 target inspector, Phase 3 screenshot QA plan generator, Phase 3 implementation patch plan generator, Phase 3 design QA gate, visual artifact checker, visual diff helper, and whether non-plugin material such as `examples/`, `launch-kit/`, `docs/`, or `PROMPTS.md` is accidentally tracked.

If you are a regular user and do not need the full CI check, run the install doctor first:

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/diagnose_install.py
```

## 阶段一 Brief 验收器 / Phase 1 Brief Validator

**中文**

阶段一结束前，可以用内置验收器确认 `phase1-ui-brief.md` 真的能指导阶段二生成资产。它会检查源审计、预览图路径、阶段二生成指南、插画/界面分层、二次可调参数、命名/导出/响应式裁切规则、完整基础组件清单和 20 个常用 icons：

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/validate_phase1_brief.py ./phase1-ui-brief.md
```

**English**

Before Phase 1 ends, validate that `phase1-ui-brief.md` can actually drive Phase 2 asset production. The validator checks source audit, preview image references, the Phase 2 generation guide, illustration/UI layer map, refinement parameters, naming/export/responsive crop rules, the complete foundation component inventory, and all 20 common icons:

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/validate_phase1_brief.py ./phase1-ui-brief.md
```

## 阶段一视觉卓越门 / Phase 1 Visual Excellence Gate

**中文**

阶段一不能只给一个“还行”的方向。先生成三个独立视觉方向，选中一个，再给选中方向按构图、层级、字体、间距、资产丰富度、交互清晰度、产品真实度和实现可行性打分。每项默认至少 8/10，才能进入阶段二。

如果预览图包含中文、日文、韩文、RTL 文本、emoji 或其他非拉丁字符，阶段一必须人工检查渲染结果，确认没有缺字、方块字、错误 fallback emoji、文字裁切或不可读文本。发现字体问题时先换成覆盖对应字符集的字体并重新截图，再运行视觉卓越门。

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/generate_visual_excellence_gate.py \
  --root ./phase1 \
  --phase1-brief ./phase1/phase1-ui-brief.md \
  --option "option-a|Executive Command|phase1-option-a.png|Dark command-center direction" \
  --option "option-b|Signal Desk|phase1-option-b.png|Lighter operational dashboard direction" \
  --option "option-c|Private Console|phase1-option-c.png|Minimal secure assistant direction" \
  --selected-option option-a \
  --score composition=9 \
  --score hierarchy=9 \
  --score typography=8 \
  --score spacing=8 \
  --score asset_richness=9 \
  --score interaction_clarity=8 \
  --score product_fidelity=9 \
  --score implementation_feasibility=8 \
  --output-dir ./phase1
```

**English**

Phase 1 should not settle for one "okay" direction. Generate three independent visual directions, select one, then score it for composition, hierarchy, typography, spacing, asset richness, interaction clarity, product fidelity, and implementation feasibility. Each criterion defaults to at least 8/10 before Phase 2 can start.

If the preview contains Chinese, Japanese, Korean, RTL text, emoji, or other non-Latin characters, Phase 1 must visually inspect the rendered image for missing glyphs, tofu boxes, wrong fallback emoji, clipped text, or unreadable copy. Fix font coverage and recapture the preview before running the visual excellence gate.

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/generate_visual_excellence_gate.py \
  --root ./phase1 \
  --phase1-brief ./phase1/phase1-ui-brief.md \
  --option "option-a|Executive Command|phase1-option-a.png|Dark command-center direction" \
  --option "option-b|Signal Desk|phase1-option-b.png|Lighter operational dashboard direction" \
  --option "option-c|Private Console|phase1-option-c.png|Minimal secure assistant direction" \
  --selected-option option-a \
  --score composition=9 \
  --score hierarchy=9 \
  --score typography=8 \
  --score spacing=8 \
  --score asset_richness=9 \
  --score interaction_clarity=8 \
  --score product_fidelity=9 \
  --score implementation_feasibility=8 \
  --output-dir ./phase1
```

## 阶段二 Manifest 生成器 / Phase 2 Manifest Generator

**中文**

阶段二可以使用内置脚本生成完整基础组件清单，避免漏掉按钮、角标、卡片、combobox、常用 icons、导航、通告、搜索、章节标题、弹窗和过渡动画状态：

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/generate_foundation_manifest.py \
  --project my-app \
  --screen dashboard \
  --target-route /dashboard \
  --style-name "approved premium direction" \
  --status review-pending \
  --output ./asset-manifest.json
```

**English**

Phase 2 can use the bundled script to generate a complete foundation component manifest so buttons, badges, cards, comboboxes, common icons, navigation, notice bars, search bars, section titles, modals, and transition states are not missed.

## 阶段二资产提示包生成器 / Phase 2 Asset Prompt Pack Generator

**中文**

当用户不懂美术、Figma 或资产切图时，可以先把阶段一 brief 和阶段二 manifest 转成一份具体的生产提示包。它会输出 AI raster、Figma/vector、CSS/SVG 三类资产生产提示、分层规则、二次调参项、manifest 路径和审核清单：

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/generate_asset_prompt_pack.py \
  --phase1-brief ./phase1-ui-brief.md \
  --manifest ./asset-manifest.json \
  --strategy hybrid \
  --output ./phase2-asset-prompt-pack.md
```

**English**

When the user does not know art direction, Figma, or asset slicing, convert the Phase 1 brief and Phase 2 manifest into a practical production prompt pack first. It outputs AI raster, Figma/vector, and CSS/SVG prompts, layer rules, refinement knobs, manifest paths, and review checklist:

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/generate_asset_prompt_pack.py \
  --phase1-brief ./phase1-ui-brief.md \
  --manifest ./asset-manifest.json \
  --strategy hybrid \
  --output ./phase2-asset-prompt-pack.md
```

## 阶段二 Manifest 验收器 / Phase 2 Manifest Validator

**中文**

生成资产后，用验收器确认完整基础组件和常用 icons 没有漏项：

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/validate_foundation_manifest.py ./asset-manifest.json
```

**English**

After asset generation, validate that the foundation component states and common icons are complete:

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/validate_foundation_manifest.py ./asset-manifest.json
```

## 阶段二资产审核包生成器 / Phase 2 Asset Review Packet Generator

**中文**

阶段二最终输出前，需要让用户明确审核资产是否通过。这个脚本会把 manifest、contact sheet、prompt pack 和 review URL 组合成普通用户能看懂的审核包，并给出四个回复选项：通过、改视觉、改命名/目录、改实现映射。

生成审核包后，必须人工检查 contact sheet 和 approval HTML，确认标题、按钮、icon label、底部说明和长文案没有裁切、溢出、缺字、方块字、隐藏到右/下边缘或变成不可读文本。

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/generate_asset_review_packet.py \
  --manifest ./asset-manifest.json \
  --phase1-brief ./phase1-ui-brief.md \
  --prompt-pack ./phase2-asset-prompt-pack.md \
  --contact-sheet ./review/phase2-contact-sheet.png \
  --assembly-preview ./review/primary-screen-asset-assembly.png \
  --visual-diff-report ./review/visual-diff-primary-screen.md \
  --review-url http://127.0.0.1:8000/component-contact-sheet.html \
  --output-dir ./review
```

**English**

Before Phase 2 final output, the user must explicitly approve or revise assets. This script combines the manifest, contact sheet, prompt pack, and review URL into a plain review packet with four decisions: approve assets, revise visual style, revise naming/organization, or revise implementation mapping.

After generating the packet, visually inspect the contact sheet and approval HTML for clipped headings, button text, icon labels, footer notes, overflow, missing glyphs, tofu boxes, right/bottom-edge truncation, or unreadable copy.

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/generate_asset_review_packet.py \
  --manifest ./asset-manifest.json \
  --phase1-brief ./phase1-ui-brief.md \
  --prompt-pack ./phase2-asset-prompt-pack.md \
  --contact-sheet ./review/phase2-contact-sheet.png \
  --assembly-preview ./review/primary-screen-asset-assembly.png \
  --visual-diff-report ./review/visual-diff-primary-screen.md \
  --review-url http://127.0.0.1:8000/component-contact-sheet.html \
  --output-dir ./review
```

## 阶段二最终交接文档生成器 / Phase 2 Final Handoff Generator

**中文**

用户明确说资产通过后，用这个脚本生成标准 `phase2-asset-handoff.md`。它会把审批文字、manifest、review packet、contact sheet、visual diff、组件调用规则、动效规则和 Phase 3 验收清单合并成一份可直接交给 `$frontend-implementation` 的文档。没有明确通过文字时，脚本会失败，防止跳过审核门禁。

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/generate_phase2_handoff.py \
  --manifest ./asset-manifest.json \
  --phase1-brief ./phase1-ui-brief.md \
  --prompt-pack ./phase2-asset-prompt-pack.md \
  --review-packet ./review/phase2-asset-approval-packet.md \
  --contact-sheet ./review/phase2-contact-sheet.png \
  --assembly-preview ./review/primary-screen-asset-assembly.png \
  --visual-diff-report ./review/visual-diff-report.md \
  --target-runtime "uni-app" \
  --approved-by "user" \
  --approval-text "Assets approved. Generate phase2-asset-handoff.md and continue to frontend implementation." \
  --output ./phase2-asset-handoff.md
```

**English**

After the user explicitly approves the assets, use this script to generate the standard `phase2-asset-handoff.md`. It combines approval text, manifest entries, review packet, contact sheet, visual diff report, component usage rules, motion rules, and the Phase 3 acceptance checklist into one document for `$frontend-implementation`. The script fails when approval text is missing or not explicit, so the review gate cannot be skipped accidentally.

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/generate_phase2_handoff.py \
  --manifest ./asset-manifest.json \
  --phase1-brief ./phase1-ui-brief.md \
  --prompt-pack ./phase2-asset-prompt-pack.md \
  --review-packet ./review/phase2-asset-approval-packet.md \
  --contact-sheet ./review/phase2-contact-sheet.png \
  --assembly-preview ./review/primary-screen-asset-assembly.png \
  --visual-diff-report ./review/visual-diff-report.md \
  --target-runtime "uni-app" \
  --approved-by "user" \
  --approval-text "Assets approved. Generate phase2-asset-handoff.md and continue to frontend implementation." \
  --output ./phase2-asset-handoff.md
```

## 阶段三目标项目检查器 / Phase 3 Target Inspector

**中文**

进入真实前端实现前，用这个脚本检查目标项目是什么框架、目标路由文件在哪里、有没有 `npm run dev`、是否需要 HBuilderX、API 客户端在哪里、资产应该放到什么目录。它会输出 JSON 和 Markdown 报告，方便 `$frontend-implementation` 在动代码前先确定运行方式和风险。

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/inspect_frontend_target.py \
  /path/to/frontend-app \
  --target-route pages/grid/grid \
  --output-md ./phase3-target-inspection.md \
  --output-json ./phase3-target-inspection.json
```

**English**

Before implementing into a real frontend, use this script to inspect the target app framework, route file, available `npm run` commands, whether HBuilderX or another external runtime is needed, API client locations, and recommended asset paths. It writes JSON and Markdown reports so `$frontend-implementation` can choose the correct run and replacement strategy before editing code.

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/inspect_frontend_target.py \
  /path/to/frontend-app \
  --target-route pages/grid/grid \
  --output-md ./phase3-target-inspection.md \
  --output-json ./phase3-target-inspection.json
```

## 阶段三截图 QA 计划生成器 / Phase 3 Screenshot QA Plan Generator

**中文**

目标项目检查完成后，用这个脚本生成桌面/移动端截图计划、Playwright 捕获脚本、截图输出路径、视觉产物检查命令和视觉差异对比命令。它不会假装项目已经能跑起来；如果检测到 HBuilderX 或外部运行环境，就会把截图计划和外部运行提示写清楚。

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/generate_screenshot_qa_plan.py \
  --inspection ./phase3-target-inspection.json \
  --base-url http://127.0.0.1:5173 \
  --route-url '#/pages/grid/grid' \
  --approved-preview ./phase1-preview-mobile.png \
  --output-dir ./phase3-screenshot-qa
```

**English**

After target inspection, use this script to generate desktop/mobile screenshot targets, a Playwright capture script, screenshot output paths, visual artifact check commands, and visual diff commands. It does not pretend the app is already runnable; if HBuilderX or another external runtime is required, the plan records that guidance.

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/generate_screenshot_qa_plan.py \
  --inspection ./phase3-target-inspection.json \
  --base-url http://127.0.0.1:5173 \
  --route-url '#/pages/grid/grid' \
  --approved-preview ./phase1-preview-mobile.png \
  --output-dir ./phase3-screenshot-qa
```

## 阶段三实现补丁计划生成器 / Phase 3 Implementation Patch Plan Generator

**中文**

真实改项目之前，用这个脚本把“要复制哪些资产、要改哪些文件、哪些 API 必须保留、哪些运行/截图检查要做”先写成计划。没有阶段二明确通过或目标路由没有匹配时，它会标记 `blockedBeforeEditing: true`，防止误改正式应用。

复制清单会按 `kind + source + destination` 去重；共享的 foundation CSS 或 icon sprite 只会列一次，同时在 JSON 中保留聚合后的 `components`、`states` 和 `entryCount`。

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/generate_implementation_patch_plan.py \
  --manifest ./asset-manifest.json \
  --inspection ./phase3-target-inspection.json \
  --phase2-handoff ./phase2-asset-handoff.md \
  --screenshot-plan ./phase3-screenshot-qa/phase3-screenshot-qa-plan.md \
  --output-dir ./phase3-patch-plan
```

**English**

Before editing a real project, use this script to plan exactly which assets to copy, which files to edit, which APIs to preserve, and which runtime/screenshot checks to run. If Phase 2 approval is missing or the target route is not matched, it records `blockedBeforeEditing: true` so the production app is not changed accidentally.

Copy operations are deduplicated by `kind + source + destination`; shared foundation CSS or icon sprites are listed once while aggregated `components`, `states`, and `entryCount` remain in the JSON plan.

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/generate_implementation_patch_plan.py \
  --manifest ./asset-manifest.json \
  --inspection ./phase3-target-inspection.json \
  --phase2-handoff ./phase2-asset-handoff.md \
  --screenshot-plan ./phase3-screenshot-qa/phase3-screenshot-qa-plan.md \
  --output-dir ./phase3-patch-plan
```

## 视觉产物检查器 / Visual Artifact Checker

**中文**

用这个脚本检查阶段一预览图、阶段二 contact sheet、审核 HTML 和阶段三截图是否存在、非空，并能读到尺寸。它不依赖 Pillow 或浏览器，适合在 CI 或普通用户电脑上快速排除空图、坏图、路径错误：

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/check_visual_artifacts.py \
  ./phase1-preview-mobile.png \
  ./review/phase2-contact-sheet.png \
  ./review/phase2-asset-approval-packet.html \
  --min-width 320 \
  --min-height 240
```

**English**

Use this script to check that Phase 1 previews, Phase 2 contact sheets, review HTML, and Phase 3 screenshots exist, are non-empty, and expose readable dimensions. It does not require Pillow or a browser, which makes it suitable for CI and non-expert local checks:

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/check_visual_artifacts.py \
  ./phase1-preview-mobile.png \
  ./review/phase2-contact-sheet.png \
  ./review/phase2-asset-approval-packet.html \
  --min-width 320 \
  --min-height 240
```

## 视觉差异对比器 / Visual Diff Helper

**中文**

当阶段二资产预览或阶段三真实截图需要对齐已批准的阶段一预览图时，用这个脚本生成 PNG 像素差异报告。它会输出尺寸、差异像素比例、平均通道差异、最大通道差异，并可写出 JSON/Markdown 证据文件：

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/compare_visual_artifacts.py \
  ./phase1-preview-mobile.png \
  ./implementation-screenshot-mobile.png \
  --pixel-tolerance 4 \
  --max-diff-pct 1 \
  --max-mean-delta 3 \
  --output-md ./visual-diff-report.md \
  --output-json ./visual-diff-report.json
```

如果两个图不是同一个尺寸，但你只想对比重叠区域，可以加 `--allow-size-mismatch`。这个报告用于 QA 证据和返工定位，不会替代用户在阶段二的明确审核通过。

**English**

When a Phase 2 asset preview or Phase 3 implementation screenshot should match an approved Phase 1 preview, use this script to generate a PNG pixel-diff report. It reports dimensions, differing-pixel ratio, mean channel delta, max channel delta, and optional JSON/Markdown evidence files:

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/compare_visual_artifacts.py \
  ./phase1-preview-mobile.png \
  ./implementation-screenshot-mobile.png \
  --pixel-tolerance 4 \
  --max-diff-pct 1 \
  --max-mean-delta 3 \
  --output-md ./visual-diff-report.md \
  --output-json ./visual-diff-report.json
```

Use `--allow-size-mismatch` if the two PNGs have different dimensions and you only want to compare the overlapping area. The report is QA evidence for refinement and handoff; it does not replace explicit Phase 2 asset approval.

## 阶段三 Design QA 门 / Phase 3 Design QA Gate

**中文**

阶段三截图和视觉差异报告出来后，用这个脚本生成 blocking `design-qa.md`。只有 `final result: passed` 才能最终交付；如果缺截图、缺 diff 或外部运行环境没法捕获，它会写成 `final result: blocked` 并列出阻塞原因。

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/generate_design_qa_gate.py \
  --source-preview ./phase1-preview-mobile.png \
  --implementation-screenshot ./implementation-screenshot-mobile.png \
  --visual-diff-json ./visual-diff-report.json \
  --require-diff \
  --output-md ./design-qa.md \
  --output-json ./design-qa.json
```

**English**

After Phase 3 screenshots and visual diff reports exist, use this script to generate the blocking `design-qa.md`. Final handoff is allowed only when it says `final result: passed`; if screenshots, diff evidence, or external runtime capture is missing, it writes `final result: blocked` with concrete blockers.

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/generate_design_qa_gate.py \
  --source-preview ./phase1-preview-mobile.png \
  --implementation-screenshot ./implementation-screenshot-mobile.png \
  --visual-diff-json ./visual-diff-report.json \
  --require-diff \
  --output-md ./design-qa.md \
  --output-json ./design-qa.json
```

## 阶段二本地审核服务器 / Phase 2 Local Review Server

**中文**

如果阶段二生成了 contact sheet、SVG sprite、字体或相对路径资源，建议用内置本地服务器打开审核包，而不是直接双击 HTML：

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/serve_review.py ./phase2/review --entry component-contact-sheet.html
```

复制输出里的 `Review URL` 到浏览器即可。

**English**

If Phase 2 generates a contact sheet, SVG sprite, fonts, or relative assets, serve the review folder locally instead of double-clicking the HTML file. Copy the printed `Review URL` into your browser.

## License

MIT
