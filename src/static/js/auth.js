const form = document.getElementById('authform');
const err  = document.getElementById('err');
const action = form.getAttribute('action');

console.log('form:', form);
console.log('err:', err);
console.log('action:', action);

form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const response = await fetch(action, { method: 'POST', body: new FormData(form) });

    if (!response.ok) {
        err.innerText = (await response.json())['err'];
        return;
    }

    location.reload();
});