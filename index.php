<?php

$fileconfig = "config.json";
$filelog = "log.txt";

header('Content-Type: application/json');

$config = json_decode(file_get_contents($fileconfig));

if(isset($_POST['time']) && DateTime::createFromFormat('Y-m-d H:i:s', $time = $_POST['time']) !== FALSE)
    $config->time_ambil = $time;
    
if(isset($_POST['start']))
    $config->mulai = $_POST['start'] != 0;

file_put_contents($fileconfig, json_encode($config, JSON_PRETTY_PRINT));

$log = "";

if (file_exists($filelog)){
    $logarray = file($filelog);
    for($i = count($logarray)<30 ? 0 : count($logarray)-31; $i < count($logarray); $i++)
        $log .= $logarray[$i];
}

echo json_encode([
    'time' => $config->time_ambil,
    'start' => $config->mulai,
    'log' => $log
]);