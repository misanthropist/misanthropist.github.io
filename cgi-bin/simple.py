#!/usr/bin/python3

from datetime import datetime
print('''\
"Content-type:text/html"

<html>
<body>
<p>Generated {0}</p>
</body>
</html>'''.format(datetime.now()))
