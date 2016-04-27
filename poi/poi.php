<?php

$dbc = pg_connect("host=localhost port=5432 dbname=poi user=postgres password=123");
if (!$dbc) {
     echo "error";
 }
$query = "select poi_hangzhou.latitude,poi_hangzhou.longitude,poi_hangzhou.type,poi_hangzhou.name,poi_hangzhou.gid from poi_road,poi_hangzhou where poi_road.poiid = poi_hangzhou.gid;";
$result = pg_query($dbc,$query);
$pois = array();
 if(!$result){
        echo '<h1>System Error</h1>';
        exit();
 }
 while ($row = pg_fetch_row($result)) {
    array_push($pois, $row);
}
?>
<!DOCTYPE html>
<html>
<head>
<meta charset=utf-8 />
<title>Plain Leaflet API</title>
<meta name='viewport' content='initial-scale=1,maximum-scale=1,user-scalable=no' />
<script src='https://api.mapbox.com/mapbox.js/v2.3.0/mapbox.js'></script>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.0/jquery.min.js"></script>
<script src="js/d3.js"></script>
<script src="js/poi_vis.js"></script>
<script src="js/L.D3SvgOverlay.min.js"></script>
<script src="js/colorbrewer.js"></script>
<link href='https://api.mapbox.com/mapbox.js/v2.3.0/mapbox.css' rel='stylesheet' />
<link href='css/style.css' rel='stylesheet' />
</head>
<body>
<div id='map'></div>
<div style="float:right;height:150;width:20%" id="category">
<b>POI Catebory:</b><br>
<span id="poi_category">

</span>
</div>
<script>
L.mapbox.accessToken = 'pk.eyJ1IjoiYmVzZmllbGQiLCJhIjoiY2lneHoyY2Y1MHV3bTRwbTNtdjE5eHgzZiJ9.DPecCdxSkx44VQLXhaKmEg';
var mapboxTiles = L.tileLayer('https://api.mapbox.com/v4/mapbox.streets/{z}/{x}/{y}.png?access_token=' + L.mapbox.accessToken, {
    attribution: '<a href="http://www.mapbox.com/about/maps/" target="_blank">Terms &amp; Feedback</a>'
});

var map = L.map('map')
    .addLayer(mapboxTiles)
    .setView([30.24659290255, 120.17695426940918], 14);
var marker = L.marker([30.24659290255, 120.17695426940918]).addTo(map);
marker.bindPopup("I'm hangzhou railway station.").openPopup();
var category_color = colorbrewer.Paired[12].concat(["#6E6E6E","#972D2D","#809C81","#5100FF","#EB25E7","#25E4EB"]);
var categories = ["美食","丽人","运动","医疗","汽车","休闲","购物","公司","政府","房地产","生活","交通","教育","金融","旅游","文化","宾馆","自然"];
d3.select("#poi_category").selectAll("input").data(categories).enter().append('label').attr('for',function(d,i){ return 'a'+i; }).text(function(d) { return d; }).style("fill",function(d,i){return category_color[i]}).append("input").attr("type", "checkbox").attr("name","poi_category").attr("id", function(d,i) { return d; }).attr("onClick", "changeSelection(this)").append("br");
d3.select("#美食").attr("checked", true);


var pois = <?php echo json_encode($pois); ?>;//all the points from database
//sample dataset
drawPOI(pois,map,category_color,categories);



</script>
</body>
</html>

