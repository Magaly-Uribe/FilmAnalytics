<?php
$uri = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$file = __DIR__ . $uri;

if ($uri !== '/' && file_exists($file) && !is_dir($file)) {
    return false;
}

if (is_dir($file)) {
    $file .= '/index.html';
}

if (file_exists($file)) {
    $ext = pathinfo($file, PATHINFO_EXTENSION);
    if ($ext === 'php') {
        require $file;
    } else {
        $mimes = ['html'=>'text/html','css'=>'text/css','js'=>'application/javascript',
                  'json'=>'application/json','png'=>'image/png','jpg'=>'image/jpeg'];
        header('Content-Type: ' . ($mimes[$ext] ?? 'text/plain'));
        readfile($file);
    }
} else {
    http_response_code(404);
    echo "404 Not Found";
}