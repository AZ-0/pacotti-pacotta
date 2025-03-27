const form = document.getElementById('authform');
const err  = document.getElementById('err');
const action = form.getAttribute('action');

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const response = await fetch(action, { method: 'POST', body: new FormData(form) });
    const data = await response.json();

    if (!response.ok) {
        err.innerText = data['err']
        return;
    }

    if (data['url'] != null) {
        location.assign(data['url']);
        return;
    }

    history.back();
});