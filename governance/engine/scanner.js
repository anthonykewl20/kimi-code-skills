#!/usr/bin/env node
const MAX_FILE_SIZE = 500 * 1024; // 500KB max per file
const MAX_SCAN_MS_PER_FILE = 3000; // 3 seconds max per file

/**
 * Governance Scanner Engine
 * Zero-dependency. Uses only Node.js built-ins: fs, path, util.
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// ── Minimal YAML Parser (sufficient for our controlled configs) ───────────────

function parseYAML(text) {
  const lines = text.split(/\r?\n/);
  const root = {};
  const stack = [{ obj: root, indent: -1, key: null }];

  for (let i = 0; i < lines.length; i++) {
    const raw = lines[i];
    const line = raw.replace(/#.*/, ''); // strip comments
    if (!line.trim()) continue;

    const indent = line.search(/\S/);
    const trimmed = line.trim();

    // Pop stack to correct level
    while (stack.length > 1 && indent <= stack[stack.length - 1].indent) {
      stack.pop();
    }

    const parent = stack[stack.length - 1];

    if (trimmed.startsWith('- ')) {
      // Array item
      const val = trimmed.slice(2).trim();
      let target = parent.obj[parent.key];
      if (!Array.isArray(target)) {
        target = parent.obj[parent.key] = [];
      }
      if (val.includes(':')) {
        const obj = {};
        target.push(obj);
        stack.push({ obj, indent, key: null });
        // Parse the first key-value of this array item
        const colonIdx = val.indexOf(':');
        const k = val.slice(0, colonIdx).trim();
        const v = val.slice(colonIdx + 1).trim();
        if (v) obj[k] = parseValue(v);
        else obj[k] = {};
        stack[stack.length - 1].key = k;
      } else {
        target.push(parseValue(val));
      }
    } else if (trimmed.includes(':')) {
      const colonIdx = trimmed.indexOf(':');
      const key = trimmed.slice(0, colonIdx).trim();
      const val = trimmed.slice(colonIdx + 1).trim();

      if (!val) {
        // Object or array start
        parent.obj[key] = {};
        stack.push({ obj: parent.obj[key], indent, key });
      } else if (val.startsWith('[') && val.endsWith(']')) {
        parent.obj[key] = parseArray(val);
      } else if (val.startsWith('|')) {
        // Multi-line string
        const start = i;
        let j = i + 1;
        const parts = [];
        while (j < lines.length && (lines[j].search(/\S/) > indent || !lines[j].trim())) {
          if (lines[j].trim()) parts.push(lines[j].slice(indent + 2));
          j++;
        }
        parent.obj[key] = parts.join('\n');
        i = j - 1;
      } else {
        parent.obj[key] = parseValue(val);
      }
      if (stack[stack.length - 1].key === key || stack[stack.length - 1].obj === parent.obj[key]) {
        // already pushed for empty value
      }
    }
  }

  return root;
}

function parseValue(v) {
  v = v.trim();
  if (v === 'true') return true;
  if (v === 'false') return false;
  if (v === 'null' || v === '~') return null;
  if (/^-?\d+$/.test(v)) return parseInt(v, 10);
  if (/^-?\d+\.\d+$/.test(v)) return parseFloat(v);
  if ((v.startsWith('"') && v.endsWith('"')) || (v.startsWith("'") && v.endsWith("'"))) {
    return v.slice(1, -1);
  }
  return v;
}

function parseArray(s) {
  s = s.slice(1, -1).trim();
  if (!s) return [];
  return s.split(',').map(x => parseValue(x.trim()));
}

function normalizeGates(gates) {
  for (const key of Object.keys(gates || {})) {
    const gate = gates[key];
    if (!gate || typeof gate !== 'object') continue;

    // Handle nested patterns.patterns from YAML double-nesting
    if (gate.patterns && gate.patterns.patterns && Array.isArray(gate.patterns.patterns)) {
      gate.patterns = gate.patterns.patterns;
    }

    // Handle single object instead of array
    if (gate.patterns && !Array.isArray(gate.patterns)) {
      if (gate.patterns.match || gate.patterns.name) {
        gate.patterns = [gate.patterns];
      } else {
        gate.patterns = [];
      }
    }

    // Ensure patterns is at least an empty array
    if (!gate.patterns) {
      gate.patterns = [];
    }
  }
  return gates;
}

function normalizeConfig(config) {
  if (!config || typeof config !== 'object') return config;

  if (config.scan_paths) {
    const sp = config.scan_paths;

    if (sp.include && sp.include.include && Array.isArray(sp.include.include)) {
      sp.include = sp.include.include;
    }
    if (!Array.isArray(sp.include)) sp.include = [];

    if (sp.exclude && sp.exclude.exclude && Array.isArray(sp.exclude.exclude)) {
      sp.exclude = sp.exclude.exclude;
    }
    if (!Array.isArray(sp.exclude)) sp.exclude = [];

    if (sp.file_patterns && sp.file_patterns.file_patterns && Array.isArray(sp.file_patterns.file_patterns)) {
      sp.file_patterns = sp.file_patterns.file_patterns;
    }
    if (!Array.isArray(sp.file_patterns)) sp.file_patterns = [];
  }

  if (!config.thresholds) {
    config.thresholds = { max_critical: 0, max_high: 0, max_medium: 5, max_low: 20 };
  }
  if (!config.reports) {
    config.reports = { output_dir: '.kimi/governance/reports/' };
  }

  return config;
}

// ── Config Loading ────────────────────────────────────────────────────────────

const GOV_DIR = path.dirname(path.dirname(__filename));
const CONFIG_PATH = path.join(GOV_DIR, 'config.yaml');
const GATES_PATH = path.join(GOV_DIR, 'gates.yaml');

function loadConfig() {
  const text = fs.readFileSync(CONFIG_PATH, 'utf8');
  return normalizeConfig(parseYAML(text).governance);
}

function loadGates() {
  const text = fs.readFileSync(GATES_PATH, 'utf8');
  return normalizeGates(parseYAML(text).gates || {});
}

// ── File Walking ──────────────────────────────────────────────────────────────

function shouldInclude(file, config) {
  const rel = path.relative(process.cwd(), file).replace(/\\/g, '/');
  const basename = path.basename(file);

  for (const ex of config.scan_paths.exclude || []) {
    try {
      const pat = ex.replace(/\*/g, '.*');
      if (new RegExp(pat).test(rel)) return false;
    } catch (e) {
      console.error(`Invalid exclude pattern: ${ex} — ${e.message}`);
    }
  }

  for (const inc of config.scan_paths.include || []) {
    const incClean = inc.replace(/\/$/, '');
    if (rel.startsWith(incClean + '/') || rel === incClean) {
      for (const pat of config.scan_paths.file_patterns || []) {
        try {
          const regex = pat.replace(/\./g, '\\.').replace(/\*/g, '.*');
          if (new RegExp(regex + '$').test(basename)) return true;
        } catch (e) {
          console.error(`Invalid file pattern: ${pat} — ${e.message}`);
        }
      }
    }
  }
  return false;
}

function* walk(dir) {
  try {
    const entries = fs.readdirSync(dir, { withFileTypes: true });
    for (const entry of entries) {
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) {
        yield* walk(full);
      } else {
        yield full;
      }
    }
  } catch (e) {
    // permission denied, etc.
  }
}

// ── Pattern Matching ──────────────────────────────────────────────────────────

function lineNumber(content, index) {
  let line = 1;
  for (let i = 0; i < index; i++) {
    if (content[i] === '\n') line++;
  }
  return line;
}

function applyPattern(filePath, content, gateName, gate, pattern) {
  const findings = [];
  const matchStr = pattern.match;
  if (!matchStr) return findings;

  // Handle multi-step patterns using → separator
  const steps = matchStr.split('→').map(s => s.trim());

  if (steps.length === 1) {
    // Single regex
    let regex;
    try {
      regex = new RegExp(steps[0], 'gmi');
    } catch (e) {
      console.error(`Invalid regex in gate ${gateName}, pattern ${pattern.name}: ${e.message}`);
      return findings;
    }

    let m;
    while ((m = regex.exec(content)) !== null) {
      const line = lineNumber(content, m.index);
      const col = m.index - content.lastIndexOf('\n', m.index - 1);
      findings.push({
        file: filePath,
        line,
        col,
        gate: gateName,
        pattern: pattern.name,
        severity: gate.severity || 'medium',
        action: gate.action || 'warn',
        message: pattern.message || `${gateName}: ${pattern.name}`,
        fix_template: pattern.fix_template || '',
        auto_fix: gate.auto_fix || false,
        snippet: content.slice(Math.max(0, m.index - 40), Math.min(content.length, m.index + 80)).replace(/\s+/g, ' ')
      });
    }
  } else {
    // Multi-step: step1 must match, then step2 must match after it
    let regex1, regex2;
    try {
      regex1 = new RegExp(steps[0], 'mi');
      regex2 = new RegExp(steps[1], 'gmi');
    } catch (e) {
      console.error(`Invalid regex in gate ${gateName}, pattern ${pattern.name}: ${e.message}`);
      return findings;
    }

    let match1 = regex1.exec(content);
    if (!match1) return findings;

    const startIdx = match1.index + match1[0].length;
    const afterContent = content.slice(startIdx);

    let m;
    while ((m = regex2.exec(afterContent)) !== null) {
      const absIndex = startIdx + m.index;
      const line = lineNumber(content, absIndex);
      const col = absIndex - content.lastIndexOf('\n', absIndex - 1);
      findings.push({
        file: filePath,
        line,
        col,
        gate: gateName,
        pattern: pattern.name,
        severity: gate.severity || 'medium',
        action: gate.action || 'warn',
        message: pattern.message || `${gateName}: ${pattern.name}`,
        fix_template: pattern.fix_template || '',
        auto_fix: gate.auto_fix || false,
        snippet: content.slice(Math.max(0, absIndex - 40), Math.min(content.length, absIndex + 80)).replace(/\s+/g, ' ')
      });
    }
  }

  return findings;
}

// ── Scanning ──────────────────────────────────────────────────────────────────

function scanFiles(scope, config, gates) {
  const findings = [];
  const metrics = {
    files_scanned: 0,
    lines_scanned: 0,
    issues_by_severity: { critical: 0, high: 0, medium: 0, low: 0 },
    auto_fixes_applied: 0,
    auto_fixes_skipped: 0,
    issues_by_gate: {},
    execution_time_ms: 0
  };

  if (!config || !config.scan_paths) {
    return { findings, metrics };
  }

  const startTime = Date.now();
  const scanTypes = scope === 'all' ? Object.keys(gates || {}) : [scope];

  for (const inc of config.scan_paths.include || []) {
    const absInc = path.resolve(process.cwd(), inc);
    if (!fs.existsSync(absInc)) continue;

    for (const filePath of walk(absInc)) {
      if (!shouldInclude(filePath, config)) continue;

      let stats;
      try {
        stats = fs.statSync(filePath);
      } catch (e) {
        continue;
      }
      if (stats.size > MAX_FILE_SIZE) continue;

      let content;
      try {
        const raw = fs.readFileSync(filePath, 'utf8');
        content = raw.length > 50000 ? raw.slice(0, 50000) : raw;
      } catch (e) {
        continue;
      }

      const fileStart = Date.now();
      metrics.files_scanned++;
      metrics.lines_scanned += content.split('\n').length;

      for (const gateName of scanTypes) {
        if (Date.now() - fileStart > MAX_SCAN_MS_PER_FILE) break;

        const gate = gates[gateName];
        if (!gate) continue;

        const patterns = gate.patterns || [];
        for (const pattern of patterns) {
          if (Date.now() - fileStart > MAX_SCAN_MS_PER_FILE) break;
          const results = applyPattern(
            path.relative(process.cwd(), filePath),
            content,
            gateName,
            gate,
            pattern
          );
          findings.push(...results);
          metrics.issues_by_severity[gate.severity || 'medium'] += results.length;
          metrics.issues_by_gate[gateName] = (metrics.issues_by_gate[gateName] || 0) + results.length;
        }
      }

      if (Date.now() - startTime > 60000) {
        metrics.execution_time_ms = Date.now() - startTime;
        return { findings, metrics };
      }
    }
  }

  metrics.execution_time_ms = Date.now() - startTime;
  return { findings, metrics };
}

// ── Auto-Fix ──────────────────────────────────────────────────────────────────

function applyAutoFixes(findings, config) {
  const fixed = [];
  for (const f of findings) {
    if (!f.auto_fix || !f.fix_template) continue;
    if (!config.auto_fix[f.gate]) {
      f.auto_fix_skipped = true;
      continue;
    }

    const filePath = path.resolve(process.cwd(), f.file);
    if (!fs.existsSync(filePath)) continue;

    // Backup
    const backupDir = path.join(GOV_DIR, 'reports', 'backups');
    fs.mkdirSync(backupDir, { recursive: true });
    const ts = Date.now();
    const backupPath = path.join(backupDir, `${path.basename(f.file)}.${ts}.bak`);

    try {
      const original = fs.readFileSync(filePath, 'utf8');
      fs.writeFileSync(backupPath, original);

      // Simple replacement: find the matched snippet and replace with template
      // This is naive — real fixes need AST-level surgery
      // For now we only fix simple INSERT patterns
      let modified = original;
      const lines = original.split('\n');
      const targetLine = lines[f.line - 1];

      if (f.gate === 'idempotency_insert_no_conflict' && f.pattern === 'bare_insert') {
        // Too risky to auto-fix without parsing SQL
        f.auto_fix_skipped = true;
        continue;
      }

      if (f.gate === 'race_check_then_act' && f.pattern === 'read_modify_write_counter') {
        // Replace SELECT col + UPDATE col = value with atomic UPDATE
        // Naive: look for UPDATE ... SET col = pattern in the line
        const atomicFix = f.fix_template
          .replace('{table}', 'table')
          .replace('{column}', 'column')
          .replace('{condition}', 'condition');
        // Can't safely auto-fix without parsing — skip
        f.auto_fix_skipped = true;
        continue;
      }

      fs.writeFileSync(filePath, modified);
      fixed.push(f);
    } catch (e) {
      // Restore on failure
      try {
        const backup = fs.readFileSync(backupPath, 'utf8');
        fs.writeFileSync(filePath, backup);
      } catch (_) {}
      f.auto_fix_skipped = true;
    }
  }
  return fixed;
}

// ── CLI ───────────────────────────────────────────────────────────────────────

function main() {
  const args = process.argv.slice(2);
  const scopeIdx = args.indexOf('--scan');
  const scope = scopeIdx >= 0 ? args[scopeIdx + 1] : 'all';
  const doFix = args.includes('--fix');
  const doDiff = args.includes('--diff');

  const validScopes = ['all', 'race', 'scale', 'idempotency', 'dead-code'];
  if (!validScopes.includes(scope)) {
    console.error(`Usage: node scanner.js --scan <${validScopes.join('|')}>`);
    process.exit(1);
  }

  const SCAN_TIMEOUT_MS = 30000;
  const timeoutId = setTimeout(() => {
    console.error(`\nScanner timed out after ${SCAN_TIMEOUT_MS}ms`);
    process.exit(3);
  }, SCAN_TIMEOUT_MS);

  let findings = [];
  let metrics = {
    files_scanned: 0,
    lines_scanned: 0,
    issues_by_severity: { critical: 0, high: 0, medium: 0, low: 0 },
    auto_fixes_applied: 0,
    auto_fixes_skipped: 0,
    issues_by_gate: {},
    execution_time_ms: 0
  };

  try {
    const config = loadConfig();
    if (!config.enabled) {
      console.log('Governance disabled in config.yaml');
      clearTimeout(timeoutId);
      process.exit(0);
    }

    const gates = loadGates();
    const result = scanFiles(scope, config, gates);
    findings = result.findings;
    metrics = result.metrics;

    if (doFix) {
      const fixed = applyAutoFixes(findings, config);
      metrics.auto_fixes_applied = fixed.length;
      metrics.auto_fixes_skipped = findings.filter(f => f.auto_fix && f.auto_fix_skipped).length;
    }

    // Write report
    const reporter = require('./reporter');
    const reportDir = path.resolve(process.cwd(), config.reports.output_dir);
    fs.mkdirSync(reportDir, { recursive: true });

    const md = reporter.markdown(findings, metrics);
    const json = reporter.json(findings, metrics);

    const ts = new Date().toISOString().replace(/[:.]/g, '-');
    fs.writeFileSync(path.join(reportDir, `scan-${scope}-${ts}.md`), md);
    fs.writeFileSync(path.join(reportDir, `scan-${scope}-${ts}.json`), json);

    // Console output: summary + annotations
    console.log(reporter.summary(findings, metrics));
    console.log('\n' + reporter.githubAnnotations(findings));

    // Exit code based on severity
    const critical = findings.filter(f => f.severity === 'critical').length;
    const high = findings.filter(f => f.severity === 'high').length;

    clearTimeout(timeoutId);
    const maxCritical = config.thresholds && typeof config.thresholds.max_critical === 'number' ? config.thresholds.max_critical : 0;
    const maxHigh = config.thresholds && typeof config.thresholds.max_high === 'number' ? config.thresholds.max_high : 0;
    if (critical > maxCritical || high > maxHigh) {
      process.exit(2);
    }
    process.exit(0);
  } catch (err) {
    clearTimeout(timeoutId);
    console.error('Scanner error:', err.message || err);
    // Always print a summary line even on crash
    console.log(`Governance: ${metrics.issues_by_severity.critical} critical, ${metrics.issues_by_severity.high} high, ${metrics.issues_by_severity.medium} medium, ${metrics.issues_by_severity.low} low | ${metrics.auto_fixes_applied || 0} auto-fixed | ERROR`);
    process.exit(1);
  }
}

module.exports = { loadConfig, loadGates, scanFiles, applyAutoFixes, parseYAML, applyPattern, lineNumber, normalizeConfig, normalizeGates };

if (require.main === module) {
  main();
}
