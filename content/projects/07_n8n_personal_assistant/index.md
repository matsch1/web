---
title: "My personal n8n AI assistant"
slug: "n8n-ai-assistant"
date: 2025-10-11
description: "Build your own personal telegram assistant using n8n"
ShowToc: true
TocOpen: true
draft: true
cover:
  image: "header.png"
  alt: "n8n-ai-assistant"
  caption: ""
  relative: true
tags:
  - n8n
  - AI
---

{{< alert type="info" title="Ongoing" >}}
The assistant does a good job and is still in daily usage.
{{< /alert >}}

## Introduction
Who would not want a personal assistant—someone who handles appointments, tasks, emails, and other administrative work? With current AI capabilities, this has become achievable even for individuals who cannot afford a human assistant.
In this post, I will show how to use n8n to build a personal AI assistant that responds to Telegram messages (including voice notes) and helps you manage appointments and tasks.

## Setup n8n
{{< figure src="https://www.webmaster-vitaliy.de/wp-content/uploads/2025/05/n8n.png" width="400" alt="n8n" link="https://n8n.io/" target="_blank">}}
Before building the assistant, we need to set up n8n. n8n is a no-code workflow automation platform that can orchestrate a wide range of integrations and automations (I may cover some additional examples in future posts).
n8n must be self-hosted on a server. I recommend following the approach from my [Coolify VPS setup](https://blog.matschcode.de/en/projects/coolify-vps-setup/). If you already have a Coolify instance running, you can simply add a new n8n resource with a few clicks.

## Create Workflow
My personal assistant workflow is not entirely self-built. I used one of the many existing templates from the n8n library as a foundation:  
[Voice & Text Assistant with Telegram, Gemini AI, Calendar, Gmail & Notion](https://n8n.io/workflows/8648-voice-and-text-assistant-with-telegram-gemini-ai-calendar-gmail-and-notion/).

In the following chapters, I will describe the most important components of this workflow and highlight the modifications I added.

### Trigger
The workflow is triggered by an incoming Telegram message.  
To enable this, you first need to create a Telegram bot using BotFather and configure the chat ID in your n8n Telegram node.

You can follow this tutorial for the bot setup:  
{{< youtube RIrIXLAj8bE >}}

Once you have the API token, create Telegram credentials in n8n, and the connection to your bot will be established.

If you want to restrict access, you can keep the existing account check, which verifies whether the incoming message originates from the correct chat ID. This is optional but can provide an extra layer of control.

#### Categorization of Text, Voice, or Image
I replaced the original switch block and introduced logic to differentiate between text, audio, and image messages.  
This enables my assistant to process not only text but also voice notes and images.

The following screenshots show how the message types are handled:
{{< galleries >}}
{{< gallery src="./settings_telegram_switch.png" title="telegram_switch_settings" >}}
{{< gallery src="telegram_message_voice_image.png" title="telegram_message_voice_image" >}}
{{< /galleries >}}

To extract the message content, I use `Get File` nodes with the following file IDs:

| Message Type | File ID |
|--------------|---------|
| Image        | {{ $json.message.voice.file_id }} |
| Voice        | {{ $json.message.voice.file_id }} |
| Text         | — |

After extracting the content, I pass it into prompts similar to the one below:

```
The user provided the following text as an audio prompt
{{ $json.content.parts[0].text }}
Hint: It is possible that it has some transcription errors.
```


With this setup, the AI agent can interpret the provided content reliably, regardless of whether it originated as text, voice, or an image.

### AI agent

#### Memory

#### Prompting

### MCP tools

### Feedback

## Usage examples

### Add appointment to calendar

### Create task for future to dos

### Adding cooking recipe to notes


