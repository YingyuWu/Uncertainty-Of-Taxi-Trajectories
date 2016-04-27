 
function makeThemeriver(mapdata,graphdataset){
  if(d3.select("#themeriver").select("svg")[0][0] == null || d3.select("#themeriver").select("svg")[0][0] == undefined){
    }else{
      d3.select("#themeriver").select("svg").remove();
      //exists = true;
    }
var n = 7, // number of layers
    m = 24, // number of samples per layer
    margin = { top: 2, right: 30, bottom:40, left: 35 },
    stack = d3.layout.stack().offset("wiggle").values(function(d){return d.values;}),
   // y =  d3.scale.linear().range([height - margin.bottom, 0])
            //.domain([ d3.min(mapdata, function(d){return d3.min(d.values,function(g){return ( g.y);})}), d3.max(mapdata, function(d){return d3.max(d.values,function(g){return (g.y);})})]),
    layers0 = stack(mapdata);
    //layers1 = stack(mapdata);
var svgWidth  = d3.select("#themeriver").node().getBoundingClientRect().width,
      svgHeight = d3.select("#themeriver").node().getBoundingClientRect().height;
var width  = d3.select("#themeriver").node().getBoundingClientRect().width  - margin.left - margin.right,
      height = d3.select("#themeriver").node().getBoundingClientRect().height- margin.top  - margin.bottom;

var c20b = d3.scale.category20b();
var xscale = d3.scale.linear().range([0, width])
            .domain([0,23]),

    yscale = d3.scale.linear().range([height, 0])
            .domain([ d3.min(layers0, function(d){return d3.min(d.values,function(g){return (g.y0 + g.y);})}), d3.max(layers0, function(d){return d3.max(d.values,function(g){return (g.y0 + g.y);})})]);
/*var x = d3.scale.linear()
    .domain([0, m - 1])
    .range([0, width - 100]);

var y = d3.scale.linear()
    .domain([0, max])
    .range([height, 0]);*/
    
var xAxis = d3.svg.axis().scale(xscale).orient('bottom')
                .innerTickSize(-height).outerTickSize(0).tickPadding(10).ticks(24),
      yAxis = d3.svg.axis().scale(yscale).orient('left')
                .innerTickSize(-width).outerTickSize(0).tickPadding(7);// 7 days a week
var color = d3.scale.linear()
    .range(["#aad", "#556"]);

var area = d3.svg.area()
    .interpolate("cardinal")
    .x(function(d) { return xscale(d.x); })
    .y0(function(d) { if(yscale(d.y0) < 0){console.log(d.y0);} return yscale(d.y0); })
    .y1(function(d) {  if(yscale(d.y0 + d.y) < 0){console.log(d.y0);}return yscale(d.y0 + d.y); });

var svg = d3.select("#themeriver").append("svg")
    .attr("width", svgWidth)
    .attr("height", svgHeight)
    .append("g")
    .attr("id","path")
    .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');
var axes = d3.select("#themeriver").select("svg").append('g').attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');;
    //.attr('clip-path', 'url(#axes-clip)');

  axes.append('g')
        .attr('class', 'x axis')
        .attr('transform', 'translate(0,' + (height + margin.bottom) + ')')
        .call(xAxis)
        .append('text')
          .attr('transform', 'rotate(-90)')
          .attr('y', 6)
          .attr('dy', '.51em')
          .style('text-anchor', 'end')
          .text(function(d,i){return i});

  /*axes.append('g')
        .attr('class', 'y axis')
        .call(yAxis)
        .append('text')
          .attr('transform', 'rotate(-90)')
          .attr('y', 6)
          .attr('dy', '.51em')
          .style('text-anchor', 'end')
          .text('Speed');*/


svg.selectAll("path")
    .data(layers0)
    .enter().append("path")
    .attr("d", function(d){
      return area(d.values)}
      )
    //.attr("id",function(d){return d.title})
    .style("fill", function(d,i) { return c20b(i); })
    .append("title")
    .text(function(d) { console.log(d);return d.name; })


  /*svg.selectAll("circle")
  .data(category)
  .enter()
  .append("circle")
  .attr("cx", width - 90)
  .attr("cy",function(d,i){return i * 20 + 50})
  .attr("r",10)
  .style("fill",function(d,i){return c20b(i)});

  svg.selectAll("text")
  .data(category)
  .enter()
  .append("text")
  .attr("x",width - 80)
  .attr("y",function(d,i){return i  * 20 + 50})
  .attr("font-size",10)
  .text(function(d){return d})*/


}




