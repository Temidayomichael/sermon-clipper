---
description: Apply the storyboard notes for a sermon job (clips marked "Needs changes", clip notes, beat notes)
argument-hint: <job>
---
Revise the clip plan for job `$ARGUMENTS` from the notes left on the storyboard page (if no job is given, use the most recently modified folder in `jobs/`).

1. Load the `viral-clips` skill. Read `prompts/pick_clips.md` (the editing rules still apply) and `jobs/<job>/plan.json`.
2. For every clip with `status: "changes"`, a non-empty `notes`, or any `beat_notes` (keys look like `cutaway@4552.8`: graphic type @ source seconds):
   - Read the relevant part of `jobs/<job>/transcript.txt` around the clip so new times land on real line timestamps.
   - Apply each note: move start/end, add or remove `trims`, swap a cutaway `visual`, change hooks, graphics, emphasis/keyword, etc. Times in plan.json are source seconds.
   - If a note asks for something the pipeline can't do yet, say so instead of faking it.
   - After applying, clear that clip's `notes` and `beat_notes`, add a short `revision` field saying what you changed, and set `status` back to "" so the user re-approves it.
   - **New illustrations:** for any cutaway whose `visual` starts with `new:` (requested at planning time or in a note), draw it:
     - Load the `remotion-markup` skill first. Copy the structure of an existing scene in `render/src/components/illustrations/` (e.g. `Door.tsx`, `Storm.tsx`): `Scene` + `Backdrop` + `Grain` from `common.tsx`, colours only from `P` in `palette.ts` (navy/gold/cream, red for one accent), flat shapes with soft glow, one simple animation driven by `t` with `ramp()`, 1080x1920.
     - Keep the main subject between y≈780 and y≈1550: the band above is reserved for the kinetic words and the hook bar.
     - Register it in `illustrations/index.tsx` with a one-line meaning, and add the same line to the visual list in `prompts/pick_clips.md`.
     - Check it: `cd render && npx tsc && npx remotion still src/index.ts Illustration /tmp/<name>.png --frame=80 --props='{"name":"<name>"}' --scale=0.4`, look at the image, and fix anything unclear (a symbol that doesn't read instantly should be replaced with a simpler one).
     - Delete `render/out/illustrations/<name>.png` if it exists (storyboard cache), then set the clip's `visual` to the new name.
3. Leave clips with `status: "approved"` and no notes untouched. Leave `status: "dropped"` clips alone.
4. Write plan.json, then tell the user, clip by clip, what changed, and ask them to refresh the storyboard (`./clip review <job>`) and approve.
5. Only when the user says to build: run `./clip make <job>` (it builds approved clips only).
