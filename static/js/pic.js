function switch_pic(csv_arr, site_meta, item) {
    var item_index = csv_arr.indexOf(item), 
        ele = func.$("#media")[0],
        pic_num = item[2],
        media_info = func.$("#media_info")[0],
        item_type = item[item.length - 1],
        img = document.createElement("img");
    document.title = item[1].slice(0, 12);
    if (item_type == "jpg") {
        var img_url = item[0]+'/'+item[0].split('/').pop()+'_1.jpg',
            info_url = item[0]+'/'+item[0].split('/').pop()+".html",
            cover = '<img src="'+item[0]+'/'+item[0].split('/').pop()+'.jpg">';
    }
    func.ajax(
        "get",
        info_url,
        function(data) {
            media_info.innerHTML = cover+data;
            if (site_meta.type == "mixed") {
                media_info.appendChild(gen_uncollect(item));
            } else {
                media_info.appendChild(gen_collect(item));
            }
        }
    );

    img.setAttribute("src", img_url);
    img.setAttribute("data-src", "1")
    img.addEventListener('click', function() {
        var num = parseInt(img.getAttribute("data-src"));
        num = num + 1;
        if (num <= pic_num) {
            img.setAttribute("src", item[0]+'/'+item[0].split('/').pop()+'_'+num+'.jpg');
            img.setAttribute("data-src", num);
            
            document.title = item[1].slice(0, 12)+num+"_"+pic_num;
        } else if(num > pic_num && site_meta.type != "mixed") {
            if (item_index < site_meta.all_item_num-1) {
                item_index = item_index + 1;
            } else {
                item_index = 0;
            }
            switch_pic(csv_arr, site_meta, csv_arr[item_index]);
        }
    })
    ele.innerHTML = "";
    ele.appendChild(img);
}
