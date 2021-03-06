<?php
/*
 * Copyright (c) 2010-2012, Contrail consortium.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms,
 * with or without modification, are permitted provided
 * that the following conditions are met:
 *
 *  1. Redistributions of source code must retain the
 *     above copyright notice, this list of conditions
 *     and the following disclaimer.
 *  2. Redistributions in binary form must reproduce
 *     the above copyright notice, this list of
 *     conditions and the following disclaimer in the
 *     documentation and/or other materials provided
 *     with the distribution.
 *  3. Neither the name of the Contrail consortium nor the
 *     names of its contributors may be used to endorse
 *     or promote products derived from this software
 *     without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
 * CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

require_once('../__init__.php');
require_module('logging');
require_module('service');
require_module('service/factory');
require_module('https');

try{

if (!isset($_SESSION['uid'])) {
	throw new Exception('User not logged in');
}

$sid = $_POST['sid'];
error_log("sid -- "+$sid);
$service_data = ServiceData::getServiceById($sid);
$service = ServiceFactory::create($service_data);


if($service->getUID() !== $_SESSION['uid']) {
    throw new Exception('Not allowed');
}

if (!isset($_POST['cool_down'])) {
	echo json_encode(array(
		'error' => 'Cool down time is not established'
	));
	exit();
}

if (!isset($_POST['response_time'])) {
	echo json_encode(array(
		'error' => 'Response time is not established'
	));
	exit();
}


$params =  array(
	'response_time' => $_POST['response_time'],
	'cool_down' => $_POST['cool_down'],
	'strategy' => $_POST['strategy'],
	'method' => 'on_autoscaling'
);


	$response = HTTPS::jsonrpc($service->getManager(),'post','on_autoscaling', $params);
	echo json_encode($response);
} catch (Exception $e) {
	echo json_encode(array('error' => $e->getMessage()));
}
?>

