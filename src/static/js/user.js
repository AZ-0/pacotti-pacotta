class UserElement extends HTMLElement {
    get uid()  { return this.getAttribute('uid') }
    get name() { return this.getAttribute('name') }
    get bday() { return this.getAttribute('bday') }

    constructor() {
        super();

        if (this.hasAttribute('disabled')) {
            this.removeAttribute('disabled');
            return;
        }

        this.attachShadow({ mode: 'open' });

        const parts = [
            `<span part="name">${this.name}</span>`
        ]

        this.shadowRoot.innerHTML = parts.join('');
    }
}

customElements.define('x-user', UserElement);