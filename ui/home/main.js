setTimeout(function() {
    const preloader = document.querySelector('.preloader');

    preloader.style.opacity = 0;
}, 500);

setTimeout(function() {
    const preloader = document.querySelector('.preloader');

    preloader.style.display = 'none';
}, 1000);

window.onresize = function() {
    if (window.innerWidth > 700) window.resizeTo(700, 1000);

    winsize();
};

var total = 100,
    px = true,
    fn = 'velocity',
    w = window,
    s, ww, wh, a = {},
    b, dots = [],
    dot, m = Math,
    mr = function(n) { return m.random() * (n || 1) };

function init() {
    $('#bg').empty();

    dots.length = 0;

    for (let i = 0; i < total; i++) dots.push($('<i/>').css({ top: px ? wh / 2 : '50%', left: px ? ww / 2 : '50%' }));

    $('#bg').append(dots);

    for (i in dots) update(i);
}

function update(n) {
    if (dot = dots[n]) {
        s = mr(60) + 4;

        a = {
            left: px ? mr(ww - s) : (mr(99) + '%'),
            top: px ? mr(wh - s) : (mr(99) + '%'),
            width: s,
            height: s,
            opacity: mr(.8) + .1
        };

        d = mr(1000) + 900;

        dot.animate(a, d, function() { update(n) });
    }
}

function winsize() {
    ww = $(w).width();
    wh = $(w).height();
}

$(function() {
    winsize();
    init();
});

// eel.expose(set_account_info);
// function set_account_info(acc_name, player_icon) {
//     account_name.innerHTML = acc_name;
//     account_image.innerHTML = '<img src="' + player_icon + '">';
// }

const checkbox = document.querySelector('.app-form input[type="checkbox"]');
const buttons = document.querySelectorAll('.app-form button');

checkbox.addEventListener('change', function() {
    const checked = this.checked;

    for (const button of buttons) button.disabled = !checked;
});
