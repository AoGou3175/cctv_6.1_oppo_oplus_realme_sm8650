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
- GitHub 备份状态：本次修改和快照已提交并推送到公开仓库 `AoGou3175/cctv_6.1_oppo_oplus_realme_sm8650` 的 `main`，提交为 `fb4b91f`。

## 2026-08-19 23:23:00

- 修改内容：在汇总 Release 中增加七版本机型、平台、Android 版本和实际源码分支对应表，分别列出 SM8650/一加12、MT6989/Ace5-Race、MT6897/一加 Pad 的来源。
- 修改原因：七个构建使用的源码和目标机型并不相同，原说明统一写成一个 SM8650 机型会造成误解。
- 影响文件：`.github/workflows/build-test_6.1_kpm.yml`、`tests/validate_batch_release.ps1`。
- 快照文件：`build-test_6.1_kpm-20260819-232300-per-version-mapping.yml`、`validate_batch_release-20260819-232300-per-version-mapping.ps1`。
- 验证：验证脚本输出 `validate_batch_release: PASS`；七个实际源码分支名称和逐版本映射表检查通过；`git diff --check` 通过。
- 问题和解决办法：原汇总说明只有一条固定机型描述，已改为逐版本 Markdown 表格并附源码分支链接。
- `AGENTS.md`：未更新，未发现需要新增的长期项目规则。
- GitHub 备份状态：本次修改和快照已提交并推送到公开仓库 `AoGou3175/cctv_6.1_oppo_oplus_realme_sm8650` 的 `main`，提交为 `64b13b3`。

## 2026-08-19 23:27:22

- 修改内容：将七版本对应表改为详细句式，例如“欧加真骁龙8Gen3通用 6.1.75 内核（基于一加12 6.1.75 版官方OKI源码）”，并保留每个版本的源码分支链接。
- 修改原因：仅显示平台和机型简称不够直观，需要在汇总 Release 中直接说明每个内核版本与官方 OKI 源码的对应关系。
- 影响文件：`.github/workflows/build-test_6.1_kpm.yml`、`tests/validate_batch_release.ps1`。
- 快照文件：`build-test_6.1_kpm-20260819-232722-detailed-mapping.yml`、`validate_batch_release-20260819-232722-detailed-mapping.ps1`。
- 验证：验证脚本输出 `validate_batch_release: PASS`；七个版本的详细说明和源码分支检查通过；`git diff --check` 通过。
- 问题和解决办法：6.1.115/134 使用天玑特供 Ace5/Race 源码，6.1.128 使用天玑特供一加 Pad 源码，已分别按真实工作流来源填写。
- `AGENTS.md`：未更新，未发现需要新增的长期项目规则。
- GitHub 备份状态：本次修改和快照已提交并推送到公开仓库 `AoGou3175/cctv_6.1_oppo_oplus_realme_sm8650` 的 `main`，提交为 `2c2b497`。

## 2026-08-20 00:12:48

- 修改内容：七个构建工作流的 apt 镜像切换逻辑同时处理 `/etc/apt/sources.list`、`/etc/apt/sources.list.d/ubuntu.sources` 和 Ubuntu 24.04 Runner 实际使用的 `/etc/apt/apt-mirrors.txt`。
- 修改原因：之前成功运行时 Azure apt 镜像可访问；本次运行中该镜像连接超时，之前的修复没有覆盖 `apt-mirrors.txt`，导致仍然访问 Azure 并在 180 秒后退出 124。
- 影响文件：七个 `.github/workflows/fastbuild_6.1.*.yml`、`tests/validate_batch_release.ps1`。
- 快照文件：七个 `fastbuild_6.1.*-20260820-001248-apt-mirrorlist-fix.yml`、`validate_batch_release-20260820-001248-apt-mirrorlist-fix.ps1`。
- 验证：验证脚本输出 `validate_batch_release: PASS`；确认七个工作流都处理 `apt-mirrors.txt`；`git diff --check` 通过。
- 问题和解决办法：旧运行使用健康的 Azure 镜像所以成功；新运行的 Runner 仍是 Ubuntu 24.04，但 Azure 镜像不可达，现改用 `archive.ubuntu.com` 并保留重试和超时保护。
- `AGENTS.md`：未更新，未发现需要新增的长期项目规则。
- GitHub 备份状态：本次修改和快照已提交并推送到公开仓库 `AoGou3175/cctv_6.1_oppo_oplus_realme_sm8650` 的 `main`，提交为 `85f6da4`。

## 2026-08-20 00:47:17

- 修改内容：汇总 Release 根据 `ksu_type` 自动从对应管理器仓库下载并附带一个管理器 APK；`resukisu` 附带 ReSukiSU arm64-v8a 版本，`sukisu`、`ksunext`、`ksu` 分别附带对应分支的最新 Release APK，`none` 不附带 APK。Release 资产同时支持七个 AnyKernel 刷机包和管理器 APK。
- 修改原因：用户希望汇总 Release 可以直接附带本次构建对应的构建管理器 APK，下载后无需再单独查找管理器。
- 标题和说明：Release 标题改为“欧加真 ${KSU_TYPENAME} 6.1.X通用内核 | 构建信息”，说明中的机型改为“欧加真6.1.X内核”，并显示实际附带的 APK 文件名。
- 影响文件：`.github/workflows/build-test_6.1_kpm.yml`、`tests/validate_batch_release.ps1`。
- 快照文件：`build-test_6.1_kpm-20260820-004717-manager-apk-title.yml`、`validate_batch_release-20260820-004717-manager-apk-title.ps1`。
- 验证：`validate_batch_release: PASS`；汇总 Release Bash 语法检查通过；`git diff --check` 通过。
- 问题和解决办法：管理器仓库的 Release 资产名称不统一，已按各分支的 APK 命名规则筛选，并排除 KernelSU Next 的 spoofed APK。
- `AGENTS.md`：未更新，未发现需要新增的长期项目规则。
- GitHub 备份状态：本次修改和快照已提交并推送到公开仓库 `AoGou3175/cctv_6.1_oppo_oplus_realme_sm8650` 的 `main`，工作流修改提交为 `ffa3fc7`；本条状态修正随后单独提交。

## 2026-08-20 01:15:38

- 修改内容：新增根目录 `AGENTS.md`，整理可迁移到其他项目的 GitHub Actions 内核批量构建规则，包括七版本汇总、构建开关、Reusable Workflow 权限、Release 标题和说明、管理器 APK 附件、apt 镜像、验证、快照和上传注意事项。
- 修改原因：方便后续其他项目复用本次构建和发布过程中确认过的注意事项与用户偏好。
- 影响文件：`AGENTS.md`、`versions/CHANGELOG.md`。
- 快照文件：`AGENTS-20260820-011538-github-actions-kernel-build-guidelines.md`。
- 验证：确认 `AGENTS.md` 已包含本次项目的批量构建、Release 和上传经验；`git diff --check` 通过（仅有 Git 的 LF→CRLF 提示）。
- 问题和解决办法：未发现新的坑点；规则按可迁移原则整理，未复制与本项目无关的具体实现细节。
- `AGENTS.md`：已新增并完成本次长期经验整理。
- GitHub 备份状态：本次修改和快照尚未上传 GitHub。

## 2026-10-11 20:56:13

- 修改内容：参考 CCTV6.6 和 CCTV6.12 的已验证处理方式，将 CCTV6.1 的七版本 Actions、本地脚本及旧发布测试入口切换为 BakaSU；同步上游补丁命令 `patch -p1 -F 3`。原 6.1.128 工作目录修复已存在，保持不变。
- 修改原因：6.1 上游已将 ReSukiSU 更新为 BakaSU；最新源码暂停 SUSFS 联合构建，旧 ReSukiSU CI APK 不应与新内核混用。直接套用其他内核参数会丢失 6.1 的 SSG 选项。
- 批量方案：默认 BakaSU、SUSFS 关闭、KPM 开启；prepare 解析本次最新 main SHA，七个子工作流接收同一 SHA 并检查安装脚本的实际 checkout。导出 workflow_call 的 ksuver、ak3name、ksu_sha，保留七版本全部成功后发布一个 Release。
- 管理器：按同 SHA、main/push、成功运行查询官方 Build Manager 工件，筛选 arm64-v8a release APK。查询/下载失败或没有匹配 APK 时注明未附带并保留官方链接，不退回旧 ReSukiSU APK；none 模式正常发布七个内核包。
- 保留内容：七版本实际源码、平台和机型说明，安装及风险提示，SSG 和其他原构建选项，apt 镜像修复，单版本发布及 batch_mode，Numbersf、CCTV6.6、CCTV6.12 均未修改。
- 影响文件：9 个 YAML 工作流、7 个本地 Shell 脚本、原 PowerShell 校验、新增两个 Python 校验和 requirements.txt、项目 AGENTS.md、.gitattributes。本条仅追加 CHANGELOG，保留本次操作前已有的未提交规则和记录。
- 问题和解决办法：旧工作流未显式映射 workflow_call.outputs，父工作流无法可靠读取版本号；现补齐输出。BakaSU setup.sh 可能在指定 SHA checkout 失败后继续默认分支；现核对实际 SHA 后失败退出。新增换行检查发现七个本地脚本原为 CRLF，已机械转换为 UTF-8/LF，不改变脚本逻辑；仓库 core.autocrlf=true 且无 .gitattributes，新增 *.sh text eol=lf 防止下次检出又被转回 CRLF（不修改全局 Git 配置）。SUSFS 根据实际源码暂停标记判断，不删除检查、不固定回退旧提交。
- 验证过程：先对旧逻辑运行检查确认失败，再修改并重跑；首次新增 LF 检查失败后，定位七个脚本全部为 CRLF并修正。
- 验证结果：actionlint v1.7.12 检查 9 个工作流通过（关闭 shellcheck/pyflakes 外部检查）；七版本调用参数、输出和 ZIP 命名检查通过；168 段 Bash 与 7 个本地脚本语法检查通过；14 项行为测试通过，涵盖上游暂停/恢复、分支别名、批量同 SHA/错误 SHA、官方 APK/旧 APK 拒绝/none 发布；PowerShell 校验 PASS；git diff --check 通过；Git 属性确认 Shell eol=lf；22 个结果快照均与当前文件 SHA-256 相同。
- 验证边界：下载、checkout、发布行为测试使用隔离目录和替身，未进行真实七版本内核编译、跨仓库工件下载、远程 Release 发布或手机刷写，不据此声称真实构建成功。
- AGENTS.md：追加当前 BakaSU、动态 SUSFS、同提交官方管理器、子工作流输出、校验方式等长期规则，注明旧 ReSukiSU APK 规则属于历史记录，不覆盖原有规则。
- GitHub 备份状态：本次修改和快照尚未上传 GitHub；未执行 git add、commit、push，未启动 Actions，未修改仓库可见性。当前原远程为公开 fork，如后续要求上传，须按用户当前私人仓库规则先确认目标。
- 结果快照（完整路径，22 个，未覆盖已有快照）：
  - `D:/Codex/构建GKI/CCTV6.1/versions/build-test-20261011-205613-bakasu-upstream.yml`
  - `D:/Codex/构建GKI/CCTV6.1/versions/build-test_6.1_kpm-20261011-205613-bakasu-upstream.yml`
  - `D:/Codex/构建GKI/CCTV6.1/versions/fastbuild_6.1.57-20261011-205613-bakasu-upstream.yml`
  - `D:/Codex/构建GKI/CCTV6.1/versions/builder_6.1.57-20261011-205613-bakasu-upstream.sh`
  - `D:/Codex/构建GKI/CCTV6.1/versions/fastbuild_6.1.75-20261011-205613-bakasu-upstream.yml`
  - `D:/Codex/构建GKI/CCTV6.1/versions/builder_6.1.75-20261011-205613-bakasu-upstream.sh`
  - `D:/Codex/构建GKI/CCTV6.1/versions/fastbuild_6.1.115-20261011-205613-bakasu-upstream.yml`
  - `D:/Codex/构建GKI/CCTV6.1/versions/builder_6.1.115-20261011-205613-bakasu-upstream.sh`
  - `D:/Codex/构建GKI/CCTV6.1/versions/fastbuild_6.1.118-20261011-205613-bakasu-upstream.yml`
  - `D:/Codex/构建GKI/CCTV6.1/versions/builder_6.1.118-20261011-205613-bakasu-upstream.sh`
  - `D:/Codex/构建GKI/CCTV6.1/versions/fastbuild_6.1.128-20261011-205613-bakasu-upstream.yml`
  - `D:/Codex/构建GKI/CCTV6.1/versions/builder_6.1.128-20261011-205613-bakasu-upstream.sh`
  - `D:/Codex/构建GKI/CCTV6.1/versions/fastbuild_6.1.134-20261011-205613-bakasu-upstream.yml`
  - `D:/Codex/构建GKI/CCTV6.1/versions/builder_6.1.134-20261011-205613-bakasu-upstream.sh`
  - `D:/Codex/构建GKI/CCTV6.1/versions/fastbuild_6.1.141-20261011-205613-bakasu-upstream.yml`
  - `D:/Codex/构建GKI/CCTV6.1/versions/builder_6.1.141-20261011-205613-bakasu-upstream.sh`
  - `D:/Codex/构建GKI/CCTV6.1/versions/validate_batch_release-20261011-205613-bakasu-upstream.ps1`
  - `D:/Codex/构建GKI/CCTV6.1/versions/validate_workflows-20261011-205613-bakasu-upstream.py`
  - `D:/Codex/构建GKI/CCTV6.1/versions/test_bakasu_policy-20261011-205613-bakasu-upstream.py`
  - `D:/Codex/构建GKI/CCTV6.1/versions/requirements-20261011-205613-bakasu-upstream.txt`
  - `D:/Codex/构建GKI/CCTV6.1/versions/AGENTS-20261011-205613-bakasu-upstream.md`
  - `D:/Codex/构建GKI/CCTV6.1/versions/gitattributes-20261011-205613-bakasu-upstream.txt`

## 2026-10-12 本地 Git 提交

- 用户要求：提交上一轮已验证的 CCTV6.1 BakaSU 更新；KPM 仅询问含义，不修改开关或实现。
- 提交范围：上一轮工作流、本地构建脚本、校验脚本、AGENTS.md、.gitattributes、CHANGELOG 和结果快照，同时纳入此前尚未提交的 AGENTS 初始快照；未修改其他项目。
- 提交前验证：actionlint 检查 9 个工作流通过；七版本参数/输出/ZIP 名称检查、168 段 Bash 和 7 个本地脚本语法检查通过；14 项行为测试通过；PowerShell 校验 PASS；git diff --check 通过；当前文本文件、快照及 Git 文本历史的常见敏感信息模式检查未发现匹配。
- 暂存检查说明：新增完整快照复制了源文件原有的尾随空格及空白结尾，完整 git diff --cached --check 报出 238 项格式提示，全部位于 versions/ 快照。保持历史快照原样，不为消除提示改写既有脚本；实际代码、规则、校验文件和本次 CHANGELOG 的暂存差异检查通过，22 个快照与源文件 SHA-256 一致。
- KPM 核对：当前开关使用 KPatch-Next 修补编译后的 Image，并打包 cctv18/KPatch-Next 的 kpn.zip；上游 AnyKernel3 在存在 /data/adb/ksud 时安装该模块，否则跳过。此说明不改变当前构建默认值，不代表手机安装已验证。
- 快照与规则：沿用上一轮 22 个结果快照，不重复创建；本次仅追加提交记录，AGENTS.md 未再次修改，未发现需要新增的长期规则。
- GitHub 备份状态：按本次“提交”要求只进行 main 分支的本地 Git 提交，不执行 push，不改变远程仓库或可见性，不启动 Actions。本次修改和快照尚未上传 GitHub。
