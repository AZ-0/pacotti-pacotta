def gen_basic():
    return r'''
<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" type="text/css" href="/static/css/generic.css"/>
    </head>
    <body>
        <ul class="header">
            <li><a href="/"><img src="/static/img/logo-white.png"></a></li>
            <li><a href="/">accueil</a></li>
            <li><a href="/wish">coin cadeau</a></li>
        </ul>
        <h1>Paccotti Paccotta</h1>
        <a href="/wish">Le coin cadeaux</a>
    </body>
</html>
'''.strip()
