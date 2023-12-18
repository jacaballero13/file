odoo.define('metrotiles_partners.config', function (require) {
    return [
        {title: 'Customers', context: 'is_creating_customer'},
        {title: 'Product Vendors', context: 'is_creating_product_vendor'},
        {title: 'Architects', context: 'is_creating_architect'},
        {title: 'Interior Designers', context: 'is_creating_interior_designer'}
    ];
});

odoo.define('metrotiles_partners.toolbar', function (require) {
    "use strict";

    var partnerConfig = require("metrotiles_partners.config");
    var core = require('web.core');
    var ListView = require('web.ListView');
    var ListController = require("web.ListController");
    var KanbanController = require("web.KanbanController");
    var self;
    var partner;

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

            partner = partnerConfig.find(value => value.title == this._title)

            if (this.modelName === 'res.partner' && partner) {
                const createBtn = this.$buttons.find('button.o_list_button_add');

                if (createBtn.length) {
                    createBtn[0].classList.add('d-none');
                }

                this.$buttons.prepend('<button type="button" class="btn btn-primary ' + partner.context + '"\n' +
                    '                            t-if="widget.modelName == \'res.partner\' and widget._title == \'' + partner.title + '\'">Create</button>');

                const customCreateBtn = this.$buttons.find('button.' + partner.context);

                customCreateBtn.on('click', this.proxy('open_res_partner_form'));
            }
        },
        open_res_partner_form: () => open_res_partner_form(partner.title, {[partner.context]: 1}),
    });

    KanbanController.include({
        renderButtons: function () {
            this._super.apply(this, arguments);

            self = this;

            partner = partnerConfig.find(value => value.title == this._title)


            if (this.modelName === 'res.partner' && partner) {

                if (this.modelName === 'res.partner' && partner && this.$buttons.find('button.o-kanban-button-new').length > 0) {
                    const createBtn = this.$buttons.find('button.o-kanban-button-new')

                    if (createBtn.length) {
                        createBtn[0].classList.add('d-none');
                    }

                    this.$buttons.prepend('<button type="button" class="btn btn-primary ' + partner.context + '" t-if="widget.modelName == \'res.partner\' and widget._title == \'Product Vendors\'">Create</button>');
                }


                const customCreateBtn = this.$buttons.find('button.' + partner.context);

                customCreateBtn.on('click', this.proxy('open_res_partner_form'));
            }
        },
        open_res_partner_form: () => open_res_partner_form(partner.title, {[partner.context]: 1}),
    });
});