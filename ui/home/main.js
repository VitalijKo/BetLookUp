var mr = (n) => Math.random() * (n || 1);
var bg = document.getElementById('bg');
var form = document.querySelector('.app-form');
var provider_select = document.getElementById('provider');
var action_select = document.getElementById('action');
var download_menu = document.getElementById('download');
var process_menu = document.getElementById('process');
var train_menu = document.getElementById('train');
var predict_menu = document.getElementById('predict');
var inputs = document.querySelectorAll('input');
var button = document.querySelector('button');
var logs = document.getElementById('logs');
var menu_list = [download_menu, process_menu, train_menu, predict_menu];
var providers = {};
var provider = null;
var action = null;
var settings = {};
var running = false;

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

    if (!running) eel.run(provider, action, settings)();

    running = !running;
    button.innerHTML = running ? 'STOP' : 'RUN';
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

eel.expose(load_providers);

function load_providers(providers) {
    for (p in providers) {
        option = document.createElement('option');
        option.innerHTML = providers[p];
        option.value = p;

        provider_select.appendChild(option);
    }
}

eel.expose(get_running);

function get_running() {
    return running;
}

eel.expose(stop);

function stop() {
    running = false;
    button.innerHTML = 'RUN';
}

eel.expose(log);

function log(message) {
    if (!message) logs.innerHTML = '';

    else {
        p = document.createElement('p');

        logs.appendChild(p);

        var typed = new Typed(p, {
            strings: [message],
            stringsElement: null,
            typeSpeed: 20,
            showCursor: false,
            autoInsertCss: true,
            attr: null,
            contentType: 'html'
        });
    }
}

provider_select.onchange = () => {
    action_select.removeAttribute('hidden');

    provider = provider_select.value;
}

action_select.onchange = () => {
    for (menu of menu_list) menu.setAttribute('hidden', true);

    menu_list[action_select.value].removeAttribute('hidden');

    action = parseInt(action_select.value);

    inputs[0].onchange();
}

for (let i = 0; i < inputs.length; i++) {
    inputs[i].onchange = () => {
        settings[inputs[i].name] = inputs[i].valueAsNumber;

        if (inputs[i].name == 'online') settings[inputs[i].name] = inputs[i].checked;

        if (action == 0 && settings.start && settings.count) button.disabled = false;
        
        else if (action == 1 || action == 2) button.disabled = false;

        else if (action == 3) button.disabled = false;

        else button.disabled = true; 
    };
}

changeWindowSize();
initBackground();

eel.load_providers();
