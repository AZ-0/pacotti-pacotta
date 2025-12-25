###################################
#- Generator machinery
####


def indent(text: str, indent: int):
    return (' '*indent).join(text.splitlines(True))

def _template_scripts(scripts: list[str]) -> str:
    return '        \n'.join(
        f'<script src="/static/js/{script}.js" defer></script>'
        for script in scripts
    )

def _template_generic(style, template_page, *scripts):
    return r'''
<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" type="text/css" href="/static/css/generic.css"/>
        <link rel="stylesheet" type="text/css" href="/static/css/%s.css"/>
        %s
    </head>
    <body>
        <ul class="header">
            <li><a href="/"><img src="/static/img/logo-white.png"/></a></li>
            <li><a href="/">accueil</a></li>
            <li><a href="/wish">coin cadeau</a></li>
        </ul>
        %s
    </body>
</html>
'''.strip() % (style, _template_scripts(scripts), indent(template_page, 8))



###################################
#- Index template
####


TEMPLATE_INDEX_PAGE = r'''
<ul class="page">
    <li><a href="/wish"><div><img src="/static/img/gift.png"/></div><p>Le coin cadeau</p></a></li>
</ul>
'''.strip()



###################################
#- Wish templates
####


TITLE_WISH_INDEX  = "Le coin cadeau"
TITLE_WISH_EDITOR = "Éditeur de souhait"
TITLE_WISH_VIEW_SELF = "Mes souhaits"
TITLE_WISH_VIEW_OTHER = "Les souhaits de {{ recipient.name }}"
TITLE_WISH_VIEW_FOREIGN = "Mes idées pour quelqu'un d'autre"

SUBTITLE_WISH_INDEX = "Un souhait est un espoir, pas une promesse..."
SUBTITLE_WISH_EDITOR = SUBTITLE_WISH_INDEX
SUBTITLE_WISH_VIEW_SELF = "J'espère que tu as été sage ! Sinon..."
SUBTITLE_WISH_VIEW_OTHER = "Allons jeter un coup d'oeil ! 🛸"
SUBTITLE_WISH_VIEW_FOREIGN = "Un grand pouvoir implique de grandes responsabilités."


def _template_wish_page(title, subtitle, template_main):
    return r'''
<div class="page">
    <ul class="menu">
        {%% for key, option in menu.items() %%}
        <li><a href="/wish/{{key}}"{%% if key == menuactive %%} class="active"{%% endif %%}>{{option}}</a></li>
        {%% endfor %%}
    </ul>
    <div class="main">
        <div class="subheader">
            <h1 class="title">%s</h1>
            <p class="subtitle">%s</p>
        </div>
        %s
    </div>
</div>
'''.strip() % (title, subtitle, indent(template_main, 8))


_TEMPLATE_WISH_RECIPIENTS = r'''
<div class="recipient">
    <p>Destinataire:</p>
    <select wishid="{{ wish.id }}">
        {% for uid, user in users.items() %}
        <option value="{{ uid }}" {% if uid == wish.recipient.id %} selected{% endif %}>{{ user.name }}</option>
        {% endfor %}
    </select>
</div>
'''.strip()

_TEMPLATE_WISH_CLAIMANT = r'''
<div class="claim">
    <p>Pris en charge par</p>
    <select wishid="{{ wish.id }}"{% if wish.claimant %} class="claimed"{% endif %} autocomplete="off">
        <option value="-1">Aucun</option>
        {% if wish.claimant %}
        <option value="{{ wish.claimant.id }}" selected{% if user.id != wish.claimant.id %} disabled hidden{% endif %}>{{ wish.claimant.name }}</option>
        {% endif %}
        {% if user.id != wish.claimant_id %}
        <option value="{{ user.id }}">{{ user.name }}</option>
        {% endif %}
    </select>
</div>
'''.strip()

_TEMPLATE_WISH_WARNING_FOREIGN = r'''
{% if wish.foreign %}
<p class="warning">
    Ce souhait est proposé par {{ wish.maker.name }}{% if wish.hidden %} — c'est une surprise !{% endif %}
</p>
{% endif %}
'''.strip()

_TEMPLATE_WISH_WARNING_NOFOREIGN = r'''
{% if wish.hidden %}
<p class="warning">
    Ce souhait est une surprise !
</p>
{% endif %}
'''.strip()

def _template_wish_list_main(self: bool, foreign: bool):
    _template_recipients = [r'', _TEMPLATE_WISH_RECIPIENTS][foreign]
    _template_claimant = [_TEMPLATE_WISH_CLAIMANT, r''][self]
    _template_warning = [_TEMPLATE_WISH_WARNING_FOREIGN, _TEMPLATE_WISH_WARNING_NOFOREIGN][foreign]

    return r'''
<div class="wish-grid">
    {%% for wish in wishes %%}
    {%% if not (%s and wish.hidden) %%}
    <div class="wish{%% if (%s and wish.foreign) or wish.hidden %%} warning{%% endif %%}">
        <h4 class="date">Créé le {{ wish.date_str() }}</h4>
        <p class="kind">{{ wish.kind }}</p>
        %s
        %s
        %s
        <p class="content">
            {{ wish.content }}
        </p>
    </div>
    <div class="control" wishid="{{ wish.id }}">
        {%% if wish.owned_by(user.id) %%}
        <button class="modify">Modifier</button>
        <button class="delete">Supprimer</button>
        {%% endif %%}
    </div>
    {%% endif %%}
    {%% endfor %%}
</div>
'''.strip() % (self, not foreign, indent(_template_recipients, 8), indent(_template_claimant, 8), indent(_template_warning, 8))


TEMPLATE_WISH_INDEX_MAIN = r'''
'''.strip()

TEMPLATE_WISH_EDITOR_MAIN = r'''
<form method="post" action="/wish/{{ action }}">
    <select name="recipient" autocomplete="off" required>
        {% for uid, user in users.items() %}
        <option value="{{ uid }}"{% if user == wish.recipient %}selected{% endif %}>{{ user.name }}</option>
        {% endfor %}
    </select>

    <select name="kind" autocomplete="off" required>
        <option value="0">Livre</option>
        <option value="1">Jeu vidéo</option>
    </select>

    <textarea name="content" autocomplete="off" required autofocus>{{ wish.content }}</textarea>

    <label>
        <input type="checkbox" name="hidden" value="0"/>
        Ce souhait est une surprise.
    </label>

    <input type="hidden" name="wishid" value="{{ wish.id }}"/>

    <button type="submit">Enregistrer</button>
</form>

<button onclick="history.back();return false;">Annuler</button>
'''.strip()


TEMPLATE_WISH_VIEW_SELF_MAIN    = _template_wish_list_main(self=True,  foreign=False)
TEMPLATE_WISH_VIEW_OTHER_MAIN   = _template_wish_list_main(self=False, foreign=False)
TEMPLATE_WISH_VIEW_FOREIGN_MAIN = _template_wish_list_main(self=False, foreign=True)



###################################
#- Templates
####



class Templates:
    INDEX = _template_generic('index', TEMPLATE_INDEX_PAGE)
    WISH_INDEX = _template_generic('wish', _template_wish_page(TITLE_WISH_INDEX, SUBTITLE_WISH_INDEX, TEMPLATE_WISH_INDEX_MAIN))
    WISH_EDITOR = _template_generic('wish', _template_wish_page(TITLE_WISH_EDITOR, SUBTITLE_WISH_EDITOR, TEMPLATE_WISH_EDITOR_MAIN))
    WISH_VIEW_SELF = _template_generic('wish', _template_wish_page(TITLE_WISH_VIEW_SELF, SUBTITLE_WISH_VIEW_SELF, TEMPLATE_WISH_VIEW_SELF_MAIN), 'wish')
    WISH_VIEW_OTHER = _template_generic('wish', _template_wish_page(TITLE_WISH_VIEW_OTHER, SUBTITLE_WISH_VIEW_OTHER, TEMPLATE_WISH_VIEW_OTHER_MAIN), 'wish')
    WISH_VIEW_FOREIGN = _template_generic('wish', _template_wish_page(TITLE_WISH_VIEW_FOREIGN, SUBTITLE_WISH_VIEW_FOREIGN, TEMPLATE_WISH_VIEW_FOREIGN_MAIN), 'wish')


if __name__ == '__main__':
    with open('wish/index.html', 'w') as file:
        file.write(Templates.WISH_INDEX)
    with open('wish/editor.html', 'w') as file:
        file.write(Templates.WISH_EDITOR)
    with open('wish/view-self.html', 'w') as file:
        file.write(Templates.WISH_VIEW_SELF)
    with open('wish/view-other.html', 'w') as file:
        file.write(Templates.WISH_VIEW_OTHER)
    with open('wish/view-foreign.html', 'w') as file:
        file.write(Templates.WISH_VIEW_FOREIGN)
    with open('index.html', 'w') as file:
        file.write(Templates.INDEX)