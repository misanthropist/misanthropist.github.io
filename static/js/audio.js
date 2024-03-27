function switch_audio(csv_arr, site_meta, item) {
    var item_index = csv_arr.indexOf(item),
        ele = func.$("#media")[0],
        au = document.createElement("audio");
    ele.innerHTML = "";
    ele.appendChild(au);

    au.addEventListener("ended", function() {
        if (item_index < site_meta.all_item_num-1) {
            item_index = item_index + 1;
        } else {
            item_index = 0;
        }
        start_audio(au, site_meta, csv_arr[item_index]);
    });
    start_audio(au, site_meta, csv_arr[item_index]);

}

function start_audio(au, site_meta, item) {
    document.title = item[1].slice(0, 12);
    if (site_meta.type == "mp3") {
        var src_url = '/'+site_meta.disk+'/'+site_meta.name+'/'+item[0]+'.mp3',
            lrc_url = '/'+site_meta.disk+'/'+site_meta.name+'/'+item[0]+'.lrc',
            cover = '<img src="/'+site_meta.disk+'/'+site_meta.name+'/'+item[0]+'.jpg">';
    }
    func.ajax(
        "get",
        lrc_url,
        function(data) {
            data = item[1] + "<br>" + data.replace(/\n/g, "<br>");
            func.$("#media_info")[0].innerHTML = cover+data;
        }
    );
    au.setAttribute("controls", "true");
    au.setAttribute("autoplay", "true");
    au.setAttribute("src", src_url);
    au.volume = 0.2;
}