---
title: "From an n8n Workflow to a Personal Agent System"
slug: "hermes-agent"
date: 2026-07-31
description: "Why I replaced my n8n assistant with a self-hosted agent system for engineering, endurance sports, and personal knowledge work."
ShowToc: true
TocOpen: true
draft: true
tags:
  - AI
  - Automation
  - Homelab
  - Obsidian
homepage:
  section: engineering
  state: active
  featured: false
project:
  status: active
---

> Draft — this project page is not published yet.

My first personal AI assistant was an n8n workflow: a Telegram message came in, a model decided, and a few MCP tools handled calendar entries, tasks, or notes. It was a useful first experiment. At the time, Hermes and comparable agent systems were not on my radar. n8n showed me which things I actually wanted to automate.

In everyday use, though, that shape became the limitation. Every new task needed its own configuration, and small deviations from the expected input regularly broke the flow. I also found the block-builder interface frustrating; in my use case, writing a small piece of code was often clearer. My questions rarely fit a fixed sequence anyway. One day I am debugging a K3s cluster, the next I am comparing two bike setups, looking for a note in my Obsidian vault, or planning the coming training week. I did not want to build another flow, prompt, and node graph for every new use case.

That is why I now run [Hermes Agent](https://hermes-agent.nousresearch.com/docs) as a personal agent system in my homelab. It is not an autonomous butler making arbitrary changes in the background. It is a technical and sporting sparring partner with tools, boundaries, and a memory I control.

## Why not simply keep n8n?

n8n remains a good tool for deterministic automation: handling webhooks, moving data between services, sending reminders, or running a scheduled job. In that setting, a visible workflow is an advantage.

Personal-assistant work often starts before automation, though. First I want to understand what is happening:

- Which hypothesis best explains this error?
- What information is missing for an infrastructure decision?
- Is this training week ambitious, or simply too much?
- Is there already a useful note on this topic, or am I about to create a duplicate?

An agent can research first, read files and logs, compare options, and then suggest a concrete next step. If the result becomes a stable, repeatable process, it can still become a conventional automation. That is the order I prefer: understand and verify first, automate afterwards.

## What Hermes Agent is for me

Hermes is a locally hosted, chat-first interface across two areas that do not obviously belong together: engineering and endurance sports. I use it mainly through Discord, with separate channels for different topics; Telegram is another available entry point. Text, voice messages, and images all end up in the same working context. In both domains, a generic "you can do it" is not useful. I need a system that places context correctly and does not guess when it is uncertain.

On the technical side, the agent supports DevOps, Docker, Kubernetes, homelab operations, debugging, architecture, and the blog itself: updating dependencies, improving SEO, building shortcodes, and tightening GitHub Actions workflows. I do not use Hermes as my primary coding environment. For focused implementation work, I use the same model through Codex with an OpenCode integration in Neovim. Hermes is the system around that work: it investigates, structures, and helps turn a rough GitOps deployment into a usable baseline. Its working style is deliberately sober: clarify the target, risks, and trade-offs; inspect logs and status; form hypotheses; test deliberately; change only after that. An answer should not merely give me a command. It should explain why that step makes sense and how to reverse it.

In sport, the same agent works with a different set of questions: How does actual training load compare with the plan? Where is recovery missing? What do the last few weeks say about readiness for an event? Which equipment solves a real problem, and which purchase is only an expensive upgrade? I do not treat training as separate from the rest of life. Sleep, mobility, yoga, strength work, and available time belong in the same view.

The shared foundation is not a magic prompt. It is clear roles, rules, and data sources.

## Architecture: an agent with clear boundaries

The system runs in Docker with a Tailscale sidecar. That is not a security guarantee, but it is an important boundary between the agent and the host. Important local directories, including the Obsidian vault, are mounted deliberately as volumes. Keys and secrets are passed as environment variables and never belong in replies or Git repositories. The agent does not receive blanket access; it only gets the access it needs for a defined task.

That separation matters because the agent does more than summarize text. When appropriate, it can read files, inspect logs, run scripts, or query defined services. Every capability therefore needs a clear frame.

For infrastructure work, that means:

1. Inspect read-only first: status, logs, configuration, and dependencies.
2. Keep changes as small and reversible as possible.
3. Stop and ask before migrations, volume changes, database changes, deletion, or unclear consequences.
4. Check dry runs, backups, and a possible rollback before changing production.

That sounds conservative because it is. An agent that runs `prune` or `delete` immediately after misunderstanding one sentence is not a useful operator.

## Obsidian is a knowledge source, not a playground

My Obsidian vault is the system's long-term memory. It contains technical notes, project context, training and health logs, research, and personal routines. It is mounted into the agent environment and synchronised to my other devices with Syncthing. The agent may read it and extend relevant existing notes, but it should not "improve" the vault by renaming files, moving them around, or inventing a new folder structure.

The writing rule is simple:

- Search for a suitable existing note first.
- If it exists, extend it deliberately instead of creating a parallel note.
- Ask when the destination is unclear.
- Do not dump tasks into the vault without asking.

This avoids a familiar AI failure mode: output that is formally correct but scattered and useless. A vault does not improve because it contains more Markdown. It improves when information lands where I can find it again.

## How I actually use it

### Engineering and homelab

The biggest benefit is not boilerplate generation. The agent is most useful when it structures failures and decisions. With a homelab issue, it starts from observable evidence: Which component is affected? What do the logs, network path, and current state say? Which assumption can a small, safe test disprove?

For architecture questions, it compares options by maintainability, complexity, security exposure, operational cost, and reversibility. That slows down action for action's sake. Not every task needs Kubernetes, Terraform, or another service. If Docker Compose is clean enough, that should be the recommendation.

### Training and health

For sport, I use training history, plan, zones, and load as a starting point. Intervals.icu is the main source, with Garmin data and limited Strava data used where useful. A useful review does not compare one ride with a target number. It looks across several weeks: volume, intensity, longest sessions, rest days, fitness development, and fatigue.

The gap between sensors and reality matters. Heart-rate load does not tell the whole story. A strength session can create little systemic load while still leaving the back, shoulders, or core too tired for the next hard ride. Subjective feeling, soreness, pain, and unfamiliar load therefore belong in the assessment as well.

For pain, warning signs, or worsening symptoms, the agent stays deliberately conservative. It cannot diagnose anything. Its job is to recommend reducing load, name warning signs clearly, and suggest a doctor or physiotherapist when a problem persists.

### Weekly reviews instead of topic chaos

The agent does not artificially blend the two domains, but it helps with prioritisation. A weekly review answers a few questions:

- What went well?
- What is open or blocked?
- Which decision is pending?
- What are the next one to three sensible steps?

That is more useful than an endless task list. In sport, it also prevents every spare hour from becoming training. Progress comes from sustainable routines, not maximum utilisation.

## What I deliberately do not automate

The agent may make suggestions and handle small, reversible tasks. It should not overwrite important files without asking, reorganise the Obsidian vault, change infrastructure, or make health decisions on its own.

That boundary is not only about safety. It keeps responsibility where it belongs. I decide on goals, risk, and priorities. The agent helps me make that decision with better information and less friction.

Its answers also need to remain verifiable. For current tools, versions, prices, products, events, or health topics, it should research first and cite sources. If there is no reliable source, it should say so instead of inventing a plausible answer.

## The current state

This is not a finished "life OS" kit. It is a growing work environment shaped around my actual projects: homelab operations, software development, Obsidian, running, and cycling. The strongest everyday uses are documenting training feedback, producing a training review, helping with the homelab, and answering the simple but frequent question: "What do I already have about this in my notes?" Some integrations are already practical. Others still need better interfaces or more reliable data.

The important change is already here: separate chat requests and n8n flows have become a system that can retain context over time, takes risk seriously, and considers maintainability and recovery alongside speed. It still needs human judgement. Architecture decisions remain mine, research quality varies, and generated training plans often need a second pass. That is not a disappointment; it is the boundary that makes the system useful.

That is the interesting part of personal agents for me. Not another bot that promises to do everything, but a tool that works reliably within a clear boundary.
