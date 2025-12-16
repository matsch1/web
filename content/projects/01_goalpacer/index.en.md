---
title: "First Flutter app for marathon training"
slug: "goalpacer-pace-estimator"
date: 2024-11-16
description: "Explanation of how I build my first app for martathon training using Flutter"
ShowToc: true
TocOpen: true
draft: false
cover:
  image: "img1.webp"
  alt: "goalpacer"
  caption: ""
  relative: true
tags:
  - flutter
  - sports
  - application
---

{{< alert type="warning" title="" >}}
The app is still available in Google Play Store. 
At the moment, I'm only doing maintenance work and not working on new features.
{{< /alert >}}

I am proud to say that I was able to build my first flutter app in 4 days more or less ready for production.

Before these days I hadn't any experience about flutter. But I always like the idea to easily build apps for personal use. 
After some failed attempts to build some useful personal apps over the last two years using python i heard about flutter.
So this month I had some free time and set me the challenge to learn flutter, build an android app and publish it to google play store IN 4 DAYS.

The app I've chosen is some kind of pacing calculator I can use for running and triathlon training. For this purpose I used a google doc so far. In only need a few simple string and math operations on a few pages, no backend required. This seems to be perfect for my first app, not to complex and I would use to optimize my training in the future.

The development process actually starts one day to early. With my plan I could not wait to start and build a coffee card app in the evening of day 0 using the [Flutter Crash Course](https://youtu.be/j_rCDc_X-k8?si=OqmFujJvhpzCYK5O) of Net Ninja on Youtube.
With the learnings I get from this tutorial I start at the morning of day 1 with my own flutter app called [Goalpacer - Google Play Store](https://play.google.com/store/apps/details?id=com.matschcode.goalpacer).

In the next 3 days I was able to build this app using VSCO on my Linux machine. I managed to provide 4 functionalities: 

- Finish Time Calculator: Calculates finish time based on your pace for running, swimming and biking.
- Pace Calculator: Calculates the necessary pace for your desired finish time
- Heart Rate Zones Calculator: Estimate your heart rate zones based on your maximum heart rate
- Pace Converter: Converts paces from min/mile to min/km

Even if the design is pretty easy and far from perfect I am really happy with the result.

The last step is to publish the app on google play store. In the end this is more complicated then I have expected. At the moment I am in a state where I am searching for closed loop testers. As a private first time developer it is necessary to do a closed loop test with 20 people, before you can publish to the play store.

{{< galleries >}}
{{< gallery src="https://play-lh.googleusercontent.com/_gqr1RR1sYASzLR5yPkzHaX3hp704e63VvNj1iWg1COAGxZYk2aUxu0MyK3GN33Mww=w2560-h1440" title="Home Screen">}}
{{< gallery src="https://play-lh.googleusercontent.com/BLCCMgKAVVZb880iBsN1-7dztMIvxrEfwzJ5fWRwx_8_4LglkeUhW91XsuHpOyR5WA=w2560-h1440" title="Time Calculator" >}}
{{< gallery src="https://play-lh.googleusercontent.com/Qq14Cvd2ZVo0jwOdaeQYBXq9QLC04kuvgzH4MiZjDCOenBtGX2bTve_a9ltRuX0hWQQ=w2560-h1440" title="Pace Calculator" >}}
{{< gallery src="https://play-lh.googleusercontent.com/I0a0iCv3VMvLLK9TpGksVQeNOknJGyFZs14RMOT32l4hU6TLOfKlijU5WzKf8deLXw=w2560-h1440" title="Heartrate zones" >}}
{{< gallery src="https://play-lh.googleusercontent.com/L0XSeuoHSrN_Wc6hBoizI4Mx9QojKRFLEwAGzeKMkmu2Ro9jflzqYuoFnDEC_bwCyyc=w2560-h1440" title="Unit Converter" >}}
{{< gallery src="https://play-lh.googleusercontent.com/xoah8BMs4Z-KymeAH-HoezaqG-cIUWQrhMDQzex3H57MffhljxDa9LLM7d8ezU2_Xw=w2560-h1440" title="Split times" >}}
{{< /galleries >}}

