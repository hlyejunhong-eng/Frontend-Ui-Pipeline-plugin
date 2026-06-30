# 案例：把普通 onboarding 页面做成高端定制前端

## 输入

产品：DraftPilot，一个给小企业主用的 AI 文案助手。

原始页面：

- 白底页面
- 左侧导航
- 欢迎标题
- 三个 setup steps
- 一个主按钮

原始文案：

- Welcome to DraftPilot
- Set up your workspace and create your first campaign.
- Add brand voice
- Connect website
- Create first campaign

## 阶段一输出

锁定方向：Editorial command center。

这个方向不是简单换颜色，而是把页面做成“有编辑感的工作台”：

- 暖纸张背景
- 高对比主标题
- 右侧进度与建议
- 明确的 setup path
- 背景插画层不遮挡内容
- 按钮、卡片、通告、组合框都有统一动效语言

产物：

- `examples/demo-draftpilot/phase1/phase1-ui-brief.md`
- `examples/demo-draftpilot/phase1/phase1-preview-desktop.png`
- `examples/demo-draftpilot/phase1/phase1-preview-mobile.png`

## 阶段二输出

不只做当前页面用到的 3 个图标，而是生成基础组件资产包：

- 背景插画
- setup step icons
- 完整 icon sprite
- button / badge / card / combobox / nav / notice / search / modal
- transition animation CSS
- component gallery
- asset manifest
- handoff 文档

产物：

- `examples/demo-draftpilot/phase2/design-system/component-kit.css`
- `examples/demo-draftpilot/phase2/design-system/icon-sprite.svg`
- `examples/demo-draftpilot/phase2/design-system/component-gallery.png`
- `examples/demo-draftpilot/phase2/phase2-asset-handoff.md`

## 阶段三输出

真实可运行前端：

- 直接打开 `examples/demo-draftpilot/phase3/implementation/index.html`
- 使用阶段二资产
- 使用 foundation component kit
- 无真实 API 时，用 `mockOnboardingSteps` 先落地
- 有桌面/移动截图证据

产物：

- `examples/demo-draftpilot/phase3/implementation/index.html`
- `examples/demo-draftpilot/phase3/implementation/styles.css`
- `examples/demo-draftpilot/phase3/implementation/app.js`
- `examples/demo-draftpilot/evidence/screenshots/draftpilot-desktop.png`
- `examples/demo-draftpilot/evidence/screenshots/draftpilot-mobile.png`

## 可发布结论

这个案例证明：它不是“AI 生成一张漂亮 UI 图”，而是从旧页面输入，一路走到设计说明、组件资产、动效规则、代码实现和截图验证。
