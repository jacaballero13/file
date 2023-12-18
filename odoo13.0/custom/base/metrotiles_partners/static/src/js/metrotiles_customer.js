odoo.define('metrotiles_customer.config', function (require) {
    return {title: 'Customers'};
});

odoo.define('metrotiles_customer.toolbar', function (require) {
    "use strict";

    var customerConfig = require("metrotiles_customer.config");
    var core = require('web.core');
    var ListView = require('web.ListView');
    var ListController = require("web.ListController");
    var KanbanController = require("web.KanbanController");
    var self;

    function open_res_partner_form(name, context) {
        self.do_action({
            name,
            type: 'ir.actions.act_window',
            res_model: 'res.partner',
            target: 'current',
            views: [[false, 'form']],
            view_type: 'form',
            view_mode: 'form',
            context,
        });
    }

    ListController.include({
        renderButtons: function () {
            this._super.apply(this, arguments)

            self = this;

            if (this.modelName === 'res.partner' && customerConfig.title === this._title) {
                this.$buttons.prepend('<button type="button" class="btn btn-primary o_list_creating_customer"\n' +
                    '                            t-if="widget.modelName == \'res.partner\' and widget._title == \'Customers\'">Add Customer</button>');


                const o_list_creating_customer = this.$buttons.find('button.o_list_creating_customer');
                const createBtn = this.$buttons.find('button.o_list_button_add');

                if (createBtn.length) {
                    createBtn[0].classList.add('d-none');
                }

                o_list_creating_customer.on('click', this.proxy('open_res_partner_customer_form'));
            }
        },
        open_res_partner_customer_form: () => open_res_partner_form('Product Vendor', {'is_creating_customer': 1}),
    });

    KanbanController.include({
        renderButtons: function () {
            this._super.apply(this, arguments);

            self = this;

            if (this.modelName === 'res.partner' && customerConfig.title === this._title) {

                if (this.modelName === 'res.partner' && customerConfig.title === this._title && this.$buttons.find('button.o-kanban-button-new').length > 0) {
                    const createBtn = this.$buttons.find('button.o-kanban-button-new')

                    if (createBtn.length) {
                        createBtn[0].classList.add('d-none');
                    }

                    this.$buttons.prepend('<button type="button" class="btn btn-primary o_kanban_is_creating_customer" t-if="widget.modelName == \'res.partner\' and widget._title == \'Customers\'">Add Customer</button>');
                }


                const o_kanban_is_creating_customer = this.$buttons.find('button.o_kanban_is_creating_customer');

                o_kanban_is_creating_customer.on('click', this.proxy('open_res_partner_creating_customer_form'));
            }
        },
        open_res_partner_creating_customer_form: () => open_res_partner_form('Customers', {'is_creating_customer': 1}),
    });
});