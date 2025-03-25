class WishElement extends HTMLElement {
    get wishID () { return this.getAttribute(    'wid') }
    get kind   () { return this.getAttribute(   'kind') }
    get content() { return this.getAttribute('content') }

    get foreign() { return this.recipient.uid != this.maker.uid }

    set wishID (val) { this.setAttribute(    'wid', val) }
    set kind   (val) { this.setAttribute(   'kind', val) }
    set content(val) { this.setAttribute('content', val) }

    constructor() {
        super();
        this.recipient = this.childNodes[0];
        this.maker     = this.childNodes[1];
        this.claim     = this.childNodes[2]; // optional

        this.attachShadow({ mode: 'open' });

        this.shadowRoot.innerHTML = [
            `<block part="content">${this.content}</block>`,
            ['', `<p part="foreign">Ce souhait a été créé par ${this.maker.name}</p>`][this.foreign],
        ].join('');
        console.log(this);
    }
}

customElements.define('x-wish', WishElement);