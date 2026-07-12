# Recipe — ElevenLabs v3 audio tags (cyBorge's acting notes)

Bracketed cues that the **`eleven_v3`** model *performs*. Drop them inline in an essay block
and the render (`tools/tts/eleven.py`, which now defaults to `eleven_v3`) hands them straight to
ElevenLabs. This is how cyBorge stops *reading* and starts *acting*.

> Requires `model_id = eleven_v3`. On `eleven_multilingual_v2` the tags are just spoken aloud as
> words. The pipeline already defaults to v3.

## How to use

Put the tag right before the words it should colour, inside the block, in the essay markdown:

```
[sigh] "I don't know," she says.

many are black, but more have swords. [whispers] None ... have cigars.

[tired] I watch the streetlights make little slugs of light crawling over a misty grey night.
```

- Tags affect the delivery **around** them; keep them sparing — one or two per block reads best.
- Punctuation and capitalisation still matter (`...`, em-dashes, CAPS for emphasis all land).
- They're **voice- and context-dependent** — not every voice performs every tag; test and adjust.
- Lower **stability** = more responsive to tags. The renderer uses `0.5` ("Natural"); drop toward
  `0.0` ("Creative") in `eleven.py` for more drama, raise toward `1.0` ("Robust") to rein it in.

## The palette

**Emotion** — `[sad]` `[angry]` `[happy]` `[excited]` `[nervous]` `[tired]` `[curious]`
`[sarcastic]` `[regretful]` `[resigned]` `[deadpan]`

**Non-verbal** — `[sigh]` / `[sighs]` `[exhales]` `[laughs]` `[laughs softly]` `[chuckles]`
`[whispers]` `[gasps]` `[gulps]` `[clears throat]` `[snorts]` `[stammers]`

**Delivery / pacing** — `[whispering]` `[shouting]` `[slowly]` `[rushed]` `[drawn out]`
`[pause]` — also plain CAPS for emphasis, and `...` for a trailing beat.

**Sound (context-dependent, use rarely)** — `[applause]` `[clapping]` `[gunshot]` — the model
*may* render these; they're least reliable.

## For this project

- Tags live in `mycelium/essays/<name>.md`, inline in the blocks — the writer's stage directions.
- After editing, re-run the render; timing/bars re-fit automatically (tags change line length).
- Full list & nuances: ElevenLabs' [audio-tag guide](https://help.elevenlabs.io/hc/en-us/articles/35869142561297-How-do-audio-tags-work-with-Eleven-v3).
