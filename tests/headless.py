#!/usr/bin/python3
"""Verify the distributable in an isolated GNOME Shell session."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
METADATA = json.loads((ROOT / 'metadata.json').read_text())
UUID = METADATA['uuid']
VERSION = METADATA['version']
SHELL_VERSION = subprocess.check_output(['gnome-shell', '--version'], text=True).strip().split()[-1]
SHELL_MAJOR = SHELL_VERSION.split('.')[0]


def stage():
    with tempfile.TemporaryDirectory(prefix='app-grid-extended-check-', ignore_cleanup_errors=True) as temporary:
        base = Path(temporary)
        extension = base / 'data/gnome-shell/extensions' / UUID
        extension.mkdir(parents=True)
        with zipfile.ZipFile(ROOT / f'{UUID}_v{VERSION}.zip') as archive:
            archive.extractall(extension)
        helper = extension.parent / 'grid-check-helper@local'
        helper.mkdir()
        (helper / 'metadata.json').write_text(json.dumps({
            'uuid': helper.name, 'name': 'Private verification helper',
            'description': 'Private test bus only', 'shell-version': [SHELL_MAJOR],
        }))
        (helper / 'extension.js').write_text('''
import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';
export default class Helper extends Extension {
    enable() { global.context.unsafe_mode = true; }
    disable() { global.context.unsafe_mode = false; }
}
''')
        runtime = base / 'runtime'
        runtime.mkdir(mode=0o700)
        env = dict(os.environ, GRID_CHECK_CHILD='1', GRID_CHECK_EXTENSION=str(extension),
                   GIO_USE_VFS='local', XDG_DATA_HOME=str(base / 'data'),
                   XDG_CONFIG_HOME=str(base / 'config'), XDG_CACHE_HOME=str(base / 'cache'),
                   XDG_STATE_HOME=str(base / 'state'), XDG_RUNTIME_DIR=str(runtime))
        env.pop('DISPLAY', None)
        env.pop('WAYLAND_DISPLAY', None)
        try:
            return subprocess.call(['dbus-run-session', '--', '/usr/bin/python3', __file__], env=env)
        finally:
            # GTK can activate a document portal with a private FUSE mount.
            document_mount = runtime / 'doc'
            if os.path.ismount(document_mount):
                unmount = subprocess.run(['fusermount3', '-u', str(document_mount)], capture_output=True)
                if unmount.returncode and os.path.ismount(document_mount):
                    unmount.check_returncode()
            time.sleep(.3)


def inspect():
    import gi
    from gi.repository import Gio, GLib
    output = ROOT / 'validation'
    output.mkdir(exist_ok=True)
    settings = Gio.Settings.new('org.gnome.shell')
    settings.set_strv('enabled-extensions', ['grid-check-helper@local', UUID])
    settings.set_boolean('disable-user-extensions', False)
    settings.set_string('welcome-dialog-last-shown-version', '999')
    Gio.Settings.new('org.gnome.desktop.notifications').set_boolean('show-banners', False)
    Gio.Settings.sync()
    log = (output / f'gnome{SHELL_MAJOR}-session.log').open('w')
    shell = subprocess.Popen(['gnome-shell', '--headless', '--wayland', '--no-x11',
                              '--virtual-monitor=1440x1000'], stdout=log, stderr=log)
    bus = Gio.bus_get_sync(Gio.BusType.SESSION, None)

    def evaluate(code):
        ok, value = bus.call_sync('org.gnome.Shell', '/org/gnome/Shell', 'org.gnome.Shell',
            'Eval', GLib.Variant('(s)', (code,)), GLib.VariantType.new('(bs)'),
            Gio.DBusCallFlags.NONE, 5000, None).unpack()
        if not ok:
            raise RuntimeError(value)
        return json.loads(value) if value else None

    results = {'shell-version': SHELL_VERSION}

    def check(name, code):
        value = evaluate(code)
        results[name] = value
        if not value:
            raise AssertionError(name)

    try:
        for _ in range(120):
            if shell.poll() is not None:
                raise RuntimeError('Shell exited; see validation session log')
            try:
                if evaluate(f'Main.extensionManager.lookup({json.dumps(UUID)})?.state === 1'):
                    break
            except Exception:
                pass
            time.sleep(.25)
        else:
            raise RuntimeError('Extension did not enable')
        time.sleep(3)
        evaluate(f'globalThis.soft = Main.extensionManager.lookup({json.dumps(UUID)}).stateObj;')
        evaluate('''globalThis.grid = Main.overview._overview.controls.appDisplay;
            Main.overview.showApps(); Main.overview.dash.showAppsButton.checked=true;
            globalThis.icons = root => {
                const found=[];
                const walk=a=>{if(a instanceof imports.gi.St.Icon)found.push(a);
                    for(const c of a.get_children())walk(c);};
                walk(root);
                return found.filter(a=>{for(let p=a.get_parent();p;p=p.get_parent())
                    if(p.has_style_class_name?.('overview-icon'))return true;return false;});
            };
            globalThis.shadow = a => {const s=a.get_theme_node().get_shadow('icon-shadow');
                return s?[s.xoffset,s.yoffset,s.blur,s.color.alpha]:null;};
            globalThis.matches = root => {
                const s=soft._settings, scale=soft._context.scale_factor;
                const expected=[s.get_int('icon-shadow-offset-x')*scale,
                    s.get_int('icon-shadow-offset-y')*scale,s.get_int('icon-shadow-blur')*scale,
                    Math.round(s.get_int('icon-shadow-intensity')*255/100)];
                return icons(root).length>0 && icons(root).every(a=>{
                    const actual=shadow(a);return actual && actual.every((v,i)=>Math.abs(v-expected[i])<=0.51);});
            };
        ''')
        time.sleep(2)
        check('default-grid-shadow', 'matches(grid)')
        evaluate('globalThis.dashBefore=JSON.stringify(icons(Main.overview.dash).map(shadow));')
        for name, values in [('custom', [73, -9, 11, 0]),
                             ('upper', [100, 32, 32, 32]), ('lower', [0, -32, -32, 0])]:
            evaluate(f'''['icon-shadow-intensity','icon-shadow-offset-x','icon-shadow-offset-y',
                'icon-shadow-blur'].forEach((key,i)=>soft._settings.set_int(key,{json.dumps(values)}[i]));''')
            check(f'{name}-live-shadow', 'matches(grid)')
        evaluate("soft._settings.set_int('icon-shadow-intensity',73);")
        evaluate('globalThis.oldTheme=soft._context.get_theme(); Main.loadTheme();')
        check('theme-replaced', 'soft._context.get_theme()!==oldTheme')
        check('theme-reload-shadow', 'matches(grid)')
        check('old-theme-cleanup', '!oldTheme.get_custom_stylesheets().some(f=>f.equal(soft._file))')
        evaluate('globalThis.oldScale=soft._context.scale_factor; soft._context.scale_factor=2;')
        check('scaled-shadow', 'matches(grid)')
        evaluate('soft._context.scale_factor=oldScale;')
        evaluate('globalThis.folder=grid._folderIcons.find(f=>f.visible); folder.open();')
        time.sleep(.8)
        check('folder-shadow', 'matches(folder._dialog)')
        check('dash-unaffected', 'JSON.stringify(icons(Main.overview.dash).map(shadow))===dashBefore')
        evaluate('folder._dialog.popdown(); globalThis.shadowFile=soft._file;')
        evaluate(f'Main.extensionManager.disableExtension({json.dumps(UUID)});')
        check('disable-cleans-style', "icons(grid).every(a=>a.get_theme_node().get_shadow('icon-shadow')===null)")
        check('disable-removes-file', '!shadowFile.query_exists(null)')
        check('disable-removes-stylesheet', '!imports.gi.St.ThemeContext.get_for_stage(global.stage).get_theme().get_custom_stylesheets().some(f=>f.equal(shadowFile))')
        evaluate(f'Main.extensionManager.enableExtension({json.dumps(UUID)});')
        evaluate(f'globalThis.soft=Main.extensionManager.lookup({json.dumps(UUID)}).stateObj;')
        check('reenable-saved-settings', "soft._settings.get_int('icon-shadow-intensity')===73 && matches(grid)")
        env = dict(os.environ, WAYLAND_DISPLAY=evaluate('GLib.getenv("WAYLAND_DISPLAY")'),
                   GDK_BACKEND='wayland',
                   GI_TYPELIB_PATH='/usr/lib64/gnome-shell/girepository-1.0:/usr/lib64/gnome-shell')
        preferences = subprocess.run(['gjs', '-m', str(ROOT / 'tests/prefs.js'),
                                     os.environ['GRID_CHECK_EXTENSION']], env=env,
                                    capture_output=True, text=True, timeout=30)
        results['preferences'] = {'passed': preferences.returncode == 0,
                                  'output': preferences.stdout.strip()}
        if preferences.returncode:
            raise RuntimeError(preferences.stderr)
        time.sleep(.3)
        check('reset-applied-live', "soft._settings.get_int('icon-shadow-intensity')===24 && matches(grid)")
        results['passed'] = True
        (output / f'gnome{SHELL_MAJOR}-results.json').write_text(json.dumps(results, indent=2) + '\n')
        print(json.dumps(results, indent=2))
    finally:
        shell.terminate()
        try:
            shell.wait(timeout=10)
        except subprocess.TimeoutExpired:
            shell.kill()
            shell.wait()
        log.close()


if __name__ == '__main__':
    if os.environ.get('GRID_CHECK_CHILD'):
        inspect()
    else:
        sys.exit(stage())
