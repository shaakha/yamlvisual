#!/usr/bin/env python
# -*- coding: utf-8 -*-

from pprint import pprint
import collections
import errno
import json
import yaml
import sys
import os

from settings import config


# https://stackoverflow.com/a/16029908/1079836
def mkdirp(path):
  if path and path != "":
    try:
      os.makedirs(path)
    except OSError as exc:
      if exc.errno == errno.EEXIST and os.path.isdir(path):
        pass
      else:
        raise

# https://stackoverflow.com/a/44858562/1079836
class stack:
  def __init__(self):
    self.items=[]
  def isEmpty(self):
    return self.items==[]
  def push(self, item):
    self.items.append(item)
  def pop(self):
    return self.items.pop()
  def size(self):
    return len(self.items)
  def peek(self):
    return self.items[-1]
  def show(self):
    return self.items


class yamlvisual:
  def __init__(self, filepath):
    if os.path.isfile(filepath):
      self.filepath = filepath
      self.verbose = config["verbose"]
      self.isqlysyaml = config["isqlysyaml"]
      self.groupchildren = config["groupchildren"]
      self.collapsecount = config["collapsecount"]
      self.saveyamldict = config["saveyamldict"]
      self.content = config["content"]
      self.yamldict = config["yamldict"]
      self.d3dict = config["d3dict"]
      self.error = config["error"]
      self.dummyroot = config["dummyroot"]
      self.modecompact = config["modecompact"]
      self.basereportsdir = "%s/reports" % (os.getcwd())
      self.currentreportsdir = "%s/%s" % (self.basereportsdir, self.filepath.split("/")[-1])
      mkdirp(self.currentreportsdir)
      self.yamljsonpath = "%s/yaml.json" % (self.currentreportsdir)
      self.yamld3jsonpath = "%s/yamld3.json" % (self.currentreportsdir)
      self.htmlplainpath = "%s/yamlplain.html" % (self.currentreportsdir)
      self.htmlzoompath = "%s/yamlzoom.html" % (self.currentreportsdir)
      self.operators = stack()
      self.opids = stack()
      self.ignorelist = []
    else:
      self.error = "no such file: %s" % (filepath)

  def yaml_to_dict(self):
    try:
      self.yamldict = yaml.load(open(self.filepath))
    except:
      return self
    if self.yamldict and self.saveyamldict:
      with open(self.yamljsonpath, "w") as fo:
        json.dump(self.yamldict, fo)
    return self

  def create_tree(self, intree, outtree, grouptree):
    if isinstance(intree, dict):
      for key, value in dict(intree).iteritems():
        if isinstance(value, dict):
          tmpnode = dict({
            "name": str(key),
            "children": list(),
            "size": len(value)
          })
          self.create_tree(value, tmpnode["children"], tmpnode)
          outtree.append(tmpnode)
        elif isinstance(value, list):
          tmpnode = dict({
            "name": str(key),
            "children": list(),
            "size": len(value)
          })
          self.create_tree(value, tmpnode["children"], tmpnode)
          outtree.append(tmpnode)
        else:
          if key not in self.ignorelist:
            if self.modecompact:
              outtree.append({"name": "%s: %s" % (key, value), "size": 1})
            else:
              outtree.append({"name": str(key), "children": list([{"name": str(value)}]), "size": 1})
    elif isinstance(intree, list):
      for item in intree:
        outtree.append({
          "name": item
        })
    return self

  def dict_to_d3(self):
    if self.yamldict:
      try:
        self.d3dict = dict({
          "name": "ROOT",
          "children": list(),
          "size": 0
        })
        self.create_tree(self.yamldict, self.d3dict["children"], self.d3dict)
        if not self.dummyroot:
          self.d3dict = self.d3dict["children"][0]
        self.d3dict["size"] = len(self.d3dict["children"])
        if self.d3dict:
          with open(self.yamld3jsonpath, "w") as fo:
            json.dump(self.d3dict, fo)
      except:
        import traceback
        traceback.print_exc()
    return self

  def create_html(self):
    htmlzoomcontent = """<!doctype html><meta charset=utf-8><link href="http://fonts.googleapis.com/css?family=Rosario:400,700"rel=stylesheet><style>body{font-family:Rosario,sans-serif}.node{cursor:pointer}.node circle{fill:#fff;stroke:#4682b4;stroke-width:1px}.node text{font-size:18px;font-weight:700}.link{fill:none;stroke:#ccc;stroke-width:2px}.templink{fill:none;stroke:red;stroke-width:3px}.ghostCircle.show{display:block}.activeDrag .ghostCircle,.ghostCircle{display:none}</style><script src=../../assets/jquery-1.10.2.min.js></script><script src=../../assets/d3.v3.min.js></script><script src=../../assets/sha256.min.js></script><script src=../../assets/color-hash.js></script><script>treeJSON=d3.json("yamld3.json",function(t,e){function r(t,e){var n=f;panTimer&&(clearTimeout(panTimer),translateCoords=d3.transform(E.attr("transform")),"left"==e||"right"==e?(translateX="left"==e?translateCoords.translate[0]+n:translateCoords.translate[0]-n,translateY=translateCoords.translate[1]):("up"==e||"down"==e)&&(translateX=translateCoords.translate[0],translateY="up"==e?translateCoords.translate[1]+n:translateCoords.translate[1]-n),scaleX=translateCoords.scale[0],scaleY=translateCoords.scale[1],scale=k.scale(),E.transition().attr("transform","translate("+translateX+","+translateY+")scale("+scale+")"),d3.select(t).select("g.node").attr("transform","translate("+translateX+","+translateY+")"),k.scale(k.scale()),k.translate([translateX,translateY]),panTimer=setTimeout(function(){r(t,n)},50))}function n(t){scale=k.scale(),x=-t.y0,y=-t.x0,x=x*scale+m/2,y=y*scale+v/2,d3.select("g").transition().duration(g).attr("transform","translate("+x+","+y+")scale("+scale+")"),k.scale(scale),k.translate([x,y])}function c(t){var e;d3.event.defaultPrevented||((e=t).children?(e._children=e.children,e.children=null):e._children&&(e.children=e._children,e._children=null),l(t=e),n(t))}function a(t){return Array.from(t,function(t){return("0"+(255&t).toString(10)).slice(-2)}).join("")}function d(t){return console.log(t,a(sha256(t))),a(sha256(t))}function l(n){var r=[1],a=function(e,t){t.children&&0<t.children.length&&(r.length<=e+1&&r.push(0),r[e+1]+=t.children.length,t.children.forEach(function(t){a(e+1,t)}))};a(0,u);var t=25*d3.max(r),e=(p=p.size([t,m])).nodes(u).reverse(),l=p.links(e);e.forEach(function(t){t.y=300*t.depth}),node=E.selectAll("g.node").data(e,function(t){return t.id||(t.id=++h)});var o=node.enter().append("g").call(dragListener).attr("class","node").attr("transform",function(t){return"translate("+n.y0+","+n.x0+")"}).on("click",c);o.append("circle").attr("class","nodeCircle").attr("r",0).style("fill",function(t){return t._children?"lightsteelblue":"#fff"}),o.append("text").attr("x",function(t){return t.children||t._children?-10:10}).attr("dy",".35em").attr("class","nodeText").attr("text-anchor",function(t){return t.children||t._children?"end":"start"}).text(function(t){return t.name}).style("fill-opacity",0),o.append("circle").attr("class","ghostCircle").attr("r",30).attr("opacity",.2).style("fill","red").attr("pointer-events","mouseover").on("mouseover",function(t){w(t)}).on("mouseout",function(t){_(t)}),node.select("text").attr("x",function(t){return t.children||t._children?-10:10}).attr("text-anchor",function(t){return t.children||t._children?"end":"start"}).text(function(t){return t.name}),node.select("circle.nodeCircle").attr("r",1*n.size).style("fill",function(t){return t._children?"white":new ColorHash({hash:d,lightness:.75,saturation:.65}).hex(t.name)}),node.transition().duration(g).attr("transform",function(t){return"translate("+t.y+","+t.x+")"}).select("text").style("fill-opacity",1);var s=node.exit().transition().duration(g).attr("transform",function(t){return"translate("+n.y+","+n.x+")"}).remove();s.select("circle").attr("r",0),s.select("text").style("fill-opacity",0);var i=E.selectAll("path.link").data(l,function(t){return t.target.id});i.enter().insert("path","g").attr("class","link").attr("d",function(t){var e={x:n.x0,y:n.y0};return C({source:e,target:e})}),i.transition().duration(g).attr("d",C),i.exit().transition().duration(g).attr("d",function(t){var e={x:n.x,y:n.y};return C({source:e,target:e})}).remove(),e.forEach(function(t){t.x0=t.x,t.y0=t.y})}var u,o=0,s=null,i=null,f=200,h=0,g=750,m=.99*$(document).width(),v=.96*$(document).height(),p=d3.layout.tree().size([v,m]),C=d3.svg.diagonal().projection(function(t){return[t.y,t.x]});(function t(e,n,r){if(e){n(e);var a=r(e);if(a)for(var l=a.length,o=0;o<l;o++)t(a[o],n,r)}})(e,function(t){o=Math.max(t.name.length,o)},function(t){return t.children&&0<t.children.length?t.children:null}),p.sort(function(t,e){return console.log(e),e.name.toLowerCase()<t.name.toLowerCase()?1:-1});var k=d3.behavior.zoom().scaleExtent([.1,3]).on("zoom",function(){E.attr("transform","translate("+d3.event.translate+")scale("+d3.event.scale+")")}),T=d3.select("#d3container").append("svg").attr("width",m).attr("height",v).attr("class","overlay").call(k);dragListener=d3.behavior.drag().on("dragstart",function(t){t!=u&&(dragStarted=!0,nodes=p.nodes(t),d3.event.sourceEvent.stopPropagation())}).on("drag",function(t){if(t!=u){if(dragStarted&&(domNode=this,e=domNode,i=t,d3.select(e).select(".ghostCircle").attr("pointer-events","none"),d3.selectAll(".ghostCircle").attr("class","ghostCircle show"),d3.select(e).attr("class","node activeDrag"),E.selectAll("g.node").sort(function(t,e){return t.id!=i.id?1:-1}),1<nodes.length&&(links=p.links(nodes),nodePaths=E.selectAll("path.link").data(links,function(t){return t.target.id}).remove(),nodesExit=E.selectAll("g.node").data(nodes,function(t){return t.id}).filter(function(t,e){return t.id!=i.id}).remove()),parentLink=p.links(p.nodes(i.parent)),E.selectAll("path.link").filter(function(t,e){return t.target.id==i.id}).remove(),dragStarted=null),relCoords=d3.mouse($("svg").get(0)),relCoords[0]<20)panTimer=!0,r(this,"left");else if(relCoords[0]>$("svg").width()-20)panTimer=!0,r(this,"right");else if(relCoords[1]<20)panTimer=!0,r(this,"up");else if(relCoords[1]>$("svg").height()-20)panTimer=!0,r(this,"down");else try{clearTimeout(panTimer)}catch(t){}t.x0+=d3.event.dy,t.y0+=d3.event.dx,d3.select(this).attr("transform","translate("+t.y0+","+t.x0+")"),A()}var e});var w=function(t){s=t,A()},_=function(t){s=null,A()},A=function(){var t=[];null!==i&&null!==s&&(t=[{source:{x:s.y0,y:s.x0},target:{x:i.y0,y:i.x0}}]);var e=E.selectAll(".templink").data(t);e.enter().append("path").attr("class","templink").attr("d",d3.svg.diagonal()).attr("pointer-events","none"),e.attr("d",d3.svg.diagonal()),e.exit().remove()},E=T.append("g");(u=e).x0=v/2,u.y0=0,l(u),n(u)})</script><div id=d3container></div>"""
    try:
      if self.yamldict and self.d3dict and self.htmlplainpath:
        with open(self.htmlzoompath, "w") as fo:
          fo.write(htmlzoomcontent)
    except:
      import traceback
      traceback.print_exc()
    return self

  def process(self):
    self.yaml_to_dict()
    self.dict_to_d3()
    self.create_html()
    return self


if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "USAGE: %s <file.yaml>" % (sys.argv[0])
    sys.exit(1)

  yv = yamlvisual(sys.argv[1])
  if not yv.error:
    yv.process()
  else:
    print yv.error
