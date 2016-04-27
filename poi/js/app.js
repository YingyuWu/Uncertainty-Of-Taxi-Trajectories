function addAxesAndLegend (svg, xAxis, yAxis, margin, chartWidth, chartHeight,exists) {
  var legendWidth  = 200,
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
  

  /*var legend = svg.append('g')
    .attr('class', 'legend')
    .attr('transform', 'translate(' + (chartWidth - legendWidth) + ', 0)');

  legend.append('rect')
    .attr('class', 'legend-bg')
    .attr('width',  legendWidth)
    .attr('height', legendHeight);

  legend.append('rect')
    .attr('class', 'outer')
    .attr('width',  75)
    .attr('height', 20)
    .attr('x', 10)
    .attr('y', 10);

  legend.append('text')
    .attr('x', 115)
    .attr('y', 25)
    .text('5% - 95%');

  legend.append('rect')
    .attr('class', 'inner')
    .attr('width',  75)
    .attr('height', 20)
    .attr('x', 10)
    .attr('y', 40);

  legend.append('text')
    .attr('x', 115)
    .attr('y', 55)
    .text('25% - 75%');

  legend.append('path')
    .attr('class', 'median-line')
    .attr('d', 'M10,80L85,80');

  legend.append('text')
    .attr('x', 115)
    .attr('y', 85)
    .text('Median');*/
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
                .innerTickSize(-chartHeight).outerTickSize(0).tickPadding(10),
      yAxis = d3.svg.axis().scale(y).orient('left')
                .innerTickSize(-chartWidth).outerTickSize(0).tickPadding(10);

  var exists = false;
  if(d3.select("#graph").select("svg")[0][0] == null || d3.select("#graph").select("svg")[0][0] == undefined){
    var svg = d3.select('#graph').append('svg')
      .attr('width',  svgWidth)
      .attr('height', svgHeight)
      .append('g')
      .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');
      exists = false;
    }else{
      var svg = d3.select("#graph").select("svg");
      exists = true;
    }

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
      dataset.forEach(function(data){
        if(data.nodes[roadID]){
          var temp = data.nodes[roadID];
          graphdataset.push({"date": data.time, "minSpeed": temp.minSpeed, "lowSD" : (temp.speed - temp.SD),"speed" : temp.speed, "highSD" : (temp.speed + temp.SD),"maxSpeed" : temp.maxSpeed,"flow" : temp.flow})
        }
      })
      console.log(graphdataset);
      data = graphdataset;
     
        makeChart(data);

      


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
