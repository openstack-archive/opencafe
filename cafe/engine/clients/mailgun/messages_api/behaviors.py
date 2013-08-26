"""
Copyright 2013 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from cafe.engine.behaviors import BaseBehavior


class MailgunBehavior(BaseBehavior):

    def __init__(self, mailgun_client, mailgun_config):
        """
        Sets up client based on parameters taken from config
        """
        super(MailgunBehavior, self).__init__()
        self.config = mailgun_config
        self.mailgun_client = mailgun_client

    def send_simple_message(self, from_user, to, cc=None, bcc=None,
                            subject=None, text=None, html=None):
        """
        Sends a plain text/html message
        """
        resp = self.mailgun_client.send_message(from_user=from_user,
                                                to=to, cc=cc, bcc=bcc,
                                                subject=subject,
                                                text=text,
                                                html=html)
        assert resp.status_code == 200, \
            ('Unexpected send message response with status code '
             '{0}, reason: {1}, content: {2}.'.format(
                 resp.status_code, resp.reason, resp.content))
        return resp.entity

    def send_scheduled_message(self, from_user, to, o_deliverytime,
                               cc=None, bcc=None, subject=None, text=None,
                               html=None):
        """
        Sends a plain text/html message with a delivery time set
        """
        resp = self.mailgun_client.send_message(from_user=from_user,
                                                to=to,
                                                o_deliverytime=o_deliverytime,
                                                cc=cc, bcc=bcc,
                                                subject=subject,
                                                text=text,
                                                html=html)
        assert resp.status_code == 200, \
            ('Unexpected send message response with status code '
             '{0}, reason: {1}, content: {2}.'.format(
                 resp.status_code, resp.reason, resp.content))
        return resp.entity

    def send_attachment_message(self, from_user, to, attachment, cc=None,
                                bcc=None, subject=None, text=None, html=None):
        """
        Sends a message with attachments
        """
        resp = self.mailgun_client.send_message(from_user=from_user,
                                                to=to, attachment=attachment,
                                                cc=cc, bcc=bcc,
                                                subject=subject,
                                                text=text,
                                                html=html)
        assert resp.status_code == 200, \
            ('Unexpected send message response with status code '
             '{0}, reason: {1}, content: {2}.'.format(
                 resp.status_code, resp.reason, resp.content))
        return resp.entity

    def send_inline_image_message(self, from_user, to, inline, html, cc=None,
                                  bcc=None, subject=None, text=None):
        """
        Sends a message with an inline image
        Mailgun assigns content-id to each image passed via inline API
        parameter, so it can be referenced in HTML part.
        e.g.
        inline (fileloc) is "files/test.jpg"
        "html": '<html>Inline image here: <img src="cid:test.jpg"></html>'
        """
        resp = self.mailgun_client.send_message(from_user=from_user,
                                                to=to, inline=inline,
                                                cc=cc, bcc=bcc,
                                                subject=subject,
                                                text=text,
                                                html=html)
        assert resp.status_code == 200, \
            ('Unexpected send message response with status code '
             '{0}, reason: {1}, content: {2}.'.format(
                 resp.status_code, resp.reason, resp.content))
        return resp.entity
