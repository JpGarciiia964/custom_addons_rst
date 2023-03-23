# -*- coding: utf-8 -*-
# Copyright 2018 Pierre Faniel
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class WebsiteConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    @api.depends("website_id")
    def has_google_tag_manager(self):
        self.has_google_tag_manager = bool(self.google_tag_manager_key)

    def inverse_has_google_tag_manager(self):
        if not self.has_google_tag_manager:
            self.google_tag_manager_key = False

    has_google_tag_manager = fields.Boolean(
        "Google Tag Manager",
        compute=has_google_tag_manager,
        inverse=inverse_has_google_tag_manager,
    )
    google_tag_manager_key = fields.Char(
        "Google Tag Manager Key",
        help="Container ID",
        related="website_id.google_tag_manager_key",
        readonly=False,
    )
