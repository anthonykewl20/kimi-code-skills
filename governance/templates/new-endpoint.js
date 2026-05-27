// Template for new API endpoints — includes all governance patterns
module.exports = {
  // POST endpoint — idempotent by design
  create: `
    <?php
    /**
     * GATE: Idempotency-Key header required for mutations
     * GATE: Use transaction with conflict handling
     * GATE: Atomic SQL updates only
     */
    if (empty($_POST['idempotency_key'])) {
        header('Content-Type: application/json');
        http_response_code(400);
        echo json_encode(['error' => 'Idempotency-Key required']);
        exit;
    }

    $idempotency_key = Wo_Secure($_POST['idempotency_key']);
    $user_id = $wo['user']['user_id'];

    global $sqlConnect;
    mysqli_begin_transaction($sqlConnect);

    try {
        // Check for existing (idempotent replay)
        $check = mysqli_query($sqlConnect,
            "SELECT id FROM {table} WHERE idempotency_key = '" . mysqli_real_escape_string($sqlConnect, $idempotency_key) . "'"
        );
        if (mysqli_num_rows($check) > 0) {
            mysqli_commit($sqlConnect);
            header('Content-Type: application/json');
            echo json_encode(['status' => 'duplicate', 'message' => 'Already processed']);
            exit;
        }

        // Insert with conflict safety net
        $columns = implode(', ', array_keys($data));
        $values = implode(', ', array_map(function($v) use ($sqlConnect) {
            return "'" . mysqli_real_escape_string($sqlConnect, $v) . "'";
        }, array_values($data)));

        $insert = mysqli_query($sqlConnect,
            "INSERT INTO {table} (idempotency_key, {$columns}) VALUES ('{$idempotency_key}', {$values})"
        );

        if (!$insert) {
            throw new Exception(mysqli_error($sqlConnect));
        }

        $record_id = mysqli_insert_id($sqlConnect);
        mysqli_commit($sqlConnect);

        header('Content-Type: application/json');
        echo json_encode(['status' => 'success', 'id' => $record_id]);

    } catch (Exception $e) {
        mysqli_rollback($sqlConnect);
        header('Content-Type: application/json');
        http_response_code(500);
        echo json_encode(['error' => $e->getMessage()]);
    }
  `,

  // PUT endpoint — atomic update with version check (optimistic locking)
  update: `
    <?php
    /**
     * GATE: Use version column for optimistic concurrency
     * GATE: Atomic update with affected-rows verification
     */
    $id = (int) $_POST['id'];
    $version = (int) $_POST['version'];
    $user_id = $wo['user']['user_id'];

    global $sqlConnect;

    // Atomic update — only succeeds if version matches
    $result = mysqli_query($sqlConnect,
        "UPDATE {table} SET {columns} = '{values}', version = version + 1 WHERE id = {$id} AND version = {$version}"
    );

    if (mysqli_affected_rows($sqlConnect) === 0) {
        header('Content-Type: application/json');
        http_response_code(409);
        echo json_encode(['error' => 'Conflict: resource modified by another request']);
        exit;
    }

    header('Content-Type: application/json');
    echo json_encode(['status' => 'success', 'version' => $version + 1]);
  `,

  // GET endpoint — always paginated
  list: `
    <?php
    /**
     * GATE: Always paginate — unbounded queries are blocked
     * GATE: Validate and cap limit
     */
    $page = isset($_GET['page']) ? max(1, (int) $_GET['page']) : 1;
    $limit = isset($_GET['limit']) ? min(100, max(1, (int) $_GET['limit'])) : 20;
    $offset = ($page - 1) * $limit;

    global $sqlConnect;

    // Bounded query
    $count_result = mysqli_query($sqlConnect, "SELECT COUNT(*) as total FROM {table}");
    $total = mysqli_fetch_assoc($count_result)['total'];

    $result = mysqli_query($sqlConnect,
        "SELECT * FROM {table} ORDER BY id DESC LIMIT {$limit} OFFSET {$offset}"
    );

    $rows = [];
    while ($row = mysqli_fetch_assoc($result)) {
        $rows[] = $row;
    }

    header('Content-Type: application/json');
    echo json_encode([
        'data' => $rows,
        'pagination' => [
            'page' => $page,
            'limit' => $limit,
            'total' => (int) $total,
            'pages' => (int) ceil($total / $limit)
        ]
    ]);
  `
};
