---
title: "From an n8n Workflow to a Personal Agent System"
slug: "hermes-agent"
date: 2026-07-31
description: "A self-hosted AI assistant for engineering, endurance sports, and personal knowledge workflows."
ShowToc: true
TocOpen: true
draft: true
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
project:
  status: active
---

## The upgrade

- Why a personal, self-hosted assistant instead of isolated automations?
  n8n was always to buggy. every new task needed a special configuration, every part which differs a bit caused problems, and I hated to work with this block builder thing (in my usecase it always was better to write a piece of code).
  The ability of hermes to learn and solve problems by himself is much better. The integration of a new functionality oftens needs only a small discord conversation and the bot figures out everything by himself
- n8n is brief context for the transition, not the subject of the article.
  When I started my n8n assistant story hermes or openclaw were not available (or popular/known by me). So as a first step to automate stuff in was a good thing. For myself I do not have a usecase for n8n which can not be done by hermes, too.

## What Hermes Agent is

- A practical assistant for engineering, homelab operations, training, and personal knowledge work.
  Agent which is hosted locally which used openai codex subscription (at least in my case)
  My usecases:
  1. homelab support: updating services, checkout logs, create basic gitops deployments as a baseline
  2. blog: Updating dependencies, SEO optimization, building shortcodes, optimize Github Action workflows
  3. training coach: analyze training data, make plans for future sport events
  4. research: sport equipment, technical stuff, basically all kinds of research
  I do not use it for coding. For that I use the same model (via Codex), but with an opencode integration in my neovim setup.
- A chat-first interface with controlled access to tools, files, and selected services.
  Talk with him using telegram or discord. I use discord with diffrent channels for different topics. Just send text, audio message or images. He understands everything
  

## System design

- Docker-based deployment and the boundary between agent and host.
  Agent runs in docker container with a tailscale sidecar container.
  Important local files are mounted as volume.
  keys and secrets are passed as environment variables
- Obsidian as a durable knowledge source, with conservative write rules.
  passed as volume (additionally synced with syncthing to other devices, link to other blog post)
- Integrations for technical operations and endurance-sport workflows.
  API key for garmin, and strava (very limited, bascially only used for activity names), and intervals.icu

## How I use it

- Engineering: debugging, architecture decisions, automation, and homelab operations.
- Sport: training review, planning, readiness, and event preparation.
- Weekly reviews that connect open work, training load, and priorities.

See above. Maybe use the previous points here

### Evidence to add

- One anonymised before/after chat excerpt.
- Two compact workflow diagrams: knowledge-work flow and weekly-review flow.
pick some by yourself

## Safety and control

- Read-only checks before changes, explicit approval for destructive actions, and rollback thinking.
- Secrets, credentials, and infrastructure boundaries.
- Where the agent should stop and ask instead of acting: everything which could be destructive or not reversible

## Lessons learned and current limits

- What is already useful in daily practice.
  that i can send audio message to an assistant which has all connections to my data (sport, tech, notes). so it can be really help full
  top usecases: 
    - documentaion of training feedback
    - give me a training review
    - help me with my homelab
    - what do i have about that in my notes
- What still needs human judgement or better integrations.
  architecture desicions, to get stuff implemented in the way you want. 
  research results are sometimes really bad and sometimes really good.
  Provided training plans often need some rework

## Next steps

- Open questions and planned improvements.
