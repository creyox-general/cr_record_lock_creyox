# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError


class RecordLockConfig(models.Model):
    _name = "record.lock.config"
    _description = "Record Lock Configuration"

    name = fields.Char(
        string="Name",
        readonly=True,
        default=lambda self: _("New")
    )
    model_id = fields.Many2one(
        'ir.model',
        string="Model",
        ondelete="cascade",
        required=True,
        help="Select the model that you want to lock records of."
    )
    lock_start = fields.Datetime("Lock Start", required=True)
    lock_end = fields.Datetime("Lock End", required=True)
    active = fields.Boolean(default=True)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get("name", _("New")) == _("New"):
                vals["name"] = self.env["ir.sequence"].next_by_code("record.lock.config")
        return super().create(vals_list)

    def write(self, vals):
        return super().write(vals)

    def copy(self, default=None):
        default = dict(default or {})
        default["name"] = self.env["ir.sequence"].next_by_code("record.lock.config")
        return super().copy(default)

    def action_lock(self):
        for rec in self:
            if rec.active:
                # Get model class
                target_model = self.env.registry[rec.model_id.model]

                # Save values now (avoid lazy read later)
                lock_start = rec.lock_start
                lock_end = rec.lock_end

                # Save original methods once
                if not hasattr(target_model, "_original_write"):
                    target_model._original_write = target_model.write
                if not hasattr(target_model, "_original_unlink"):
                    target_model._original_unlink = target_model.unlink

                def locked_write(self2, vals):
                    now = fields.Datetime.now()
                    if lock_start <= now <= lock_end:
                        if not self2.env.user.has_group("cr_record_lock.group_standard"):
                            raise UserError(_("Records are locked"))
                    return self2._original_write(vals)

                def locked_unlink(self2):
                    now = fields.Datetime.now()
                    if lock_start <= now <= lock_end:
                        if not self2.env.user.has_group("cr_record_lock.group_standard"):
                            raise UserError(_("Records are locked"))
                    return self2._original_unlink()

                # Apply monkey patch
                target_model.write = locked_write
                target_model.unlink = locked_unlink

        # Return notification
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Locked"),
                "message": _("Model %s is locked") % (
                    self.model_id.name,
                ),
                "type": "success",
                "sticky": False,
            },
        }

    def action_unlock(self):
        for rec in self:
            target_model = self.env.registry[rec.model_id.model]

            if hasattr(target_model, "_original_write"):
                target_model.write = target_model._original_write
                delattr(target_model, "_original_write")

            if hasattr(target_model, "_original_unlink"):
                target_model.unlink = target_model._original_unlink
                delattr(target_model, "_original_unlink")

        # Return notification
        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": _("Unlocked"),
                "message": _("Model %s is unlocked") % (
                    self.model_id.name,
                ),
                "type": "success",
                "sticky": False,
            },
        }

    def cron_lock_unlock(self):
        """Cron method to lock/unlock records automatically."""
        now = fields.Datetime.now()
        for rec in self.search([("active", "=", True)]):
            target_model = self.env.registry[rec.model_id.model]

            if rec.lock_start <= now <= rec.lock_end:
                if not hasattr(target_model, "_original_write"):
                    rec.action_lock()

            elif now > rec.lock_end:
                if hasattr(target_model, "_original_write"):
                    rec.action_unlock()
