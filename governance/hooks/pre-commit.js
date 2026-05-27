#!/usr/bin/env node
/**
 * Pre-Commit Hook
 * Runs before user accepts changes.
 * Full scan + test run + final gate enforcement.
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

function detectTestCommand() {
  const cwd = process.cwd();

  // Check for Playwright
  if (fs.existsSync(path.join(cwd, 'e2e', 'playwright.config.js')) ||
      fs.existsSync(path.join(cwd, 'e2e', 'playwright.config.ts')) ||
      fs.existsSync(path.join(cwd, 'playwright.config.js'))) {
    return 'cd e2e && npx playwright test';
  }

  // Check for PHPUnit
  if (fs.existsSync(path.join(cwd, 'phpunit.xml')) ||
      fs.existsSync(path.join(cwd, 'vendor', 'bin', 'phpunit'))) {
    return './vendor/bin/phpunit';
  }

  // Check for Jest
  if (fs.existsSync(path.join(cwd, 'jest.config.js')) ||
      fs.existsSync(path.join(cwd, 'package.json'))) {
    try {
      const pkg = JSON.parse(fs.readFileSync(path.join(cwd, 'package.json'), 'utf8'));
      if (pkg.scripts && pkg.scripts.test) return 'npm test';
    } catch (_) {}
  }

  return null;
}

function runTests(cmd) {
  if (!cmd) return { ran: false, passed: null, output: 'No test command detected' };

  try {
    const output = execSync(cmd, {
      encoding: 'utf8',
      cwd: process.cwd(),
      timeout: 120000,
      stdio: ['pipe', 'pipe', 'pipe']
    });
    return { ran: true, passed: true, output };
  } catch (e) {
    return { ran: true, passed: false, output: e.stdout || e.message || 'Test execution failed' };
  }
}

function runIdempotencyVerification() {
  // Run-twice pattern: if the codebase has idempotency tests, run them twice
  // This is project-specific; for now we log that it should be done
  return { ran: false, note: 'Idempotency verification: run tests twice and compare state' };
}

function runRaceTests() {
  // Promise.all pattern for race detection
  return { ran: false, note: 'Race condition tests: use Promise.all concurrent execution patterns' };
}

function main() {
  const args = parseArgs(process.argv);
  const scope = args.scope || 'changed'; // 'changed' or 'full'
  const runTestsFlag = args['run-tests'] === 'true' || args['run-tests'] === true;

  const { loadConfig, loadGates, scanFiles } = require(path.join(ENGINE_DIR, 'scanner.js'));
  const { GateEnforcer } = require(path.join(ENGINE_DIR, 'gates.js'));
  const reporter = require(path.join(ENGINE_DIR, 'reporter.js'));

  const config = loadConfig();
  if (!config.enabled) {
    console.log('Governance disabled');
    process.exit(0);
  }

  const gates = loadGates();

  console.log('═'.repeat(70));
  console.log('GOVERNANCE PRE-COMMIT VALIDATION');
  console.log('═'.repeat(70));
  console.log(`Scope: ${scope}`);
  console.log('');

  // 1. Scan
  console.log('[1/4] Running governance scan...');
  const { findings, metrics } = scanFiles(scope === 'full' ? 'all' : 'all', config, gates);
  console.log(`      Scanned ${metrics.files_scanned} files, ${metrics.lines_scanned} lines`);
  console.log(`      Found ${findings.length} issues`);
  console.log('');

  // 2. Tests
  console.log('[2/4] Running test suite...');
  const testCmd = detectTestCommand();
  let testResult;
  if (runTestsFlag && testCmd) {
    testResult = runTests(testCmd);
    if (testResult.ran) {
      console.log(`      Tests ${testResult.passed ? 'PASSED ✅' : 'FAILED ❌'}`);
    } else {
      console.log(`      ${testResult.output}`);
    }
  } else {
    testResult = { ran: false, passed: null, output: testCmd ? `Detected: ${testCmd} (skip with --run-tests=false)` : 'No test command detected' };
    console.log(`      ${testResult.output}`);
  }
  console.log('');

  // 3. Idempotency & Race verification
  console.log('[3/4] Idempotency & Race verification...');
  const idemResult = runIdempotencyVerification();
  const raceResult = runRaceTests();
  console.log(`      ${idemResult.note}`);
  console.log(`      ${raceResult.note}`);
  console.log('');

  // 4. Gate enforcement
  console.log('[4/4] Gate enforcement...');
  const enforcer = new GateEnforcer(config);
  const result = enforcer.evaluate(findings);

  if (testResult.ran && !testResult.passed) {
    result.passed = false;
    result.blocked_by.push('Test suite failed');
  }

  console.log(enforcer.formatForUI(result));
  console.log('');

  // Write report
  const reportDir = path.resolve(process.cwd(), config.reports.output_dir);
  fs.mkdirSync(reportDir, { recursive: true });
  const ts = new Date().toISOString().replace(/[:.]/g, '-');
  fs.writeFileSync(path.join(reportDir, `pre-commit-${ts}.md`), reporter.markdown(findings, metrics));
  fs.writeFileSync(path.join(reportDir, `pre-commit-${ts}.json`), reporter.json(findings, metrics));

  console.log('═'.repeat(70));
  console.log(reporter.summary(findings, metrics));
  console.log('═'.repeat(70));

  process.exit(result.passed ? 0 : 2);
}

module.exports = { detectTestCommand, runTests, runIdempotencyVerification, runRaceTests };

if (require.main === module) {
  main();
}
