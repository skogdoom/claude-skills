# claude-skills

A collection of custom [Claude Code skills](https://code.claude.com/docs/en/claude-code-on-the-web).
Each skill lives in its own top-level directory containing a `SKILL.md`
(and any supporting scripts/assets) that Claude loads when the task matches.

## Skills

| Skill | Description |
|---|---|
| [`shelf-catalog`](./shelf-catalog/SKILL.md) | Transcribes every book, comic, or media spine visible in a photo of a shelf (or multiple shelves) into a structured list, delivered as a spreadsheet or other file. Handles the hard part of reading small, low-resolution, rotated, or partially-obscured spine text by systematically cropping and zooming into the image rather than guessing from a single downscaled view. |

## Adding a skill

Add a new top-level directory with a `SKILL.md` (YAML frontmatter with
`name` and `description`, followed by the skill's instructions), plus any
supporting scripts, and add a row to the table above.
