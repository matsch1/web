---
title: "Setting up Giscus comments for Hugo blog"
slug: "giscus-hugo-comments"
date: 2025-12-04
description: "Giscus the Git Discussion based commenting system for Hugo blogs"
ShowToc: true
TocOpen: true
draft: false
cover:
  image: "giscus.png"
  alt: "giscus-hugo-comments"
  caption: "Giscus the Git Discussion based commenting system for Hugo blogs"
  relative: true
tags:
  - hugo
---

## Introduction: Why Add Comments?

I wanted to enable readers to easily comment on my Hugo blog posts, aiming for a solution that is both **simple for users** and **lightweight/easy to maintain** for me.

Hugo offers official support for integrating various commercial and open-source commenting systems.

## Choosing a Commenting System
### Commercial vs. Open-Source

While several commercial options like **Disqus** exist (free for non-commercial use but often includes ads), I opted for an **open-source** solution to maintain control and avoid third-party advertising.

Here are some popular choices in each category:

| Commercial Systems | Open-Source Systems |
| :--- | :--- |
| Emote | Cactus Comments |
| Graph Comment | Comentario |
| Hyvor Talk | **Giscus** |
| IntenseDebate | Isso |
| ReplyBox | Remark42 |

### Zero-Maintenance Open-Source: Giscus vs. Utterances

My initial requirement was to avoid self-hosting a server, leading me to focus on systems that use an existing third-party backend. The two main open-source options that don't require self-hosting are:

* **Utterances:** Uses **GitHub Issues** as a backend.
* **Giscus:** Uses **GitHub Discussions** as a backend.

I chose **Giscus** because **GitHub Discussions** are inherently better suited for threaded conversations, allowing nested replies compared to the flat list of comments in GitHub Issues. Giscus also offers modern features like:

* Reactions to the main post.
* Strict page matching to prevent comment mix-ups.
* More active maintenance.

{{< alert type="warning" title="" >}}
This system relies on GitHub Discussions, which means readers need a GitHub account to write comments.  
{{< /alert >}}

## Giscus Setup Guide
Integrating Giscus into your Hugo blog involves three simple steps: preparing your GitHub repository, generating the embed code, and creating a Hugo shortcode.

### 1. Repository Preparation

Giscus connects directly to your blog's source code repository on GitHub. Ensure the following conditions are met:

- The repository must be public
- The [Giscus app](https://github.com/apps/giscus) must be installed.
- The Discussion feature must be enabled ([enabling Discussion feature](https://docs.github.com/en/github/administering-a-repository/managing-repository-settings/enabling-or-disabling-github-discussions-for-a-repository)).

### 2. Generate the Giscus Embed Code

Navigate to the official [Giscus app website](https://giscus.app/) to configure and generate your embed code. You'll need to specify a few parameters:

* **Repository:** The name of your public repository (e.g., `username/blog-repo`).
* **Discussion Category:** The category in your GitHub Discussions where new post comments will be created (e.g., "Blog Comments").
* **Mapping Strategy:** How Giscus links a blog post to a specific Discussion. Using `pathname` is the standard choice.
* **Theme:** The visual theme (light/dark/custom) for the comment section.

The website will automatically generate an HTML snippet (`<script>...</script>`) based on your choices. **Copy this code.**

### 3. Hugo Integration (Using PaperMod as an Example)

I use the popular [PaperMod Hugo theme](https://github.com/adityatelange/hugo-PaperMod/wiki/Features#comments), which is already set up to handle comments easily.

#### A. Enable Comments in `hugo.toml`
Add the following parameter to your main configuration file to tell your theme to render a comment section:

```toml
[params]
  comments = true
```

#### B. Create the Giscus Shortcode

Create a new file at `layouts/partials/comments.html`` and paste the generated Giscus <script> tag inside it.
That's it! Giscus automatically handles the discussion mapping, keeps all data on GitHub, and requires zero server setup on your end.


## Consideration: Self-Hosting Options

If the requirement for a GitHub account is a non-starter, you might prefer a fully self-hosted solution, which grants complete control over data and privacy.

Strong options in this category include:

- Commento
- Isso
- Remark42

Of these, Remark42 stands out as an exceptionally feature-rich and robust choice. It offers modern commenting features, supports various login methods (not just GitHub), and is actively maintained.

While self-hosting requires allocating server resources and handling maintenance, systems like Remark42 provide the ultimate independence and customization. However, for those prioritizing a serverless, hassle-free setup, Giscus remains the perfect starting point.

## Conclusion

Giscus is an excellent, modern, and open-source solution for adding comments to a static Hugo blog. It bypasses the complexity of self-hosting, leverages the superior threading of GitHub Discussions, and offers a seamless integration experience.

It's the ideal starting point for anyone looking to enable reader engagement without the hassle of server management.

