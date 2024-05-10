function switch_audio(csv_arr, site_meta, item) {
    var item_index = csv_arr.indexOf(item),
        au = document.createElement("audio");

    if (site_meta.type != "mixed") {
        au.addEventListener("ended", function() {
            if (item_index < site_meta.all_item_num-1) {
                item_index = item_index + 1;
            } else {
                item_index = 0;
            }
            start_audio(au, site_meta, csv_arr[item_index]);
        });
    }
    start_audio(au, site_meta, csv_arr[item_index]);

}

function start_audio(au, site_meta, item) {
    var media_info = func.$("#media_info")[0],
        lrc_ele = document.createElement("p");
        ele = func.$("#media")[0],
        item_type = item[item.length - 1];

    ele.innerHTML = "";
    ele.appendChild(au);
    document.title = item[1].slice(0, 12);
    if (item_type == "mp3") {
        var src_url = item[0]+'.mp3',
            lrc_url = item[0]+'.lrc',
            cover = '<img src="'+item[0]+'.jpg">';
    }
    func.ajax(
        "get",
        lrc_url,
        function(data) {
            data = data.replace(/\n/g, "<br>");
            lrc_ele.innerHTML = item[1] + "<br>" + data;
            media_info.innerHTML = cover;
            ele.appendChild(lrc_ele);
            func.css(lrc_ele, {"text-align": "left"});
            if (site_meta.type == "mixed") {
                media_info.appendChild(gen_uncollect(item));
            } else {
                media_info.appendChild(gen_collect(item));
            }
        }
    );
    au.setAttribute("controls", "true");
    au.setAttribute("autoplay", "true");
    au.setAttribute("src", src_url);
    au.volume = 0.2;
}