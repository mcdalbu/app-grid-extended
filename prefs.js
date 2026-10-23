// SPDX-License-Identifier: GPL-2.0-or-later
import Adw from 'gi://Adw';
import Gio from 'gi://Gio';
import Gtk from 'gi://Gtk';
import {ExtensionPreferences} from 'resource:///org/gnome/Shell/Extensions/js/extensions/prefs.js';

export default class AppGridSoftPreferences extends ExtensionPreferences {
    fillPreferencesWindow(window) {
        const settings = this.getSettings();
        const page = new Adw.PreferencesPage({
            title: 'Aparência', icon_name: 'preferences-desktop-appearance-symbolic',
        });
        const group = new Adw.PreferencesGroup({
            title: 'Sombra dos ícones',
            description: 'Aplicada ao vivo na grade de aplicativos e nas pastas. A cor da sombra é preta.',
        });
        window.add(page);
        page.add(group);

        const keys = [];
        for (const [key, title, subtitle, lower, upper] of [
            ['icon-shadow-intensity', 'Opacidade (%)', '0% transparente; 100% opaca.', 0, 100],
            ['icon-shadow-offset-x', 'Deslocamento horizontal (px)',
                'Valores negativos movem para a esquerda; positivos, para a direita.', -32, 32],
            ['icon-shadow-offset-y', 'Deslocamento vertical (px)',
                'Valores negativos movem para cima; positivos, para baixo.', -32, 32],
            ['icon-shadow-blur', 'Desfoque (px)', 'Zero produz uma sombra nítida.', 0, 32],
        ]) {
            const row = new Adw.SpinRow({
                title, subtitle, digits: 0,
                adjustment: new Gtk.Adjustment({
                    lower, upper, step_increment: 1, page_increment: 5,
                }),
            });
            settings.bind(key, row, 'value', Gio.SettingsBindFlags.DEFAULT);
            group.add(row);
            keys.push(key);
        }

        const reset = new Adw.ActionRow({
            title: 'Restaurar os padrões',
            subtitle: 'Opacidade 24%, horizontal 0 px, vertical 2 px e desfoque 4 px.',
        });
        const button = new Gtk.Button({label: 'Restaurar', valign: Gtk.Align.CENTER});
        button.connect('clicked', () => {
            for (const key of keys)
                settings.reset(key);
        });
        reset.add_suffix(button);
        reset.activatable_widget = button;
        group.add(reset);
    }
}
