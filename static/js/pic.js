function switch_pic(csv_arr, site_meta, item) {
    var item_index = csv_arr.indexOf(item), 
        ele = func.$("#media")[0],
        pic_num = item[2],
        img = document.createElement("img");
    document.title = item[1].slice(0, 12);
    if (site_meta.type == "jpg") {
        var img_url = '/'+site_meta.disk+'/'+site_meta.name+'/'+item[0]+'/'+item[0]+'_1.jpg',
            info_url = '/'+site_meta.disk+"/"+site_meta.name+"/"+item[0]+'/'+item[0]+".html",
            cover = '<img src="/'+site_meta.disk+'/'+site_meta.name+'/'+item[0]+'/'+item[0]+'.jpg">';
    }
    func.ajax(
        "get",
        info_url,
        function(data) {
            func.$("#media_info")[0].innerHTML = cover+data;
        }
    );

    img.setAttribute("src",img_url);
    img.setAttribute("data-src", "1")
    img.addEventListener('click', function() {
        var num = parseInt(img.getAttribute("data-src"));
        num = num + 1;
        if (num > pic_num) {
            if (item_index < site_meta.all_item_num-1) {
                item_index = item_index + 1;
            } else {
                item_index = 0;
            }
            switch_pic(csv_arr, site_meta, csv_arr[item_index]);
        } else {
            img.setAttribute("src", '/'+site_meta.disk+'/'+site_meta.name+'/'+item[0]+'/'+item[0]+'_'+num+'.jpg');
            img.setAttribute("data-src", num);
            
            document.title = item[1].slice(0, 12)+num+"_"+pic_num;
        }
    })
    ele.innerHTML = "";
    ele.appendChild(img);
}
