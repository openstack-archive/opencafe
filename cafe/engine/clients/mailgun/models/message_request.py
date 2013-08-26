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

from cafe.engine.models.base import AutoMarshallingModel


class SendMessageItem(AutoMarshallingModel):
    """
    @summary: Send Message Request Object
    """

    def __init__(self, from_user, to, cc=None, bcc=None,
                 subject=None, text=None, html=None, attachment=None,
                 inline=None, o_tag=None, o_campaign=None, o_dkim=None,
                 o_deliverytime=None, o_testmode=None, o_tracking=None,
                 o_tracking_clicks=None, o_tracking_opens=None,
                 h_x_my_header=None, v_my_var=None):
        """
        @summary: Sends an email
        @param from_user: Email address for From header
        @param to: Email address of the recipient(s).
            Example: "Bob <bob@host.com>". You can use commas to separate
            multiple recipients.
        @type to:  string
        @param cc: Same as To but for Cc
        @type cc:  string
        @param bcc: Same as To but for Bcc
        @type bcc:  string
        @param subject: Message subject
        @type subject:  string
        @param text: Body of the message. (text version)
        @type text:  string
        @param html: Body of the message. (HTML version)
        @type html:  string
        @param attachment: File attachment. You can post multiple attachment
            values. Important: You must use multipart/form-data encoding when
            sending attachments.
        @type attachment:  string
        @param inline: Attachment with inline disposition. Can be used to
            send inline images. You can post multiple inline values.
        @type inline:  string
        @param o_tag: Tag string.
        @type o_tag:  string
        @param o_campaign: Id of the campaign the message belongs to.
        @type o_campaign:  string
        @param o_dkim: Enables/disables DKIM signatures on per-message basis.
            Pass yes or no
        @type o_dkim:  string
        @param o_deliverytime: Desired time of delivery.
        @type o_deliverytime:  string
        @param o_testmode: Enables sending in test mode. Pass yes if needed.
        @type o_testmode:  string
        @param o_tracking: Toggles tracking on a per-message basis.
            Pass yes or no.
        @type o_tracking:  string
        @param o_tracking_clicks: Toggles clicks tracking on a per-message
            basis. Has higher priority than domain-level setting.
            Pass yes, no or htmlonly.
        @type o_tracking_clicks:  string
        @param o_tracking_opens: Toggles opens tracking on a per-message
            basis. Has higher priority than domain-level setting.
            Pass yes or no.
        @type o_tracking_opens:  string
        @param h_x_my_header: h: prefix followed by an arbitrary value allows
            to append a custom MIME header to the message (X-My-Header in
            this case). For example, h:Reply-To to specify Reply-To address.
        @type h_x_my_header:  string
        @param v_my_var: v: prefix followed by an arbitrary name allows to
            attach a custom JSON data to the message.
        @type v_my_var:  string
        @notes: http://documentation.mailgun.com/api-sending.html
        """
        super(SendMessageItem, self).__init__()
        self.from_user = from_user
        self.to = to
        self.cc = cc
        self.bcc = bcc
        self.subject = subject
        self.text = text
        self.html = html
        self.attachment = attachment
        self.inline = inline
        self.o_tag = o_tag
        self.o_campaign = o_campaign
        self.o_dkim = o_dkim
        self.o_deliverytime = o_deliverytime
        self.o_testmode = o_testmode
        self.o_tracking = o_tracking
        self.o_tracking_clicks = o_tracking_clicks
        self.o_tracking_opens = o_tracking_opens
        self.h_x_my_header = h_x_my_header
        self.v_my_var = v_my_var

    def _obj_to_dict(self):
        """
        @summary: Convert send message object to JSON dictionary
        @return: Dictionary of send message object
        """
        return self._remove_empty_values(self._get_attribute_dictionary())

    def _get_attribute_dictionary(self):
        attrs = dict()
        attrs["from"] = self.from_user
        attrs["to"] = self.to
        attrs["cc"] = self.cc
        attrs["bcc"] = self.bcc
        attrs["subject"] = self.subject
        attrs["text"] = self.text
        attrs["html"] = self.html
        attrs["attachment"] = self.attachment
        attrs["inline"] = self.inline
        attrs["o:tag"] = self.o_tag
        attrs["o:campaign"] = self.o_campaign
        attrs["o:dkim"] = self.o_dkim
        attrs["o:deliverytime"] = self.o_deliverytime
        attrs["o:testmode"] = self.o_testmode
        attrs["o:tracking"] = self.o_tracking
        attrs["o:tracking-clicks"] = self.o_tracking_clicks
        attrs["o:tracking-opens"] = self.o_tracking_opens
        attrs["h:X-My-Header"] = self.h_x_my_header
        attrs["v:my-var"] = self.v_my_var
        return attrs
