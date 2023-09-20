(function(){
  var _global = (function(){ return this || (0, eval)('this'); }())  
  , util = {
    name: 'util'
    /*
    识别数据类型
    any => string
    util.type({}) => "object"
    */
    , type: function (o) {
      var s = Object.prototype.toString.call(o);
      return s.match(/\[object (.*?)\]/)[1].toLowerCase();
    }
    /*
    将源对象自有数据，复制到目的对象，并控制是否覆盖相同属性。
    (object, object, boolean) => object
    util.extend({a:"a",b:"b"}, {b:"c", c:"c"}, true) => {a:"a",b:"b",c:"c"}
     */
    , extend: function(src, des, override) {
      for (var key in src) {
        if (src.hasOwnProperty(key) && (!des.hasOwnProperty(key) || override)) {
          des[key] = src[key];
        }
      }
      return des;
    }
    /*
    包装自定义对象到某一对象下，并控制是否覆盖已存在对象（默认不覆盖），且自定义对象必须包含name属性。
    (object, object, boolean) => 添加对象到全局
    util.wrap({name:test; hi: "yes!"}, true) => 全局对象上test为{name: "test", hi: "yes!"}
    */
    , wrap: function(plugin, global, override) {
      var _global = global || (function(){return this || (0, eval)('this');}())
      , name = plugin.name

      if ((name in _global) && !override) {
        console.log(name+' has been located in '+_global);
      } else {
        _global[name] = plugin;
      }
    }
  
  }
  
  , name = util.name;
  if (name in _global) {
    console.log(name+' has been located in '+_global);
  } else {
    _global[name] = util;
  }
}());
