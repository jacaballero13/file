from odoo import models, fields, api

class GroupByOrderlineByLocation(models.Model):
    _inherit = 'sale.order'

    location_subtotal_group = fields.Binary(string="Location Subtotal", compute="location_group_order_line")
    location_variant_group = fields.Binary(string="Location Variant Group", compute="location_group_order_line")

    def group_order_lines_by_location(self, vals_list):
        sections = []
        order_line = []
        no_location = []
        biggest_sequence = 0

        for line in vals_list.get('order_line', []):
            location_id = line[2].get('location_id', 0)

            if location_id > 0:
                location = self.env['metrotiles.location'].sudo().search([('id', '=', location_id)], order='id asc',
                                                                         limit=1)

                if not location.name in sections:
                    sections.append(location.name)
                    seq_no = sections.index(location.name) + 2 if len(sections) > 0 else 1
                    biggest_sequence = seq_no if biggest_sequence < seq_no else biggest_sequence

                    order_line.append([0, 0, {
                        'sequence': seq_no,
                        'display_type': 'line_section',
                        'name': location.name,
                    }])

                    for l in vals_list.get('order_line', []):
                        if l[2].get('location_id', 0) == location_id:
                            l[2]['sequence'] = seq_no + 1
                            order_line.append(l)
            else:
                no_location.append(line)

        if len(no_location) > 0:
            order_line.append([0, 0, {
                'sequence': biggest_sequence + 2,
                'display_type': 'line_section',
                'name': 'Location not specified',
            }])
            for nl in no_location:
                nl[2]['sequence'] = biggest_sequence + 3
            order_line.extend(no_location)
        vals_list['order_line'] = order_line

    def group_lines_by_section(self, section, lines):
        has_no_location_specified = False

        for line in lines:
            if line.location_id.name:
                if not section.get(line.location_id.name, False):
                    sec = self.env['sale.order.line'].sudo().create(
                        {'name': line.location_id.name, 'display_type': 'line_section', 'order_id': self.id})

                    section[line.location_id.name] = {'section': sec, 'items': []}
                section[line.location_id.name]['items'].append(line)
            else:
                if not section.get('Location not specified', False):
                    sec = self.env['sale.order.line'].sudo().create(
                        {'name': 'Location not specified', 'display_type': 'line_section', 'order_id': self.id})

                    section['Location not specified'] = {'section': sec, 'items': []}

                has_no_location_specified = True
                section['Location not specified']['items'].append(line)

    def update_order_line_sequence(self, section):
        section_keys = sorted(section.keys())
        index = 0
        deleted_key_section_count = 0

        for i, key in enumerate(section_keys):
            if len(section[key].get('items')) == 0:
                section[key].get('section').unlink()
                deleted_key_section_count += 1
                continue

            if key != 'Location not specified':
                index += 1
                section[key].get('section').update({'sequence': index})
                index += 1
                for item in section[key].get('items'):
                    item.update({'sequence': index})
            else:
                seq = ((len(section_keys)) - deleted_key_section_count) * 2 - 1
                section[key].get('section').update({'sequence': seq})

                for item in section[key].get('items'):
                    item.update({'sequence': seq + 1})

    def re_arrange_order_lines(self, values):
        re_arrange_order_line = False

        for line in values.get('order_line', []):
            operation = line[0]
            if operation == 4:
                continue
            elif operation == 1:
                if line[2].get('location_id', False):
                    re_arrange_order_line = True
                    break
            elif operation == 0 or operation == 2:
                re_arrange_order_line = True
                break

        if not re_arrange_order_line:
            return

        order_line = self.env['sale.order.line'].search([('order_id', '=', self.id)], order="id asc")
        sections = {}
        lines = []

        for line in order_line:
            if line.display_type == "line_section":
                if sections.get(line.name, False):
                    line.unlink()
                else:
                    sections[line.name] = {'section': line, 'items': []}
            else:
                lines.append(line)

        self.group_lines_by_section(sections, lines)
        self.update_order_line_sequence(sections)

    def create_new_group(self, vals):
        return {
            'price_total': vals.price_subtotal,
            'lines': [self.create_new_line(vals)]
        }

    def create_new_line(self, vals):
        discounts = None

        for discount in vals.discounts:
            discounts = discount.name if not discounts else '{}, {}'.format(discounts, discount.name)

        return {
            'product_tmpl_id': vals.product_id.product_tmpl_id.id,
            'location': vals.location_id.name,
            'application': vals.application_id.name,
            'factory': vals.factory_id.name_abbrev,
            'product': self.product_description_exlude_variant(vals),
            'product_display_name': vals.product_id.name,
            'qty': vals.product_uom_qty,
            'uom': vals.product_uom.name,
            'size': vals.size,
            'price_unit': vals.price_unit,
            'discounts': discounts,
            'price_net': vals.price_net,
            'price_subtotal': vals.price_subtotal,
            'display_type': None,
        }

    def product_description_exlude_variant(self, val):
        name = ''
        product = val.product_id
        attributes = product.product_template_attribute_value_ids
        attrs = []

        for value in attributes:
            if value.attribute_id.name != 'Variants':
                attrs.append(value.name)

        if len(attrs):
            name = "%s (%s)" % (product.name, ", ".join(attrs))
        else:
            name = val.name

        return name

    def append_if_not_exist(self, group, line):
        is_exist = False

        for l in group['lines']:
            line_name_excluded_variant = self.product_description_exlude_variant(line)

            if l.get('product_tmpl_id') == line.product_id.product_tmpl_id.id \
                    and l.get('price_unit') == line.price_unit \
                    and l.get('product') == line_name_excluded_variant\
                    and l.get('application') == line.application_id.name:

                is_exist = True

                l['qty'] += line.product_uom_qty
                l['price_subtotal'] += line.price_subtotal
                l['product'] = line_name_excluded_variant

                break

        if not is_exist:
            group['lines'].append(self.create_new_line(line))

    @api.depends('order_line.price_subtotal', 'partner_id')
    def location_group_order_line(self):
        for rec in self:
            group = {}
            location_subtotal = []
            location_variant_group = []

            for l in rec.order_line:
                if not l.display_type:
                    if l.location_id.name:
                        if not group.get(l.location_id.name):
                            group[l.location_id.name] = self.create_new_group(l)
                        else:

                            group[l.location_id.name]['price_total'] += l.price_subtotal
                            self.append_if_not_exist(group[l.location_id.name], l)
                    else:
                        if not group.get('Location not specified'):
                            group['Location not specified'] = self.create_new_group(l)
                        else:

                            print(l.price_subtotal)
                            group['Location not specified']['price_total'] += l.price_subtotal
                            self.append_if_not_exist(group['Location not specified'], l)

            for key in group.keys():
                location_subtotal.append((key, group.get(key).get('price_total')))

                location_variant_group.append({
                    'name': key,
                    'display_type': 'line_section'
                })

                location_variant_group.extend(group.get(key).get('lines'))

                location_variant_group.append({
                    'amount': group.get(key).get('price_total'),
                    'display_type': 'line_total'
                })

            rec.location_subtotal_group = location_subtotal
            rec.location_variant_group = location_variant_group

    @api.model
    def create(self, vals_list):
        self.group_order_lines_by_location(vals_list)

        return super(GroupByOrderlineByLocation, self).create(vals_list)

    def write(self, values):
        super(GroupByOrderlineByLocation, self).write(values)

        self.re_arrange_order_lines(values)
