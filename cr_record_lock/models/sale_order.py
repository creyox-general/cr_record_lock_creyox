# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class SaleOrder(models.Model):
    _inherit = "sale.order"

    locked = fields.Boolean(string="Locked", default=False)

    def action_lock_manual(self):
        """Lock records manually (no time interval)."""
        for rec in self:
            rec.locked = True
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Locked"),
                "message": _("Selected sale orders are now locked."),
                "type": "success",
                "sticky": False,
            },
        }

    def action_unlock_manual(self):
        """Unlock records manually."""
        for rec in self:
            rec.locked = False
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Unlocked"),
                "message": _("Selected sale orders are now unlocked."),
                "type": "success",
                "sticky": False,
            },
        }

    # Override write & unlink
    def write(self, vals):
        for rec in self:
            if rec.locked and not self.env.user.has_group("cr_record_lock.group_standard"):
                raise UserError(_("This record is locked and cannot be modified."))
        return super().write(vals)

    def unlink(self):
        for rec in self:
            if rec.locked and not self.env.user.has_group("cr_record_lock.group_standard"):
                raise UserError(_("This record is locked and cannot be deleted."))
        return super().unlink()