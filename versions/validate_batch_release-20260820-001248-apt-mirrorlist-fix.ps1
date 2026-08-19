$ErrorActionPreference = 'Stop'

$root = Split-Path -Parent $PSScriptRoot
$workflowRoot = Join-Path $root '.github\workflows'
$batchPath = Join-Path $workflowRoot 'build-test_6.1_kpm.yml'
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
    if ($workflow -notmatch '(?ms)^\s{2}release:\s*\r?\n\s+if:\s*\$\{\{ !inputs\.batch_mode \}\}') {
        $failures.Add("6.1.$version 没有保留单独运行发布、批量调用跳过的条件")
    }
    if ($workflow -notmatch '(?m)^\s{6}batch_mode:\s*$') {
        $failures.Add("6.1.$version workflow_call is missing batch_mode")
    }
    if ($workflow -notmatch 'Acquire::Retries=3' -or $workflow -notmatch 'archive\.ubuntu\.com' -or $workflow -notmatch 'apt-mirrors\.txt') {
        $failures.Add("6.1.$version is missing apt mirror retry settings")
    }
    if ($version -eq '128' -and $workflow -notmatch '(?ms)name: .*KernelSU.*?cd kernel_workspace\s+if') {
        $failures.Add('6.1.128 does not enter kernel_workspace before KernelSU setup')
    }
}

foreach ($version in $versions) {
    if ($batch -notmatch "(?m)^\s{2}build_${version}:\s*$") {
        $failures.Add("批量入口缺少 6.1.$version 构建 job")
    }
}

if ([regex]::Matches($batch, '(?m)^\s{6}batch_mode:\s+true\s*$').Count -ne 7) {
    $failures.Add('batch workflow does not pass batch_mode: true to all 7 builds')
}

foreach ($requiredReleaseText in @(
    'ReSukiSU_CI',
    'SukiSU-Ultra',
    'KernelSU-Next',
    'HorizonKernelFlasher',
    'Installation Guide',
    'KernelFlasher'
)) {
    if ($batch -notmatch [regex]::Escape($requiredReleaseText)) {
        $failures.Add("batch Release notes is missing: $requiredReleaseText")
    }
}
if ($batch -notmatch 'needs\.build_57\.outputs\.ksuver') {
    $failures.Add('batch Release notes does not use the build output KSU version')
}
foreach ($sourceBranch in @(
    'sm8650_u_14.0.0_oneplus12',
    'sm8650_v_15.0.0_oneplus12',
    'mt6989_v_15.0.2_ace5_race',
    'sm8650_b_16.0.0_oneplus12',
    'mt6897_v_15.0.0_oneplus_pad',
    'mt6989_b_16.0.0_ace5_race',
    'sm8650_b_16.0.0_oneplus12_6.1.141'
)) {
    if ($batch -notmatch [regex]::Escape($sourceBranch)) {
        $failures.Add("batch Release notes is missing source branch: $sourceBranch")
    }
}
if ($batch -notmatch '(?m)^\s*\|\s*6\.1\.57\s*\|') {
    $failures.Add('batch Release notes is missing the per-version mapping table')
}
foreach ($version in $versions) {
    if ($batch -notmatch "(?m)^\s*\|\s*6\.1\.$version\s*\|.*6\.1\.$version.*\|") {
        $failures.Add("batch Release notes is missing a detailed description for 6.1.$version")
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
