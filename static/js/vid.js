function switch_vid(csv_arr, site_meta, item) {
    var item_index = csv_arr.indexOf(item),
        ele = func.$("#media")[0],
        vid = document.createElement("div");
    ele.innerHTML = "";
    vid.setAttribute("id", "dplayer");
    ele.appendChild(vid);
    const dp = new DPlayer({
        container: document.getElementById('dplayer'),
        video: {
            url: '',
            type: 'auto'
        },
        contextmenu: [
            {
                text: '1X',
                click: (player) => {
                    player.speed(1);
                },
            },
            {
                text: '1.5X',
                click: (player) => {
                    player.speed(1.5);
                },
            },
        ]
    });
    if (site_meta.type != "mixed") {
        dp.on("ended", function() {
            if (item_index < site_meta.all_item_num-1) {
                item_index = item_index + 1;
            } else {
                item_index = 0;
            }
            start_vid(dp, site_meta, csv_arr[item_index]);
        });
    }
    start_vid(dp, site_meta, csv_arr[item_index]);

}

function start_vid(dp, site_meta, item) {
    var media_info = func.$("#media_info")[0],
        item_type = item[item.length - 1];;

    document.title = item[1].slice(0, 12);
    if (item_type == "m3u8") {
        var media_info_path = item[0]+"/info.html",
            cover = '<img src="'+item[0]+'/cover.jpg">',
            url_path = item[0]+'/hls.m3u8';
    } else if (item_type == "mp4") {
        var media_info_path = item[0]+".html",
            cover = '<img src="'+item[0]+'.jpg">',
            url_path = item[0]+'.mp4';
    }
    func.ajax(
        "get",
        media_info_path,
        function(data) {
            media_info.innerHTML = cover+data;
            if (site_meta.type == "mixed") {
                media_info.appendChild(gen_uncollect(item));
            } else {
                media_info.appendChild(gen_collect(item));
            }
        }
    );
    dp.switchVideo(
        {
            url: url_path,
        }
    );
    dp.play();
}
