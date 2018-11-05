#! /usr/bin/python3

import time
from time import sleep
import sys
from slackclient import SlackClient
from googletrans import Translator
import re
import os


def triple_quote(msg):
    return "```" + msg + "```"


def normalize_tags(s):
    x = s
    bad_tags = re.findall(r"<@ [A-Z0-9]{9}>", s)
    for bad_tag in bad_tags:
        good_tag = bad_tag.replace(" ", "")
        x = x.replace(bad_tag, good_tag)
    return x


def make_help(bot_name):
    help_msg = "```"
    help_msg += "@%s help\n" % bot_name
    help_msg += "@%s list\n" % bot_name
    help_msg += "@%s add src:dst\n" % bot_name
    help_msg += "@%s rm src:dst\n" % bot_name
    help_msg += "```"
    return help_msg


def public_channels(sc):
    try:
        res = sc.api_call(
            "conversations.list", exclude_archived="true", types="public_channel"
        )
        if res["ok"]:
            channels = {x["name"]: x["id"] for x in res["channels"]}
            reversed_channels = {x["id"]: x["name"] for x in res["channels"]}
            return channels, reversed_channels
    except Exception:
        pass
    return {}, {}


def private_channels(sc):
    try:
        res = sc.api_call(
            "conversations.list", exclude_archived="true", types="private_channel"
        )
        if res["ok"]:
            channels = {x["name"]: x["id"] for x in res["channels"]}
            reversed_channels = {x["id"]: x["name"] for x in res["channels"]}
            return channels, reversed_channels
    except Exception:
        pass
    return {}

def all_channels(sc):
    direct_channels, reversed_channels = {}, {}
    private_direct, private_reversed = private_channels(sc)
    public_direct, public_reversed = public_channels(sc)
    direct_channels.update(private_direct)
    direct_channels.update(public_direct)
    reversed_channels.update(private_reversed)
    reversed_channels.update(public_reversed)
    return direct_channels, reversed_channels


def channel_members(sc, channel_id):
    try:
        res = sc.api_call("conversations.members", channel="%s" % channel_id)
        return res["members"] if res["ok"] else []
    except Exception:
        pass
    return []


class TransClient:
    def __init__(self, bot_id, bot_name, bot_token, home_name, map_fpath):
        self._bot_id = bot_id
        self._bot_name = bot_name
        self._bot_token = bot_token
        self._bot_tag = "<@%s>" % self._bot_id
        self._home_name = home_name
        self._home_id = ""
        self._boss_ids = []
        self._map_fpath = map_fpath
        self._sc = SlackClient(self._bot_token)
        self._translator = Translator()
        self._trans_map = {}
        self._direct_channels = {}
        self._reversed_channels = {}
        self._help_msg = make_help(bot_name)

    def __is_valid(self):
        return self.__validate_home()

    def __validate_home(self):
        self.__refresh_channels()
        if self._home_name in self._direct_channels:
            self._home_id = self._direct_channels[self._home_name]
            self._boss_ids = channel_members(self._sc, self._home_id)
            return self._bot_id in self._boss_ids
        return False

    def __refresh_bosses(self):
        self._boss_ids = channel_members(self._sc, self._home_id)

    def __is_my_boss(self, user_id):
        self.__refresh_bosses()
        return user_id in self._boss_ids

    def __refresh_channels(self):
        self._direct_channels, self._reversed_channels = all_channels(self._sc)

    def __is_member_of(self, channel_name):
        if channel_name in self._direct_channels:
            channel_id = self._direct_channels[channel_name]
            members = channel_members(self._sc, channel_id)
            return self._bot_id in members
        return False

    def __validate_cmd(self, cmdline):
        tokens = cmdline.split()
        if len(tokens) == 1 and (tokens[0] == "list" or tokens[0] == "help"):
            return tokens[0], None
        elif (
            len(tokens) == 2
            and (tokens[0] == "add" or tokens[0] == "rm")
            and len(tokens[1].split(":")) == 2
        ):
            return tokens[0], tokens[1].split(":")
        return "none", None

    def __post_msg(self, msg, channels):
        for chan in channels:
            try:
                self._sc.api_call(
                    "chat.postMessage", as_user="true", channel=chan, text=msg
                )
            except Exception:
                print("Failed to post translated msg to %s" % chan)

    def cmd_none(self, args):
        msg = "Opps!!! Command not found. Supported commands:\n"
        msg += self._help_msg
        return msg

    def cmd_help(self, args):
        msg = "Hi there, I am here to help you understand each other\n"
        msg += "Supported commands:\n"
        msg += self._help_msg
        return msg

    def cmd_list(self, args):
        if not self._trans_map:
            msg = "Channel pairs:\n"
            msg += triple_quote("No channel pairs added yet")
        else:
            msg = "Channel pairs:\n"
            pairs = ""
            for src, dsts in self._trans_map.items():
                for dst in dsts:
                    pairs += "%s -> %s\n" % (src, dst)
            msg += triple_quote(pairs)
        return msg

    def cmd_add(self, args):
        src, dst = args
        self.__refresh_channels()
        if not self.__is_member_of(src):
            msg = "Seems that I am not a member of %s" % src
        elif not self.__is_member_of(dst):
            msg = "Seems that I am not a member of %s" % dst
        else:
            if src not in self._trans_map:
                self._trans_map[src] = set([])
            self._trans_map[src].add(dst)
            msg = "Added:\n"
            msg += triple_quote("%s -> %s" % (src, dst))
        return msg

    def cmd_rm(self, args):
        src, dst = args
        if src in self._trans_map and dst in self._trans_map[src]:
            self._trans_map[src].remove(dst)
            if not self._trans_map[src]:
                del self._trans_map[src]
            msg = "Removed:\n"
            msg += triple_quote("%s -> %s" % (src, dst))
        else:
            msg = "Channel pair not found. Nothing to be removed\n"
            msg += triple_quote("%s -> %s" % (src, dst))
        return msg

    def __do_settings(self, cmdline):
        cmd, args = self.__validate_cmd(cmdline)
        functor = getattr(self, "cmd_%s" % cmd)
        msg = functor(args)
        return msg

    def save_settings(self):
        lines = []
        for src_chan, dst_chans in self._trans_map.items():
            for dst_chan in dst_chans:
                lines.append("%s:%s\n" % (src_chan, dst_chan))
        if lines:
            open(self._map_fpath, "w").writelines(lines)

    def load_settings(self):
        if not os.path.exists(self._map_fpath):
            return
        lines = open(self._map_fpath, "r").readlines()
        lines = [x.strip() for x in lines]
        for line in lines:
            src_chan, dst_chan = line.split(":")
            self.cmd_add((src_chan, dst_chan))

    def __translate(self, msg):
        succeeded, transed_msg = False, msg
        try:
            transed_msg = self._translator.translate(msg, dest="en").text
            succeeded = True
        except Exception:
            pass
        return (succeeded, transed_msg)

    def __connect(self):
        print("Connecting to slack")
        return self._sc.rtm_connect()

    def run_forever(self):
        # invalid ?
        if not self.__is_valid():
            print("Invalid home channel: %s" % self._home_name)
            time.sleep(3.0)
            return

        # connect to slack
        if not self.__connect():
            print("Couldn't connect to slack")
            time.sleep(3.0)
            return

        # keep running
        while True:
            reconnect_needed = False

            # listen to channels
            for slack_event in self._sc.rtm_read():
                print(slack_event)
                msg_type = slack_event.get("type")
                # goodbye message -> reconnect
                if msg_type == "goodbye":
                    print("Goodbye. Reconnecting needed")
                    time.sleep(3.0)
                    reconnect_needed = True
                    break
                # things other than message -> skip
                elif msg_type != "message":
                    continue
                # validate channel, msg, sender, subtype
                src_chan_id = slack_event.get("channel")
                org_msg = slack_event.get("text")
                user = slack_event.get("user")
                subtype = slack_event.get("subtype")
                if (
                    not org_msg
                    or not user
                    or user == self._bot_id
                    or subtype == "bot_message"  # posted by a bot
                ):
                    continue
                # if the bot is mentioned in the message
                if src_chan_id == self._home_id and org_msg.find(self._bot_tag) == 0:
                    # refresh list of bosses
                    self.__refresh_bosses()
                    # if the sender is not the bot's boss -> warn him
                    if user not in self._boss_ids:
                        msg = (
                            "Sorry, You are not my boss. Please join %s first!"
                            % self._home_name
                        )
                        self.__post_msg(msg, [src_chan_id])
                    # do settings
                    else:
                        cmdline = org_msg[len(self._bot_tag) :].strip()
                        msg = self.__do_settings(cmdline)
                        self.save_settings()
                        self.__post_msg(msg, [src_chan_id])
                # normal message
                else:
                    # somehow the bot cannot see the channel
                    if src_chan_id not in self._reversed_channels:
                        continue
                    src_chan_name = self._reversed_channels[src_chan_id]
                    # if the channel is not in the translation map
                    if src_chan_name not in self._trans_map:
                        continue
                    # good to go
                    succeeded, transed_msg = self.__translate(org_msg)
                    print(succeeded, transed_msg)
                    transed_msg = transed_msg.replace("`", "")
                    transed_msg = transed_msg.strip()
                    transed_msg = normalize_tags(transed_msg)
                    dst_chan_names = self._trans_map[src_chan_name]
                    dst_chan_ids = [
                        self._direct_channels[x] for x in dst_chan_names
                    ]
                    msg = "_In *#%s*, <@%s> said:_\n" % (src_chan_name, user)
                    msg += ">>>" + transed_msg
                    self.__post_msg(msg, dst_chan_ids)
                time.sleep(0.1)

            if reconnect_needed:
                break


def grab_env_vars():
    try:
        bot_id = os.environ["BOT_ID"]
        bot_name = os.environ["BOT_NAME"]
        bot_token = os.environ["BOT_TOKEN"]
        home_chan = os.environ["HOME_CHANNEL"]
        return (bot_id, bot_name, bot_token, home_chan)
    except Exception as ex:
        print("Exception: %s" % ex)
    return ("", "", "", "")


if __name__ == """__main__""":
    if len(sys.argv) != 2:
        print("Invalid inputs")
        sys.exit(1)

    # trans map fpath
    map_fpath = sys.argv[1]

    # grab env variables
    (bot_id, bot_name, bot_token, home_chan) = grab_env_vars()
    if not bot_id or not bot_name or not bot_token or not home_chan:
        print("Invalid env variables")
        sys.exit(1)

    # the bot
    transbot = TransClient(bot_id, bot_name, bot_token, home_chan, map_fpath)

    # load saved settings
    transbot.load_settings()

    # serve forever (hopefully)
    while True:
        try:
            transbot.run_forever()
        except KeyboardInterrupt:
            print("Exited upon KeyboardInterrupt")
            break
        except Exception as ex:
            print("Exception: %s" % ex)
            time.sleep(1.0)

    # save current settigns
    transbot.save_settings()
