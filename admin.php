<?php
// SMM Panel Admin - API Proxy
// File này sẽ proxy requests đến backend Python

// Get route parameter
$route = $_GET['route'] ?? '';

$backend_url = 'http://127.0.0.1:8000';

// Build request URL
if ($route) {
    $request_url = $backend_url . '/' . $route;
} else {
    $request_url = $backend_url . $_SERVER['REQUEST_URI'];
}

// Get the request method
$method = $_SERVER['REQUEST_METHOD'];

// Prepare curl
$ch = curl_init($request_url);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, true);
curl_setopt($ch, CURLOPT_HEADER, false);

// Set headers
$headers = [];
foreach (getallheaders() as $name => $value) {
    if (strtolower($name) !== 'host') {
        $headers[] = "$name: $value";
    }
}
curl_setopt($ch, CURLOPT_HTTPHEADER, $headers);

// Set method
curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);

// Set body if POST/PUT
if ($method === 'POST' || $method === 'PUT') {
    $data = file_get_contents('php://input');
    curl_setopt($ch, CURLOPT_POSTFIELDS, $data);
}

// Execute request
$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
$content_type = curl_getinfo($ch, CURLINFO_CONTENT_TYPE);

// Set response headers
header("HTTP/1.1 $http_code");
if ($content_type) {
    header("Content-Type: $content_type");
}

echo $response;
curl_close($ch);
?>
