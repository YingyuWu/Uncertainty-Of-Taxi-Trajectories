var poi_layers = {};
var poi_data = {};
var categories;
var category_color;
var sample;
function drawPOI(pois,map,color,category){
	categories = category;
	category_color = color;
	poi_data['美食'] = pois.filter(function(d){return d[2].indexOf('美食') != -1;});
	poi_data['丽人'] = pois.filter(function(d){return d[2].indexOf('丽人') != -1;});
	poi_data['运动'] = pois.filter(function(d){return d[2].indexOf('运动') != -1;});
	poi_data['医疗'] = pois.filter(function(d){return d[2].indexOf('医疗') != -1;});
	poi_data['汽车'] = pois.filter(function(d){return d[2].indexOf('汽车') != -1;});
	poi_data['休闲'] = pois.filter(function(d){return d[2].indexOf('休闲') != -1;});
	poi_data['购物'] = pois.filter(function(d){return d[2].indexOf('购物') != -1;});
	poi_data['公司'] = pois.filter(function(d){return d[2].indexOf('公司') != -1;});
	poi_data['政府'] = pois.filter(function(d){return d[2].indexOf('政府') != -1;});
	poi_data['房地产'] = pois.filter(function(d){return d[2].indexOf('房地产') != -1;});
	poi_data['生活'] = pois.filter(function(d){return d[2].indexOf('生活') != -1;});
	poi_data['交通'] = pois.filter(function(d){return d[2].indexOf('交通') != -1;});
	poi_data['教育'] = pois.filter(function(d){return d[2].indexOf('教育') != -1;});
	poi_data['金融'] = pois.filter(function(d){return d[2].indexOf('金融') != -1;});
	poi_data['旅游'] = pois.filter(function(d){return d[2].indexOf('旅游') != -1;});
	poi_data['文化'] = pois.filter(function(d){return d[2].indexOf('文化') != -1;});
	poi_data['宾馆'] = pois.filter(function(d){return d[2].indexOf('宾馆') != -1;});
	poi_data['自然'] = pois.filter(function(d){return d[2].indexOf('自然') != -1;});


	drawCircles(poi_data['美食'],map,'美食');//init map
}


function drawCircles(data,map,category_id){
	var zoomDraw = false;
	var citiesOverlay = L.d3SvgOverlay(function(sel,proj){
	  var citiesUpd = sel.selectAll('circle').data(data);
	  citiesUpd.enter()
	    .append('circle')
	    .attr('r',function(d){return  proj.unitsPerMeter * 15;})//control the size of circle remain at the same zoom level
	    .attr('cx',function(d){return proj.latLngToLayerPoint([d[0],d[1]]).x;})
	    .attr('cy',function(d){return proj.latLngToLayerPoint([d[0],d[1]]).y;})
	    .attr("id",function(d){return d[4]})//return gid as id
	    .attr('stroke','black')
	    .attr('stroke-width',function(d){return  proj.unitsPerMeter * 2;})
	    .style("opacity",0.8)
	    .attr('fill',function(d){return category_color[categories.indexOf(category_id)];})
	    .on("click",function(d){
	    	var object = {};
	    	object['cx'] = d3.select(this).attr("cx");
			object['cy'] = d3.select(this).attr("cy");
			object['name'] = d[3];
	      //update dataset
	      readData(map,d[4],object);
	  });
	});
	citiesOverlay.addTo(map);
	poi_layers[category_id]= citiesOverlay;
}

function changeSelection(e){

	if(e.checked){//new layer should be added to map
		drawCircles(poi_data[e.id],map,e.id);

	}else{//old layer should be remove from map
		if(poi_layers[e.id] != undefined){//check if layer exists on map
			 map.removeLayer(poi_layers[e.id]);
			 delete poi_layers[e.id];
		}
	}

}

function readData(map,gid,object){
	$.ajax({ url: "readData.php",
   						type: 'post',
                       data: {poi_id: gid},
                       dataType:'json',
                       success: function(data) {
                       		//sample = data;
                       		drawHeatMap(map,gid,data,object);
                        }
   });
}


function drawHeatMap(map,gid,sample,object){
   
  if(d3.select("svg").select("#heatmap")[0][0] != null){
    
    d3.select("svg").select("#heatmap").attr("transform","translate("+ (object['cx']-100) +","+ (object['cy']-100) + ")").selectAll(".hour").data(sample);
	d3.select("svg").select("#heatmap").select("#close").select("#name").text(object['name']);
    return;
  }
  var colorforscale = []
  //colorforscale.push(colorbrewer.YlGnBu[9][0]);
  colorforscale.push(colorbrewer.YlGnBu[9][2]);
  colorforscale.push(colorbrewer.YlGnBu[9][3]);
  colorforscale.push(colorbrewer.YlGnBu[9][4]);
  colorforscale.push(colorbrewer.YlGnBu[9][5]);
  colorforscale.push(colorbrewer.YlGnBu[9][7]);
  var colorscale = d3.scale.quantile().range(colorforscale).domain([0,10,20]);
  var distancesclae = d3.scale.linear().range([0,20]).domain([0,4]);
   var margin = { top: 50, right: 0, bottom: 100, left: 30 },
          gap = 50,
          width = 450 - margin.left - margin.right,
          height = 370 - margin.top - margin.bottom,
          gridSize = Math.floor(width / 24),
          legendElementWidth = gridSize*2,
          buckets = 9,
          distance = [7,14,20,27,34,40,47,53,60],
          //colors = ["#ffffd9","#edf8b1","#c7e9b4","#7fcdbb","#41b6c4","#1d91c0","#225ea8","#253494","#081d58"], // alternatively colorbrewer.YlGnBu[9]
          days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"],
          times = ["1a", "2a", "3a", "4a", "5a", "6a", "7a", "8a", "9a", "10a", "11a", "12a", "1p", "2p", "3p", "4p", "5p", "6p", "7p", "8p", "9p", "10p", "11p", "12p"];
     var svg = d3.select("svg").append("g").attr("id","heatmap").attr("transform","translate("+ object['cx'] +","+ object['cy'] + ")")//.attr("id","main-svg").attr("class","svg").attr("width", width + margin.left + margin.right)
          //.attr("height", height + margin.top + margin.bottom)
          //.append("g");
    var background = svg.append("rect").attr("width",(width + 50)).attr("height",height).attr("x",0).attr("y",0).style("fill","white").style("opacity",0.9)
    var dayLabels = svg.selectAll(".dayLabel")
          .data(days)
          .enter().append("text")
            .text(function (d) { return d; })
            .attr("x", gap)
            .attr("y", function (d, i) { return gap + i * gridSize; })
            .style("text-anchor", "end")
            .attr("transform", "translate(-6," + gridSize / 1.5 + ")")
            .attr("class", function (d, i) { return ((i >= 0 && i <= 4) ? "dayLabel mono axis axis-workweek" : "dayLabel mono axis"); });

      var timeLabels = svg.selectAll(".timeLabel")
          .data(times)
          .enter().append("text")
            .text(function(d) { return d; })
            .attr("x", function(d, i) { return gap + i * gridSize; })
            .attr("y", gap)
            .style("text-anchor", "middle")
            .attr("transform", "translate(" + gridSize / 2 + ", -6)")
            .attr("class", function(d, i) { return ((i >= 7 && i <= 16) ? "timeLabel mono axis axis-worktime" : "timeLabel mono axis"); });

      var hours = svg.selectAll(".hour").data(sample).enter().append("g").attr("transform",function(d,i){return "translate(" + gap + "," + (gap + i * gridSize) + ")"});
      var grids = hours.selectAll("rect").data(function(d){return d;}).enter().append("rect")
              .attr("x", function(d,i) { return i * gridSize; })
              //.attr("y", function(d,i) { console.log(d); return gap + i * gridSize; })
              .attr("rx", 4)
              .attr("ry", 4)
              .attr("class", "hour bordered")
              .attr("width", gridSize)
              .attr("height", gridSize)
              .style("fill", function(d){ 
              	return colorscale((d * 60))});
      
      var colorrange = svg.append("g").selectAll(".rect")
            .data(colorforscale)
            .enter()
            .append("rect")
            .attr("x", function(d, i) { return gap + legendElementWidth * i; })
            .attr("y", height - 25)
            .attr("width", legendElementWidth)
            .attr("height", gridSize / 2)
            .style("fill", function(d, i) { return d; });

      var colortext = svg.append("g").attr("transform","translate(" + gap + "," + (height - 10) + ")").selectAll(".mono").data(colorforscale).enter().append("text")
            .attr("class", "mono")
            .text(function(d,i) { return  distancesclae(i); })
            .attr("x", function(d, i) { return  legendElementWidth * i; })
            //.attr("y", height - 10)
            .style("fill","black");

      //add close button on the right-top corner of heatmap
      var closebutton = svg.append("g").attr("id","close").on("click", function(d){return d3.select("#heatmap").remove();});
      var close = closebutton.append("circle").attr("id","close").attr("cx",width + margin.left).attr("cy",20).attr("r",10).style("fill","grey").style("opacity",0.9);
      var closex = closebutton.append("text").attr("id","closex").attr("x",width + margin.left - 4).attr("y",25).text("X").style("fill","white");
      var name = closebutton.append("text").attr("id","name").attr("x",margin.left - 4).attr("y",25).text(object['name']).style("fill","black");

}
//var svg = d3.select(map.getPanes().overlayPane).append("svg").attr("id","main-svg").attr("class","main-svg").style("width","100%");

/*for(var i = 0; i < pois.length; i++){
  var curr = pois[i];
  var circle = L.circleMarker([curr[0], curr[1]], 10, {
    color: 'red',
    fillColor: '#f03',
    fillOpacity: 0.5
  }).addTo(map).on("click",function(e){
     if(d3.select("svg")[0][0] != null){
        d3.select("svg").remove();
     }
     var svg = d3.select(map.getPanes().overlayPane).append("svg").attr("id","main-svg").attr("class","svg").style("width",300).style("height",300);
  });
}*/

/*var food = pois.filter(function(d){return d[2].indexOf('美食') != -1;});
	var beauty = pois.filter(function(d){return d[2].indexOf('丽人') != -1;});
	var sport = pois.filter(function(d){return d[2].indexOf('运动') != -1;});
	var health = pois.filter(function(d){return d[2].indexOf('医疗') != -1;});
	var car = pois.filter(function(d){return d[2].indexOf('汽车') != -1;});
	var entertainment = pois.filter(function(d){return d[2].indexOf('休闲') != -1;});
	var shopping = pois.filter(function(d){return d[2].indexOf('购物') != -1;});
	var company = pois.filter(function(d){return d[2].indexOf('公司') != -1;});
	var government = pois.filter(function(d){return d[2].indexOf('政府') != -1;});
	var building = pois.filter(function(d){return d[2].indexOf('房地产') != -1;});
	var life = pois.filter(function(d){return d[2].indexOf('生活') != -1;});
	var transport = pois.filter(function(d){return d[2].indexOf('交通') != -1;});
	var education = pois.filter(function(d){return d[2].indexOf('教育') != -1;});
	var fianical = pois.filter(function(d){return d[2].indexOf('金融') != -1;});
	var travel = pois.filter(function(d){return d[2].indexOf('旅游') != -1;});
	var culture = pois.filter(function(d){return d[2].indexOf('文化') != -1;});
	var hotel = pois.filter(function(d){return d[2].indexOf('宾馆') != -1;});
	var nature = pois.filter(function(d){return d[2].indexOf('自然') != -1;});*/