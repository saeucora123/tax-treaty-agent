# Stage 1 Hard Commitments Map

Date: 2026-03-12
Source report: `docs/superpowers/research/stage-1-evidence/2026-03-12-stage-1-initial-report.json`

## `HC-1`

系统不会在运行时凭模型记忆生成协定税率；输出税率必须来自结构化 treaty 数据。

- validating case count: `44`
- validating cases: `happy-div-cn-nl-001`, `happy-div-cn-nl-002`, `happy-div-cn-nl-003`, `happy-int-cn-nl-001`, `happy-int-cn-nl-002`, `happy-int-cn-nl-003`, `happy-roy-cn-nl-001`, `happy-roy-cn-nl-002`, `happy-roy-cn-nl-003`, `happy-div-nl-cn-001`, `happy-div-nl-cn-002`, `happy-div-nl-cn-003`, `happy-int-nl-cn-001`, `happy-int-nl-cn-002`, `happy-int-nl-cn-003`, `happy-roy-nl-cn-001`, `happy-roy-nl-cn-002`, `happy-roy-nl-cn-003`, `boundary-roy-001`, `boundary-roy-002`, `boundary-roy-003`, `boundary-roy-004`, `boundary-roy-005`, `boundary-roy-006`, `boundary-roy-007`, `boundary-roy-008`, `boundary-roy-009`, `boundary-roy-010`, `boundary-roy-011`, `boundary-roy-012`, `adversarial-001`, `adversarial-002`, `adversarial-003`, `adversarial-004`, `adversarial-005`, `adversarial-006`, `multi-branch-001`, `multi-branch-002`, `multi-branch-003`, `multi-branch-004`, `multi-branch-005`, `multi-branch-006`, `multi-branch-007`, `multi-branch-008`

## `HC-2`

系统不会对当前不在支持范围内的国家对返回包含条款编号或税率的实质性预审结果。

- validating case count: `8`
- validating cases: `out-country-001`, `out-country-002`, `out-country-003`, `out-country-004`, `out-country-005`, `out-country-006`, `adversarial-007`, `adversarial-008`

## `HC-3`

当同一条款存在多个可信税率分支且系统无法自动区分时，系统返回全部候选分支，而非选择其一。

- validating case count: `8`
- validating cases: `multi-branch-001`, `multi-branch-002`, `multi-branch-003`, `multi-branch-004`, `multi-branch-005`, `multi-branch-006`, `multi-branch-007`, `multi-branch-008`

## `HC-4`

系统输出中包含税率时，必须同时附带至少一个 source_reference 和至少一个适用条件说明。

- validating case count: `44`
- validating cases: `happy-div-cn-nl-001`, `happy-div-cn-nl-002`, `happy-div-cn-nl-003`, `happy-int-cn-nl-001`, `happy-int-cn-nl-002`, `happy-int-cn-nl-003`, `happy-roy-cn-nl-001`, `happy-roy-cn-nl-002`, `happy-roy-cn-nl-003`, `happy-div-nl-cn-001`, `happy-div-nl-cn-002`, `happy-div-nl-cn-003`, `happy-int-nl-cn-001`, `happy-int-nl-cn-002`, `happy-int-nl-cn-003`, `happy-roy-nl-cn-001`, `happy-roy-nl-cn-002`, `happy-roy-nl-cn-003`, `boundary-roy-001`, `boundary-roy-002`, `boundary-roy-003`, `boundary-roy-004`, `boundary-roy-005`, `boundary-roy-006`, `boundary-roy-007`, `boundary-roy-008`, `boundary-roy-009`, `boundary-roy-010`, `boundary-roy-011`, `boundary-roy-012`, `adversarial-001`, `adversarial-002`, `adversarial-003`, `adversarial-004`, `adversarial-005`, `adversarial-006`, `multi-branch-001`, `multi-branch-002`, `multi-branch-003`, `multi-branch-004`, `multi-branch-005`, `multi-branch-006`, `multi-branch-007`, `multi-branch-008`
