odoo.define('metrotiles.commission.difference', function (require) {

        function checkSetVersionState(self_, field) {
            const saleOrder = self_.getParent().getParent();
            const orderLine = saleOrder.recordData[data.target_field];
            const orderLineChanges = saleOrder.recordData[data.parent_field];

            if (orderLine.data.find(line => line.data.id === self_.recordData.id)) {
                if (!self_.recordData.previous_version_id) {
                    self_.recordData['version_state'] = 'NEW';
                } else {
                    self_.recordData['version_state'] = 'DUPLICATED';
                }
            } else {
                const currentOrderLine = orderLine.data
                    .find(line => (line.data.previous_version_id || {data: {display_name: ''}}).data.display_name == self_.recordData.id);

                if (currentOrderLine) {
                    self_.recordData['version_state'] = 'MODIFIED';
                    self_.recordData['currentOrderLine'] = currentOrderLine;
                } else {
                    self_.recordData['version_state'] = 'REMOVED';
                }
            }
        }

        function check_version_state_new_if_changed(self_, field) {
            const watch_field = self_.nodeOptions.watch_field;

            self_.recordData['watched_field_changed'] = !!self_.recordData['is_' + watch_field + '_changed'];
        }

        function getDifference(self_, field) {
            if (!self_.recordData.version_state) {
                checkSetVersionState(self_, field);
            }

            if (self_.recordData.version_state === 'MODIFIED') {
                if (check_version_state_new_if_changed(self_, field)) {
                    self_.recordData[field] = self_.recordData[field] || 0;
                    self_.recordData['new_' + field] = self_.recordData.currentOrderLine.data[field] || 0;
                    self_.recordData['is_modified'] = true;
                } else {
                    self_.recordData['new_' + field] = self_.recordData.currentOrderLine.data[field];
                    self_.recordData['difference'] = self_.recordData['new_' + field] - self_.recordData[field];
                    self_.recordData['is_' + field + '_changed'] = self_.recordData['new_' + field] != self_.recordData[field];

                    if (!self_.recordData['is_modified']) {
                        self_.recordData['is_modified'] = self_.recordData['is_' + field + '_changed']
                    }
                }
            }
        }

        function getModifiedName(self_, field) {
            if (!self_.recordData.version_state) {
                checkSetVersionState(self_, field);
            }

            if (self_.recordData.version_state === 'NEW' || self_.recordData.version_state === 'REMOVED') {
                self_.recordData[field] = self_.recordData[field] || {data: {id: 0, display_name: ''}};
            } else if (self_.recordData.version_state === 'MODIFIED') {
                if (check_version_state_new_if_changed(self_, field)) {
                    self_.recordData[field] = self_.recordData[field] || {data: {id: 0, display_name: ''}};
                    self_.recordData['new_' + field] = self_.recordData.currentOrderLine.data[field] || {
                        data: {
                            id: 0,
                            display_name: ''
                        }
                    };
                    self_.recordData['is_modified'] = true;
                } else {
                    self_.recordData[field] = self_.recordData[field] || {data: {id: 0, display_name: ''}};
                    self_.recordData['new_' + field] = self_.recordData.currentOrderLine.data[field] || {
                        data: {
                            id: 0,
                            display_name: ''
                        }
                    };
                    self_.recordData['is_' + field + '_changed'] = self_.recordData['new_' + field].data.id != self_.recordData[field].data.id;

                    if (!self_.recordData['is_modified']) {
                        self_.recordData['is_modified'] = self_.recordData['is_' + field + '_changed']
                    }
                }
            }
        }

        function getStringChanges(self_, field) {
            if (!self_.recordData.version_state) {
                checkSetVersionState(self_, field);
            }

            if (self_.recordData.version_state === 'MODIFIED') {
                if (check_version_state_new_if_changed(self_, field)) {
                    self_.recordData[field] = self_.recordData[field] || 0;
                    self_.recordData['new_' + field] = self_.recordData.currentOrderLine.data[field] || '';
                    self_.recordData['is_modified'] = true;
                } else {
                    self_.recordData['new_' + field] = self_.recordData.currentOrderLine.data[field];
                    self_.recordData['is_' + field + '_changed'] = self_.recordData['new_' + field] != self_.recordData[field];

                    if (!self_.recordData['is_modified']) {
                        self_.recordData['is_modified'] = self_.recordData['is_' + field + '_changed']
                    }
                }
            }
        }

        var data = {target_field: null, parent_field: null, getDifference, getModifiedName, getStringChanges};

        return data;
    }
);

odoo.define('metrotiles.sale.amendment', function (require) {
    var core = require('web.core');
    var session = require('web.session');
    var fieldRegistry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var fieldUtils = require('web.field_utils');
    var orderLinesDiff = require('metrotiles.commission.difference');
    var QWeb = core.qweb;

    var discountDiffence = AbstractField.extend({
        _render: function () {
            var self = this;
            const fieldName = self.attrs.name;

            if(self.attrs.type === 'Legends') {
                this.$el.html($(QWeb.render('MetrotileSaleAmendmentLegends', null)));
                return;
            }

            orderLinesDiff.target_field = self.nodeOptions.target_field;
            orderLinesDiff.parent_field = self.nodeOptions.parent_field;

            switch (self.attrs.type) {
                case 'Many2one':
                    orderLinesDiff.getModifiedName(self, fieldName);

                    this.$el.html($(QWeb.render('MetrotileSaleAmendmentMany2one', {
                        line: self.recordData,
                        fieldName
                    })));

                    break;
                case 'Number':
                    orderLinesDiff.getDifference(self, fieldName);

                    this.$el.html($(QWeb.render('MetrotileSaleAmendmentNumber', {
                        line: self.recordData,
                        fieldName
                    })));

                    break;

                case 'Text':
                    orderLinesDiff.getStringChanges(self, fieldName);

                    this.$el.html($(QWeb.render('MetrotileSaleAmendmentString', {
                        line: self.recordData,
                        fieldName
                    })));

                    break;

                case 'Status':
                    this.$el.html($(QWeb.render('MetrotileSaleAmendmentStatus', {
                        line: self.recordData,
                        fieldName
                    })));
            }
        }
    });
    fieldRegistry.add('metrotiles-sale-amendment-changes', discountDiffence);
});

