var mr = (n) => Math.random() * (n || 1);
var bg = document.getElementById('bg');
var form = document.getElementsByClassName('app-form')[0];
var provider_select = document.getElementById('provider');
var action_select = document.getElementById('action');
var download_menu = document.getElementById('download');
var prepare_menu = document.getElementById('prepare');
var train_menu = document.getElementById('train');
var predict_menu = document.getElementById('predict');
var inputs = document.querySelectorAll('input');
var button = document.querySelector('button');
var menu_list = [download_menu, prepare_menu, train_menu, predict_menu];
var providers = {};
var provider = null;
var action = null;
var settings = {};

setTimeout(() => {
    const preloader = document.querySelector('.preloader');

    preloader.style.opacity = 0;
}, 500);

setTimeout(() => {
    const preloader = document.querySelector('.preloader');

    preloader.style.display = 'none';
}, 1000);

window.onresize = () => {
    if (window.innerWidth > 700) window.resizeTo(700, 1000);

    changeWindowSize();
};

form.onsubmit = (e) => {
    e.preventDefault();

    run();
}

provider_select.onchange = () => {
    action_select.removeAttribute('hidden');

    provider = provider_select.value;
}

action_select.onchange = () => {
    for (menu of menu_list) menu.setAttribute('hidden', true);

    menu_list[action_select.value].removeAttribute('hidden');

    action = parseInt(action_select.value);

    inputs[0].onchange()
}

for (let i = 0; i < inputs.length; i++) {
    inputs[i].onchange = () => {
        settings[inputs[i].name] = inputs[i].valueAsNumber;

        if (inputs[i].name == 'online') settings[inputs[i].name] = inputs[i].checked;

        if (action == 0 && settings.start && settings.count) button.disabled = false;
        
        else if (action == 1) button.disabled = false;

        else if (action == 2 && settings.multiplier) button.disabled = false;

        else if (action == 3) button.disabled = false;

        else button.disabled = true; 
    };
}

function initBackground() {
    bg.innerHTML = '';

    for (let i = 0; i < 100; i++) {
        dot = document.createElement('i');

        dot.style.top = wh / 2;
        dot.style.left = ww / 2;

        bg.appendChild(dot);
    }

    for (dot of bg.children) update(dot);
}

function update(dot) {
    s = mr(60) + 4;

    a = {
        left: mr(ww - s),
        top: mr(wh - s),
        width: s,
        height: s,
        opacity: mr(.8) + .1
    };

    d = mr(1000) + 900;

    Velocity(dot, a, d, function() { update(dot) });
}

function changeWindowSize() {
    ww = window.innerWidth;
    wh = window.innerHeight;
}

function run() {
    eel.run(provider, action, settings);
}

eel.expose(load_providers);

function load_providers(providers) {
    for (p in providers) {
        option = document.createElement('option');
        option.innerHTML = providers[p];
        option.value = p;

        provider_select.appendChild(option);
    }
}

changeWindowSize();
initBackground();

eel.load_providers();
