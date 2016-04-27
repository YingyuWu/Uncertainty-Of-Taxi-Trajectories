<?php
$gid = $_POST['poi_id'];
if($gid == ''){
	echo "gid error";
	exit();
}
$dbc = pg_connect("host=localhost port=5432 dbname=poi user=postgres password=123");
if (!$dbc) {
     echo "error";
 }
$query = "select roadid from poi_road where poi_road.poiid = '".$gid."';";
$result = pg_query($dbc,$query);
$pois = array();
 if(!$result){
        echo '<h1>System Error</h1>';
        exit();
 }
 $curr;
 while ($row = pg_fetch_row($result)) {
    $curr = $row[0];
}
$roads = explode(",", $curr);
$query = "select detailtimes from traveltime where ";
for($i = 0; $i < sizeof($roads); $i++){
	if($roads[$i] != "" && $roads[$i] != " "){
			$query = $query."roadid ='".$roads[$i]."' or ";
		
		
	}
}
$query = substr($query, 0, -3);
$result = pg_query($dbc,$query);
if(!$result){
        echo '<h1>System Error</h1>';
        exit();
 }
$curr = array();
 while ($str = pg_fetch_row($result)) {
 	$tmp = explode("},{",substr($str[0],2,-2) );
 	$a = array();
 	for($i = 0; $i<sizeof($tmp); $i++){
 		$b = explode(",",$tmp[$i]);
 		array_push($a,$b);
 	}
    array_push($curr,$a);
}
#Cheng 
$result = array();
for($i = 0; $i < sizeof($curr[0]); $i++){
	$tmp = array();
	for($j=0; $j < sizeof($curr[0][0]); $j++){
		array_push($tmp, 10);
	}
	array_push($result,$tmp);
}


for($i = 0; $i < sizeof($curr); $i++){
	for($j = 0; $j < sizeof($curr[$i]); $j++){
		for($k = 0; $k < sizeof($curr[$i][$j]); $k++){
			$tmp = floatval($curr[$i][$j][$k]);
			if ($result[$j][$k] > $tmp)
				$result[$j][$k] = $tmp;
		}
	}
}

echo json_encode($result);
?>