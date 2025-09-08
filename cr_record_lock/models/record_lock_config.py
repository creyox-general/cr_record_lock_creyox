# -*- coding: utf-8 -*-
# Part of Creyox Technologies

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


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
        required= True,
        help="Select the model that you want to lock records of."
    )
    lock_start = fields.Datetime("Lock Start", required= True)
    lock_end = fields.Datetime("Lock End", required= True)
    active = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        # Generate a sequence number for the name if not provided
        if vals.get("name", _("New")) == _("New"):
            vals["name"] = self.env["ir.sequence"].next_by_code("record.lock.config")
        return super(RecordLockConfig, self).create(vals)

    def write(self, vals):
        return super(RecordLockConfig, self).write(vals)

    def copy(self, default=None):
        default = dict(default or {})
        default["name"] = self.env["ir.sequence"].next_by_code("record.lock.config")
        return super(RecordLockConfig, self).copy(default)

    def action_lock(self):
        for rec in self:
            if rec.active:
                print("==========================")