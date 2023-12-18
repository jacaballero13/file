odoo.define('metrotiles_vendors.config', function (require) {
    return {title: 'Product Vendors'};
});

odoo.define('metrotiles_vendors.toolbar', function (require) {
    "use strict";

    var vendorConfig = require("metrotiles_vendors.config");
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

            if (this.modelName === 'res.partner' && vendorConfig.title === this._title) {
                const createBtn = this.$buttons.find('button.o_list_button_add');

                if (createBtn.length) {
                    createBtn[0].classList.add('d-none');
                }

                this.$buttons.prepend('<button type="button" class="btn btn-primary o_list_create_product_vendor"\n' +
                    '                            t-if="widget.modelName == \'res.partner\' and widget._title == \'Product Vendors\'">Add Vendor</button>');

                const o_list_create_product_vendor = this.$buttons.find('button.o_list_create_product_vendor');
                o_list_create_product_vendor.on('click', this.proxy('open_res_partner_product_vendor_form'));
            }
        },
        open_res_partner_product_vendor_form: () => open_res_partner_form('Product Vendor', {'is_creating_product_vendor': 1}),
    });

    KanbanController.include({
        renderButtons: function () {
            this._super.apply(this, arguments);

            self = this;

            if (this.modelName === 'res.partner' && vendorConfig.title === this._title) {

                if (this.modelName === 'res.partner' && vendorConfig.title === this._title && this.$buttons.find('button.o-kanban-button-new').length > 0) {
                    const createBtn = this.$buttons.find('button.o-kanban-button-new')

                    if (createBtn.length) {
                        createBtn[0].classList.add('d-none');
                    }

                    this.$buttons.prepend('<button type="button" class="btn btn-primary o_kanban_create_product_vendor" t-if="widget.modelName == \'res.partner\' and widget._title == \'Product Vendors\'">Add Vendor</button>');
                }


                const o_kanban_create_product_vendor = this.$buttons.find('button.o_kanban_create_product_vendor');

                o_kanban_create_product_vendor.on('click', this.proxy('open_res_partner_product_vendor_form'));
            }
        },
        open_res_partner_product_vendor_form: () => open_res_partner_form('Product Vendor', {'is_creating_product_vendor': 1}),
    });
});