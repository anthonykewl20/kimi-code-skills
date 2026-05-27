// Template for DB migrations — pre-hardened for governance
module.exports = {
  // New table must include governance columns
  createTable: `
    <?php
    /**
     * GATE: New table must include governance columns
     * GATE: Idempotency support — add to all mutation tables
     * GATE: Optimistic locking — version column
     * GATE: Audit trail
     * GATE: Add UNIQUE constraints for idempotency
     */
    global $sqlConnect;

    $table = '{table}';

    $sql = "CREATE TABLE IF NOT EXISTS {$table} (
        id INT AUTO_INCREMENT PRIMARY KEY,

        -- GATE: Idempotency support — add to all mutation tables
        idempotency_key VARCHAR(64) UNIQUE,
        INDEX idx_idempotency_key (idempotency_key),

        -- GATE: Optimistic locking — version column
        version INT DEFAULT 1,

        -- GATE: Audit trail
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

        -- ... your columns here

        -- GATE: Add UNIQUE constraints for idempotency
        UNIQUE KEY uq_{table}_business_key (business_key_column)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;";

    if (!mysqli_query($sqlConnect, $sql)) {
        die("Failed to create table {$table}: " . mysqli_error($sqlConnect));
    }

    echo "Table {$table} created with governance columns.\\n";
  `,

  // ALTER must use batching for large tables
  alterColumn: `
    <?php
    /**
     * GATE: Batch updates to avoid table locks
     * GATE: Use LIMIT on UPDATE for large tables
     */
    global $sqlConnect;

    $table = '{table}';
    $column = '{column}';
    $value = '{value}';
    $BATCH_SIZE = 1000;

    $lastId = 0;
    $updated = 0;

    do {
        $result = mysqli_query($sqlConnect,
            "UPDATE {$table}
             SET {$column} = '{$value}'
             WHERE {$column} IS NULL AND id > {$lastId}
             ORDER BY id
             LIMIT {$BATCH_SIZE}"
        );

        $batchUpdated = mysqli_affected_rows($sqlConnect);
        $updated += $batchUpdated;

        // Get last updated id
        $maxResult = mysqli_query($sqlConnect,
            "SELECT MAX(id) as max_id FROM {$table} WHERE {$column} = '{$value}'"
        );
        $maxRow = mysqli_fetch_assoc($maxResult);
        $lastId = $maxRow['max_id'] ?? $lastId;

        echo "Batch updated {$batchUpdated} rows (total: {$updated})\\n";

    } while ($batchUpdated === $BATCH_SIZE);

    echo "Alter complete. Total rows updated: {$updated}\\n";
  `,

  // Add idempotency key to existing table
  addIdempotencyKey: `
    <?php
    /**
     * GATE: Add idempotency_key to existing table
     */
    global $sqlConnect;

    $table = '{table}';

    $sql = "ALTER TABLE {$table}
        ADD COLUMN idempotency_key VARCHAR(64) NULL AFTER id,
        ADD UNIQUE INDEX idx_idempotency_key (idempotency_key);";

    if (!mysqli_query($sqlConnect, $sql)) {
        die("Failed to alter table {$table}: " . mysqli_error($sqlConnect));
    }

    echo "Added idempotency_key to {$table}.\\n";
  `
};
