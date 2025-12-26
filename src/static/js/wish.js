const userID = document.getElementsByClassName('main')[0].getAttribute('userID');


function onClickModify(control) {
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
        Array.from(control.getElementsByClassName('modify')).forEach(
            button => button.addEventListener('click', onClickModify(control))
        );
        Array.from(control.getElementsByClassName('delete')).forEach(
            button => button.addEventListener('click', onClickDelete(grid, control))
        );
    })
);


function onSelectClaimant(selector) {
    const wishid = selector.getAttribute('wishid');

    return async (e) => {
        console.log("selector: ", selector);
        const claimant = selector.getAttribute('claimant');
        const claimantid = selector.getAttribute('claimantid');
        const claimed = claimantid != -1 && claimantid != userID;

        if (selector.value == -1) {
            msg = `Veux tu vraiment annuler la revendication de ce souhait ?${claimed ? `\nÇa se fait pas pour ${claimant}.` : ""}`
            if (!confirm(msg)) {
                selector.value = claimantid;
                return;
            }

            const response = await fetch('/wish/desist', {
                method: "post",
                body: new URLSearchParams({ 'wishid': wishid })
            });

            if (!response.ok) {
                alert(`Une erreur est survenue lors du désistement${claimed ? " forcé" : ""} (code ${response.status}):\n${response.json()['err']}`);
                selector.value = claimantid;
                return;
            }

            selector.classList.remove('claimed');
        }
        else {
            msg = `Veux tu vraiment revendiquer ce souhait ?${claimed ? `\n${claimant} était là en premier.` : ""}`
            if (!confirm(msg)) {
                selector.value = claimantid;
                return;
            }

            const response = await fetch('/wish/claim', {
                method: "post",
                body: new URLSearchParams({ 'wishid': wishid })
            });

            if (!response.ok) {
                alert(`Une erreur est survenue lors de la revendication (code ${response.status}):\n${response.json()['err']}`);
                selector.value = claimantid;
                return;
            }

            selector.classList.add('claimed');
        }

        selector.setAttribute('claimant', selector.options[selector.selectedIndex].text);
        selector.setAttribute('claimantid', selector.value);
    }
}

Array.from(document.getElementsByClassName('claimant')).forEach(selector => {
    selector.setAttribute('claimant', selector.options[selector.selectedIndex].text);
    selector.setAttribute('claimantid', selector.value);
    selector.addEventListener('change', onSelectClaimant(selector));
});


const form = document.getElementById('other-select-form')
if (form) {
    const user = document.getElementById('user')
    form.addEventListener('submit', event => {
        event.preventDefault()
        location.assign(`/wish/view/${user.value}`)
    })
}
