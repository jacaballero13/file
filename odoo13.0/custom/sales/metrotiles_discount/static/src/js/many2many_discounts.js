odoo.define('metrotiles.discount.many2many.discount', function (require) {
    var core = require('web.core');
    var session = require('web.session');
    var fieldRegistry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var fieldUtils = require('web.field_utils');
    var QWeb = core.qweb;


    var discounts = AbstractField.extend({
        _render: function () {
            var self = this;
            const fieldName = self.nodeOptions.target_field;

            if (self.recordData[fieldName].data.length <= 0) {
                return false;
            }

            let untaxed_ammount = self.recordData.amount_untaxed;

            let currency;

            if (this.record.data.currency_id.data) {
                currency = session.get_currency(this.record.data.currency_id.data.id)
            }

            const discounts = self.recordData[fieldName].data.map(discount => {
                const dis = discount.data.display_name.split('%');
                const format = {discount_type: '', value: 0, amount: 0};
                format.value = +dis[0];

                if (dis.length > 1) {
                    percentAmount = untaxed_ammount * (format.value / 100);
                    untaxed_ammount -= percentAmount;

                    format.discount_type = 'percentage';

                    if (currency) {
                        format.amount = fieldUtils.format.float(percentAmount, null, {digits: currency.digits});
                        format.display_amount = currency.position == 'before' ? ` ${currency.symbol}${format.amount}` : `${format.amount}${currency.symbol}`
                    } else {
                        format.amount = percentAmount;
                        format.display_amount = percentAmount;
                    }

                } else {
                    untaxed_ammount -= format.value;

                    format.discount_type = 'amount';

                    if (currency) {
                        format.amount = fieldUtils.format.float(format.value, null, {digits: currency.digits});
                        format.display_amount = currency.position == 'before' ? `${currency.symbol}${format.amount}` : `${format.amount}${currency.symbol}`
                    } else {
                        format.amount = format.value;
                        format.display_amount = format.value;
                    }
                }

                return format;
            });

            this.$el.html($(QWeb.render('Many2ManyDiscountsReadOnly', {
                discounts,
                currency
            })));
        }
    });
    fieldRegistry.add('metrotiles_many2many_discount', discounts);
});