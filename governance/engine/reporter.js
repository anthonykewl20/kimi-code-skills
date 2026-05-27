#!/usr/bin/env node
/**
 * Report Generation
 * Formats findings into markdown, JSON, and GitHub annotations.
 */

function severityIcon(sev) {
  const map = { critical: '🔴', high: '🟠', medium: '🟡', low: '🟢' };
  return map[sev] || '⚪';
}

function severityGHLevel(sev) {
  if (sev === 'critical' || sev === 'high') return 'error';
  if (sev === 'medium') return 'warning';
  return 'notice';
}

function markdown(findings, metrics) {
  const lines = [];
  lines.push('# Governance Scan Report');
  lines.push(`**Generated:** ${new Date().toISOString()}`);
  lines.push(`**Scope:** ${process.argv.includes('--scan') ? process.argv[process.argv.indexOf('--scan') + 1] : 'all'}`);
  lines.push('');
  lines.push('## Metrics');
  lines.push(`| Metric | Value |`);
  lines.push(`|--------|-------|`);
  lines.push(`| Files scanned | ${metrics.files_scanned} |`);
  lines.push(`| Lines scanned | ${metrics.lines_scanned} |`);
  lines.push(`| Critical | ${metrics.issues_by_severity.critical} |`);
  lines.push(`| High | ${metrics.issues_by_severity.high} |`);
  lines.push(`| Medium | ${metrics.issues_by_severity.medium} |`);
  lines.push(`| Low | ${metrics.issues_by_severity.low} |`);
  lines.push(`| Execution time | ${metrics.execution_time_ms}ms |`);
  if (metrics.auto_fixes_applied !== undefined) {
    lines.push(`| Auto-fixes applied | ${metrics.auto_fixes_applied} |`);
    lines.push(`| Auto-fixes skipped | ${metrics.auto_fixes_skipped} |`);
  }
  lines.push('');

  if (findings.length === 0) {
    lines.push('## ✅ No issues found');
    return lines.join('\n');
  }

  lines.push('## Findings');
  lines.push('');

  const byGate = {};
  for (const f of findings) {
    (byGate[f.gate] = byGate[f.gate] || []).push(f);
  }

  for (const gateName of Object.keys(byGate).sort()) {
    lines.push(`### ${gateName}`);
    lines.push('');
    lines.push(`| Severity | File | Line | Message | Pattern |`);
    lines.push(`|----------|------|------|---------|---------|`);
    for (const f of byGate[gateName]) {
      const fileLink = `${f.file}:${f.line}`;
      lines.push(`| ${severityIcon(f.severity)} ${f.severity} | \`${fileLink}\` | ${f.line} | ${f.message} | ${f.pattern} |`);
    }
    lines.push('');
  }

  lines.push('## Snippets');
  lines.push('');
  for (const f of findings.slice(0, 50)) {
    lines.push(`### ${f.file}:${f.line} (${f.gate} / ${f.pattern})`);
    lines.push('```');
    lines.push(f.snippet);
    lines.push('```');
    if (f.fix_template) {
      lines.push('**Suggested fix:**');
      lines.push('```');
      lines.push(f.fix_template);
      lines.push('```');
    }
    lines.push('');
  }

  return lines.join('\n');
}

function json(findings, metrics) {
  return JSON.stringify({ findings, metrics, generated_at: new Date().toISOString() }, null, 2);
}

function githubAnnotations(findings) {
  const lines = [];
  for (const f of findings) {
    const level = severityGHLevel(f.severity);
    lines.push(`::${level} file=${f.file},line=${f.line},col=${f.col}::[${f.gate}] ${f.message}`);
  }
  return lines.join('\n');
}

function summary(findings, metrics) {
  const total = findings.length;
  const critical = findings.filter(f => f.severity === 'critical').length;
  const high = findings.filter(f => f.severity === 'high').length;
  const medium = findings.filter(f => f.severity === 'medium').length;
  const low = findings.filter(f => f.severity === 'low').length;
  const fixed = metrics.auto_fixes_applied || 0;

  const blocked = critical > 0 || high > 0;
  const status = blocked ? 'BLOCKED' : (total > 0 ? 'PASSED_WITH_WARNINGS' : 'PASS');

  return `Governance: ${critical} critical, ${high} high, ${medium} medium, ${low} low | ${fixed} auto-fixed | ${status}`;
}

module.exports = { markdown, json, githubAnnotations, summary };

if (require.main === module) {
  const fs = require('fs');
  const [findingsPath, metricsPath] = process.argv.slice(2);
  if (!findingsPath) {
    console.error('Usage: node reporter.js <findings.json> [metrics.json]');
    process.exit(1);
  }
  const findings = JSON.parse(fs.readFileSync(findingsPath, 'utf8'));
  const metrics = metricsPath ? JSON.parse(fs.readFileSync(metricsPath, 'utf8')) : {};
  console.log(markdown(findings, metrics));
}
