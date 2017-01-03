from openerp import models, api

class FooterlessNotification(models.Model):
    _inherit = 'mail.notification'

    @api.model
    def get_signature_footer(self, user_id, res_model=None, res_id=None, context=None, user_signature=True):
        return ""