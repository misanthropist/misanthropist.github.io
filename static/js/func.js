util.wrap({
    name: "func"
    /* 
    异步传输数据
    (string, string, object, function) => undefine
    func.ajax("get", "http://localhost:2018/static/json/films.json", function(data){console.log(data);}) => 异步获取电影信息并打印
     */
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
    /*
    使用CCS选择器获得元素数组
    string => array
    func.$('body') => [htmlbodyelement]
    */
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
    /*
    深度优先遍历节点内所有子元素，并对每个节点调用函数。
    node => undefined
    walk_ele(document, function(node){console.log(node);}) => 深度遍历页面内所有节点并打印
    */
    , walk_ele: function walk(node, func) {
        func(node);
        node = ele.firstElementChild;
        while (node) {
            walk(node, func);
            node = node.nextElementSibling;
        }
    }
    /*
    判断页面内元素是否在可见区域内
    element => boolean
    func.is_in_viewport(document.body) => true 
    */
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
    /* 
    添加内部样式并返回
    string => htmlstyleelement
    func.add_style('body { background-color: #aaa; }') => <style>body { background-color: #aaa; }</style>
    */
    , add_style: function(css) {
        var ret = document.createElement('style');
        ret.textContent = css;
        (document.head || document.getElementsByTagName('head')[0]).appendChild(ret);
        return ret;
    }
    /* 
    添加行内样式并返回
    (element, object) => element
    func.css(func.$('body')[0], {backgroundColor: "#aaa"}) => <body style="background-color: rgb(170, 170, 170;">...</body>
    */
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
            n = img.length
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
        // , create_ce: function(url) {
        //     that = this;
        //     this.init({'db_name':'ce', 'db_version':'1', 'db_store_name':'test'});
        //     var data = '';
        //     func.ajax('get', url, function(data){
        //         data = data.split('\r\n').slice(31, -1);
        //         var transaction = that.db.transaction('test', "readwrite");
        //         var store = transaction.objectStore('test');
        //         var request;
        //         data.forEach(function(value, key, item) {
        //             var key=value.split('/')[0].split(' ')[1];
        //             request = store.put(value,key);
        //         });
        //         request.onsuccess = function(){
        //             console.log("put success");
        //         };
        //         request.onerror = function(event){
        //             console.log(event);
        //         }
        //     });
        // }
        , init: function(args, fn) {
            var that = this;
            this.db_name = args.db_name;
            this.db_version = args.db_version;
            this.db_store_name = args.db_store_name;
            // this.db_saved = true;
            if (!window.indexedDB) {
                window.alert("Not Support");
            }
            var request = indexedDB.open(this.db_name, this.db_version);
            request.onerror = function(event) {
                window.alert(event.target.errorCode);
            };
            request.onupgradeneeded = function(e) {
                that.db = e.target.result;
                if (!that.db.objectStoreNames.contains(that.db_store_name)) {
                    that.db.createObjectStore(that.db_store_name);
                  }
                // that.db_saved = false;
                console.log("create success");
            };
            request.onsuccess = function(e) {
                that.db = e.target.result;
                console.log("connect success");
                if (fn) {
                    fn();
                }
            };
        }
        , add: function(key, args) {
            var store = this.db.transaction([this.db_store_name], "readwrite").objectStore(this.db_store_name);
            var request = store.add(args, key);
            request.onsuccess = function(){
                console.log("add success");
            };
            request.onerror = function(event){
                console.log(event);
            }

        }
        , put: function(key,args) {
            var transaction = this.db.transaction(this.db_store_name, "readwrite");
            var store = transaction.objectStore(this.db_store_name);
            var request = store.put(args,key);
            request.onsuccess = function(){
                console.log("put success");
            };
            request.onerror = function(event){
                console.log(event);
            }
        }
        , delete: function() {
            request = this.db.transaction(this.db_store_name, "readwrite").objectStore(this.db_store_name).delete(id);
            request.onsuccess = function() {
                console.log('delete success');
            }
        }
        , select: function(key, fn) {
            var that = this;
            var store = this.db.transaction([this.db_store_name],"readwrite").objectStore(this.db_store_name);
            if(key)
                var request = store.get(key);
            else
                var request = store.getAll();
            request.onsuccess = function() {
                that.result[key]=request.result;
                if(fn) {
                    fn(that.result);
                }
            }
        }
        , clear: function() {
            var request = this.db.transaction(this.db_store_name, "readwrite").objectStore(this.db_store_name).clear();
            request.onsuccess = function() {
                console.log(request.result);
            }
        }
        , search: function(keyword, limit) {
            var that = this;
            var transaction = this.db.transaction(this.db_store_name, "readonly");
            var objectStore = transaction.objectStore(this.db_store_name);
            var request = objectStore.openCursor();
            var most = 0;
            request.onsuccess = function(event) {
                var cursor = event.target.result;
                if (cursor) {
                    if (cursor.value.indexOf(keyword) !== -1&&most<=limit) {
                        most++;
                        key = cursor.key;
                        value = cursor.value;
                        src = {};
                        src[key] = value;
                        that.result = util.extend(src, that.result, true);
                    }
                    cursor.continue();
                } else {
                    console.log(that.result);
                }
            };
        }
    }
});
