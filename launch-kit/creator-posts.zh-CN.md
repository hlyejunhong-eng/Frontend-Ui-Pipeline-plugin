# 自媒体发布脚本

## 爆款标题方向

1. 不会 UI、不会前端，我用 Codex 做了一个高端定制页面
2. 别再只让 AI 画 UI 图了，我要的是能落地的前端
3. 一个普通白底页面，三阶段变成高端 SaaS 工作台
4. AI 做 UI 最大的问题不是不好看，是不能交付
5. 我做了一个 Codex 插件：从旧页面到可运行前端

## 小红书 / 即刻图文稿

标题：

不会画 UI 也能做高端前端？我做了一个 Codex 插件

正文：

很多 AI UI 工具的问题是：给你一张好看的图，然后就结束了。

但真实产品要的是：

- 设计风格能锁定
- 组件资产能复用
- 图标、按钮、卡片、弹窗、动效都有
- 最后能接进真实前端

所以我做了 Frontend UI Pipeline。

怎么开始：

1. 先把插件下载到 `~/plugins/frontend-ui-pipeline`
2. 用 `install_local_marketplace.py` 注册到 Codex 个人 marketplace
3. 执行 `codex plugin add frontend-ui-pipeline@personal`
4. 打开 Codex 应用，新建线程
5. 在底部输入框粘贴旧页面截图、项目路径、localhost 地址、Figma 链接或页面描述，再粘贴启动 prompt

它分三步：

1. 阶段一：看旧页面，生成高端 UI brief 和预览图
2. 阶段二：生成完整基础组件资产包，不只做当前页面用到的组件
3. 阶段三：把资产和动效落到真实可运行前端，没有 API 就先用同结构 mock

我放了一个 DraftPilot demo：从普通 onboarding 页面到高端定制 SaaS 工作台。

GitHub 搜：Frontend-Ui-Pipeline-plugin

## 短视频 45 秒脚本

0-3 秒：

这不是 AI UI 图，这是能落地的前端。

3-10 秒：

左边是普通白底 onboarding，右边是高端定制 SaaS 工作台。

10-18 秒：

怎么用很具体：下载插件，注册到 Codex，打开 Codex 新线程，把旧页面截图或项目路径发到输入框。

18-28 秒：

我做了一个 Codex 插件，分三阶段：
先锁风格，再生成完整组件资产包，最后落到真实代码。

28-38 秒：

重点是阶段二：按钮、数字角标、卡片、组合框、常用 icons、导航、通告、搜索、弹窗、过渡动画，全都生成。

38-44 秒：

阶段三接真实 API；没有 API，就用同结构 mock 先跑起来。

44-50 秒：

GitHub 已开源，想看案例和安装命令，评论区拿链接。

## B 站 / YouTube 简介

这期展示一个 Codex 插件 Frontend UI Pipeline：让不懂 UI 美术和前端的人，也能从已有页面快速生成高端定制 UI、完整组件资产包、动效规则，并真实落地到可运行前端。

本期案例：DraftPilot onboarding dashboard。

核心区别：不是只生成一张图，而是输出 Phase 1 brief、Phase 2 asset handoff、完整 foundation kit、Phase 3 runnable frontend。

GitHub:
https://github.com/hlyejunhong-eng/Frontend-Ui-Pipeline-plugin

## 置顶评论

安装命令：

```bash
mkdir -p ~/plugins
git clone https://github.com/hlyejunhong-eng/Frontend-Ui-Pipeline-plugin.git ~/plugins/frontend-ui-pipeline
python3 ~/plugins/frontend-ui-pipeline/scripts/install_local_marketplace.py
codex plugin add frontend-ui-pipeline@personal
```

启动方式：

1. 打开 Codex 应用
2. 新建线程
3. 在底部消息输入框粘贴旧页面截图、项目路径、localhost 地址、Figma 链接或页面描述
4. 再粘贴 `launch-kit/install-to-use.zh-CN.md` 里的万能 prompt
5. 回车发送
