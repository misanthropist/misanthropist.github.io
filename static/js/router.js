util.wrap({
    name: 'router'
    , routes: {}
    , currentUrl: ''
    , currentHash: ''
    , route: function(path, callback) {
        this.routes[path] = callback || function(){};
    }
    , refresh: function() {
        this.currentUrl = location.pathname;
        this.currentHash = location.hash;
        if(this.currentHash){
            if (this.routes.hasOwnProperty(this.currentHash)) {
                this.routes[this.currentHash]();
            } else{
                console.log(this.currentHash+"->此hash未注册")
            } 
        }
        if (this.routes.hasOwnProperty(this.currentUrl)){
            this.routes[this.currentUrl]();
        } else {
            console.log(this.currentUrl+"->此链接未注册")
        }
    }
    , init: function() {
        window.addEventListener('DOMContentLoaded', this.refresh.bind(this), false);
        window.addEventListener('hashchange', this.refresh.bind(this), false);
    }
});


/* 特定页面调用特定功能 */
router.init();
router.route('#a', function() {
    console.log("hi, a");
});

/* 一级页面header随机显示header.json条目*/
function header_random() {
    func.ajax("get", "/static/json/header.json", function(data){
        content = JSON.parse(data);
        name_i = Math.floor(Math.random()*content.items_name.length);
        item_name = content.items_name[name_i];
        content_i = Math.floor(Math.random()*content.items_content[item_name].length);
        item_content = content.items_content[item_name][content_i];
        item = item_content+" —— "+item_name;
        ele = func.$("header>p")[0];
        ele.innerHTML = item;
    })
}
router.route('/', function() {
    header_random();
});

router.route('/static/html/'+encodeURI('追寻所有社会现象的历史起源')+'.html', function () {
    func.ajax("GET", "/static/json/timeline.json", function (data) {
        timeline = func.$("#timeline")[0];
        timeline.textContent = data;
    });
});

router.route('/static/html/'+encodeURI('自拍')+'.html', function() {
    func.lazy_load_pics();
});


router.route('/static/html/pi_car.html', function() {
    var commands = func.$("a");
    for (var i = 0; i < commands.length; i++) (function(elem){
        commands[i].addEventListener("click", function(e) {
            console.log(elem.id);
            func.ajax("POST", "/cgi-bin/car.py", {"command":elem.id}, function(data){
                console.log(data);
                var log = func.$("#log")[0];
                log.innerHTML += data+"<br>";
            });
            e.stopPropagation();
            e.preventDefault();
        })
    })(commands[i]);
});

router.route('/static/html/tello.html', function() {
    var commands = func.$("a"),
    pic = func.$("#tello_pic")[0],
    log = func.$("#log")[0];
    pic.src = "";
    for (var i=0; i<commands.length; i++) (function(elem) {
        elem.addEventListener("click", function(e) {
            func.ajax("POST", "/cgi-bin/tello.py", {"command":elem.id}, function(data) {
                console.log(data);
                log.innerHTML += data+"<br>";
                pic.src="/temp/h2640.jpeg?t="+(new Date());
            });
            e.stopPropagation();
            e.preventDefault();
        });
    })(commands[i]);
});