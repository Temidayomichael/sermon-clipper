---
name: viral-clips
description: Make sermon clips more likely to trend on Reels, TikTok and YouTube Shorts - score clips for virality, write stronger hooks and titles, pick A/B variants, and plan posting. Use when planning or revising clips, writing hooks/titles/captions, or reviewing why a clip under-performed.
---

# Viral sermon clips

Guidance for picking and packaging sermon clips so they travel beyond the church audience, distilled from what
works for leading faith-podcast and sermon channels (their biggest videos are about money, success and marriage, not
church-internal topics; personal/family and one-liner reels routinely get several times the likes of event flyers)
and general short-form practice. Read the preacher profile in `config.json` for audience, region and languages.
Treat platform "rules" as starting points to test, not guarantees: algorithms change and no checklist guarantees a hit.

**Layering.** This skill sits on top of industry-standard frameworks. The "Social Media Skills" plugin is enabled on
this account: when its skills are available in the session, load `hook-writer` for hooks, `youtube-shorts`,
`tiktok-growth` and `instagram-growth` for platform rules, `captions-and-clipping` for packaging, and
`viral-reverse-engineering` when studying a video that over-performed. Ignore their publishing steps (WoopSocial):
this project renders files and the team posts them. This file adds the sermon-specific rules and guardrails. General hook/retention frameworks below are summarised from the MIT-licensed
open-source skills vyralcontent/content-skills (`viral-hooks`) and arhamhi/hooksmith.

## 1. Score every candidate clip (0-2 each, max 20)

| # | Signal | 2 = strong |
|---|---|---|
| 1 | **Scroll-stop hook** | The first sentence (first ~2 s) is a claim, a question or a conflict, not a warm-up |
| 2 | **Tension / contrarian** | It challenges something the audience believes ("people don't reward service", "tithe and offering are not the same") |
| 3 | **Life topic** | Money, work, marriage/relationships, family, purpose, the nation/society, mental health, success. Pure church-internal topics score 0-1 |
| 4 | **Specific & concrete** | Names, numbers, places, a vivid scene (a local landmark, the landlord, "they cooked for you") beats abstraction |
| 5 | **Emotion** | Laughter, conviction, surprise or relief, ideally a peak you can feel |
| 6 | **Payoff** | Ends on a punchline, rule or reframe the viewer can repeat; no trailing off |
| 7 | **Self-contained** | A stranger understands it with zero context |
| 8 | **Share trigger** | People would send it to someone ("tag the friend who lives with relatives") or post it to say something about themselves |
| 9 | **Comment trigger** | It's debatable or invites "this is me" replies (but see guardrails) |
| 10 | **Length & pace** | 30-60 s after edits, no dead air; rewatchable |

Rank by score. Prefer **15+**; anything under 11 needs a strong reason. Put the score breakdown's two weakest signals
in the clip's `why` so the user sees what to watch.

## 2. Hooks (on-screen title bar, ≤ 8 words)

**A hook is a system, not a line.** Three layers must work together in the first 1-2 s: what they **see** (his face
mid-gesture, a zoom), what they **hear** (his first sentence) and what they **read** (the title bar + first caption).
It must work **with the sound off** (most feeds start muted).

**Five-point hook test (all must pass):**
1. Contains a **specific noun** (landlord, tithe, wife, salary), not "this", "something", "life"
2. Shows or implies the **payoff** (what the viewer gets by staying)
3. **Resolves the "why watch" by second 3**
4. **Works muted** (title bar + captions carry it)
5. **The clip delivers it** (no bait-and-switch)

**Process:** draft 6-10 hooks across at least three different patterns below, run the test, keep the best as `hook`
and a different-pattern runner-up as `hook_alt`.

**Anti-patterns:** welcome/greeting openers, logos or intros, vague teases ("you won't believe this"), commands
with no reason ("watch till the end"), story set-ups that take 10 s to matter, a hook the clip doesn't pay off.

Write the hook for the person scrolling, not the congregation. Proven sermon patterns:
- **The reversal:** "Nobody will reward you for serving them"
- **The taboo question:** "Do you even need God to get rich?" / "The question Christians are afraid to ask"
- **The direct call-out:** "Living in someone's house for free? Watch this"
- **The number:** "3 reasons Christians stay broke"
- **The relatable scene:** "Try telling your landlord 'all things are mine'"
- **The hidden truth:** "What no one told you about ___"
- **The identity line:** "If you're the 'helpful one' in your family…"
- **The cost confession:** his own failure or price paid ("I thought I was serving God. I was shortening my life.")
- **The investigator:** "Why do unbelievers get rich and Christians don't?"

Rules: true to what he says (never imply something he then qualifies), no ALL-CAPS shouting, no emoji in the bar,
one idea only. Always write **one alternative hook** (`hook_alt`) using a *different* pattern for A/B testing.

## 3. Titles and captions

- **Shorts title (≤ 70 chars):** a curiosity gap plus the topic keyword people search ("money", "marriage", "tithe").
  Proven patterns: "What no one told you about…", "Why … (it's not …)", "It takes 5 minutes to know…".
- **Caption:** 1-2 lines that restate the tension + **one genuine question** that invites opinions
  ("Is it wrong to live with relatives without contributing?"). Then 3-5 hashtags: 1-2 broad (#faith #christian),
  2-3 niche (e.g. #christianfinance plus your city or country). Avoid engagement bait ("comment AMEN", "share or…"), which
  platforms down-rank.

## 4. Retention: hook → retain → reward

- **Open a loop** early (a question, a "three reasons", a story that hasn't landed) and close it near the end.
- **Rehook at 12-20 s**: a new beat (list item, cutaway, punchline, a "but here's the thing") right where viewers drift.
- **Reward**: the payoff line is the last thing they hear, which makes it shareable and rewatchable.
In the plan, make sure each clip has an open loop and a rehook moment; place a graphic or the cutaway on the rehook.

## 5. The edit (the pipeline already does most of this; check it)

- First frame: his face mid-sentence plus the hook bar. No logos, no warm-up, no "praise the Lord".
- Captions on, big; key words highlighted.
- Something changes every 2-4 s (jump-cut zoom, graphic, cutaway); one illustrated cutaway on the core metaphor.
- End on the payoff; a clean cut back to the opening idea helps loops.

**Platform mechanics (from the youtube-shorts / growth skills; re-check quarterly):**
- Short-form feeds have no thumbnail click: the metric that matters is **viewed vs swiped away** in the first ~3 s,
  then **average % viewed** (aim ~70%+). Each post is tested on a small seed audience; the **first 30-60 minutes**
  largely decide whether it spreads.
- Length is bimodal: **under ~30 s** maximises completion, **~50-60 s** maximises total watch time. Choose the shortest
  length that completes the idea.
- **Information gain** beats volume: recycled, samey clips get suppressed. Each clip needs a distinct angle.
- No bought views, follow-for-follow or template spam. AI-generated visuals may need the platform's
  "altered/AI content" label.

## 6. Posting

- **Same clip on all three platforms** (Reels, TikTok, Shorts); post the `hook_alt` version on a second platform or a week later as the A/B test.
- **Cadence:** ~3-7 clips a week, steady, beats 7 on Sunday. Batch-render on Monday, schedule through the week. Reach on a clip fades after roughly a month, so keep shipping.
- **Timing to test first (in your audience's time zone):** weekday evenings ~7-9 pm and Sunday afternoon after service. Keep what the analytics confirm.
- **First hour:** reply to early comments; pin a comment that extends the debate.
- Encourage fan/clip pages: give church members a shared folder of finished clips.

## 7. Learn from results (weekly)

**Studying a clip that took off (ours or another preacher's):** use `viral-reverse-engineering`. Work only from what
you can actually see (transcript, frames, visible stats, top comments); find the 1-2 load-bearing drivers by asking
"remove this, does it still work?"; name the **share trigger** (identity, strong emotion, practical value,
relatability); check replicability (big account, timing, luck); then apply the *mechanism*, never copy the content.


Look at **retention at 3 s and average % watched** (did the hook work?), **shares and saves** (was it valuable?), and
**comments** (did it spark something?). Before planning, read `assets/learnings.md`. After posting, note which hook patterns and topics won there and favour
them in the next plan. A clip that holds viewers but gets no shares needs a stronger payoff; one that loses
people in the first 3 s needs a better hook or first frame.

## Guardrails

- Never misrepresent him to get views: no out-of-context lines, no titles he wouldn't stand behind.
- No invented stories, testimonies or numbers in titles/captions.
- Contrarian is good; mocking people or groups is not. Debate the idea, not a person.
- If a clip would embarrass the pastor or the church out of context, drop it regardless of score.
