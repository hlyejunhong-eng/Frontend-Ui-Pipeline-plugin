# 从安装到真正开始用

目标用户：不会画 UI、不会做美术资产、不熟前端实现，但想把已有页面做成高端定制体验的人。

## 先把一句话说清楚

“安装后给一个旧页面就能开始”具体是：

1. 安装的是 **Codex 插件**：Frontend UI Pipeline。
2. 打开的是 **Codex 应用**：安装插件后，新建一个 Codex 线程。
3. 发送的位置是 **Codex 新线程底部的消息输入框**。
4. 发送的内容是：旧页面截图、本地项目路径、本地运行地址、Figma 链接，或者一段页面描述，再加上启动 prompt。
5. Codex 会按插件里的三个 skills 继续追问、生成文档、生成资产、最后实现前端。

## 1. 准备环境

你需要先有：

- Codex 应用或 Codex CLI，可以正常打开一个新线程。
- Git，用来下载插件仓库。
- Python 3，用来注册本地 marketplace。
- 如果要让阶段三直接改真实项目，还需要把你的前端项目放在本机，并能在 Codex 里访问到项目路径。

## 2. 下载插件

```bash
mkdir -p ~/plugins
git clone https://github.com/hlyejunhong-eng/Frontend-Ui-Pipeline-plugin.git ~/plugins/frontend-ui-pipeline
```

这一步的结果是：你的电脑里会出现一个插件目录：

```text
~/plugins/frontend-ui-pipeline
```

## 3. 注册插件到 Codex 的个人 marketplace

```bash
python3 ~/plugins/frontend-ui-pipeline/scripts/install_local_marketplace.py
```

这一步会把插件写入你的个人 marketplace，让 Codex 能看到它。

## 4. 在 Codex 里添加插件

```bash
codex plugin add frontend-ui-pipeline@personal
```

完成后，关闭当前 Codex 线程，重新打开一个新线程。新线程才会加载刚安装的插件 skills。

## 5. 打开哪个应用

打开 **Codex 应用**。

然后：

1. 点击新建线程。
2. 选择或确认当前工作目录。
3. 在底部消息输入框粘贴你的旧页面材料和启动 prompt。

如果你使用的是 Codex CLI，就在终端里的 Codex 对话输入区粘贴同样的内容。

## 6. “旧页面”到底怎么给

你可以任选一种方式：

### 方式 A：给截图

适合：没有代码，只有一个旧页面或竞品页面。

你发送：

```text
Use the Frontend UI Pipeline on this old page screenshot.

Input:
- 我上传了一张旧页面截图。

Goal:
请把这个页面重做成高端定制 UI，先输出阶段一 brief 和预览图，再进入阶段二资产生产，最后实现可运行前端。如果没有真实项目，就先生成独立可运行 demo。
```

### 方式 B：给本地项目路径

适合：你有真实前端项目，想让 Codex 直接改项目。

你发送：

```text
Use the Frontend UI Pipeline on this real frontend route.

Project path:
/Users/<你的用户名>/path/to/your-frontend-project

Target route or screen:
/dashboard/onboarding

Goal:
请基于当前页面重新设计高端 UI，生成完整组件资产包和动效规则。阶段三请直接在这个项目里实现；如果接口不清楚，先用同结构 mock 数据。
```

### 方式 C：给本地运行地址

适合：项目已经能跑起来，比如 `npm run dev` 后有 localhost。

你发送：

```text
Use the Frontend UI Pipeline on this running local app.

Local URL:
http://localhost:3000/dashboard/onboarding

Project path:
/Users/<你的用户名>/path/to/your-frontend-project

Goal:
请先审视这个页面，再生成阶段一高端 UI brief 和预览图。阶段二生成完整资产包，阶段三热更替换到真实前端项目。
```

### 方式 D：给 Figma 链接

适合：已有设计稿，但想变成更高级的可实现方案。

你发送：

```text
Use the Frontend UI Pipeline on this Figma screen.

Figma:
<粘贴 Figma 链接>

Goal:
请基于这个页面重新生成高端定制方向、资产系统和真实前端实现方案。如果不能直接读取 Figma，请告诉我需要补充哪些截图或节点信息。
```

### 方式 E：只给页面描述

适合：你还没有页面，但知道功能。

你发送：

```text
Use the Frontend UI Pipeline to create a premium frontend flow.

Page description:
这是一个给小商家使用的 AI 文案助手 onboarding 页面。页面需要展示欢迎语、三个设置步骤、品牌语气、网站连接、创建第一条营销内容，以及右侧进度建议。

Goal:
请从阶段一开始，生成高端 UI brief、预览图、阶段二资产包，最后做一个可运行前端 demo。
```

## 7. 启动全流程的通用 prompt

如果你只想复制一段万能版，就用这段：

```text
Use the Frontend UI Pipeline to redesign and implement this app flow.

Input:
- <粘贴旧页面截图、本地项目路径、localhost 地址、Figma 链接或页面描述>

Target user:
- <这个页面给谁用>

Business goal:
- <为什么要把它做高级>

Implementation target:
- 如果有真实前端项目，请直接改真实项目。
- 如果没有真实项目，请生成独立可运行 demo。
- 如果有真实 API 就接 API，没有就用同结构 mock 数据。

Output requirements:
- Phase 1: 高端 UI brief、桌面/移动预览图、像素级布局/文字/按钮/动效要求。
- Phase 2: 完整基础组件资产包、命名资产、asset manifest、asset handoff，并在最终输出前让我审核资产是否通过。
- Phase 3: 可运行前端、资产接入、接口或 mock、桌面/移动截图和验证命令。
```

## 8. 推荐给 Codex 的补充信息

最少只需要其中一种：

- 旧页面截图
- 本地项目路径
- 本地运行地址
- Figma 链接
- 页面功能描述

更好的输入：

- 目标用户是谁
- 想变高级的原因
- 有无品牌颜色或参考风格
- 真实 API 是否已经存在

## 9. 三阶段会发生什么

### 阶段一：锁定高级风格

输出：

- `phase1-ui-brief.md`
- 桌面/移动预览图
- 组件、按钮、文案、动效、背景的像素级要求
- 给阶段二的生成指南
- 插画分层、透明度、模糊、阴影、遮罩、动效参数

### 阶段二：生成完整资产系统

输出：

- 背景、插图、遮罩、图标
- 按钮、数字角标、卡片、组合框
- 首页、个人页、通用页、扫一扫、购物车、支付、聊天、确认、关闭、返回/前往、热门、点赞、设置、帮助、信息、钱包、列表、收藏、搜索等通用 icons
- 导航栏、通告栏、搜索栏、章节标题、弹窗
- 过渡动画、按压反馈、hover、loading、reduced-motion
- `asset-manifest.json`
- `phase2-asset-handoff.md`
- 可视化资产审核页

阶段二必须让用户审核通过后再进入最终交付。

### 阶段三：真实落地前端

输出：

- 可运行前端页面
- 接真实 API 或同结构 mock
- 导入阶段二资产和基础组件库
- 桌面/移动截图
- 运行命令、验证结果和剩余风险

## 10. 怎么判断真的成功

成功不是“有一张好看的图”。成功应该至少有：

- 设计 brief
- 预览图
- 完整基础组件资产包
- asset handoff
- 可运行代码
- 桌面/移动截图

仓库里的 DraftPilot demo 就是这个标准。
