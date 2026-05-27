#!/usr/bin/env node
/**
 * Post-Generate Hook
 * Runs after Kimi generates/modifies files.
 * Scans ONLY changed files for fast feedback.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const GOV_DIR = path.dirname(path.dirname(__filename));
const ENGINE_DIR = path.join(GOV_DIR, 'engine');

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i += 2) {
    const key = argv[i].replace(/^--/, '');
    args[key] = argv[i + 1] || '';
  }
  return args;
}

function getChangedFiles(diffArg) {
  if (diffArg) {
    return diffArg.split(',').map(f => f.trim()).filter(Boolean);
  }

  // Try git diff
  try {
    const out = execSync('git diff --name-only HEAD', { encoding: 'utf8', cwd: process.cwd() });
    return out.split('\n').map(f => f.trim()).filter(Boolean);
  } catch (e) {
    return [];
  }
}

function scanChangedFiles(files, config, gates) {
  const { applyPattern, lineNumber } = require(path.join(ENGINE_DIR, 'scanner.js'));
  const findings = [];
  const metrics = {
    files_scanned: 0,
    lines_scanned: 0,
    issues_by_severity: { critical: 0, high: 0, medium: 0, low: 0 },
    execution_time_ms: 0
  };

  const startTime = Date.now();
  const scanTypes = Object.keys(gates);

  for (const filePath of files) {
    const absPath = path.resolve(process.cwd(), filePath);
    if (!fs.existsSync(absPath)) continue;

    let content;
    try {
      content = fs.readFileSync(absPath, 'utf8');
    } catch (e) {
      continue;
    }

    metrics.files_scanned++;
    metrics.lines_scanned += content.split('\n').length;

    for (const gateName of scanTypes) {
      const gate = gates[gateName];
      if (!gate) continue;
      const patterns = gate.patterns || [];
      for (const pattern of patterns) {
        const results = applyPattern(filePath, content, gateName, gate, pattern);
        findings.push(...results);
        metrics.issues_by_severity[gate.severity || 'medium'] += results.length;
      }
    }
  }

  metrics.execution_time_ms = Date.now() - startTime;
  return { findings, metrics };
}

function main() {
  const args = parseArgs(process.argv);
  const diffFiles = getChangedFiles(args.diff || args.files);

  if (diffFiles.length === 0) {
    console.log('// Governance post-generate: No changed files detected');
    process.exit(0);
  }

  // Load config and gates
  const { loadConfig, loadGates } = require(path.join(ENGINE_DIR, 'scanner.js'));
  const { GateEnforcer } = require(path.join(ENGINE_DIR, 'gates.js'));
  const reporter = require(path.join(ENGINE_DIR, 'reporter.js'));

  const config = loadConfig();
  if (!config.enabled) {
    console.log('Governance disabled');
    process.exit(0);
  }

  const gates = loadGates();
  const { findings, metrics } = scanChangedFiles(diffFiles, config, gates);

  // Evaluate
  const enforcer = new GateEnforcer(config);
  const result = enforcer.evaluate(findings);

  // Output annotations
  console.log(reporter.githubAnnotations(findings));
  console.log('\n' + reporter.summary(findings, metrics));

  if (!result.passed) {
    console.log('\n::error::POST_GENERATE GATE BLOCKED');
    for (const b of result.blocked_by) {
      console.log(`::error::${b}`);
    }
    process.exit(2);
  }

  process.exit(0);
}

module.exports = { getChangedFiles, scanChangedFiles };

if (require.main === module) {
  main();
}
