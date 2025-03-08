from core.base.mail import BaseEmailMessage


class UserInviteEmail(BaseEmailMessage):
    template_name = "email/user_invite.html"
