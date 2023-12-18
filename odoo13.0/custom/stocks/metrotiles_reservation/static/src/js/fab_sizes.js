odoo.define('metrotiles.fab_sizes', function (require) {
    var core = require('web.core');
    var session = require('web.session');
    var fieldRegistry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var fieldUtils = require('web.field_utils');
    var QWeb = core.qweb;


    var fab_sizes = AbstractField.extend({
        _render: function () {
            var self = this;
            const data = {
                'size': this.recordData.size,
                'cut_sizes': this.recordData.cut_sizes_display
            };

            this.$el.html($(QWeb.render('FabSizes', {data})));
        }
    });
    fieldRegistry.add('metrotiles_fab_sizes', fab_sizes);
});