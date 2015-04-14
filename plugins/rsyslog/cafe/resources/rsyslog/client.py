# Copyright 2015 Rackspace
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import socket

from portal.input.syslog.usyslog import SyslogMessageHead


class RSyslogClient(object):

    def __init__(self, host='127.0.0.1', port=5140, default_sd=None):
        super(RSyslogClient, self).__init__()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.default_sd = default_sd

    def connect(self, host=None, port=None):
        address = (host or self.host, port or self.port)
        self.sock.connect(address)

    def close(self):
        self.sock.close()

    def send(self, priority, version=1, timestamp=None, app_name=None,
             host_name=None, message_id=None, process_id=None,
             msg=None, sd=None):
        if self.default_sd:
            composite_sd = self.default_sd
            composite_sd.update(sd or {})
            sd = composite_sd

        msg_handler = MessageHandler()
        header = self.build_header(app_name, host_name, message_id,
                                   priority, process_id, version,
                                   timestamp, sd)

        msg_handler.add_message_head(header)
        msg_handler.add_message_part(msg)
        syslog_msg = msg_handler.get_full_message()

        return self.sock.sendall(syslog_msg)

    @classmethod
    def build_header(self, app_name, host_name, message_id, priority,
                     process_id, version, timestamp, sd):
        """ Builds a Syslog Message Header Object
        Also handles replacing passed None's with syslog "nil" values.
        """
        head = SyslogMessageHead()
        head.appname = app_name or '-'
        head.hostname = host_name or '-'
        head.messageid = message_id or '-'
        head.priority = priority or '-'
        head.processid = process_id or '-'
        head.timestamp = timestamp or '-'
        head.version = version or '-'
        head.sd = sd or {}
        return head


class MessageHandler(object):

    def __init__(self):
        self.msg = b''
        self.msg_head = None
        self.msg_count = 0

    def add_message_head(self, message_head):
        self.msg_count += 1
        self.msg_head = message_head

    def add_message_part(self, message_part):
        self.msg += bytes(message_part)

    def get_full_message(self, message_end=''):
        full_message = bytes(self.msg + message_end)
        syslog_message = self.msg_head.as_dict()
        syslog_message['message'] = full_message
        cee_msg = self.to_cee(syslog_message)

        return self.cee_dict_to_rsyslog(cee_msg)

    @classmethod
    def to_cee(cls, syslog_message):
        cee_message = {
            'time': syslog_message.get('timestamp'),
            'host': syslog_message.get('hostname'),
            'pname': syslog_message.get('appname'),
            'pri': syslog_message.get('priority'),
            'ver': syslog_message.get('version'),
            'pid': syslog_message.get('processid'),
            'msgid': syslog_message.get('messageid'),
            'msg': syslog_message.get('message'),
            'native': syslog_message.get('sd')
        }

        return cee_message

    @classmethod
    def sd_dict_to_syslog_str(cls, sd_dict):
        """ Converts structured data dictionary to a syslog str """
        syslog_sds = ''
        for sd_key, sd_val in list(sd_dict.items()):
            syslog_str = '[{sd_key}'.format(sd_key=sd_key)

            for sub_key, sub_val in list(sd_val.items()):
                syslog_str = '{orig} {key}="{value}"'.format(
                    orig=syslog_str, key=sub_key, value=sub_val)
            syslog_str += ']'

            syslog_sds += syslog_str

        return syslog_sds

    @classmethod
    def cee_dict_to_rsyslog(cls, cee_dict):
        """ Converts a CEE format dictionary and converts it to a syslog
        message string.
        """
        structured_data = cee_dict.get('native')
        if structured_data is not None:
            structured_data = cls.sd_dict_to_syslog_str(structured_data)

        log = ('<{pri}>{ver} {time} {host} {app} {pid} {msgid} {sd} '
               '{msg}').format(
            pri=cee_dict.get('pri'),
            time=cee_dict.get('time', '-'),
            ver=cee_dict.get('ver'),
            host=cee_dict.get('host', '-'),
            app=cee_dict.get('pname', '-'),
            pid=cee_dict.get('pid', '-'),
            msgid=cee_dict.get('msgid', '-'),
            sd=structured_data or '-',
            msg=cee_dict.get('msg'))

        return b'{length} {syslog}'.format(length=len(log), syslog=log)
