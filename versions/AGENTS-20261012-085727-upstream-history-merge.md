# GitHub Actions 内核批量构建项目规则

本文件记录本项目中可迁移到其他内核构建项目的长期经验。修改其他项目时，可以按需复制相关章节；不要覆盖目标项目已有的 `AGENTS.md` 规则。

## 1. 批量构建设计

- 多版本构建应使用独立的矩阵任务或可复用工作流，分别构建每个内核版本。
- 汇总 Release 必须等待全部版本成功后再创建，不能因为部分版本成功就发布不完整的 Release。
- 每个版本必须保留清晰的版本号、源码分支、平台和目标机型映射；不能把使用 MT6989、MT6897 源码的版本统一写成 SM8650。
- Release 说明中建议用 Markdown 表格列出每个版本的详细名称，例如：`欧加真骁龙8Gen3通用 6.1.75 内核（基于一加12 6.1.75 版官方OKI源码）`。

## 2. 构建选项

- `workflow_dispatch.inputs` 用于网页手动构建参数：`type: boolean` 是开关，`type: choice` 是下拉选择，`required: true` 表示必须填写，不表示自动开启。
- KPM、susfs、LZ4、LZ4KD 等功能应通过输入参数传递到所有子工作流，不要只修改汇总工作流的显示文字。
- 需要默认开启的功能明确设置 `default: true`；需要默认关闭的功能设置 `default: false`。
- `ksu_type` 应使用固定选项，例如 `resukisu`、`sukisu`、`ksunext`、`ksu`、`none`，并在 Release 说明中转换成易读名称。

## 3. Reusable Workflow 权限

- 如果子工作流会创建 Release、上传资产或写入仓库，调用方和被调用方都要明确允许 `contents: write`。
- 还需要检查子工作流内部 job 的 `permissions`；调用方不能把权限提升到被调用方未声明的范围。
- 常见错误是：子工作流的 `release` job 请求 `contents: write`，但批量调用工作流只提供了 `contents: read`，最终导致 workflow 在运行前直接判定无效。
- 修改权限后，先检查 YAML 静态结构，再重新运行工作流，不要只根据网页表面配置判断权限是否生效。

## 4. 汇总 Release 标题和说明

- 汇总标题统一使用动态名称：`欧加真 ${KSU_TYPENAME} 6.1.X通用内核 | 构建信息`。
- 汇总说明中的通用机型写成：`机型：欧加真6.1.X内核`。
- 不要把所有版本写成“SM8650 七版本内核”；七个版本的实际源码平台可能不同，必须保留逐版本详细对应表。
- Release 说明应保留单独构建时已有的安装方法、管理器下载链接、元模块提示和刷写风险提示。
- Release 说明中的版本号、KSU 版本号和构建时间应尽量使用实际构建输出或工作流输出，不要手写容易过期的固定值。

## 5. 附带管理器 APK

- 汇总 Release 可以根据 `ksu_type` 自动附带对应管理器 APK：
  - `resukisu`：ReSukiSU arm64-v8a APK；
  - `sukisu`：SukiSU Ultra APK；
  - `ksunext`：KernelSU Next 非 spoofed APK；
  - `ksu`：原版 KernelSU APK；
  - `none`：不附带管理器 APK。
- 管理器 APK 应从对应仓库的最新 Release 通过 GitHub API 查询，并依据实际资产命名规则筛选，不能假设所有仓库使用同一个文件名。
- 下载的 APK 与七个 AnyKernel 刷机包一起传给 `gh release create`，并在 Release 说明中显示实际附带的 APK 文件名。
- 管理器下载链接仍应保留，附件是本次构建使用的便捷副本，不替代上游 Release 链接。
- `none` 模式必须可以正常发布七个内核包，不能因为没有 APK 就让汇总 Release 失败。

## 6. Ubuntu Runner 和 apt 镜像

- Ubuntu 24.04 Runner 的 apt 源不一定只来自 `/etc/apt/sources.list`。切换镜像时同时检查并处理：
  - `/etc/apt/sources.list`；
  - `/etc/apt/sources.list.d/ubuntu.sources`；
  - `/etc/apt/apt-mirrors.txt`。
- 不要假设 Azure 镜像一直可用；曾经成功的运行可能只是当时镜像正常，后续运行仍可能因镜像连接超时而失败。
- apt 更新和安装应保留合理的重试、超时和失败检查；日志中确认实际访问的域名已经切换到预期镜像。
- 遇到 `exit code 124` 时，优先检查网络或 apt 镜像超时，不要先判断为内核源码或编译参数错误。

## 7. 验证、快照和上传

- 修改工作流后至少执行：批量 Release PowerShell 校验脚本、汇总 Release Bash 语法检查、`git diff --check`。
- 校验脚本应检查七个版本、子工作流调用、权限、Release 标题、Release 说明、APK 附件处理和 `none` 分支行为。
- 每次修改后在外层 `versions/` 保存结果快照，并在 `versions/CHANGELOG.md` 记录修改原因、影响文件、验证结果、问题和解决办法。
- 上传 GitHub 前检查差异中没有 Token、密码、私钥或其他敏感信息；GitHub Actions 使用 Secrets 或运行环境变量，不把真实密钥写入 YAML。
- 未明确要求上传时，只修改本地文件并报告“尚未上传 GitHub”；明确要求上传后，再执行提交、推送并通过 `git ls-remote` 核对远程分支提交。
- 已有 Release 不会自动改变；修改工作流后必须重新运行批量工作流，才会生成带新标题、说明和 APK 附件的新 Release。

## 8. 文字和兼容性偏好

- 面向中文用户时保留中文界面文字、安装说明和用户指定的命名格式；动态变量只替换确实需要变化的部分。
- YAML、PowerShell 和 Markdown 默认保持 UTF-8；不要因为 PowerShell 5.1 的默认显示编码造成误判，读取中文文件时显式使用 UTF-8。
- 修改应尽量小范围、可恢复，保留原有单版本工作流，不要为了实现汇总功能重构无关构建逻辑。

## 9. 2026-10 上游 BakaSU 更新规则

本节是当前 6.1 项目的具体补充；上面第 2、5 节中的 `resukisu` 和旧 ReSukiSU APK 映射是历史记录，不再用于当前 BakaSU 工作流。

- 当前默认分支选项为 `bakasu`，其余保留 `sukisu`、`ksunext`、`ksu`、`none`。上游当前 `bakasu` 和 `sukisu` 都拉取 BakaSU；说明和 APK 必须按实际源码标识，不能按旧选项名称附带 SukiSU APK。
- 使用最新 `Baka-SU/BakaSU` main；批量准备阶段只解析一次最新 SHA，七个子工作流接收同一个 `ksu_ref`，安装后检查实际 checkout SHA，防止上游安装脚本静默退回默认分支。
- `workflow_call.outputs` 必须显式导出 `ksuver`、`ak3name`、`ksu_sha`，仅设置 `jobs.build.outputs` 不足以让父工作流读取。
- SUSFS 默认关闭，批量 KPM 默认开启。若选中 SUSFS，检查所选 BakaSU 源码的 `kernel/tools/susfs_compat.mk`：出现 `Please wait susfs update` 时明确失败，不能回退旧提交或删除上游检查。上游恢复后才允许联合构建。
- BakaSU 不开启 SUSFS 时保留 `CONFIG_KSU_TRACEPOINT_HOOK=y`。同步 6.6/6.12 经验时保留 6.1 的 `ssg_enable`，不能换成其他内核的参数。
- 管理器优先下载 BakaSU 官方 `build-manager.yml` 中同 SHA、main/push、成功运行的 `Manager-release` 工件，筛选唯一的 arm64-v8a release APK。查询、下载失败或工件不可用时注明“未附带”，保留官方下载链接；不混入旧 ReSukiSU 或其他来源/签名的 APK。
- 七个 AnyKernel 工件名称包含各自的完整版本号，仍须全部成功且七个 ZIP 到齐才创建一个汇总 Release；保留逐版本真实平台/源码说明、安装方法及风险提示。
- 上游补丁容错 `patch -p1 -F 3` 同时检查七个 Actions 工作流与七个本地脚本；不覆盖已有 apt 修复、6.1.128 工作目录修复和单版本发布逻辑。
- 本地验证（先安装 `tests/requirements.txt`）：`python tests/validate_workflows.py`、`python tests/test_bakasu_policy.py .`、`powershell -NoProfile -ExecutionPolicy Bypass -File tests/validate_batch_release.ps1`、`git diff --check`。Windows 使用 Git Bash，避免误用 WSL 的 `bash.exe`。
- 测试中的下载、checkout、发布操作使用隔离目录和替身；静态检查及行为测试通过不代表七个内核真实编译或手机刷写通过。未经用户明确要求，不上传、不提交、不启动 Actions。

## 10. 上游代码同步与 Git 历史合并

- 复制或移植上游代码不等于合并上游提交历史；需要消除 GitHub 的 behind 提示时，先 fetch 和审阅上游差异，再正式 merge 保留双方历史。不能用覆盖定制分支、重写历史或忽略整个上游的合并策略代替逐项整合。
- 对上游与本地修改重叠的冲突，逐段核对已移植的上游改动，保留 workflow_call 接口、inputs.xxx、批量同 SHA、SUSFS 检查、官方管理器、apt 修复和版本说明；合并后检查冲突标记、实际文件差异与必要测试。
- 合并是否成功要用上游 SHA 的祖先检查及远程 compare 验证；推送后确认 behind=0。ahead 表示仍有本地定制提交，不需要归零。脚本内容未变时沿用已有结果快照，不重复创建相同脚本快照。
