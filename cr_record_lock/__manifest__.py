# -*- coding: utf-8 -*-
# Part of Creyox Technologies
{
    "name": "Recod Locking System",
    "author": "Creyox Technologies",
    "website": "https://www.creyox.com",
    "support": "support@creyox.com",
    "category": "Inventory",
    "summary": "This module is used to lock the record of specific model for specific time & manually except the standard access users.",
    "license": "LGPL-3",
    "version": "18.0.0.0",
    "description": """ 
        """,
    "depends": ["base", "sale_management"],
    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "data/ir_sequence_data.xml",
        "data/ir_cron_record_lock.xml",
        "views/record_lock_config_view.xml",
    ],
    "installable": True,
    "auto_install": False,
    "application": True,
}
