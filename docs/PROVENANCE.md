# Source and evidence

The upstream is [ExpressLRS/Backpack](https://github.com/ExpressLRS/Backpack),
by ExpressLRS LLC and its contributors, under the existing GPL-3.0 license.
This fork starts from upstream commit
`437a4f4` (full source history is preserved). The relevant upstream code is
`src/hdzero.cpp`, `src/Vrx_main.cpp`, `src/rx5808.h`, `lib/MSP`, `lib/CRC`,
`targets/common.ini` and the firmware-options build/configuration scripts.

The original S3 adaptations by Louis Hitchcock are commits
`84acc8e` (target), `04bf850` (USB diagnostics) and
`a936cad1f80187c742b5d94e464e53aad6221c30` (one-wire repeats).
This publication adds equivalent C3 targets and the correct GPIO21 startup
message, documentation, unbound-image validation, packaging and focused CI.
No personal binding configuration or captured device logs are published.

The receiver integration and project-specific findings extend
[C5VRX](https://github.com/Twotoz/C5VRX) by Twotoz and the C5VRX contributors.
Its [official website](https://twotoz.github.io/C5VRX/) hosts the original
project and its Discord invite. This is an unofficial derivative; preserve
the GPL-3.0-only terms and notices of C5VRX-derived material.

Receiver references:

- [PR #189](https://github.com/Twotoz/C5VRX/pull/189), head
  `ff3135decac87f3d8c8df0a4b4313265c79cb2fd`: original V4 UART/MSPv2
  receiver, wire protocol, mapping and S3 bench results.
- [PR #271](https://github.com/Twotoz/C5VRX/pull/271), head
  `b28c42e59fd37ef2f69e2f713edb324c7aeabc65`: V5 control-task port.
- C3 bench 2026-10-25: locally bound DEBUG build on a C3 SuperMini,
  GPIO21 -> 1 kOhm -> XIAO C5 D10 plus GND. The ELRS radio sent R3 and R5.
  V5 logged `SET_CHANNEL_INDEX 36 -> R5 5806 MHz: ESP_OK`; receive counters
  increased through 114 frames with no CRC/UART/rejected errors. This
  establishes channel control, not video quality/range.
- S3 bench 2026-10-07: a locally bound S3 build controlled V4 R3/R5,
  recorded in #189. The new unbound S3 release has not been board-tested.
- Generic public images are fresh builds with no binding UID. Runtime
  binding of these generic images still needs a board check; the earlier
  bench images had binding configured locally.
