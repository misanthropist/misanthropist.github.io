util.wrap({
    name: "func"
    /* 异步传输数据
    (string, string, object, function) => undefine
    func.ajax("get", "http://localhost:2018/static/json/films.json", function(data){console.log(data);})*/
    , ajax: function(method, url, data, onload) {
        var xhr = new XMLHttpRequest();
        if (typeof data === 'function') {
            onload = data;
            data = null;
        }
        xhr.open(method, url);
        var fd = new FormData();
        if (method === 'POST' && data) {
            for (var key in data) {
                fd.append(key, data[key]);
            }
        }
        xhr.onload = function () {
          onload(xhr.response);
        };
        xhr.send(data ? fd : null);
    }
    /* 使用CCS选择器获得元素数组
    string => array
    func.$('body') => [htmlbodyelement]*/
    , "$": function(selector) {
        var nodes = document.querySelectorAll.bind(document)(selector);
        return Array.prototype.slice.call(nodes);
    }
    /* ele随机显示xhr_json中任一条目 */
    , random_item: function(ele, xhr_json) {
        this.ajax("get", xhr_json, function(data){
            content = JSON.parse(data);
            names = Object.keys(content);
            name_i = Math.floor(Math.random() * names.length)
            item_name = names[name_i];
            item_contents = content[item_name];
            item_contents_i = Math.floor(Math.random() * item_contents.length);
            item_content = item_contents[item_contents_i];
            item = item_content+" —— "+item_name;
            ele.innerHTML = item;
        })
    }
    /* 深度优先遍历节点内所有子元素，并对每个节点调用函数。
    node => undefined
    walk_ele(document, function(node){console.log(node);}) => 深度遍历页面内所有节点并打印*/
    , walk_ele: function walk(node, func) {
        func(node);
        node = ele.firstElementChild;
        while (node) {
            walk(node, func);
            node = node.nextElementSibling;
        }
    }
    /* 判断页面内元素是否在可见区域内
    element => boolean
    func.is_in_viewport(document.body) => true */
    , is_in_viewport: function (ele) {
        var rect = ele.getBoundingClientRect()
        , html = document.documentElement;
        return (
            rect.top >= 0 &&
            rect.left >= 0 &&
            rect.top < (window.innerHeight || html.clientHeight) &&
            rect.left < (window.innerWidth || html.clientWidth)
        );
    }
    /* 添加行内样式并返回
    (element, object) => element
    func.css(func.$('body')[0], {backgroundColor: "#aaa"}) => <body style="background-color: rgb(170, 170, 170;">...</body>*/
    , css: function(e, s) {
        for (var p in s) {
            var attr = p.replace(/[A-Z]/g, function(w) {
                return '-' + w.toLowerCase();
            })
            e.style[attr] = s[p];
        }
        return e;
    }

    /* 延时加载图片 */
    , lazy_load_pics: function() {
        var img = func.$("img"),
            n = img.length;
            m = n;
        lazyload(img, 'data-src', 'src');
        var int = setInterval(function() {
            n -= 1;
            if (n <= 0) {
                int = window.clearInterval(int);
            } else {
                var i = m - n;
                img[i].setAttribute('src', img[i].getAttribute('data-src'));
                img[i].setAttribute('data-src', '');

            }

        }, 1000);
        function lazyload(arr, des, src) {
            for (var i = 1; i < n; i++) {
                img[i].setAttribute(des, img[i].getAttribute(src));
                img[i].setAttribute(src, '../pic/base.png');
            }
        }
    }
    
    /* IndexDB接口 */
    , dbObject: {
        result: {}
        , init: function(args, fn) {
            var that = this;
            this.db_name = args.db_name;
            this.db_version = args.db_version;
            this.db_table_name = args.db_table_name;
            if (!window.indexedDB) {
                window.alert("Not Support");
            }
            var request = indexedDB.open(this.db_name, this.db_version);
            request.onerror = function(event) {
                window.alert(event.target.errorCode);
            };
            request.onupgradeneeded = function(e) {
                that.db = e.target.result;
                if (!that.db.objectStoreNames.contains(that.db_table_name)) {
                    that.db.createObjectStore(that.db_table_name);
                  }
                console.log("The "+that.db_table_name+" table is successfully created.");
            };
            request.onsuccess = function(e) {
                that.db = e.target.result;
                console.log("The "+that.db_name+" database is successfully connected.");
                if (fn) {
                    fn();
                }
            };
        }
        , add: function(key, args) {
            var request = this.db.transaction([this.db_table_name], "readwrite").objectStore(this.db_table_name).add(args, key);
            request.onsuccess = function() {
                console.log("The data item was successfully added");
            };
            request.onerror = function(event) {
                console.log(event.target.errorCode);
            };
        }
        , select: function(key, fn) {
            var that = this;
            if (key)
                var request = this.db.transaction([this.db_table_name], "readonly").objectStore(this.db_table_name).get(key);
            else
                var request = this.db.transaction([this.db_table_name], "readonly").objectStore(this.db_table_name).getAll();
            request.onsuccess = function() {
                that.result[key]=request.result;
                if (fn) {
                    fn(that.result);
                }
            }
            request.onerror = function(event) {
                console.log(event.target.errorCode);
            };
        }
        , put: function(key,args) {
            var request = this.db.transaction(this.db_table_name, "readwrite").objectStore(this.db_table_name).put(args,key);
            request.onsuccess = function() {
                console.log("The data item was successfully updated");
            };
            request.onerror = function(event) {
                console.log(event.target.errorCode);
            };
        }
        , delete: function(key) {
            var request = this.db.transaction(this.db_table_name, "readwrite").objectStore(this.db_table_name).delete(key);
            request.onsuccess = function() {
                console.log('The data item was successfully deleted');
            }
            request.onerror = function(event) {
                console.log(event.target.errorCode);
            };
        }
    }
});
