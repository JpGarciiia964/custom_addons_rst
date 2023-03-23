/* Copyright 2019 Adgensee - Vincent Garcies
 * License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl.html). */

odoo.define("website_snippet_html.html_option", function (require) {
    "use strict";
    var core = require("web.core");
    var options = require("web_editor.snippets.options");
    var utils = require("website.utils");
    var _t = core._t;

    /**
     * Option for editing html snippet
     */
    options.registry.snippet_html = options.Class.extend({

        /**
         * Let user edit HTML
         */
        html_ask: function (previewMode, value) {
            var self = this;
            var def = utils.prompt({
                'id': 'website_snippet_html_ask',
                "window_title": _t("Edit HTML"),
                "textarea": _t("Edit html"),
                "default": this.$target.html(),
            }).done(this.html_update.bind(this));
        },

        /**
         * Update HTML
         */
        html_update: function (new_html, $textarea, $dialog) {
            this.$target.html(new_html);
        },

        onBuilt: function () {
            var self = this;
            this._super();
            this.html_ask('click').guardedCatch(function () {
                self.getParent()._onRemoveClick($.Event( "click" ));
            });
        },        

    });

    // return {
    //     Option: options.registry.html,
    // };
});
