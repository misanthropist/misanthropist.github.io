util.wrap({
    name: 'router'
    , routes: {}
    , current_url: ''
    , current_hash: ''
    , route: function(path, callback) {
        this.routes[path] = callback || function(){};
    }
    , refresh: function() {
        this.current_url = location.pathname;
        this.current_hash = location.hash;
        if (this.current_hash) {
            if (this.routes.hasOwnProperty(this.current_hash)) {
                this.routes[this.current_hash]();
            } else{
                console.log(this.current_hash + "->此hash未注册")
            } 
        }
        if (this.routes.hasOwnProperty(this.current_url)){
            this.routes[this.current_url]();
        } else {
            console.log(this.current_url + "->此链接未注册")
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

/* 首页header元素随机显示header.json中任一条目 */
router.route('/', function() {
    var ele = func.$("header>p")[0];
    func.random_item(ele, "/static/json/header.json");
});

router.route('/static/html/'+encodeURI('中学教师')+'.html', function () {
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