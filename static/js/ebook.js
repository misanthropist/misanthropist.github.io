function switch_epub(csv_arr, site_meta, item) {
    var ele = func.$("#media")[0],
        eb = document.createElement("div"),
        eb_info = `
<div id="epub_setting">
<a href="#color_mode" id="color_mode">纯白</a>
<a href="#switch_page_mode" id="switch_page_mode">上下翻页</a>
<a href="#progress_bar" id="progress_bar">进度</a>
<input id="full-search" type="text" name="full-search" placeholder="搜索">
<div id="search-result"></div>
<br>
</div>
<div id="epub_page">
<a href="#epub_area" id="prev">上一页</a>
<a href="#epub_area" id="next">下一页</a>
</div>
<div id="catalog"></div>`;
    eb.innerHTML = `
<div id="epub_area">
<a href="#epub_area"  id="left_page"></a>
<a href="#epub_area"  id="right_page"></a>
<a href="#epub_area"  id="up_page"></a>
<a href="#epub_area"  id="down_page"></a>
</div>`;

    ele.innerHTML = "";
    ele.appendChild(eb);
    func.css(ele, {width: "100%", paddingLeft: "0px"});
    
    let cover = '<img src="/'+site_meta.disk+'/'+site_meta.name+'/'+item[0]+'/'+item[1]+'.jpg">';
    func.$("#media_info")[0].innerHTML = cover+eb_info;


    var book = ePub('/'+site_meta.disk+'/'+site_meta.name+'/'+item[0]+'/'+item[1]+".epub"),
        rendition = book.renderTo("epub_area", {
            manager: "continuous",
            flow: "paginated",
            width: "100%"
        });
        /*
        type RenditionOptions = {
            width?: string | number; // 视图宽度
            height?: string | number; // 视图高度
            ignoreClass?: string; // 忽略类名
            manager?: 'continuous' | 'default'; // 布局管理器
            view?: 'iframe' | Object | Function; // 视图容器
            flow?: 'paginated' | 'scrolled'; // 阅读方式
            layout?: string; // TODO: 我没看懂
            spread?: 'none' | boolean; // 是否显示双页
            minSpreadWidth?: number; // 最小触发双页的宽度
            resizeOnOrientationChange?: boolean; // 在窗口 resize 时调整内容尺寸
            script?: string; // 注入到 View 中的 js 代码
            stylesheet?: string; // 注入到 View 中的 css 样式
            infinite?: boolean; // 是否无限翻页
            overflow?: string; // 设置视图的 CSS overflow 属性
            snap?: boolean; // 是否支持翻页
            defaultDirection?: string; // 阅读方向
            allowScriptedContent?: boolean; // iframe 沙盒是否能够执行 js
        };
        */
    rendition.display();
    /*
    // 百分比的情况
    if (this.book.locations.length() && isFloat(target)) {
    target = this.book.locations.cfiFromPercentage(parseFloat(target));
    }
    // 目录路径、epub-cfi 的情况，我们只关注目录路径的情况
    section = this.book.spine.get(target);
    */
    //显示图书目录
    book.loaded.navigation.then(function(toc) {
        toc.forEach(function(chapter) {
            var nav_a = document.createElement("a");
            nav_a.setAttribute("href", "#epub_area");
            nav_a.setAttribute("aria-data", chapter.href);
            nav_a.textContent = chapter.label + " | ";
            nav_a.addEventListener("click", function() {
                rendition.display(chapter.href);
            })
            func.$("#catalog")[0].appendChild(nav_a);
        });
    });
    // 翻页快捷键
    func.$("#prev")[0].addEventListener("click", function() {
        rendition.prev();
    });
    func.$("#next")[0].addEventListener("click", function() {
        rendition.next();
    });
    func.$("#left_page")[0].addEventListener("click", function() {
        rendition.prev();
    });
    func.$("#right_page")[0].addEventListener("click", function() {
        rendition.next();
    });
    func.$("#up_page")[0].addEventListener("click", function() {
        rendition.prev();
    });
    func.$("#down_page")[0].addEventListener("click", function() {
        rendition.next();
    });
    var keyListener = function(e){
        if ((e.keyCode || e.which) == 37) {
            rendition.prev();
        }
        if ((e.keyCode || e.which) == 39) {
            rendition.next();
        }
    };

    document.addEventListener("keyup", keyListener, false);
        
    let LR = true
        lr_display_setting = {
            "width": "30%",
            "height": "100%",
            "z-index": "99"
        },
        ud_display_setting = {
            "width": "100%",
            "height": "30%",
            "z-index": "99"
        },
        hide_setting = {
            "width": "0",
            "height": "0",
            "z-index": "-1"
        };
    func.$("#switch_page_mode")[0].addEventListener("click", function(e) {
        if (!LR) {
            func.css(func.$("#left_page")[0], lr_display_setting);
            func.css(func.$("#right_page")[0], lr_display_setting);
            func.css(func.$("#up_page")[0], hide_setting);
            func.css(func.$("#down_page")[0], hide_setting);
            e.target.text = "上下翻页";
            LR =true;
        } else {
            func.css(func.$("#right_page")[0], hide_setting);
            func.css(func.$("#left_page")[0], hide_setting);
            func.css(func.$("#up_page")[0], ud_display_setting);
            func.css(func.$("#down_page")[0], ud_display_setting);
            e.target.text = "左右翻页";
            LR =false;
        }
    });
    //图书背景
    let white = false;
    func.$("#color_mode")[0].addEventListener("click", function(e) {
        if (!white) {
            func.css(func.$("#epub_area")[0], {"background-color": "#fff"});
            // func.css(func.$("#epub_page")[0], {"background-color": "#fff"});
            // func.css(func.$("#catalog")[0], {"background-color": "#fff"});
            e.target.text = "暗黄";
            white = true;
        } else {
            func.css(func.$("#epub_area")[0], {"background-color": "#8e7f6b"});
            // func.css(func.$("#epub_page")[0], {"background-color": "#8e7f6b"});
            // func.css(func.$("#catalog")[0], {"background-color":"#8e7f6b"});
            e.target.text = "纯白";
            white = false;
        }
    });
    //存储进度
    var bar = func.$("#progress_bar")[0],
        last_progress_cfi = '',
        last_progress_cfi_name = item[0]+"_"+item[1] + '-progress-cfi',
        all_locations = item[0]+"_"+item[1] + '-all-locations',
        site_meta_key = site_meta.type+"_"+site_meta.name,
        book_comment = item[0]+"_"+item[1]+"-comment",
        metadata = '',
        total = '';

    book.ready.then(function() {
        metadata = book.package.metadata;
        const stored = site_meta[all_locations];
        if (stored) {
            return book.locations.load(stored);
        } else {
            return book.locations.generate(1024); 
        }
    }).then(function() {
        site_meta[all_locations] = book.locations.save()
        localStorage.setItem(site_meta_key, JSON.stringify(site_meta));
    }).then(function() {
        
        last_progress_cfi = site_meta[last_progress_cfi_name]
        total = book.locations.total
        if (last_progress_cfi) {
            let progress = book.locations.locationFromCfi(last_progress_cfi)+'/'+total;
            bar.textContent="进度|"+progress;
            rendition.display(last_progress_cfi);
        }
    });
    bar.addEventListener("click", function(e) {
        let current_cfi = rendition.location.start.cfi,
            progress = book.locations.locationFromCfi(current_cfi)+'/'+total;
        e.target.text="进度|"+ progress;
        site_meta[last_progress_cfi_name] = current_cfi;
        localStorage.setItem(site_meta_key, JSON.stringify(site_meta));

    });
    rendition.on('relocated', function(location) {
        let current_cfi = location.start.cfi,
            progress = book.locations.locationFromCfi(current_cfi)+'/'+total;
        bar.textContent="进度|"+ progress;
        site_meta[last_progress_cfi_name] = current_cfi;
        localStorage.setItem(site_meta_key, JSON.stringify(site_meta));
    });
    //全文搜索
    var doSearch = (q) => {
        return Promise.all(book.spine.spineItems.map(item => 
            item
                .load(book.load.bind(book))
                .then(item.find.bind(item, q))
                .finally(item.unload.bind(item))
        )).then(results => Promise.resolve([].concat.apply([], results)))
    }
    var search = (q) => {
        doSearch(q).then((result) => {
            let p = document.createElement("p"),
                num = result.length;
            func.$('#search-result')[0].innerHTML = '';
            p.textContent = "共"+num + "条";
            if (num < 25 && num > 0) {
                result.forEach((item) => {
                    let a = document.createElement("a");
                    a.setAttribute("href", "#epub_area");
                    a.setAttribute("style", "display: block;");
                    a.setAttribute("ref", item.cfi);
                    a.textContent = item.excerpt.replaceAll(q, `<strong>${q}</strong>`);
                    a.addEventListener("click", function() {
                            rendition.display(item.cfi);
                            rendition.annotations.highlight(item.cfi);
                    });
                    p.appendChild(a);
                    let br = document.createElement("br");
                    p.appendChild(br);
                    func.$('#search-result')[0].appendChild(p);
                });
            } else if (num > 25) {
                func.$('#search-result')[0].appendChild(p);
            }
        });
    }

    func.$("#full-search")[0].addEventListener("keyup", function (event) {
        event = event || window.event;
        q = func.$("#full-search")[0].value;
        if (event.keyCode == 13 && q !== "") {
            search(q);
        }
    }, false);

    //添加书评
    rendition.on("selected", function(cfiRange, contents) {
        var comment = document.createElement("textarea"),
            bt = document.createElement("a"),
            info = func.$("#info")[0],
            info_content = info.innerHTML;
        bt.setAttribute("class", "button");
        bt.setAttribute("href", "#");
        bt.textContent = "保存";
        bt.addEventListener("click", function() {
            if (site_meta[book_comment] !== undefined) {
                site_meta[book_comment].push(cfiRange+": "+comment.value);
            } else {
                site_meta[book_comment] = [];
                site_meta[book_comment].push(cfiRange+": "+comment.value);

            }
            localStorage.setItem(site_meta.type+"_"+site_meta.name, JSON.stringify(site_meta));
            info.innerHTML = info_content;
        });
        info.innerHTML = "";
        info.appendChild(comment);
        info.appendChild(bt);
    });
}