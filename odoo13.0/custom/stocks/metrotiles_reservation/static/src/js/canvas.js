odoo.define('metrotiles.canvas', function (require) {
    var core = require('web.core');
    var rpc = require('web.rpc');
    var session = require('web.session');
    var fieldRegistry = require('web.field_registry');
    var AbstractField = require('web.AbstractField');
    var fieldUtils = require('web.field_utils');
    var QWeb = core.qweb;
    var context = null;
    var sizes = [];
    var rectTarget = null;
    var targetIndex = -1;
    var offsetX = 0;
    var offsetY = 0;
    var rawMaterial;
    var trashZone = {x: 670, y: 30, w: 100, h: 100};

    /**
     *
     *
     * @param this_
     */

    var FieldOne2Many = require('web.relational_fields').FieldOne2Many;
    var fieldRegistry = require('web.field_registry');
    var ListRenderer = require('web.ListRenderer');
    var config = require('web.config');
    var self = null;

    function startCanvas(this_) {
        context = document.getElementById('canvas').getContext('2d');
        addButton.onclick = addWidth;
        canvas.onmousedown = canvasOnClick
        canvas.onmousemove = canvasOnMouseMove;
        // canvas.onmousedown = canvasOnMouseDown
        // canvas.onmouseup = canvasOnMouseUp;
        size_ = self.recordData.size.split('x');
        rawMaterial = {x: 400 - ((size_[0] * 5) / 2), y: 400 - ((size_[1] * 5) / 2), w: size_[0] * 5, h: size_[1] * 5}
        drawRects();

        observeFabricate();
    }

    function observeFabricate() {
        document.getElementsByName('to_fabricate')[0].getElementsByTagName('input')
            [0].onchange = (event) => {
            if (event.target.checked) {
                self.trigger_up('field_changed', {
                    dataPointID: self.record.id,
                    changes: {
                        defined_tile_cuts: JSON.stringify(sizes)
                    },
                });
                startCanvas(self);
            }
            setTimeout(() => observeFabricate(), 100);
        }
    }

    function drawRects() {
        const len = sizes.length;

        context.clearRect(0, 0, 800, 800);
        context.fillStyle = '#fff';
        context.fillRect(rawMaterial.x, rawMaterial.y, rawMaterial.w, rawMaterial.h);
        context.strokeRect(rawMaterial.x, rawMaterial.y, rawMaterial.w, rawMaterial.h);

        drawTrashZone();

        for (let i = 0; i < len; i++) {
            context.strokeRect(sizes[i].x, sizes[i].y, sizes[i].w * 5, sizes[i].h * 5);
            console.log(sizes[i]);
            if (!sizes[i].valid) {
                context.fillStyle = 'rgba(255,0,0, 0.3)';
                context.fillRect(sizes[i].x, sizes[i].y, sizes[i].w * 5, sizes[i].h * 5);
            } else {
                context.fillStyle = 'rgba(0, 255, 4, 0.3)';
                context.fillRect(sizes[i].x, sizes[i].y, sizes[i].w * 5, sizes[i].h * 5);
            }

            context.fillStyle = '#000';
            if (sizes[i].w <= 11) {
                context.font = "10px Verdana";
                context.fillText(`${sizes[i].w}x${sizes[i].h}`, sizes[i].x + 2, sizes[i].y + 15);

            } else {
                context.font = "14px Verdana";
                context.fillText(`${sizes[i].w}x${sizes[i].h}`, sizes[i].x + 5, sizes[i].y + 22);
            }
        }
    }

    function drawTrashZone() {
        // context.font = "10px Verdana";
        // context.textAlign = 'center';
        // context.fillText(`DROP HERE \n TO REMOVE`, trashZone.x + (trashZone.w / 2), trashZone.y + (trashZone.h / 2));
        // context.strokeRect(trashZone.x, trashZone.y, trashZone.w, trashZone.h);
    }

    function addWidth() {
        sizes.push({x: 0, y: 0, w: cutWidth.value, h: cutHeight.value, valid: true});
        drawRects();
        // self._r
        // self._rpc({
        //     model: "sale.order.line",
        //     method: 'defined_tile_cuts_',
        //     args: [],
        //     context: {},
        // }).then(function (res) {
        //     console.log('res',res);
        // });

    }

    function canvasOnClick(event) {
        const postX = event.clientX - canvas.getBoundingClientRect().left;
        const postY = event.clientY - canvas.getBoundingClientRect().top;

        if (!rectTarget) {
            const postX = event.clientX - canvas.getBoundingClientRect().left;
            const postY = event.clientY - canvas.getBoundingClientRect().top

            rectTarget = sizes.reverse().find((value, index) => {
                    const x = postX > value.x && postX < (value.x + (value.w * 5));
                    const y = postY > value.y && postY < (value.y + (value.h * 5));

                    if (x && y) {
                        offsetX = postX - value.x;
                        offsetY = postY - value.y;
                        targetIndex = index;
                    }

                    return (x && y);
                }
            );
        } else {
            if (!rectTarget) {
                return;
            }

            const x1 = rectTarget.x - rawMaterial.x;
            const y1 = rectTarget.y - rawMaterial.y;
            let targetError = false;

            if (Math.abs(x1) < 20) {
                rectTarget.x = rawMaterial.x;
            }

            if (Math.abs(y1) < 20) {
                rectTarget.y = rawMaterial.y;
            }

            for (let i = 0; i < sizes.length; i++) {
                if (targetIndex != i) {
                    const x = rectTarget.x - (sizes[i].x + (sizes[i].w * 5));
                    const y = rectTarget.y - sizes[i].y;
                    const x1 = rectTarget.x - sizes[i].x;
                    const y1 = rectTarget.y - (sizes[i].y + (sizes[i].h * 5));

                    if (Math.abs(x) < 20) {
                        rectTarget.x = (sizes[i].x + (sizes[i].w * 5));
                    }

                    if (Math.abs(x1) < 20) {
                        rectTarget.x = sizes[i].x;
                    }

                    if (Math.abs(y) < 20) {
                        rectTarget.y = sizes[i].y;
                    }

                    if (Math.abs(y1) < 20) {
                        rectTarget.y = (sizes[i].y + (sizes[i].h * 5));
                    }
                    ;
                }
            }

            for (let i = 0; i < sizes.length; i++) {
                if (targetIndex != i) {
                    const dx = (sizes[i].x + ((sizes[i].w * 5) / 2)) - (rectTarget.x + ((rectTarget.w * 5) / 2));
                    const dy = (sizes[i].y + ((sizes[i].h * 5) / 2)) - (rectTarget.y + ((rectTarget.h * 5) / 2));
                    if (
                        Math.sqrt(dx * dx) < (((sizes[i].w / 2) * 5) + ((rectTarget.w / 2) * 5)) &&
                        Math.sqrt(dy * dy) < (((sizes[i].h / 2) * 5) + ((rectTarget.h / 2) * 5))
                    ) {
                        targetError = true;
                    }
                }
            }

            sizes[targetIndex].valid = !targetError;
            drawRects();

            self.trigger_up('field_changed', {
                dataPointID: self.record.id,
                changes: {
                    defined_tile_cuts: JSON.stringify(sizes)
                },
            });

            rectTarget = null;
        }
        // console.log(postX, postY);
    }

    function canvasOnMouseMove(event) {
        if (rectTarget) {
            const postX = event.clientX - canvas.getBoundingClientRect().left;
            const postY = event.clientY - canvas.getBoundingClientRect().top;

            rectTarget.x = postX - offsetX;
            rectTarget.y = postY - offsetY;

            drawRects();
        }
    }

    function canvasOnMouseDown(event) {
        const postX = event.clientX - canvas.getBoundingClientRect().left;
        const postY = event.clientY - canvas.getBoundingClientRect().top

        rectTarget = sizes.reverse().find((value, index) => {
                const x = postX > value.x && postX < (value.x + (value.w * 5));
                const y = postY > value.y && postY < (value.y + (value.h * 5));

                if (x && y) {
                    offsetX = postX - value.x;
                    offsetY = postY - value.y;
                    targetIndex = index;
                }

                return (x && y);
            }
        );
    }

    function canvasOnMouseUp(event) {
        if (!rectTarget) {
            return;
        }

        const x1 = rectTarget.x - rawMaterial.x;
        const y1 = rectTarget.y - rawMaterial.y;
        let targetError = false;

        if (Math.abs(x1) < 20) {
            rectTarget.x = rawMaterial.x;
        }

        if (Math.abs(y1) < 20) {
            rectTarget.y = rawMaterial.y;
        }

        for (let i = 0; i < sizes.length; i++) {
            if (targetIndex != i) {
                const x = rectTarget.x - (sizes[i].x + (sizes[i].w * 5));
                const y = rectTarget.y - sizes[i].y;
                const x1 = rectTarget.x - sizes[i].x;
                const y1 = rectTarget.y - (sizes[i].y + (sizes[i].h * 5));

                if (Math.abs(x) < 20) {
                    rectTarget.x = (sizes[i].x + (sizes[i].w * 5));
                }

                if (Math.abs(x1) < 20) {
                    rectTarget.x = sizes[i].x;
                }

                if (Math.abs(y) < 20) {
                    rectTarget.y = sizes[i].y;
                }

                if (Math.abs(y1) < 20) {
                    rectTarget.y = (sizes[i].y + (sizes[i].h * 5));
                }
                ;
            }
        }

        for (let i = 0; i < sizes.length; i++) {
            if (targetIndex != i) {
                const dx = (sizes[i].x + ((sizes[i].w * 5) / 2)) - (rectTarget.x + ((rectTarget.w * 5) / 2));
                const dy = (sizes[i].y + ((sizes[i].h * 5) / 2)) - (rectTarget.y + ((rectTarget.h * 5) / 2));
                if (
                    Math.sqrt(dx * dx) < (((sizes[i].w / 2) * 5) + ((rectTarget.w / 2) * 5)) &&
                    Math.sqrt(dy * dy) < (((sizes[i].h / 2) * 5) + ((rectTarget.h / 2) * 5))
                ) {
                    targetError = true;
                }
            }
        }

        sizes[targetIndex].valid = !targetError;
        drawRects();

        self.trigger_up('field_changed', {
            dataPointID: self.record.id,
            changes: {
                defined_tile_cuts: JSON.stringify(sizes)
            },
        });

        rectTarget = null;
    }


    var fab_sizes = AbstractField.extend({
        _render: function () {
            self = this;
            sizes = JSON.parse(self.recordData.defined_tile_cuts || '[]');

            if (!document.getElementById('canvas')) {
                this.$el.html($(QWeb.render('Canvas')));
                setTimeout(() => startCanvas(this), 500);
            } else {
                this.$el.html($(QWeb.render('Canvas')));
                setTimeout(() => startCanvas(this), 1);
            }
        },
        setValue: function (value) {
            console.log(value);
        },

        getValue: function () {
            console.log(this.get('value'));
        },
    });

    /**
     *  one2many
     *
     */

    var SectionListRenderer = ListRenderer.extend({
        init: function (parent, state, params) {
            this.sectionFieldName = "is_page";
            this._super.apply(this, arguments);
        },
        _checkIfRecordIsSection: function (id) {
            var record = this._findRecordById(id);
            return record && record.data[this.sectionFieldName];
        },
        _findRecordById: function (id) {
            return _.find(this.state.data, function (record) {
                return record.id === id;
            });
        },
        /**
         * Allows to hide specific field in case the record is a section
         * and, in this case, makes the 'title' field take the space of all the other
         * fields
         * @private
         * @override
         * @param {*} record
         * @param {*} node
         * @param {*} index
         * @param {*} options
         */
        _renderBodyCell: function (record, node, index, options) {
            var $cell = this._super.apply(this, arguments);

            var isSection = record.data[this.sectionFieldName];

            if (isSection) {
                if (node.attrs.widget === "handle" || node.attrs.name === "random_questions_count") {
                    return $cell;
                } else if (node.attrs.name === "title") {
                    var nbrColumns = this._getNumberOfCols();
                    if (this.handleField) {
                        nbrColumns--;
                    }
                    if (this.addTrashIcon) {
                        nbrColumns--;
                    }
                    if (record.data.questions_selection === "random") {
                        nbrColumns--;
                    }
                    $cell.attr('colspan', nbrColumns);
                } else {
                    $cell.removeClass('o_invisible_modifier');
                    return $cell.addClass('o_hidden');
                }
            }
            return $cell;
        },
        /**
         * Adds specific classes to rows that are sections
         * to apply custom css on them
         * @private
         * @override
         * @param {*} record
         * @param {*} index
         */
        _renderRow: function (record, index) {
            var $row = this._super.apply(this, arguments);
            if (record.data[this.sectionFieldName]) {
                $row.addClass("o_is_section");
            }
            return $row;
        },
        /**
         * Adding this class after the view is rendered allows
         * us to limit the custom css scope to this particular case
         * and no other
         * @private
         * @override
         */
        _renderView: function () {
            var def = this._super.apply(this, arguments);
            self = this;

            return def.then(function () {
                // this.$el.html($(QWeb.render('Canvas')));
                self.$('table.o_list_table').addClass('o_section_list_view');
                self.$('table.o_list_table').parent().prepend($(QWeb.render('Canvas')));
                setTimeout(() => startCanvas(self), 1000);
            });
        },
        // Handlers
        /**
         * Overridden to allow different behaviours depending on
         * the row the user clicked on.
         * If the row is a section: edit inline
         * else use a normal modal
         * @private
         * @override
         * @param {*} ev
         */
        _onRowClicked: function (ev) {
            var parent = this.getParent();
            var recordId = $(ev.currentTarget).data('id');
            var is_section = this._checkIfRecordIsSection(recordId);
            if (is_section && parent.mode === "edit") {
                this.editable = "bottom";
            } else {
                this.editable = null;
            }
            this._super.apply(this, arguments);
        },
        /**
         * Overridden to allow different behaviours depending on
         * the cell the user clicked on.
         * If the cell is part of a section: edit inline
         * else use a normal edit modal
         * @private
         * @override
         * @param {*} ev
         */
        _onCellClick: function (ev) {
            var parent = this.getParent();
            var recordId = $(ev.currentTarget.parentElement).data('id');
            var is_section = this._checkIfRecordIsSection(recordId);
            if (is_section && parent.mode === "edit") {
                this.editable = "bottom";
            } else {
                this.editable = null;
                this.unselectRow();
            }
            this._super.apply(this, arguments);
        },
        /**
         * In this case, navigating in the list caused issues.
         * For example, editing a section then pressing enter would trigger
         * the inline edition of the next element in the list. Which is not desired
         * if the next element ends up being a question and not a section
         * @override
         * @param {*} ev
         */
        _onNavigationMove: function (ev) {
            this.unselectRow();
        },
    });

    var SectionFieldOne2Many = FieldOne2Many.extend({
        init: function (parent, name, record, options) {
            this._super.apply(this, arguments);
            this.sectionFieldName = "is_page";
            this.rendered = false;
        },
        /**
         * Overridden to use our custom renderer
         * @private
         * @override
         */
        _getRenderer: function () {
            if (this.view.arch.tag === 'tree') {
                return SectionListRenderer;
            }
            return this._super.apply(this, arguments);
        },
        /**
         * Overridden to allow different behaviours depending on
         * the object we want to add. Adding a section would be done inline
         * while adding a question would render a modal.
         * @private
         * @override
         * @param {*} ev
         */
        _onAddRecord: function (ev) {
            this.editable = null;
            if (!config.device.isMobile) {
                var context_str = ev.data.context && ev.data.context[0];
                var context = new Context(context_str).eval();
                if (context['default_' + this.sectionFieldName]) {
                    this.editable = "bottom";
                }
            }
            this._super.apply(this, arguments);
        },
    });
    fieldRegistry.add('canvas', fab_sizes);
})
;