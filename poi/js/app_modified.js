   var dataset;
   var map;
   var colors = ["#a50026","#f46d43","#fee08b","#d9ef8b","#66bd63","#1a9850","#006837"];
  var colorscale = d3.scale.quantile().domain([0,120]).range(colors);
function drawRoadNetwork(mymap){
map = mymap;

//var colorscale = d3.scale.linear().domain([0,120]).range(["red","blue"]);
d3.json("data/OneMonth_201101_1hour_WithWeekdaySpeeds.json", function(error,data){

  dataset = data;

  d3.select("#timerange").append("select").attr("id","menu").selectAll("option").data(dataset).enter().append("option").attr("value",function(d,i){return i;}).text(function(d){return d.time});

  d3.select("#menu").on("change", function(){
    var timeUnit = eval(d3.select(this).property("selectedIndex"));
    changeLayer(timeUnit,dataset,filternetwork);
  });
  
  d3.select("#colors").append("svg").attr("height","100%").selectAll("rect").data(colors).enter().append("rect").attr("width","30px").attr("height","20px").attr("x", function(d,i){return 30 * i}).attr("y",0).style("fill",function(d){return d;})

  d3.select("#colors").select("svg").selectAll("text").data(colors).enter().append("text").attr("x", function(d,i){return 30 * i;}).attr("y",25).text(function(d,i){
    return showColorText(0,i,dataset);
  }).style("font-size","12px")

  var filternetwork = L.geoJson(roadnetwork, {
        
        filter: function (feature, layer) {
          if (feature.properties) {
            // If the property "underConstruction" exists and is true, return false (don't render features under construction)
            var id = feature.properties.partitionID;
            if(dataset[0].nodes[id]){//id exists in our dataset
              feature.properties.speed = dataset[0].nodes[id].speed;
              feature.properties.flow = dataset[0].nodes[id].flow;
              feature.properties.travelTime = dataset[0].nodes[id].travelTime;
              feature.properties.distance = dataset[0].nodes[id].distance;
              feature.properties.SD = dataset[0].nodes[id].SD;
              feature.properties.RSDwidth = dataset[0].nodes[id].RSDwidth;
            }
            return dataset[0].nodes[id] ? true : false;
          }
          return false;
        },
        style: function(feature) {
          return  assignColor(feature,dataset[0].maxSpeed,dataset[0].minSpeed);  
          },
        onEachFeature: onEachFeature
      }).addTo(map);
  
});//d3.json end

}
function showColorText(dataindex, i,dataset){
  var sdRange = dataset[dataindex].maxSpeed - dataset[dataindex].minSpeed;
  if(i == 0){
    return  0;
  }else if(i == 1){
    return   10 ;
  }else if(i == 2){
    return   25;
  }else if(i == 3){
    return  50;
  }else if(i == 4){
    return   75;
  }else if(i == 5){
    return   90;
  }else{
    return  115;
  }
  /*if(i == 0){
    return parseInt(dataset[dataindex].minSpeed) + "-" + parseInt(((1/ 6) * sdRange +  dataset[dataindex].minSpeed));
  }else if(i == 1){
    return parseInt(((1/ 6) * sdRange +  dataset[dataindex].minSpeed)) + " - " +  parseInt(((1/ 3) * sdRange +  dataset[dataindex].minSpeed));
  }else if(i == 2){
    return parseInt(((1/ 3) * sdRange +  dataset[dataindex].minSpeed)) + " - " +  parseInt(((1/ 2) * sdRange +  dataset[dataindex].minSpeed));
  }else if(i == 3){
    return parseInt(((1/ 2) * sdRange +  dataset[dataindex].minSpeed)) + " - " +  parseInt(((2/ 3) * sdRange +  dataset[dataindex].minSpeed));
  }else if(i == 4){
    return parseInt(((2/ 3) * sdRange +  dataset[dataindex].minSpeed)) + " - " +  parseInt(((5/ 6) * sdRange +  dataset[dataindex].minSpeed));
  }else if(i == 5){
    return parseInt(((5/ 6) * sdRange +  dataset[dataindex].minSpeed)) + " - " +   parseInt(dataset[dataindex].maxSpeed);
  }else{
    return " > " + parseInt(dataset[dataindex].maxSpeed);
  }*/
}
function changeLayer(index,dataset,filternetwork){
  map.removeLayer(filternetwork);
  d3.select("#colors").select("svg").selectAll("text").text(function(d,i){
    return showColorText(index,i,dataset);
  })
    filternetwork = L.geoJson(roadnetwork, {
      
      filter: function (feature, layer) {
        if (feature.properties) {
          // If the property "underConstruction" exists and is true, return false (don't render features under construction)
          var id = feature.properties.partitionID;
          if(dataset[index].nodes[id]){//id exists in our dataset
            feature.properties.speed = dataset[index].nodes[id].speed;
            feature.properties.flow = dataset[index].nodes[id].flow;
            feature.properties.travelTime = dataset[index].nodes[id].travelTime;
            feature.properties.distance = dataset[index].nodes[id].distance;
            feature.properties.SD = dataset[index].nodes[id].SD;
            feature.properties.RSDwidth = dataset[index].nodes[id].RSDwidth;
          }
          return dataset[index].nodes[id] ? true : false;
        }
        return false;
      },
      style: function(feature) {
        var id = feature.properties.partitionID;
        return assignColor(feature,dataset[index].maxSpeed,dataset[index].minSpeed);          
        },
      onEachFeature: onEachFeature
    }).addTo(map);
  
}

function assignColor(feature,maxSpeed,minSpeed){
        var sdRange = maxSpeed - minSpeed;
        var opacityvalue = 0.8;
        if(feature.properties.speed >= 0){
          return {color: colorscale(feature.properties.speed),weight: feature.properties.RSDwidth,opacity: opacityvalue};
          /*if(feature.properties.speed >= 0 && feature.properties.speed < 10){
            return {color: "#a50026", weight: feature.properties.RSDwidth,opacity: opacityvalue};
          }else if(feature.properties.speed >= 10 && feature.properties.speed < 25){
            return {color: "#f46d43", weight: feature.properties.RSDwidth  ,opacity: opacityvalue};
          }else if(feature.properties.speed >= 25  && feature.properties.speed < 50 ){
            return {color: "#fee08b", weight: feature.properties.RSDwidth ,opacity: opacityvalue};
          }else if(feature.properties.speed >= 50 && feature.properties.speed < 75 ){
            return {color: "#d9ef8b", weight: feature.properties.RSDwidth ,opacity: opacityvalue};
          }else if(feature.properties.speed >= 75 && feature.properties.speed < 90 ){
            return {color: "#66bd63", weight:feature.properties.RSDwidth ,opacity: opacityvalue};
          }else if(feature.properties.speed >= 90 && feature.properties.speed < 115) {
            return {color: "#1a9850", weight: feature.properties.RSDwidth ,opacity: opacityvalue};
          }else if(feature.properties.speed >=  115 ){
            return {color: "#006837", weight: feature.properties.RSDwidth ,opacity: opacityvalue};
          }*/
        }else{
          //console.log(feature.properties.speed);
        }
}
var clickedID;
function onEachFeature(feature, layer) {
      var popupContent = "<p>Road ID : " +
          feature.properties.partitionID + " <br>Speed : "+ feature.properties.speed +  " <br>SD : "+ feature.properties.SD +   " <br> RSD : "+ feature.properties.RSDwidth +  " <br> Flow : "+ feature.properties.flow +"</p>";
          layer.on("click",function(e){
            graphDataProcess(dataset,feature.properties.partitionID);
          })
      
      layer.bindPopup(popupContent);
}       
         


//draw graph
function addAxesAndLegend (svg, xAxis, yAxis, margin, chartWidth, chartHeight,exists) {
  var legendWidth  = 100,
      legendHeight = 100;

  // clipping to make sure nothing appears behind legend
  /*svg.append('clipPath')
    .attr('id', 'axes-clip')
    .append('polygon')
      .attr('points', (-margin.left)                 + ',' + (-margin.top)                 + ' ' +
                      (chartWidth - legendWidth - 1) + ',' + (-margin.top)                 + ' ' +
                      (chartWidth - legendWidth - 1) + ',' + legendHeight                  + ' ' +
                      (chartWidth + margin.right)    + ',' + legendHeight                  + ' ' +
                      (chartWidth + margin.right)    + ',' + (chartHeight + margin.bottom) + ' ' +
                      (-margin.left)                 + ',' + (chartHeight + margin.bottom));*/
  if(!exists){
      var axes = svg.append('g');
    //.attr('clip-path', 'url(#axes-clip)');

      axes.append('g')
        .attr('class', 'x axis')
        .attr('transform', 'translate(0,' + chartHeight + ')')
        .call(xAxis);

      axes.append('g')
        .attr('class', 'y axis')
        .call(yAxis)
        .append('text')
          .attr('transform', 'rotate(-90)')
          .attr('y', 6)
          .attr('dy', '.71em')
          .style('text-anchor', 'end')
          .text('Speed');
  }else{
    svg.selectAll(".x axis").call(xAxis);
    svg.selectAll(".y axis").call(yAxis);
  }
  

  var legend = svg.append('g')
    .attr('class', 'legend')
    .attr('transform', 'translate(' + (chartWidth - legendWidth) + ', 0)');

  /*legend.append('rect')
    .attr('class', 'legend-bg')
    .attr('width',  legendWidth)
    .attr('height', legendHeight);*/

  legend.append('rect')
    .attr('class', 'outer')
    .attr('width',  75)
    .attr('height', 10)
    .attr('x', 10)
    .attr('y', 10);

  legend.append('text')
    .attr('x', 110)
    .attr('y', 25)
    .style("fill","black")
    .text('Speed');

  legend.append('rect')
    .attr('class', 'inner')

    .attr('width',  75)
    .attr('height', 10)
    .attr('x', 10)
    .attr('y', 45);

  legend.append('text')
    .attr('x', 110)
    .attr('y', 55)
    .text('SD')
    .style("fill","black");

  legend.append('path')
    .attr('class', 'median-line')
    .attr('d', 'M10,80L85,80');

  legend.append('text')
    .attr('x', 110)
    .attr('y', 85)
    .text('Average Speed')
    .style("fill","black");
}

function drawPaths (svg, data, x, y, exists) {
  svg.datum(data);
  var upperOuterArea = d3.svg.area()
    .interpolate('basis')
    .x (function (d,i) { return x(i) || 1; })//x(d.date)
    .y0(function (d) { return y(d.maxSpeed); })
    .y1(function (d) { return y(d.highSD); });

  var upperInnerArea = d3.svg.area()
    .interpolate('basis')
    .x (function (d,i) { return x(i) || 1; })
    .y0(function (d) { return y(d.highSD); })
    .y1(function (d) { return y(d.speed); });

  var medianLine = d3.svg.line()
    .interpolate('basis')
    .x(function (d,i) { return x(i) || 1;  })
    .y(function (d) { return y(d.speed); });

  var lowerInnerArea = d3.svg.area()
    .interpolate('basis')
    .x (function (d,i) { return x(i) || 1;  })
    .y0(function (d) { return y(d.speed); })
    .y1(function (d) { return y(d.lowSD); });

  var lowerOuterArea = d3.svg.area()
    .interpolate('basis')
    .x (function (d,i) { return x(i) || 1;  })
    .y0(function (d) { return y(d.lowSD); })
    .y1(function (d) { return y(d.minSpeed); });

  
  if(!exists){//svg not exists
       svg.append('path')
        .attr('class', 'area upper outer')
        .attr('d', upperOuterArea)
        .attr('clip-path', 'url(#rect-clip)');

      svg.append('path')
        .attr('class', 'area lower outer')
        .attr('d', lowerOuterArea)
        .attr('clip-path', 'url(#rect-clip)');

      svg.append('path')
        .attr('class', 'area upper inner')
        .attr('d', upperInnerArea)
        .attr('clip-path', 'url(#rect-clip)');

      svg.append('path')
        .attr('class', 'area lower inner')
        .attr('d', lowerInnerArea)
        .attr('clip-path', 'url(#rect-clip)');

      svg.append('path')
        .attr('class', 'median-line')
        .attr('d', medianLine)
        .attr('clip-path', 'url(#rect-clip)');
  }else{
       svg.selectAll('.area.upper.outer')
        //.attr('class', 'area upper outer')
        .attr('d', upperOuterArea)
        //.attr('clip-path', 'url(#rect-clip)');

      svg.selectAll('.area.lower.outer')
        //.attr('class', 'area lower outer')
        .attr('d', lowerOuterArea)
        //.attr('clip-path', 'url(#rect-clip)');

      svg.selectAll('.area.upper.inner')
        //.attr('class', 'area upper inner')
        .attr('d', upperInnerArea)
        //.attr('clip-path', 'url(#rect-clip)');

      svg.selectAll('.area.lower.inner')
        //.attr('class', 'area lower inner')
        .attr('d', lowerInnerArea)
        //.attr('clip-path', 'url(#rect-clip)');

      svg.selectAll('.median-line')
        //.attr('class', 'median-line')
        .attr('d', medianLine)
        //.attr('clip-path', 'url(#rect-clip)');
      }
 
}

function addMarker (marker, svg, chartHeight, x) {
  var radius = 32,
      xPos = x(marker.date) - radius - 3,
      yPosStart = chartHeight - radius - 3,
      yPosEnd = (marker.type === 'Client' ? 80 : 160) + radius - 3;

  var markerG = svg.append('g')
    .attr('class', 'marker '+marker.type.toLowerCase())
    .attr('transform', 'translate(' + xPos + ', ' + yPosStart + ')')
    .attr('opacity', 0);

  markerG.transition()
    .duration(1000)
    .attr('transform', 'translate(' + xPos + ', ' + yPosEnd + ')')
    .attr('opacity', 1);

  markerG.append('path')
    .attr('d', 'M' + radius + ',' + (chartHeight-yPosStart) + 'L' + radius + ',' + (chartHeight-yPosStart))
    .transition()
      .duration(1000)
      .attr('d', 'M' + radius + ',' + (chartHeight-yPosEnd) + 'L' + radius + ',' + (radius*2));

  markerG.append('circle')
    .attr('class', 'marker-bg')
    .attr('cx', radius)
    .attr('cy', radius)
    .attr('r', radius);

  markerG.append('text')
    .attr('x', radius)
    .attr('y', radius*0.9)
    .text(marker.type);

  markerG.append('text')
    .attr('x', radius)
    .attr('y', radius*1.5)
    .text(marker.version);
}

function startTransitions (svg, chartWidth, chartHeight, rectClip, markers, x) {
  rectClip.transition()
    .duration(1000*markers.length)
    .attr('width', chartWidth);

  markers.forEach(function (marker, i) {
    setTimeout(function () {
      addMarker(marker, svg, chartHeight, x);
    }, 1000 + 500*i);
  });
}

function makeChart (data) {
  var svgWidth  = d3.select("#graph").node().getBoundingClientRect().width,
      svgHeight = d3.select("#graph").node().getBoundingClientRect().height,
      margin = { top: 2, right: 30, bottom: 30, left: 35 },
      chartWidth  = svgWidth  - margin.left - margin.right,
      chartHeight = svgHeight - margin.top  - margin.bottom;
  //original
  /*var x = d3.time.scale().range([0, chartWidth])
            .domain(d3.extent(data, function (d) { return d.date; })),*/
  //var hours = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24];
    var x = d3.scale.linear().range([0, chartWidth])
            .domain([0,23]),
      y = d3.scale.linear().range([chartHeight, 0])
            .domain([ d3.min(data, function (d) { return d.minSpeed; }), d3.max(data, function (d) { return d.maxSpeed; })]);

  var xAxis = d3.svg.axis().scale(x).orient('bottom')
                .innerTickSize(-chartHeight).outerTickSize(0).tickPadding(10).ticks(24),
      yAxis = d3.svg.axis().scale(y).orient('left')
                .innerTickSize(-chartWidth).outerTickSize(0).tickPadding(10);

  var exists = false;
  if(d3.select("#graph").select("svg")[0][0] == null || d3.select("#graph").select("svg")[0][0] == undefined){
    }else{
      d3.select("#graph").select("svg").remove();
      //exists = true;
    }

    var svg = d3.select('#graph').append('svg')
      .attr('width',  svgWidth)
      .attr('height', svgHeight)
      .append('g')
      .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');
      //exists = false;

  // clipping to start chart hidden and slide it in later
  /*var rectClip = svg.append('clipPath')
    .attr('id', 'rect-clip')
    .append('rect')
      .attr('width', 0)
      .attr('height', chartHeight);*/

  addAxesAndLegend(svg, xAxis, yAxis, margin, chartWidth, chartHeight,exists);
  drawPaths(svg, data, x, y,exists);
  //startTransitions(svg, chartWidth, chartHeight, rectClip, markers, x);
}

//data processing for onclick event
var data;
function graphDataProcess(dataset, roadID){

  //for hour
      var graphdataset = [];
      var themeriverdataset = [];
      var numberoflayer = 7;
      var days = ["Sunday","Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
      for(var i = 0; i < numberoflayer; i++){
        themeriverdataset.push({"name":roadID, "values":[]});
      }
      dataset.forEach(function(data,index){
        if(data.nodes[roadID]){
          var temp = data.nodes[roadID];
          var weekdaySpeeds = temp.weekdaySpeeds;
          var tempdataset = [];
          weekdaySpeeds.forEach(function(d,i){
             themeriverdataset[i].name = days[i];
             themeriverdataset[i].values.push({"x":index, "y": d});
          })
          //themeriverdataset.push(tempdataset);
          graphdataset.push({"date": data.time, "minSpeed": temp.minSpeed, "lowSD" : (temp.speed - temp.SD),"speed" : temp.speed, "highSD" : (temp.speed + temp.SD),"maxSpeed" : temp.maxSpeed,"flow" : temp.flow})
        }
      });
      //console.log(themeriverdataset);
      data = graphdataset;
     
      makeChart(data);

      makeThemeriver(themeriverdataset,graphdataset);


  //for day

}
var parseDate  = d3.time.format('%Y-%m-%d').parse;
/*d3.json('OneMonth_201101_1hour.json', function (error, rawData) {
  if (error) {
    console.error(error);
    return;
  }

  var data = rawData.map(function (d) {
    return {
      date:  d.time
      pct05: d.pct05 / 1000,
      pct25: d.pct25 / 1000,
      pct50: d.pct50 / 1000,
      pct75: d.pct75 / 1000,
      pct95: d.pct95 / 1000
    };
  });*/

  /*d3.json('markers.json', function (error, markerData) {
    if (error) {
      console.error(error);
      return;
    }

    var markers = markerData.map(function (marker) {
      return {
        date: parseDate(marker.date),
        type: marker.type,
        version: marker.version
      };
    });

    makeChart(data, markers);
  });
});*/
