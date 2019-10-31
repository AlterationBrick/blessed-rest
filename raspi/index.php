<?php
exec("gpio mode 0 out");
exec("gpio mode 2 out");
exec("gpio mode 3 out");
if (isset($_GET['tiltUp'] == 1)) {
	if ($_GET['tiltUp'] == 1) {
		exec("gpio write 0 1");
	} else {
		exec("gpio write 0 0");	
	}
if (isset($_GET['tiltDown'] == 1)) {
	if ($_GET['tiltDown'] == 1) {
		exec("gpio write 2 1");
	} else {
		exec("gpio write 2 0");
	}
}
}
?>