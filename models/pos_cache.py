# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
import logging
import base64
import json
from odoo.exceptions import ValidationError, RedirectWarning, UserError

_logger = logging.getLogger(__name__)

class almouggar_pos_cache (models.Model):
    _name = 'pos.cache'
    _inherit = 'pos.cache'

    time_format = "%Y-%m-%d %H:%M:%S"

    @api.model
    def refresh_all_caches(self):
        self.env['pos.cache'].search([]).update_cache()

    @api.one
    def update_cache(self):
        # We decode the existing cache
        decoded_cache = json.loads(base64.decodestring(self.cache).decode('utf-8'))
        decoded_cache = self._remove_unavailable_products_from_decoded_cache(decoded_cache)
        decoded_cache = self._add_or_update_products_in_decoded_cache(decoded_cache)
        datas = {
            'cache': base64.encodestring(json.dumps(decoded_cache).encode('utf-8')),
        }
        self.write(datas)

    def _get_products_products_based_on_products_template(self, domain):
        products_template = self.env['product.template'].sudo(self.compute_user_id.id).search(domain)
        ids = list(map(lambda product_tml: product_tml.id,
                        products_template))
        return self.env['product.product'].sudo(self.compute_user_id.id).search([('product_tmpl_id', 'in', ids)])

    def _remove_unavailable_products_from_decoded_cache(self, decoded_cache):
        products_to_remove = self._get_products_products_based_on_products_template([
            ('write_date', '>', self.write_date.strftime(self.time_format)),
            '!', ('available_in_pos', '=', 'True')
        ])
        for prod in products_to_remove:
            index = next((index for (index, cache_elem) in enumerate(decoded_cache) if cache_elem['id'] == prod.id),
                         None)
            if index:
                decoded_cache.pop(index)
        return decoded_cache

    def _add_or_update_products_in_decoded_cache(self, decoded_cache):
        products = self._get_products_products_based_on_products_template(
            [['write_date', '>', self.write_date.strftime(self.time_format)]] +
            self.get_product_domain()
        )
        # prod_ctx.sudo(self.compute_user_id.id)
        prod_ctx = products.with_context(pricelist=self.config_id.pricelist_id.id, display_default_code=False,
                              lang=self.compute_user_id.lang)
        prod_ctx.sudo(self.compute_user_id.id)
        for prod in prod_ctx:
            index = next((index for (index, cache_elem) in enumerate(decoded_cache) if cache_elem['id'] == prod.id),
                         None)
            if index:
                decoded_cache[index] = prod.read(self.get_product_fields())[0]
            else:
                decoded_cache = decoded_cache + prod.read(self.get_product_fields())
        return decoded_cache
