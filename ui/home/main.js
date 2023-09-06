window.addEventListener('load', function() {
    setTimeout(function() {
        var preloader = document.querySelector('.preloader');

        preloader.style.opacity = 0;
    }, 500);

    setTimeout(function() {
        var preloader = document.querySelector('.preloader');

        preloader.style.display = 'none';
    }, 1000);
});

eel.expose(set_account_info);

function set_account_info(acc_name, player_icon) {
    account_name.innerHTML = acc_name;
    account_image.innerHTML = '<img src="' + player_icon + '">';
}

window.onresize = function() {
    if (window.innerWidth > 1280)
        window.resizeTo(1280, 800);
};
