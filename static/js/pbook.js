
function switch_pdf(site_meta, item) {
    var canvas = document.createElement("canvas"),
        prev = document.createElement("a"),
        next = document.createElement("a"),
        pdf_div = document.createElement("div"),
        media = func.$("#media")[0],
        loadingTask = pdfjsLib.getDocument(item[0]+".pdf"),
        pageRendering = true,
        page_num = 1,
        max_width = media.clientWidth,
        media_info = func.$("#media_info")[0];
    media.innerHTML = "";
    func.css(media, {width: "100%", paddingLeft: "0px"});
    prev.setAttribute("class", "button");
    prev.textContent = "上一页";
    next.setAttribute("class", "button");
    next.textContent = "下一页";
    prev.addEventListener("click", function() {
        var max_page_num = 1;
        loadingTask.promise.then(function(pdfDoc_) {
            max_page_num = pdfDoc_.numPages;
            if (page_num <= 1) {
                page_num = max_page_num;
                display_pdf(loadingTask, canvas, page_num);
            } else {
                page_num --;
                display_pdf(loadingTask, canvas, page_num);
            }
        });
    })

    next.addEventListener("click", function() {
        var max_page_num = 1;
        loadingTask.promise.then(function(pdfDoc_) {
            max_page_num = pdfDoc_.numPages;
            if (page_num >= max_page_num) {
                page_num = 1;
                display_pdf(loadingTask, canvas, page_num, max_width);
            } else {
                page_num ++;
                display_pdf(loadingTask, canvas, page_num, max_width);
            }
        });
    })
    display_pdf(loadingTask, canvas, page_num);
    
    pdf_div.appendChild(canvas);
    media_info.innerHTML = "<h2>"+item[1]+"</h2>";
    media_info.appendChild(prev);
    media_info.appendChild(next);
    if (site_meta.type == "mixed") {
        media_info.appendChild(gen_uncollect(item));
    } else {
        media_info.appendChild(gen_collect(item));
    }
    media.appendChild(pdf_div);

}

function display_pdf(loadingTask, canvas, page_num) {
    var ctx = canvas.getContext('2d');
    loadingTask.promise.then(function(pdfDoc_) {
        pdfDoc = pdfDoc_;
        pdfDoc.getPage(page_num).then(function(page) {
            var viewport = page.getViewport({scale: 1}),
                outputScale = 1.2;
            canvas.height = Math.floor(viewport.height * outputScale);
            canvas.width = Math.floor(viewport.width * outputScale);
            var transform = outputScale !== 1 ? [outputScale, 0, 0, outputScale, 0, 0] : null;
            // Render PDF page into canvas context
            var renderContext = {
                canvasContext: ctx,
                transform: transform,
                viewport: viewport
            };
            var renderTask = page.render(renderContext);

            // Wait for rendering to finish
            renderTask.promise.then(function() {
                pageRendering = false;
            });
        });
    });
}
