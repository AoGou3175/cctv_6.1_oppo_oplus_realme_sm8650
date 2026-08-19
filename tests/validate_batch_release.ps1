$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$workflowRoot = Join-Path $root '.github\workflows'
$batchPath = Join-Path $workflowRoot 'build-test.yml'
$batch = Get-Content -Raw -Encoding UTF8 $batchPath

$expectedInputs = @(
    'ksu_type',
    'susfs_enable',
    'kpm_enable',
    'lz4_enable',
    'lz4kd_enable',
    'bbr_enable',
    'droidspaces_enable',
    'better_net',
    'ssg_enable',
    'rekernel_enable',
    'baseband_guard',
    'ccache_update',
    'ccache_debug',
    'kernel_suffix'
)
$versions = @('57', '75', '115', '118', '128', '134', '141')
$failures = [System.Collections.Generic.List[string]]::new()

if (-not (Test-Path -LiteralPath $batchPath)) {
    $failures.Add('缺少批量入口 .github/workflows/build-test.yml')
}

foreach ($input in $expectedInputs) {
    if ($batch -notmatch "(?m)^\s{6}$([regex]::Escape($input)):\s*$") {
        $failures.Add("批量入口缺少输入: $input")
    }
    if ($batch -notmatch "inputs\.$([regex]::Escape($input))" -and $input -ne 'kernel_suffix') {
        $failures.Add("批量入口没有传递输入: $input")
    }
}

foreach ($version in $versions) {
    $workflowPath = Join-Path $workflowRoot "fastbuild_6.1.$version.yml"
    if (-not (Test-Path -LiteralPath $workflowPath)) {
        $failures.Add("缺少版本工作流: 6.1.$version")
        continue
    }

    $workflow = Get-Content -Raw -Encoding UTF8 $workflowPath
    if ($workflow -notmatch '(?m)^\s{2}workflow_call:\s*$') {
        $failures.Add("6.1.$version 没有 workflow_call")
    }
    foreach ($input in $expectedInputs) {
        $declarations = [regex]::Matches($workflow, "(?m)^\s{6}$([regex]::Escape($input)):\s*$").Count
        if ($declarations -lt 2) {
            $failures.Add("6.1.$version 的 workflow_call 缺少输入: $input")
        }
    }
    if ($workflow.Contains('github.event.inputs.')) {
        $failures.Add("6.1.$version 仍使用 github.event.inputs")
    }
    if (-not $workflow.Contains('${{ env.SUB_VERSION }}')) {
        $failures.Add("6.1.$version 的 ZIP 名称没有 SUB_VERSION")
    }
    if ($workflow -notmatch '(?ms)^\s{2}release:\s*\r?\n\s+if:\s*\$\{\{ github\.event_name == ''workflow_dispatch'' \}\}') {
        $failures.Add("6.1.$version 没有保留单独运行发布、批量调用跳过的条件")
    }
}

foreach ($version in $versions) {
    if ($batch -notmatch "(?m)^\s{2}build_${version}:\s*$") {
        $failures.Add("批量入口缺少 6.1.$version 构建 job")
    }
}

$releaseSection = $batch.Substring($batch.IndexOf("  release:"))
foreach ($version in $versions) {
    if ($releaseSection -notmatch "(?m)^\s{6}-\s+build_${version}\s*$") {
        $failures.Add("统一 release 没有等待 6.1.$version")
    }
}
if ($batch -notmatch '(?m)^\s{2}release:\s*$') {
    $failures.Add('批量入口缺少统一 release job')
}
if ($batch -notmatch 'AnyKernel3_\*\.zip') {
    $failures.Add('统一 release 没有下载 AnyKernel3 ZIP')
}
if ($batch -notmatch '\$\{#zips\[@\]\}.*-ne\s*7') {
    $failures.Add('统一 release 没有检查七个 ZIP 是否全部存在')
}
if ($batch -notmatch 'gh release create') {
    $failures.Add('统一 release 没有创建 GitHub Release')
}

if ($failures.Count -gt 0) {
    $failures | ForEach-Object { "FAIL: $_" }
    exit 1
}

Write-Output 'validate_batch_release: PASS'
