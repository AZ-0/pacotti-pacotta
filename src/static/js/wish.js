class WishElement extends HTMLElement {
    get wishID () { return this.getAttribute(    'wid') }
    get kind   () { return this.getAttribute(   'kind') }
    get content() { return this.getAttribute('content') }
    get hiddenFromRecipient() { return this.hasAttribute('x-hidden') }

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

        const parts = [
            `<p part="content">${this.content}</p>`,
            '<span part="warnings">',
        ];
        if (this.foreign)
            parts.push(`<span part="warning"><span part="warning-sign">⚠</span> Ce souhait a été créé par ${this.maker.name}</span>`);
        if (this.hiddenFromRecipient)
            parts.push(`<span part="warning"><span part="warning-sign">⚠</span> ${this.recipient.name} n'est pas au courant de ce souhait</span>`);
        parts.push('<span/>');

        this.shadowRoot.innerHTML = parts.join('')
        console.log(this);
    }
}

customElements.define('x-wish', WishElement);