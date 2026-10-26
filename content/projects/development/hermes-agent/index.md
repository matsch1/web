---
title: "From an n8n Workflow to a Personal Agent System"
slug: "hermes-agent"
date: 2026-10-26
description: "Why I replaced my n8n assistant with a self-hosted agent system for engineering, training, and personal knowledge work."
ShowToc: true
TocOpen: true
cover:
  alt: "Diagram: Hermes Agent links engineering and training with Obsidian and Git"
  caption: ""
  image: editorial-cover.webp
  relative: true
draft: false
tags:
  - AI
  - Automation
  - Homelab
  - Obsidian
source_lang: en
translation_lock: true
homepage:
  section: engineering
  state: active
  featured: false
  title: "A personal system with Hermes Agent"
  teaser: "A self-hosted agent for engineering, training, and knowledge work—built around tools, context, and guarded actions."
project:
  status: active
---

{{< alert type="info" title="" >}}
I still use Hermes every day, and I'm enjoying it.
{{< /alert >}}

My first personal AI assistant was an n8n workflow. I'd send it a Telegram message, a model would work out what to do, and a few MCP tools would handle calendar entries, tasks, or notes. I hadn't come across Hermes or similar agent systems yet. I was trying things out, and n8n helped me figure out what I wanted an assistant to do.

Eventually, I got tired of maintaining it. Every new task needed its own configuration, and small differences in how I phrased a request regularly broke the flow. I also found myself fighting the visual editor when I'd rather have written a few lines of code.

The requests themselves didn't help. One day I'm debugging a K3s cluster, the next I'm comparing bike setups, searching my Obsidian vault, or planning a training week. I didn't want to build another node graph each time.

I now run [Hermes Agent](https://hermes-agent.nousresearch.com/docs) in my homelab, with access to the tools and notes I use for those things.

## Why not simply keep n8n?

n8n still makes sense to me when I know the steps in advance. For a webhook that moves data between services or sends a reminder, being able to see the whole workflow is useful.

But I often start with something much less defined. I have an error I don't understand, or I'm wondering whether I've put too much into next week's training plan. I need to look at logs, read up on something, or check my notes before I even know what to ask next.

That's where Hermes is more useful to me. It can do that investigation with me. If we end up with a repeatable process, I can still turn it into a regular automation afterwards.

## Where Hermes fits

I mostly talk to Hermes through Discord, with separate channels for engineering and endurance sports. Telegram is available too. I can send text, voice messages, or images and pick up the conversation later.

For focused coding, I use the same model through Codex with an OpenCode integration in Neovim. Hermes is where I work through the questions around the code: what's going wrong in a deployment, whether a different setup would be easier to maintain, or what I need to check before making a change.

Training gets its own channel. Keeping the conversations separate helps, but both need context from my notes. I don't want generic encouragement when I'm asking whether I need more recovery. I'd rather it ask how I'm feeling.

## How it runs

Hermes runs in Docker with a Tailscale sidecar. I mount the directories it needs as volumes, including my Obsidian vault, and pass keys and secrets through environment variables. Docker gives it some separation from the host, though I don't treat that as a security guarantee. I limit its access to what it needs, and secrets must stay out of replies and Git repositories.

It can read files, inspect logs, run scripts, and query services. For infrastructure work, I've told it to start with read-only checks and keep any changes small and reversible. Migrations, volume or database changes, deletion, and anything with unclear consequences need my approval first. Before touching production, it should check backups, use dry runs where available, and work out how to roll back.

I don't want a misunderstood message to turn into a `prune` or `delete` command.

## Working with my Obsidian vault

My Obsidian vault contains technical notes, project details, training and health logs, research, and personal routines. Having it available means I don't have to explain all of that again in each conversation. The vault is mounted into the agent environment and synchronised to my other devices with Syncthing.

Hermes can read it and add to relevant notes. I've asked it to search for an existing note before creating one, and to ask me if it isn't clear where something belongs. It also needs to ask before adding tasks. Filenames and the folder structure are mine to change.

I need to be able to find things again. A well-written answer saved in an unexpected place just gives me another thing to search for.

## How I actually use it

### Engineering and homelab

I use Hermes for Docker, Kubernetes, debugging, and general homelab maintenance. It also helps with this blog, from dependency updates and shortcodes to SEO and GitHub Actions workflows.

With a homelab problem, the useful part is narrowing down what's wrong. I want it to check the affected component, read the logs, and test the network path before suggesting changes. A command is more useful when I understand what we're testing and what the result would tell us. If it changes anything, I want to know how to undo it.

For architecture questions, I care about how much work a setup will be to maintain, what it costs, and what security problems it might introduce. I also care if the setup is state of the art ore overkill for my usecase. Because I want to have a proper homelab, but I want to learn about DevOps stuff as well.

### Training and health

Intervals.icu is the main source for my training history, plan, zones, and load, with Garmin and some Strava data alongside it. I use Hermes to review several weeks at a time. Did I do what I'd planned? How much of it was hard? Where were the rest days, and how tired am I now? That's more useful to me than checking whether a single ride hit its target.

The numbers need some explanation from me, though. A strength session can look easy in the heart-rate data while leaving my back, shoulders, or core too tired for the next hard ride. So I also tell it how I feel, whether anything is sore or painful, and whether I've done something new or unusually hard.

Sleep, mobility, yoga, and the time I have available matter too, especially when planning towards an event. Equipment comes up as well. Sometimes I want help deciding whether a purchase would solve a problem or whether I'm just looking at an expensive upgrade.

I don't use the agent for diagnoses. With pain or worsening symptoms, I expect conservative advice: reduce the load, point out warning signs, and suggest a doctor or physiotherapist if the problem persists.

### Weekly reviews

A weekly review helps me pull things together from the separate conversations. I look at what went well, what's still open or blocked, and which decisions I need to make. Then I pick one to three things to do next.

I find that more useful than adding to an endless task list. For training, it also helps me resist filling every spare hour with another session.

## The current state

Most of what I use Hermes for is fairly ordinary: saving feedback after training, reviewing a few weeks of rides and runs, working through a homelab problem, or finding an old note. Some integrations are reliable enough that I use them regularly. Others still need better interfaces or better data.

It still gets things wrong. Generated training plans often need another pass, and research quality varies. I've asked it to look up current information and cite sources when we discuss tools, versions, products, prices, events, or health. If it can't find a reliable source, I want it to say so. I still need to check the answers and decide whether a recommendation makes sense for me. It also needs to ask before overwriting important files.

Even with that checking, I spend less time configuring things than I did with n8n. I can ask a question, let Hermes check my notes or investigate, and work through the answer in the same conversation. For the things I use it for, that's been worth the switch.
