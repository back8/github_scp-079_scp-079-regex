# SCP-079-REGEX - Manage the regex patterns
# Copyright (C) 2019 SCP-079 <https://scp-079.org>
#
# This file is part of SCP-079-REGEX.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging

from pyrogram import Client, Filters

from .. import glovar
from ..functions.etc import code, get_text, thread, user_mention
from ..functions.filters import regex_group, test_group
from ..functions.telegram import send_message
from .. functions.words import data_exchange, get_type, similar, words_add, words_list, words_remove

# Enable logging
logger = logging.getLogger(__name__)


@Client.on_message(Filters.incoming & Filters.group & regex_group
                   & Filters.command(glovar.add_commands, glovar.prefix))
def add_words(client, message):
    try:
        cid = message.chat.id
        mid = message.message_id
        text, markup = words_add(message)
        thread(send_message, (client, cid, text, mid, markup))
        if "已添加" in text:
            thread(data_exchange, (client,))
    except Exception as e:
        logger.warning(f"Add words error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.group & test_group
                   & Filters.command(["ping"], glovar.prefix))
def ping(client, message):
    try:
        text = code(f"{code('Pong!')}")
        thread(send_message, (client, message.chat.id, text))
    except Exception as e:
        logger.warning(f"Ping error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.group & regex_group
                   & Filters.command(glovar.list_commands, glovar.prefix))
def list_words(client, message):
    try:
        cid = message.chat.id
        mid = message.message_id
        text, markup = words_list(message)
        thread(send_message, (client, cid, text, mid, markup))
    except Exception as e:
        logger.warning(f"List words error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.group & regex_group
                   & Filters.command(commands=glovar.remove_commands, prefix=glovar.prefix))
def remove_words(client, message):
    try:
        cid = message.chat.id
        mid = message.message_id
        text = words_remove(message)
        thread(send_message, (client, cid, text, mid))
        if "已移除" in text:
            thread(data_exchange, (client,))
    except Exception as e:
        logger.warning(f"Remove words error: {e}", exc_info=True)


@Client.on_message(Filters.incoming & Filters.group & regex_group
                   & Filters.command(commands=glovar.search_commands, prefix=glovar.prefix))
def search_words(client, message):
    try:
        cid = message.chat.id
        uid = message.from_user.id
        mid = message.message_id
        text = ""
        command_list = message.command
        if len(command_list) > 1:
            i, word_type = get_type(command_list)
            if len(command_list) > 2 and word_type in glovar.names:
                word = get_text(message)[1 + len(command_list[0]) + i + len(command_list[1]):].strip()
                include_words = [w for w in eval(f"glovar.{word_type}_words") if similar("loose", w, word)]
                if include_words:
                    for w in include_words:
                        text += f"{code(w)}\n\n"

                    text = text[:-2]
                    text = (f"类别：{code(glovar.names[word_type])}\n"
                            f"查询：{code(word)}\n"
                            f"结果：------------------------\n\n{text}")
                else:
                    text = (f"类别：{code(glovar.names[word_type])}\n"
                            f"查询：{code(word)}\n"
                            f"结果：{code('无法显示')}\n"
                            f"原因：{code('没有找到')}")
            else:
                text = (f"类别：{code(glovar.names.get(word_type, word_type))}\n"
                        f"结果：{code('无法显示')}\n"
                        f"原因：{code('格式有误')}")
        else:
            text = (f"结果：{code('无法显示')}\n"
                    f"原因：{code('格式有误')}")

        text = f"管理：{user_mention(uid)}\n" + text
        thread(send_message, (client, cid, text, mid))
    except Exception as e:
        logger.warning(f"Search words error: {e}", exc_info=True)
