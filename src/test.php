<?php
$arr = file('./campaign.dat');
$obj = json_decode($arr[0]);
print_r($obj);
?>