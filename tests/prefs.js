import Adw from 'gi://Adw';
import Gio from 'gi://Gio';
import GLib from 'gi://GLib';
import Gtk from 'gi://Gtk';

Gio.Resource.load('/usr/share/gnome-shell/org.gnome.Shell.Extensions.src.gresource')._register();
const root = ARGV[0];
const {default: Preferences} = await import(`file://${root}/prefs.js`);
const [, data] = GLib.file_get_contents(`${root}/metadata.json`);
const metadata = JSON.parse(new TextDecoder().decode(data));
metadata.dir = Gio.File.new_for_path(root);
metadata.path = root;
Adw.init();
const preferences = new Preferences(metadata);
const window = new Adw.PreferencesWindow();
preferences.fillPreferencesWindow(window);
const rows = [];
let reset;
function visit(widget) {
    if (widget instanceof Adw.SpinRow)
        rows.push(widget);
    if (widget instanceof Gtk.Button && widget.label === 'Restaurar')
        reset = widget;
    for (let child = widget.get_first_child(); child; child = child.get_next_sibling())
        visit(child);
}
visit(window);
function assert(value, message) {
    if (!value)
        throw new Error(message);
}
assert(rows.length === 4 && reset, 'Four controls and reset button');
const settings = preferences.getSettings();
const controls = [
    ['icon-shadow-intensity', 24, 0, 100, 73],
    ['icon-shadow-offset-x', 0, -32, 32, -9],
    ['icon-shadow-offset-y', 2, -32, 32, 11],
    ['icon-shadow-blur', 4, 0, 32, 0],
];
for (let i = 0; i < controls.length; i++) {
    const [key, standard, lower, upper, custom] = controls[i];
    const row = rows[i];
    settings.reset(key);
    assert(row.value === standard, `${key}: default`);
    assert(row.adjustment.lower === lower && row.adjustment.upper === upper, `${key}: range`);
    row.value = custom;
    assert(settings.get_int(key) === custom, `${key}: UI writes settings`);
    settings.set_int(key, upper);
    assert(row.value === upper, `${key}: settings update UI`);
    row.value = lower - 10;
    assert(settings.get_int(key) === lower, `${key}: clamps lower bound`);
    row.value = upper + 10;
    assert(settings.get_int(key) === upper, `${key}: clamps upper bound`);
}
reset.emit('clicked');
assert(controls.every(([key, standard], i) => settings.get_int(key) === standard &&
    rows[i].value === standard), 'Reset restores all four controls and settings');
window.close();
print('Preferences: bidirectional bindings, ranges and reset passed');
