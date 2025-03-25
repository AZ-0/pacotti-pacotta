class UserElement extends HTMLElement {
    get uid()  { return this.getAttribute('uid') }
    get name() { return this.textContent }
    get bday() { return this.getAttribute('bday') }

    constructor() {
        super();
        this.hidden = true;
    }
}

customElements.define('x-user', UserElement);