odoo.define('metrotiles.quotation_location_subtotal', function (require) {
    var core = require('web.core');
    var session = require('web.session');
    var fieldRegistry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var fieldUtils = require('web.field_utils');
    var QWeb = core.qweb;


    var locations_subtotal = AbstractField.extend({
        _render: function () {
            var self = this;
            datas = self.recordData.location_subtotal_group

            let currency;

            if (this.record.data.currency_id.data) {
                currency = session.get_currency(this.record.data.currency_id.data.id)
            }

            datas = datas.map(value => {
                let amount;

                if (currency) {
                    amount = fieldUtils.format.float(value[1], null, {digits: currency.digits});
                    amount = currency.position == 'before' ? ` ${currency.symbol}${amount}` : `${amount}${currency.symbol}`
                } else {
                    amount = value[1];
                }

                return {name: value[0], amount}

            })
            this.$el.html($(QWeb.render('LocationsSubtotal', {
                datas
            })));
        }
    });
    fieldRegistry.add('metrotiles_location_subtotal', locations_subtotal);
});