# 七版本批量构建统一发布设计

## 目标

通过 `build-test.yml` 提供一个统一入口，使用同一组选项构建 6.1.57、6.1.75、6.1.115、6.1.118、6.1.128、6.1.134 和 6.1.141 七个版本。只有七个版本全部成功并上传产物后，才创建一个包含全部 ZIP 的 GitHub Release。

## 约束

- 保留每个 `fastbuild_6.1.*.yml` 的直接 `workflow_dispatch` 单版本构建和发布行为。
- 批量入口必须暴露现有 14 个构建选项，并把同一值传给七个版本。
- 批量调用时跳过各版本内部的 Release，避免创建七个独立 Release。
- 七个 ZIP 的文件名必须包含 `SUB_VERSION`，避免汇总时重名。
- 任意一个构建失败时，汇总发布任务不得执行。
- 不提交、不推送、不创建远程 Release；本地只验证工作流结构。

## 方案

为七个现有工作流增加 `workflow_call` 输入，并将输入引用统一为兼容 `workflow_dispatch` 与 `workflow_call` 的 `inputs.*`。调用者通过七个显式 reusable-workflow job 并行构建，构建工作流在被调用时只上传 ZIP。`build-test.yml` 的汇总 job 使用 `actions/download-artifact` 下载全部七个 ZIP，检查数量后调用 `gh release create` 创建一个带时间标签的 Release。

## 验收

- 七个工作流都声明 `workflow_call`，且输入集合一致。
- 七个 ZIP 命名包含各自的 `SUB_VERSION`。
- 单版本调用仍保留内部发布 job；批量调用时内部发布 job 被跳过。
- 批量工作流包含全部 14 个输入、七个构建 job、统一 `needs` 和七个 ZIP 数量检查。
- 静态检查无明显 YAML 结构错误、无残留 `github.event.inputs.*` 引用。
