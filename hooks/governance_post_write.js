#!/usr/bin/env node
/**
 * Governance Post-Write Bridge
 * Called by Kimi CLI PostToolUse hook after WriteFile/StrReplaceFile.
 * Scans the written file against governance gates.
 */

const fs = require('fs');
const path = require('path');

const GOV_DIR = path.join(__dirname, '..', 'governance');
const ENGINE_DIR = path.join(GOV_DIR, 'engine');

let data;
try {
  data = JSON.parse(fs.readFileSync(0, 'utf8'));
} catch (e) {
  process.exit(0);
}

const event = data.hook_event_name || '';
const toolName = data.tool_name || '';
const toolInput = data.tool_input || {};

if (event !== 'PostToolUse' || !['WriteFile', 'StrReplaceFile'].includes(toolName)) {
  process.exit(0);
}

const filepath = toolInput.path || '';
if (!filepath) process.exit(0);

const filename = path.basename(filepath).toLowerCase();
const prodExts = ['.php', '.js', '.ts', '.jsx', '.tsx', '.py', '.go', '.sql', '.tpl'];
if (!prodExts.some(ext => filename.endsWith(ext))) {
  process.exit(0);
}

// Load scanner modules
const scanner = require(path.join(ENGINE_DIR, 'scanner.js'));
const { GateEnforcer } = require(path.join(ENGINE_DIR, 'gates.js'));

let content;
try {
  content = fs.readFileSync(filepath, 'utf8');
} catch (e) {
  process.exit(0);
}

const config = scanner.loadConfig();
if (!config.enabled) {
  process.exit(0);
}

const gates = scanner.loadGates();
const findings = [];

for (const gateName of Object.keys(gates)) {
  const gate = gates[gateName];
  if (!gate) continue;
  for (const pattern of (gate.patterns || [])) {
    findings.push(...scanner.applyPattern(filepath, content, gateName, gate, pattern));
  }
}

const enforcer = new GateEnforcer(config);
const result = enforcer.evaluate(findings);

if (!result.passed) {
  console.error('::error::GOVERNANCE GATE BLOCKED this write');
  for (const b of result.blocked_by) {
    console.error(`::error::${b}`);
  }
  process.exit(2);
}

if (findings.length > 0) {
  const reporter = require(path.join(ENGINE_DIR, 'reporter.js'));
  console.error(reporter.githubAnnotations(findings));
  console.error(reporter.summary(findings, { files_scanned: 1, lines_scanned: content.split('\n').length, issues_by_severity: { critical: 0, high: 0, medium: 0, low: 0 }, execution_time_ms: 0 }));
}

process.exit(0);
