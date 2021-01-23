
(function() {
    test("Async Test #1", function(){
        pause();
        setTimeout(function() {
            assert(true, "First test completed");
            resume();
        }, 1000);
    });
    test("Async Test #2", function(){
        pause();
        setTimeout(function() {
            assert(true, "Second test completed");
            resume();
        }, 1000);
    });
    test("function declaration", function() {
        window.v1 = function n1() {return true;};
        assert(window.v1.name == "n1", "v1's real name is n1");
    });
    test("function scope", function(){
        assert(typeof a!=="number", "a is not in scope");
        assert(typeof f1=="function", "f1 is in scope");
        assert(typeof b !== "number", "b is not in scope");
        var a = 1;
        function f1() {};
        window.b = 1;
    });
    test("function invoke", function() {
        function Ninja() {
            this.skulk = function() { return this; };
        }
        var ninja1 = new Ninja();
        assert(ninja1.skulk() === ninja1,
            "The ninja1 is skulking");
    });
    test("recursion", function() {
        var ninja = {
            isPalindrome: function(text) {
                if (text.length <=1 && text!==null && text!==undefined) return true;
                if (text.charAt(0) != text.charAt(text.length - 1)) return false;
                return this.isPalindrome(text.substr(1, text.length - 2));
            }
        };
        var samurai = {isPalindrome: ninja.isPalindrome};
        ninja = {}
        assert(samurai.isPalindrome("madam"), "madam is palindrome");
    });
    test("memoization", function() {
        function isPrime(value) {
            if (!isPrime.answers) isPrime.answers = {};
            if (isPrime.answers[value] != null) {
                return isPrime.answers[value];
            }
            var prime = value != 1;
            for (var i = 2; i < value; i++) {
                if (value % i == 0) {
                    prime = false;
                    break;
                }
            }
            return isPrime.answers[value] = prime;
        }
        assert(isPrime(5), "5 is prime!");
        assert(isPrime.answers[5], "the answer was cached!");
    });
    test("closure", function() {
        pause();
        function animateIt(elementId) {
            var elem = document.getElementById(elementId);
            var tick = 0;
            var timer = setInterval(function() {
                if (tick < 100) {
                    elem.style.left = elem.style.top = tick + "px";
                    tick++;
                }
                else {
                    clearInterval(timer);
                    assert(tick == 100, "Tick accessed via a closure.");
                    assert(elem, "Element also accessed via a closure");
                    assert(timer, "Timer reference also obtained via a closure.");
                    resume();
                }
            }, 10);
        }
        animateIt('box');
    });
    test("prototype", function() {
        function Ninja() {
            this.swung = true;
            this.swingSword = function() {
                return !this.swung;
            };
        }
        
        var ninja = new Ninja();
        
        Ninja.prototype.swingSword = function() {
            return this.swung;
        };

        assert(ninja.swingSword(), "Called the instance method, not the prototype method.");
        Object.prototype.keys = function() {
            var keys = [];
            for (var p in this) keys.push(p);
            return keys;
        };
        var obj = {a:1, b:2, c:3};
        assert(obj.keys().length == 3, "There are three properties in this object.");
    });
    test("regex", function() {
        function compress(source) {
            var keys = {};
            source.replace(
                /([^=&]+)=([^&]*)/g,
                function(full, key, value) {
                    keys[key] = (keys[key] ? keys[key] + "," : "") + value;
                    return 
                }
            );
            var result = [];
            for (var key in keys) {
                if (keys.hasOwnProperty(key)) {
                    result.push(key + "=" + keys[key]);
                }
            }

            return result.join("&");
        }
        assert(compress("foo=1&foo=2&blah=a&blah=b&foo=3") == "foo=1,2,3&blah=a,b","Compression is OK!");
    });

})();
