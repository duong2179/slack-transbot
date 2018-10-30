# slack-transbot
Slack translation bot


### Dependencies

+ Slack client library

  `pip3 install slackclient`

+ Google translate library

  `pip3 install googletrans`


### Configure slack-transbot

+ Slack-transbot supports M-N translation map:

  channel_1 --> trans_channel_1

  channel_2 --> { trans_channel_1, trans_channel_2 }


### Install & Obtain slack bot token

<img width="1101" alt="01" src="https://user-images.githubusercontent.com/16577855/47733617-f7389900-dcab-11e8-8ccb-6df698caf316.png">
<img width="1101" alt="02" src="https://user-images.githubusercontent.com/16577855/47733619-f7d12f80-dcab-11e8-8e9e-d568fcdd7b81.png">
<img width="1100" alt="03" src="https://user-images.githubusercontent.com/16577855/47733620-f7d12f80-dcab-11e8-8f2b-3e3a57b2f8ea.png">
<img width="1100" alt="04" src="https://user-images.githubusercontent.com/16577855/47733621-f7d12f80-dcab-11e8-9685-ba3f9fcfe091.png">
<img width="1100" alt="05" src="https://user-images.githubusercontent.com/16577855/47733622-f869c600-dcab-11e8-9aed-1405b7156de6.png">
<img width="1100" alt="06" src="https://user-images.githubusercontent.com/16577855/47733623-f869c600-dcab-11e8-97fc-ff52e725e424.png">
<img width="1100" alt="07" src="https://user-images.githubusercontent.com/16577855/47733624-f869c600-dcab-11e8-910c-54862322dec7.png">
<img width="1100" alt="08" src="https://user-images.githubusercontent.com/16577855/47733625-f9025c80-dcab-11e8-8970-081f585d23ce.png">
<img width="1100" alt="09" src="https://user-images.githubusercontent.com/16577855/47733627-f9025c80-dcab-11e8-9cf0-46824dec66d9.png">
<img width="1100" alt="10" src="https://user-images.githubusercontent.com/16577855/47733628-f9025c80-dcab-11e8-9e49-1206ad8477a6.png">
<img width="1100" alt="11" src="https://user-images.githubusercontent.com/16577855/47733629-f99af300-dcab-11e8-964b-2c914588adb3.png">


### Create home channel for slack-transbot

Create a private channel (named `home-transbot` -- e.g). Let use this channel as home channel for slack-transbot. We will do all settings for slack-transbot in the home channel.

<img width="1101" alt="12" src="https://user-images.githubusercontent.com/16577855/47733631-f99af300-dcab-11e8-92f5-b0470f67f5d1.png">

Invite slack-transbot (named `transbot`) to the channel.

<img width="1101" alt="13" src="https://user-images.githubusercontent.com/16577855/47733633-f99af300-dcab-11e8-88f9-16ee6810f5bd.png">


### Find slack-transbot user ID

In the home channel, click "View member list" -> Right-click on `transbot` -> Copy Link -> The copied link should look like `https://...slack.com/team/UXXXXXXXX`. The last part (`UXXXXXXXX`) is `BOT_ID` of slack-transbot.

<img width="1103" alt="14" src="https://user-images.githubusercontent.com/16577855/47733634-fa338980-dcab-11e8-8b36-6719d46ef9b4.png">


### Start slack-transbot

+ `export` following params as environment variables.

  `BOT_TOKEN`: Slack-transbot token (`xoxb-xxxxxx...`, e.g)
  
  `BOT_ID`: Slack-transbot user ID (`UXXXXXXXX`, e.g)
  
  `BOT_NAME`: Slack-transbot name (`transbot`, e.g)
  
  `HOME_CHANNEL`: Home channel for slack-transbot (`home-transbot`, e.g)

+ Start slack-transbot

  `python3 /path/to/transbot.py path/to/transmap`

  Where: `path/to/transmap` points to where to save translation map. If launching from scratch, simply points to a non-existing file.

+ Go to the home channel. If slack-transbot has started well you will see `transbot` is shown with a green circle under Apps section.


### Configure slack-transbot

+ To configure slack-transbot, post command messages in the home channel.

+ `@transbot help`: Say hello and provide you some help.

+ `transbot list`: Show translation map.

+ `transbot add src:dst`: Add a pair of channels to translation map.

+ `transbot rm src:dst`: Remove a pair of channels from translation map.

<img width="1101" alt="15" src="https://user-images.githubusercontent.com/16577855/47733636-fa338980-dcab-11e8-9c62-284dacce0ae6.png">

### Test slack-transbot

+ Create two channels named `test-src` and `test-dst`. Invite slack-transbot to both channels.

+ In the home channel, post `@transbot add test-src:test-dst`.

<img width="1101" alt="16" src="https://user-images.githubusercontent.com/16577855/47733637-fa338980-dcab-11e8-8341-8f3f322933c9.png">

+ Now, go to `test-src` channel and post some Korean messages. Check out translated messages in `test-dst` channel.

<img width="1101" alt="17" src="https://user-images.githubusercontent.com/16577855/47733640-fa338980-dcab-11e8-9b9d-63e0a254ead3.png">
<img width="1101" alt="18" src="https://user-images.githubusercontent.com/16577855/47733641-facc2000-dcab-11e8-8fec-b979322ed578.png">
