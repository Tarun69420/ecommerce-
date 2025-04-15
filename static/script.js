document.addEventListener('DOMContentLoaded', (event) => {
    let count = 0;

    const button = document.getElementById('incrementButton');
    const display = document.getElementById('displayNumber');
    count = display.innerHTML;
    button.addEventListener('click', () => {
        count++;
        display.innerHTML = count;
    });
});
