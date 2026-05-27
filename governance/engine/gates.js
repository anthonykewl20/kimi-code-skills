#!/usr/bin/env node
/**
 * Gate Enforcement Logic
 * Evaluates scan findings against thresholds and gate rules.
 */

class GateEnforcer {
  constructor(config) {
    this.config = config;
  }

  evaluate(findings) {
    const critical = findings.filter(f => f.severity === 'critical');
    const high = findings.filter(f => f.severity === 'high');
    const medium = findings.filter(f => f.severity === 'medium');
    const low = findings.filter(f => f.severity === 'low');

    const blocked = [];
    const warnings = [];

    if (this.config.fail_on_critical && critical.length > this.config.thresholds.max_critical) {
      blocked.push(`${critical.length} critical issues (max: ${this.config.thresholds.max_critical})`);
    }
    if (this.config.fail_on_high && high.length > this.config.thresholds.max_high) {
      blocked.push(`${high.length} high issues (max: ${this.config.thresholds.max_high})`);
    }
    if (this.config.fail_on_medium && medium.length > this.config.thresholds.max_medium) {
      blocked.push(`${medium.length} medium issues (max: ${this.config.thresholds.max_medium})`);
    }
    if (this.config.fail_on_low && low.length > this.config.thresholds.max_low) {
      blocked.push(`${low.length} low issues (max: ${this.config.thresholds.max_low})`);
    }

    // Collect warnings for medium/low even if not blocking
    if (medium.length > 0 && !this.config.fail_on_medium) {
      warnings.push(`${medium.length} medium issues (warn-only mode)`);
    }
    if (low.length > 0 && !this.config.fail_on_low) {
      warnings.push(`${low.length} low issues (logged only)`);
    }

    return {
      passed: blocked.length === 0,
      blocked_by: blocked,
      warnings,
      counts: { critical: critical.length, high: high.length, medium: medium.length, low: low.length },
      can_proceed_with_warnings: blocked.length === 0
    };
  }

  formatForUI(result) {
    const lines = [];
    if (!result.passed) {
      lines.push('::error::Governance gates BLOCKED this operation');
      for (const b of result.blocked_by) {
        lines.push(`::error::${b}`);
      }
    }
    for (const w of result.warnings) {
      lines.push(`::warning::${w}`);
    }
    lines.push(`::notice::Governance summary — Critical: ${result.counts.critical}, High: ${result.counts.high}, Medium: ${result.counts.medium}, Low: ${result.counts.low}`);
    return lines.join('\n');
  }
}

module.exports = { GateEnforcer };

// CLI usage
if (require.main === module) {
  const fs = require('fs');
  const path = require('path');
  const { parseYAML } = require('./scanner');

  const configPath = path.join(__dirname, '..', 'config.yaml');
  const config = parseYAML(fs.readFileSync(configPath, 'utf8')).governance;

  const findingsPath = process.argv[2];
  if (!findingsPath) {
    console.error('Usage: node gates.js <findings.json>');
    process.exit(1);
  }

  const findings = JSON.parse(fs.readFileSync(findingsPath, 'utf8'));
  const enforcer = new GateEnforcer(config);
  const result = enforcer.evaluate(findings);

  console.log(enforcer.formatForUI(result));
  process.exit(result.passed ? 0 : 2);
}
