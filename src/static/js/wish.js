class WishElement extends HTMLElement {
    get wishID () { return this.getAttribute( 'wishid') }
    get kind   () { return this.getAttribute(   'kind') }
    get content() { return this.getAttribute('content') }
    get hiddenFromRecipient() { return this.hasAttribute('x-hidden') }

    get foreign() { return this.recipient.uid != this.maker.uid }

    set wishID (val) { this.setAttribute( 'wishid', val) }
    set kind   (val) { this.setAttribute(   'kind', val) }
    set content(val) { this.setAttribute('content', val) }

    constructor() {
        super();
        this.recipient = this.childNodes[0];
        this.maker     = this.childNodes[1];
        this.claim     = this.childNodes[2]; // optional

        this.attachShadow({ mode: 'open' });

        const parts = [
            `<p part="content">${this.content}</p>`,
            '<div part="warnings">',
        ];
        if (this.foreign)
            parts.push(`<span part="warning"><span part="warning-sign">⚠</span> Ce souhait a été créé par ${this.maker.name}</span>`);
        if (this.hiddenFromRecipient)
            parts.push(`<span part="warning"><span part="warning-sign">⚠</span> ${this.recipient.name} n'est pas au courant de ce souhait</span>`);
        parts.push('<div/>');

        this.shadowRoot.innerHTML = parts.join('')
        console.log(this);
    }
}

customElements.define('x-wish', WishElement);



function onClickModify(grid, control) {
    return (e) => location.assign(`/wish/edit/${control.getAttribute('wishid')}`);
}


function onClickDelete(grid, control) {
    const wishid = control.getAttribute('wishid');

    return async (e) => {
        if (!confirm("Veux tu vraiment supprimer ce souhait ?"))
            return;

        const response = await fetch('/wish/delete', {
            method: "post",
            body: new URLSearchParams({ 'wishid': wishid })
        })

        if (!response.ok) {
            alert(`Une erreur est survenue lors de la suppression (code ${response.status}):\n${response.json()['err']}`);
            return;
        }

        Array.from(grid.children)
            .filter(child => child.getAttribute('wishid') == wishid)
            .forEach(child => grid.removeChild(child));
    }
}


Array.from(document.getElementsByClassName('wish-grid')).forEach(grid =>
    Array.from(grid.getElementsByClassName('control')).forEach(control => {
        control.getElementsByClassName('modify')[0]
            .addEventListener('click', onClickModify(grid, control));
        control.getElementsByClassName('delete')[0]
            .addEventListener('click', onClickDelete(grid, control));
    })
);
