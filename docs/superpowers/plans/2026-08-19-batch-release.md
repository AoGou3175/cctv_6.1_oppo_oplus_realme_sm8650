# 七版本批量构建统一发布 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a single workflow-dispatch entry that builds seven 6.1 kernel variants with one shared option set and publishes one release only after all seven succeed.

**Architecture:** The seven existing workflows become reusable workflows in addition to retaining direct manual dispatch. A direct dispatch keeps its existing per-version release job; a reusable call skips that job and uploads a uniquely named ZIP to the caller run. `build-test.yml` calls all seven workflows in parallel, downloads their artifacts, verifies exactly seven ZIPs, and creates one release.

**Tech Stack:** GitHub Actions YAML, reusable workflows, `actions/upload-artifact@v7`, `actions/download-artifact@v8`, GitHub CLI.

**Spec:** `docs/superpowers/specs/2026-08-19-batch-release-design.md`

## Global Constraints

- Preserve direct `workflow_dispatch` behavior for all seven existing fastbuild workflows.
- Keep the existing 14 build inputs and pass one shared value set to all seven calls.
- Include `SUB_VERSION` in every generated ZIP filename.
- Do not create a release unless all seven called workflows succeed.
- Do not commit or push changes during this task.

---

### Task 1: Add the static regression test

**Files:**
- Create: `tests/validate_batch_release.ps1`

**Interfaces:**
- Consumes: local `.github/workflows/*.yml` files.
- Produces: exit code 0 only when the batch workflow contract is present.

- [ ] **Step 1: Write the failing test**

  The test must assert that `build-test.yml` has the 14 expected dispatch inputs, seven version jobs, a release job that needs all seven, seven ZIP validation, and that every fastbuild file has `workflow_call`, `inputs.*` references, and `SUB_VERSION` in its ZIP name.

- [ ] **Step 2: Run the test to verify it fails**

  Run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tests\validate_batch_release.ps1`.

  Expected result: failure because the current `build-test.yml` is the old single-version dummy test and the fastbuild files do not yet declare `workflow_call`.

- [ ] **Step 3: Keep the test as the implementation gate**

  Do not weaken assertions to match the existing workflows; the test describes the approved batch-release behavior.

### Task 2: Make the seven builds reusable

**Files:**
- Modify: `.github/workflows/fastbuild_6.1.57.yml`
- Modify: `.github/workflows/fastbuild_6.1.75.yml`
- Modify: `.github/workflows/fastbuild_6.1.115.yml`
- Modify: `.github/workflows/fastbuild_6.1.118.yml`
- Modify: `.github/workflows/fastbuild_6.1.128.yml`
- Modify: `.github/workflows/fastbuild_6.1.134.yml`
- Modify: `.github/workflows/fastbuild_6.1.141.yml`

**Interfaces:**
- Consumes: the existing 14 manual inputs.
- Produces: reusable workflow inputs and uniquely named ZIP artifacts.

- [ ] **Step 1: Add `workflow_call` input declarations**

  Declare the same input names and compatible types as the existing manual inputs under `on.workflow_call.inputs`.

- [ ] **Step 2: Normalize input references**

  Replace `github.event.inputs.<name>` with `inputs.<name>` so both manual dispatch and reusable calls use the same context.

- [ ] **Step 3: Preserve direct publishing and skip it for reusable calls**

  Add `if: ${{ github.event_name == 'workflow_dispatch' }}` to the existing `release` job.

- [ ] **Step 4: Make ZIP names unique**

  Insert `${{ env.SUB_VERSION }}` into both `AK3_NAME` assignment branches.

### Task 3: Build the batch entry and unified release

**Files:**
- Modify: `.github/workflows/build-test.yml`

**Interfaces:**
- Consumes: the same 14 manual inputs.
- Produces: one release with seven versioned ZIP assets.

- [ ] **Step 1: Declare the shared inputs**

  Expose `ksu_type`, `susfs_enable`, `kpm_enable`, `lz4_enable`, `lz4kd_enable`, `bbr_enable`, `droidspaces_enable`, `better_net`, `ssg_enable`, `rekernel_enable`, `baseband_guard`, `ccache_update`, `ccache_debug`, and `kernel_suffix`.

- [ ] **Step 2: Call all seven reusable workflows**

  Add one explicit job per version, each passing all 14 values from `inputs.*` to the corresponding fastbuild workflow.

- [ ] **Step 3: Download and verify the seven artifacts**

  Make the release job depend on all seven build jobs, download `AnyKernel3_*.zip`, and fail unless exactly seven ZIP files exist.

- [ ] **Step 4: Create the single release**

  Generate a unique time-based tag, write notes containing all seven versions and the selected options, and upload all seven ZIPs with `gh release create`.

### Task 4: Verify the result

**Files:**
- Test: `tests/validate_batch_release.ps1`

- [ ] **Step 1: Run the regression test**

  Run `powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\tests\validate_batch_release.ps1` and require exit code 0.

- [ ] **Step 2: Validate YAML structure**

  Parse all eight workflow files with an available YAML parser or run targeted structural checks if no parser is installed.

- [ ] **Step 3: Inspect the final diff**

  Run `git diff --check`, `git status --short`, and inspect the changed workflow names, inputs, `needs`, artifact paths, and release condition.
