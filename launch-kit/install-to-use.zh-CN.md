# 从安装到实用

目标用户：不会画 UI、不会做美术资产、不熟前端实现，但想把已有页面做成高端定制体验的人。

## 1. 安装插件

```bash
mkdir -p ~/plugins
git clone https://github.com/hlyejunhong-eng/Frontend-Ui-Pipeline-plugin.git ~/plugins/frontend-ui-pipeline
python3 ~/plugins/frontend-ui-pipeline/scripts/install_local_marketplace.py
codex plugin add frontend-ui-pipeline@personal
```

安装后新开一个 Codex 线程。

## 2. 准备输入

最少只需要给其中一种：

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

## 3. 一句话启动全流程

```text
Use the Frontend UI Pipeline to redesign and implement this app flow.

Target:
- <旧页面截图、本地项目路径、Figma、路由或页面描述>

Goal:
我不懂 UI 美术和前端实现。请帮我把它做成高端定制 UI，生成完整基础组件资产包、动效规则，并最终落到真实可运行前端。如果没有真实 API，就用同结构 mock 数据先实现。
```

## 4. 三阶段会发生什么

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

## 5. 怎么判断真的成功

成功不是“有一张好看的图”。成功应该至少有：

- 设计 brief
- 预览图
- 完整基础组件资产包
- asset handoff
- 可运行代码
- 桌面/移动截图

仓库里的 DraftPilot demo 就是这个标准。
