from odoo import models, fields, api, _
from odoo.exceptions import UserError


class LogicResignationForm(models.Model):
    _name = 'logic.resignation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'display_name'
    _description = "Resignation"

    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, default=lambda self: self.env.user.employee_id, readonly=True)
    department_id = fields.Many2one('hr.department', string="Department", related='employee_id.department_id')
    joining_date = fields.Date(string="Joining Date", required=True)
    reason = fields.Text(string="Reason", required=True)
    notice_period = fields.Char(string="Notice Period")
    state = fields.Selection(
        [('draft', 'Draft'), ('head_approve', 'Head Approve'), ('confirm', 'HR Approve'), ('approved', 'Approved'),
         ('cancel', 'Rejected')], string='Status', default='draft')
    resignation_type = fields.Selection(
        [('normal_resignation', 'Normal Resignation'), ('fired_by_the_company', 'Fired By The Company')],
        string="Resignation Type")
    expected_revealing_date = fields.Date(string="Expected Revealing Date", required=True)
    resign_confirm_date = fields.Date(string="Resign Confirm Date")

    def _compute_display_name(self):
        if self.employee_id:
            self.display_name = self.employee_id.name + ' - ' + 'Resignation Form'

    def action_confirm(self):

        existing_record = self.env['logic.resignation'].search([('employee_id', '=', self.employee_id.id), ('state', 'in', ['head_approve', 'confirm'])],
                                      )
        print(existing_record)
        if existing_record:
            raise UserError(
                "An active resignation request in 'Head Approve' or 'Confirm' state already exists for this employee.")
        else:
            head = self.employee_id.parent_id.user_id.id
            self.activity_schedule('logic_resignation.resignation_activity_for_head_approve', user_id=head,
                                   note=f'{self.employee_id.name} Has resigned please provide your confirmation', date_deadline=self.expected_revealing_date)
            self.state = 'head_approve'

    def action_head_approve(self):
        if self.employee_id.parent_id.user_id.id == self.env.user.id:
            self.state = 'confirm'
            activity_id = self.env['mail.activity'].search(
                [('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
                    'activity_type_id', '=',
                    self.env.ref('logic_resignation.resignation_activity_for_head_approve').id)])

            activity_id.action_feedback(feedback='Head Approved')
            hr = self.env.ref('logic_resignation.hr_resignation').users
            for i in hr:
                self.activity_schedule('logic_resignation.resignation_activity_for_head_approve', user_id=i.id,
                                       note=f'{self.employee_id.name} Has resigned please provide your confirmation', date_deadline=self.expected_revealing_date)
        else:
            raise UserError("You are not authorized to approve this resignation request.")


    def action_head_reject(self):
        if self.employee_id.parent_id.user_id.id == self.env.user.id:
            self.state = 'cancel'
            activity_id = self.env['mail.activity'].search([('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
                'activity_type_id', '=', self.env.ref('logic_resignation.resignation_activity_for_head_approve').id)])
            activity_id.action_feedback(feedback='Head Rejected')
        else:
            raise UserError("You are not authorized to reject this resignation request.")

    def action_hr_approve(self):
        self.state = 'approved'
        activity_id = self.env['mail.activity'].search([('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
            'activity_type_id', '=', self.env.ref('logic_resignation.resignation_activity_for_head_approve').id)])

        activity_id.action_feedback(feedback='HR Approved')

    def action_hr_reject(self):
        self.state = 'cancel'
        activity_id = self.env['mail.activity'].search([('res_id', '=', self.id), ('user_id', '=', self.env.user.id), (
            'activity_type_id', '=', self.env.ref('logic_resignation.resignation_activity_for_head_approve').id)])
        activity_id.action_feedback(feedback='HR Rejected')

    def action_return_to_draft(self):
        self.state = 'draft'
