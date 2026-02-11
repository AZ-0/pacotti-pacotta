from sys import path
path.append('../..')
from src.model import WishKind, WISHSORT


###################################
#- Generator machinery
####



def indent(text: str, indent: int):
    return (' '*indent).join(text.splitlines(True))


def _template_scripts(scripts: list[str]) -> str:
    return '        \n'.join(
        f'<script src="{script}" defer></script>'
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
        <div class="header">
            <a href="/"><img src="/static/img/logo-white.png"/></a>
            <a href="/">Accueil</a>
            <a href="/wish">Coin cadeaux</a>
            <a class="log" href="/{%% if user %%}logout">Déconnexion{%% else %%}login">Connexion{%% endif %%}</a>
        </div>
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
TITLE_WISH_VIEW_OTHER_SELECT = "De qui veux-tu consulter les souhaits ?"
TITLE_WISH_VIEW_SELF = "Mes souhaits"
TITLE_WISH_VIEW_OTHER = "Les souhaits de {{ recipient.name }}"
TITLE_WISH_VIEW_FOREIGN = "Mes idées pour quelqu'un d'autre"
TITLE_WISH_VIEW_CLAIMED = "Les souhaits que j'ai revendiqués"

SUBTITLE_WISH_INDEX = "Un souhait est un espoir, pas une promesse..."
SUBTITLE_WISH_EDITOR = SUBTITLE_WISH_INDEX
SUBTITLE_WISH_VIEW_OTHER_SELECT = "Allons jeter un coup d'oeil ! 🛸"
SUBTITLE_WISH_VIEW_SELF = "J'espère que tu as été sage ! Sinon..."
SUBTITLE_WISH_VIEW_OTHER = SUBTITLE_WISH_VIEW_OTHER_SELECT
SUBTITLE_WISH_VIEW_FOREIGN = "Un grand pouvoir implique de grandes responsabilités."
SUBTITLE_WISH_VIEW_CLAIMED = "Le consumérisme vous a eu... 💸"


def _template_wish_page(title, subtitle, template_main):
    return r'''
<div class="page">
    <ul class="menu">
        {%% for key, option in menu.items() %%}
        <li><a href="/wish/{{key}}"{%% if key == menuactive %%} class="active"{%% endif %%}>{{option}}</a></li>
        {%% endfor %%}
    </ul>
    <div class="main" userID={{ user.id }}>
        <div class="subheader">
            <h1 class="title">%s</h1>
            <p class="subtitle">%s</p>
        </div>
        %s
    </div>
</div>
'''.strip() % (title, subtitle, indent(template_main, 8))


TEMPLATE_WISH_INDEX_MAIN = r'''
'''.strip()


TEMPLATE_WISH_EDITOR_MAIN = r''.join([r'''
<form id="editor" method="post" action="/wish/{{ action }}">
    <p class="important" id="recipienttitle">Destinataire</p>
    <select name="recipient" id="recipient" autocomplete="off" required>
        {% for uid, user in users.items() %}
        <option value="{{ uid }}"{% if user == wish.recipient %} selected{% endif %}>{{ user.name }}</option>
        {% endfor %}
    </select>

    <p class="important" id="kindtitle">Catégorie</p>
    <select name="kind" id="kind" autocomplete="off" required>''',
    *(rf'''
        <option value="{category.value}"{{% if wish.kind.value == {category.value} %}} selected{{% endif %}}>{category}</option>'''
        if isinstance(category, WishKind) else ''.join([rf'''
        <optgroup label="{category[0]}">''',
            *(rf'''
            <option value={kind.value}{{% if wish.kind.value == {kind.value} %}} selected{{% endif %}}'''rf'''>{kind}</option>'''
            for kind in category[1]
            ), rf'''
        </optgroup>'''
        ])
        for category in WISHSORT
    ), r'''
    </select>

    <p class="important" id="contenttitle">Contenu</p>
    <textarea name="content" id="content" autocomplete="off" required autofocus>{{ wish.content }}</textarea>

    <label id="surprise" class="important">
        <input type="checkbox" name="hidden" value="0"/>
        Ce souhait est une surprise. Il ne sera pas visible par le destinataire.
    </label>

    <input type="hidden" name="wishid" value="{{ wish.id }}"/>

    <button class="important" type="button" id="cancel" onclick="history.back();return false;">Annuler</button>
    <button class="important" type="submit" id="submit">Enregistrer</button>
</form>
''']).strip()


TEMPLATE_WISH_VIEW_OTHER_SELECT_MAIN = r'''
<form id="other-select-form">
    <select id="user" required>
        {% for uid, user in users.items() %}
        <option value="{{ uid }}">{{ user.name }}</option>
        {% endfor %}
    </select>
    <button type="submit">Go!</button>
</form>
'''.strip()


# --- TEMPLATE : WISH LIST MAIN

_TEMPLATE_WISH_RECIPIENTS = r'''
<div class="recipient">
    <p class="important">Destinataire:</p>
    <select wishid="{{ wish.id }}" class="recipient" autocomplete="off">
        {% for uid, user in users.items() %}
        <option value="{{ uid }}" {% if uid == wish.recipient.id %} selected{% endif %}>{{ user.name }}</option>
        {% endfor %}
    </select>
</div>
'''.strip()

_TEMPLATE_WISH_CLAIMANT = r'''
{% if not hide_claimant %}
<div class="claim">
    <p class="important">Pris en charge par</p>
    <select wishid="{{ wish.id }}" class="claimant{% if wish.claimant %} claimed{% endif %}" autocomplete="off">
        <option value="-1">Aucun</option>
        {% if wish.claimant %}
        <option value="{{ wish.claimant.id }}" selected{% if user.id != wish.claimant.id %} disabled hidden{% endif %}>{{ wish.claimant.name }}</option>
        {% endif %}
        {% if user.id != wish.claimant_id %}
        <option value="{{ user.id }}">{{ user.name }}</option>
        {% endif %}
    </select>
</div>
{% endif %}
'''.strip()

_TEMPLATE_WISH_WARNING_FOREIGN = r'''
{% if wish.foreign %}<p class="important warning">Ce souhait est proposé par {{ wish.maker.name }}{% if wish.hidden %} — c'est une surprise !{% endif %}</p>{% endif %}
'''.strip()

_TEMPLATE_WISH_WARNING_NOFOREIGN = r'''
{% if wish.hidden %}<p class="important warning">Ce souhait est une surprise !</p>{% endif %}
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
        <h4 class="important date">Créé le {{ wish.date_str() }}</h4>
        <p class="important kind">{{ wish.kind }}</p>
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

# --- END TEMPLATE : WISH LIST MAIN


TEMPLATE_WISH_VIEW_SELF_MAIN    = _template_wish_list_main(self=True,  foreign=False)
TEMPLATE_WISH_VIEW_OTHER_MAIN   = _template_wish_list_main(self=False, foreign=False)
TEMPLATE_WISH_VIEW_FOREIGN_MAIN = _template_wish_list_main(self=False, foreign=True)
TEMPLATE_WISH_VIEW_CLAIMED_MAIN = _template_wish_list_main(self=False, foreign=True)


###################################
#- Templates
####

SCRIPT_WISH = "/static/js/wish.js"

class Templates:
    INDEX = _template_generic('index', TEMPLATE_INDEX_PAGE)
    WISH_INDEX = _template_generic('wish', _template_wish_page(TITLE_WISH_INDEX, SUBTITLE_WISH_INDEX, TEMPLATE_WISH_INDEX_MAIN))
    WISH_EDITOR = _template_generic('wish', _template_wish_page(TITLE_WISH_EDITOR, SUBTITLE_WISH_EDITOR, TEMPLATE_WISH_EDITOR_MAIN))
    WISH_VIEW_OTHER_SELECT = _template_generic('wish', _template_wish_page(TITLE_WISH_VIEW_OTHER_SELECT, SUBTITLE_WISH_VIEW_OTHER_SELECT, TEMPLATE_WISH_VIEW_OTHER_SELECT_MAIN), SCRIPT_WISH)
    WISH_VIEW_SELF = _template_generic('wish', _template_wish_page(TITLE_WISH_VIEW_SELF, SUBTITLE_WISH_VIEW_SELF, TEMPLATE_WISH_VIEW_SELF_MAIN), SCRIPT_WISH)
    WISH_VIEW_OTHER = _template_generic('wish', _template_wish_page(TITLE_WISH_VIEW_OTHER, SUBTITLE_WISH_VIEW_OTHER, TEMPLATE_WISH_VIEW_OTHER_MAIN), SCRIPT_WISH)
    WISH_VIEW_FOREIGN = _template_generic('wish', _template_wish_page(TITLE_WISH_VIEW_FOREIGN, SUBTITLE_WISH_VIEW_FOREIGN, TEMPLATE_WISH_VIEW_FOREIGN_MAIN), SCRIPT_WISH)
    WISH_VIEW_CLAIMED = _template_generic('wish', _template_wish_page(TITLE_WISH_VIEW_CLAIMED, SUBTITLE_WISH_VIEW_CLAIMED, TEMPLATE_WISH_VIEW_CLAIMED_MAIN), SCRIPT_WISH)


if __name__ == '__main__':
    with open('wish/index.html', 'w') as file:
        file.write(Templates.WISH_INDEX)

    with open('wish/editor.html', 'w') as file:
        file.write(Templates.WISH_EDITOR)

    with open('wish/view-other-select.html', 'w') as file:
        file.write(Templates.WISH_VIEW_OTHER_SELECT)

    with open('wish/view-self.html', 'w') as file:
        file.write(Templates.WISH_VIEW_SELF)

    with open('wish/view-other.html', 'w') as file:
        file.write(Templates.WISH_VIEW_OTHER)

    with open('wish/view-foreign.html', 'w') as file:
        file.write(Templates.WISH_VIEW_FOREIGN)

    with open('wish/view-claimed.html', 'w') as file:
        file.write(Templates.WISH_VIEW_CLAIMED)

    with open('index.html', 'w') as file:
        file.write(Templates.INDEX)