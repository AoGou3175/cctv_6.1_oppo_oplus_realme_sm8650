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
