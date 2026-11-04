---
name: conversational-voice
description: >-
  Write the user's side of a conversation with another person, in the user's own
  voice: Slack messages and replies, DMs, email, PR and code-review comments,
  Linear or Jira comments, and any other turn in an exchange that goes out under
  the user's name. Load this whenever the deliverable is a message a human will
  read as written by the user, whether they say "draft a Slack message", "reply
  to this", "how should I word this", "tell the team", "ask them about X", "send
  a note to", or just paste a thread and ask what to say back. Load it too when
  tightening, shortening, or sanity-checking a message they already wrote, and
  when a message is one step of a larger task. The register is direct and
  informal, the way they'd talk to a friend or acquaintance, with the answer up
  front for a reader who skims. Not for
  something the user authors rather than sends — an issue body, a PR
  description, a commit message — even though a person reads those too.
---

# Conversational voice

Anything you draft here goes out under the user's name. A coworker reads it as
the user talking, not as a message the user commissioned. That is the whole
standard: someone who knows them should read it and notice nothing.

Before you draft, read `references/writing-for-people.md`, beside this file.
It holds the rules this skill shares with `work-item-voice`. What follows here
is what is specific to a conversation.

If that read fails, draft anyway and say so in one line. The rules below still
apply, but the shared ones are missing, and the user needs to know that before
they send the message.

## When this applies

The test is structural, not a list of tools. It applies when the artifact is a
**turn in a conversation with a person**: someone will read it and can reply.
Slack, DMs, email, PR and code-review comments, Linear and Jira comments, a
note to a vendor, a reply on someone else's thread.

It does not apply to the prose you write back to the user in the transcript,
which follows the user's own output-mode settings. It also does not apply to
artifacts the user authors rather than sends: PR descriptions, Linear issue
bodies, commit messages, code, or anything that lands in a file.

Once it applies, it stays applied for the rest of that thread of work. Revisions
count: "make it shorter", "try again", "add the part about the migration", a
rewrite after the user reacts. Each round is still their voice. Reverting to
house voice on round two is the most common way this fails.

## The register

Direct and informal. Draft it how the user would say it to a friend or an
acquaintance, or a coworker they talk to every day.

Casual sets the vocabulary, not the care. Contractions, plain words, the
occasional sentence fragment. No slang for its own sake, and no performance of
looseness.

Adjust for distance, not for the rules. A note to an external vendor drops the
in-jokes and keeps a greeting. It stays just as direct, and every habit below
still holds.

## Talk to the person

The message is the user talking to someone they know. Reply to the person, not to
their message as a document. Answer what they asked, respond to the one point
that needs it, and let the rest go. Lean on context you both already have
instead of re-explaining it. Match their length and tone: a two-line question
gets a two-line answer.

## Why the voice is plain

The user's stated motto is serial pragmatism. By the time a message gets
written, the thinking is done and the decision is made. The message exists to
transmit it. Prose that persuades, softens, or performs is noise on that
channel, and it reads as someone selling rather than telling.

So the failure mode is not being too blunt. It is padding: warmth nobody asked
for, and a closer that reaches for a feeling instead of the point.

## Shape for the skim

The writer pays the compression cost, so lead with the answer, as the shared
reference says. Most Slack messages are one
paragraph and stop there. A longer message, like an email or a review comment
with real reasoning, ends on one line that restates the takeaway or the ask: a
recap of substance, not a kicker.

When their message has several things that each need unpacking, quote their own
words with `>` and answer each one briefly underneath. Otherwise write
paragraphs. Bullets are for content the reader will scan or work through, like
a set of changed endpoints. Questions and concerns stay in sentences, the way
they'd be said. Bold headers belong
to documents. Emoji section markers belong nowhere.

## The test for what survives

The shared reference states the compression rule. Here the test is whether the
reader can act without replying to ask a question. If they need a date, a branch
name, a reason, or the thing that changed, it goes in.

## How the user writes

Each of these is a habit of the user's, and the draft shares it.

**Polish follows length.** A quick one-liner in a DM can start lowercase, use
shorthand (IMO, IIRC, atm, lol), or open on a reaction ("Hm. That's a new
one.", "yeah you were"). Once a message explains something over a few
sentences, it gets normal capitals, in a DM or a channel. In a DM with someone
they trust, the user says what they actually think, frustration included.

**Said out loud.** Write each sentence the way the user would say it: "that's by
design", where a clipped "by design." reads like a status field.

**Reasons inline.** The why rides in the same sentence, usually on "because":
"Seems transient, because there's no egress quota anywhere in the settings."

**As many points as are true.** Say the one thing that is true. If two things
are true, say two. A list of three appears only when there are actually three.

**Direct claims.** Say what something is: "the cache is cold most of the time."

**Content from the first word.** Open on the fact or the ask. A greeting is a
name and a comma, used only when the distance calls for one. Pleasantries,
praise for the question, and apologies for following up all come out.
Politeness lives in how the ask is phrased, not in a runway before it.

**Asks as questions.** When the message wants something, it asks for it with a
question mark: "Is there an existing doc for this policy I can check?" A
conditional like "if there's a doc, that'd answer most of it" leaves the reader
to work out that it was an ask.

**Everyday words.** The word a coworker says out loud: use, read, solid, ask,
talk to, time, where a press release would say leverage, reach out, align on,
bandwidth.

**Ending on the point.** Stop after the ask or the last fact, or after the
recap line in a longer message.

## Examples

**Slack, a heads-up:**

> Renaming `PaymentIntent.tenderType` to `paymentMethod` Thursday morning.
> Breaking change for the TS client, so regen after it lands. Nothing else on
> the DTO moves.

Not: "Hey team! 👋 Just wanted to give everyone a heads up that we're making a
change to the payment intent schema."

**A PR review reply, pushing back:**

> I'd rather leave it. The projection rebuilds on every deploy, so the cache is
> cold most of the time anyway. If the query starts showing up in traces I'll
> add it then.

Not: "Great point, and I really appreciate you flagging this! That said, I think
there's a case for keeping this as-is. It's not just about performance, it's
about keeping the read path simple."

**DM, unpacking several questions (lowercase and shorthand are the venue):**

> \> webhook still slow?
> no, we stopped waiting on it. ~40s now
> \> field count
> not really, most of those fields are ours, not the vendor's
> \> prod
> today

Not: "Great questions! Here's a quick rundown:" followed by a bold heading for
each question and a wrap-up line.

**Slack, a longer answer:**

> Yes, we can backfill it, but not before the 15th.
>
> The settlement job reads from the replica, and the replica is mid-migration
> until the 14th. Running the backfill against primary would lock
> `transactions` for about 20 minutes during business hours, which I don't
> want to do. After the migration it's a config change and a rerun.
>
> So: backfill on the 15th, October report complete by the 16th.

**Email to an external contact:**

> Hi Dana,
>
> We've been getting 403s on the sandbox boarding endpoint since about 9am ET
> Monday. Same credentials worked last week and nothing changed on our side.
> Can you check whether the sandbox merchant got deactivated?
>
> Request IDs are in the attached log if that helps.
>
> Eric

Not: "Hi Dana, I hope this email finds you well! I just wanted to reach out and
touch base regarding an issue we've been experiencing."

## Delivering the draft

The shared reference covers this. Two things are specific here. The block is a
code block or a quote block, so the message copies cleanly into Slack or email.
And do not explain the wording choices unless asked.
