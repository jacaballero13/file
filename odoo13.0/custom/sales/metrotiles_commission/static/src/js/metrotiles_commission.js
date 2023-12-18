odoo.define('metrotiles_commission.config', function (require) {
        return {title: 'Architects and Interior Designers'};
});

odoo.define('metrotiles_commission.toolbar', function (require) {
    "use strict";

    var commissionConfig = require("metrotiles_commission.config");
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

            if (this.modelName === 'res.partner' && commissionConfig.title === this._title) {
                const o_create_architect = this.$buttons.find('button.o_list_create_architect');
                const o_create_interior_designer = this.$buttons.find('button.o_list_create_interior_designer');

                o_create_architect.on('click', this.proxy('open_res_partner__architect_form'));
                o_create_interior_designer.on('click', this.proxy('open_res_partner_interior_designer_form'));
            }
        },
        open_res_partner__architect_form: () =>  open_res_partner_form('Architect', {'is_creating_architect': 1}),
        open_res_partner_interior_designer_form:  () => open_res_partner_form('Interior Designer', {'is_creating_interior_designer': 1}),
    });

    KanbanController.include({
        renderButtons: function () {
            this._super.apply(this, arguments);

            self = this;

            if (this.modelName === 'res.partner' && commissionConfig.title === this._title) {
                const o_create_architect = this.$buttons.find('button.o_kanban_create_architect');
                const o_create_interior_designer = this.$buttons.find('button.o_kanban_create_interior_designer');

                o_create_architect.on('click', this.proxy('open_res_partner__architect_form'));
                o_create_interior_designer.on('click', this.proxy('open_res_partner_interior_designer_form'));

                if(this.modelName === 'res.partner' && commissionConfig.title === this._title && this.$buttons.find('button.o-kanban-button-new').length > 0) {
                    this.$buttons.find('button.o-kanban-button-new')[0].classList.add('d-none');
                }
            }
        },
        open_res_partner__architect_form: () => open_res_partner_form('Architect', {'is_creating_architect': 1}),
        open_res_partner_interior_designer_form:  () => open_res_partner_form('Interior Designer',{'is_creating_interior_designer': 1}),
    });
});