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
        Array.from(control.getElementsByClassName('modify')).forEach(
            button => button.addEventListener('click', onClickModify(grid, control))
        );
        Array.from(control.getElementsByClassName('delete')).forEach(
            button => button.addEventListener('click', onClickDelete(grid, control))
        );
    })
);
