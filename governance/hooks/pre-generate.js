#!/usr/bin/env node
/**
 * Pre-Generate Hook
 * Runs before Kimi starts generating code.
 * Analyzes the prompt, injects governance templates into context.
 */

const fs = require('fs');
const path = require('path');

const GOV_DIR = path.dirname(path.dirname(__filename));
const TEMPLATES_DIR = path.join(GOV_DIR, 'templates');

function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i += 2) {
    const key = argv[i].replace(/^--/, '');
    args[key] = argv[i + 1] || '';
  }
  return args;
}

function loadTemplate(name) {
  const p = path.join(TEMPLATES_DIR, `${name}.js`);
  if (!fs.existsSync(p)) return null;
  return require(p);
}

function analyzePrompt(prompt) {
  const lower = (prompt || '').toLowerCase();
  const intents = [];

  if (/new\s+(endpoint|route|api|xhr)/.test(lower)) intents.push('endpoint');
  if (/migration|schema\s+change|alter\s+table|create\s+table/.test(lower)) intents.push('migration');
  if (/new\s+(service|module|class)/.test(lower)) intents.push('service');
  if (/payment|wallet|callback|stripe|paypal/.test(lower)) intents.push('payment');

  return intents;
}

function buildContext(intents, prompt) {
  const sections = [];

  sections.push('═'.repeat(70));
  sections.push('GOVERNANCE CONTEXT INJECTION');
  sections.push('═'.repeat(70));
  sections.push('');
  sections.push('The following hard-gate rules are ACTIVE for this generation:');
  sections.push('');

  // Universal rules
  sections.push('## Universal Rules (ALL code)');
  sections.push('- No SELECT without LIMIT on large tables');
  sections.push('- No file_get_contents / curl_exec / shell_exec without timeout');
  sections.push('- No financial UPDATE without atomic operation (SET col = col + ?)');
  sections.push('- No INSERT without conflict handling (ON CONFLICT / IGNORE / UPSERT)');
  sections.push('- No session_start() in AJAX without session_write_close()');
  sections.push('- All new XHR endpoints must close mysqli or use shutdown handler');
  sections.push('');

  if (intents.includes('endpoint')) {
    sections.push('## Endpoint Rules');
    sections.push('- Accept Idempotency-Key header for mutations');
    sections.push('- Use atomic SQL updates (not read-modify-write)');
    sections.push('- Always paginate list endpoints (max 100/page)');
    sections.push('- Return 409 Conflict for optimistic locking failures');
    sections.push('');

    const tmpl = loadTemplate('new-endpoint');
    if (tmpl) {
      sections.push('## Endpoint Template');
      sections.push('```php');
      sections.push(tmpl.create || '');
      sections.push('```');
      sections.push('');
    }
  }

  if (intents.includes('migration')) {
    sections.push('## Migration Rules');
    sections.push('- All new tables need idempotency_key column with UNIQUE index');
    sections.push('- All tables need version column for optimistic locking');
    sections.push('- Batch updates with LIMIT for large tables');
    sections.push('- Add UNIQUE constraints for business keys');
    sections.push('');

    const tmpl = loadTemplate('new-migration');
    if (tmpl) {
      sections.push('## Migration Template');
      sections.push('```js');
      sections.push(tmpl.createTable || '');
      sections.push('```');
      sections.push('');
    }
  }

  if (intents.includes('payment')) {
    sections.push('## Payment Rules (CRITICAL)');
    sections.push('- ALL payment callbacks MUST check txn_id against T_PAYMENT_TRANSACTIONS before processing');
    sections.push('- Use atomic wallet UPDATE: UPDATE users SET wallet = wallet + ? WHERE user_id = ?');
    sections.push('- Never read wallet/balance into PHP variable then write literal');
    sections.push('- Return 200 for duplicate callbacks (idempotent)');
    sections.push('');
  }

  sections.push('## Validation Contract Template');
  sections.push('```');
  sections.push('ASSERT-SEC-001: Financial operation is atomic and idempotent');
  sections.push('ASSERT-ST-001: Success state creates exactly one record');
  sections.push('ASSERT-ST-002: Retry returns same result without side effects');
  sections.push('ASSERT-P-001: External I/O times out within 5 seconds');
  sections.push('ASSERT-P-002: Large queries are bounded with LIMIT');
  sections.push('```');
  sections.push('');
  sections.push('═'.repeat(70));

  return sections.join('\n');
}

function main() {
  const args = parseArgs(process.argv);
  const prompt = args.prompt || '';
  const intents = analyzePrompt(prompt);

  if (intents.length === 0) {
    // No specific governance context needed
    console.log('// Governance: No specific templates for this prompt');
    process.exit(0);
  }

  const context = buildContext(intents, prompt);
  console.log(context);
  process.exit(0);
}

module.exports = { analyzePrompt, buildContext };

if (require.main === module) {
  main();
}
