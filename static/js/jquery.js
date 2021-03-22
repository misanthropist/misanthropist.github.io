(function (window, undefined) {
    var jQuery = (function () {
        var jQuery = function (selector, context) {
            return new jQuery.fn.init(selector, context, rootjQuery);
        },
        rootjQuery;

        jQuery.fn = jQuery.prototype = {
            constructor: jQuery,
            init: function (selector, context, rootjQuery) {
                return 'hello';

                
            }
        }
        
        jQuery.fn.init.prototype = jQuery.fn;
        jQuery.extend = jQuery.fn.extend = function () {
            
        };
        jQuery.extend({
            
        });
        
        return jQuery;

    })();
    window.jQuery = window.$ = jQuery;
})(window);