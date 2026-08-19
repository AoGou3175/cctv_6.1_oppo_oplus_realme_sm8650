# 版本快照记录

## 2026-08-19 15:05:39

- 修改内容：将 `build-test.yml` 改为七版本批量构建和统一发布入口；为七个 `fastbuild_6.1.*.yml` 增加 `workflow_call`，统一使用 `inputs.*`，批量调用时跳过单版本 Release，并在 ZIP 名称中加入 `SUB_VERSION`。
- 修改原因：让 6.1.57、6.1.75、6.1.115、6.1.118、6.1.128、6.1.134、6.1.141 使用同一组选项构建，全部成功后只创建一个 Release。
- 影响文件：`.github/workflows/build-test.yml`、七个 `.github/workflows/fastbuild_6.1.*.yml`、`tests/validate_batch_release.ps1`、设计和实施计划文档。
- 快照文件：
  - `build-test-20260819-150539-batch-release.yml`
  - `fastbuild_6.1.115-20260819-150539-batch-release.yml`
  - `fastbuild_6.1.118-20260819-150539-batch-release.yml`
  - `fastbuild_6.1.128-20260819-150539-batch-release.yml`
  - `fastbuild_6.1.134-20260819-150539-batch-release.yml`
  - `fastbuild_6.1.141-20260819-150539-batch-release.yml`
  - `fastbuild_6.1.57-20260819-150539-batch-release.yml`
  - `fastbuild_6.1.75-20260819-150539-batch-release.yml`
- 验证：`powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tests\validate_batch_release.ps1`，结果为 `validate_batch_release: PASS`；`git diff --check` 未发现差异错误。
- 问题和解决办法：原批量测试只打包虚拟 `testfile`；原 ZIP 名称缺少子版本号。已改为调用真实构建工作流，并加入子版本号以保证七个 Artifact 唯一。
- `AGENTS.md`：未更新，未发现需要新增的长期项目规则。
- GitHub 备份状态：本次修改和快照尚未上传 GitHub。

## 2026-08-19 16:09:57

- 修改内容：新增 `.github/workflows/build-test_6.1_kpm.yml`，显示名称为 `build-test_6.1_kpm`，默认开启 KPM；同时依赖七个可复用的 `fastbuild_6.1.*.yml` 工作流。
- 修改原因：让 Actions 页面可以单独执行七个版本的批量构建，并在七个版本全部成功后创建一个统一 Release。
- 影响文件：`.github/workflows/build-test_6.1_kpm.yml`、七个 `.github/workflows/fastbuild_6.1.*.yml`。
- 快照文件：`build-test_6.1_kpm-20260819-160957-kpm-enabled.yml`。
- 验证：批量工作流静态检查通过；`validate_batch_release.ps1` 输出 `validate_batch_release: PASS`；`git diff --check` 未发现差异错误。
- 问题和解决办法：该批量工作流不能单独上传，七个被调用的工作流必须同时声明 `workflow_call` 输入；已确认本地配套文件已具备这些声明。
- `AGENTS.md`：未更新，未发现需要新增的长期项目规则。
- GitHub 备份状态：准备上传到公开仓库，上传前尚未执行构建。

## 2026-08-19 16:17:41

- 修改内容：将 `.github/workflows/build-test_6.1_kpm.yml` 的调用方权限从 `contents: read`、`packages: none` 调整为 `contents: write`、`packages: write`。
- 修改原因：GitHub 启动阶段拒绝可复用工作流的嵌套 `release` job，因为它请求写权限而调用方只提供读权限。
- 影响文件：`.github/workflows/build-test_6.1_kpm.yml`。
- 快照文件：`build-test_6.1_kpm-20260819-161741-permissions-fix.yml`。
- 验证：根据 Actions 运行 32231639371 的 Annotation 定位到权限错误；本地批量工作流验证继续通过。
- 问题和解决办法：这是工作流启动权限校验错误，不是 KPM 或内核编译错误；已在调用方补齐嵌套 Release 所需权限。
- `AGENTS.md`：未更新，未发现需要新增的长期项目规则。
- GitHub 备份状态：修复已在本地，准备推送。

## 2026-08-19 22:37:35

- 修改内容：为七个 `fastbuild_6.1.*.yml` 增加 Ubuntu apt 镜像切换、软件包检测、重试和 180 秒超时；修复 `6.1.128` 添加 KernelSU 前漏掉 `cd kernel_workspace`；增加 `batch_mode`，批量调用时跳过七个单版本 Release。
- 修改原因：上次运行中五个版本卡在 `azure.archive.ubuntu.com`，6.1.128 因工作目录错误找不到 `drivers/`，并且 6.1.75 产生了不应出现的单版本 Release。
- 影响文件：`.github/workflows/build-test_6.1_kpm.yml`、七个 `.github/workflows/fastbuild_6.1.*.yml`、`tests/validate_batch_release.ps1`。
- 快照文件：`build-test_6.1_kpm-20260819-223735-build-stability.yml`、七个 `fastbuild_6.1.*-20260819-223735-build-stability.yml`、`validate_batch_release-20260819-223735-build-stability.ps1`。
- 验证：`validate_batch_release.ps1` 输出 `validate_batch_release: PASS`；apt、`batch_mode`、6.1.128 工作目录和七个 ZIP 数量检查通过；`git diff --check` 通过。当前环境没有 Python/YAML 解析器，未执行本地 YAML 解析，最终工作流语法由 GitHub Actions 启动校验。
- 问题和解决办法：GitHub runner 的 Azure Ubuntu 镜像在本次运行中长时间无响应；工作流现在优先跳过已安装依赖，缺少依赖时切换到 `archive.ubuntu.com` 并限制重试时间。
- `AGENTS.md`：未更新，未发现需要新增的长期项目规则。
- GitHub 备份状态：本次修改和快照已提交并推送到公开仓库 `AoGou3175/cctv_6.1_oppo_oplus_realme_sm8650` 的 `main`，提交为 `ceecd4f`。

## 2026-08-19 23:06:34

- 修改内容：将单独构建 Release 中的管理器下载链接、更新内容、安装方法、元模块说明和刷写风险提示同步到 `build-test_6.1_kpm.yml` 的汇总 Release；增加 KSU 分支显示名称转换，并使用 `needs.build_57.outputs.ksuver` 显示实际构建输出的版本号。
- 修改原因：批量汇总 Release 使用独立的 `release_notes.md`，不会自动继承单独构建工作流的完整说明。
- 影响文件：`.github/workflows/build-test_6.1_kpm.yml`、`tests/validate_batch_release.ps1`。
- 快照文件：`build-test_6.1_kpm-20260819-230634-release-notes.yml`、`validate_batch_release-20260819-230634-release-notes.ps1`。
- 验证：验证脚本输出 `validate_batch_release: PASS`；确认管理器链接、Installation Guide、KernelFlasher 和批量 KSU 版本输出引用均存在；`git diff --check` 通过。
- 问题和解决办法：批量 Release 不会复用子工作流的说明，已在汇总工作流中补齐完整 Markdown 文本。
- `AGENTS.md`：未更新，未发现需要新增的长期项目规则。
- GitHub 备份状态：本次修改和快照尚未推送 GitHub。

## 2026-08-19 23:23:00

- 修改内容：在汇总 Release 中增加七版本机型、平台、Android 版本和实际源码分支对应表，分别列出 SM8650/一加12、MT6989/Ace5-Race、MT6897/一加 Pad 的来源。
- 修改原因：七个构建使用的源码和目标机型并不相同，原说明统一写成一个 SM8650 机型会造成误解。
- 影响文件：`.github/workflows/build-test_6.1_kpm.yml`、`tests/validate_batch_release.ps1`。
- 快照文件：`build-test_6.1_kpm-20260819-232300-per-version-mapping.yml`、`validate_batch_release-20260819-232300-per-version-mapping.ps1`。
- 验证：验证脚本输出 `validate_batch_release: PASS`；七个实际源码分支名称和逐版本映射表检查通过；`git diff --check` 通过。
- 问题和解决办法：原汇总说明只有一条固定机型描述，已改为逐版本 Markdown 表格并附源码分支链接。
- `AGENTS.md`：未更新，未发现需要新增的长期项目规则。
- GitHub 备份状态：本次修改和快照尚未推送 GitHub。
