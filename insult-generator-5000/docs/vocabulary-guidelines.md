# Vocabulary guidelines

## What belongs

Words and short fixed phrases that can take part in a natural English insult, whether as the
insult itself ("dolt"), a descriptive adjective ("obtuse"), a verb ("dissemble"), or a positive
word that works through negation ("perspicacity").

Prefer words people actually use. Do not add a word because it sounds fancy.

## What does not belong

- **Slurs** aimed at race, ethnicity, religion, nationality, sex, gender, sexuality, disability
  or other protected characteristics, including reclaimed ones.
- **Gendered sexual insults** and sexual content. The `vulgar` register is profanity and crude
  slang about conduct and character.
- **Words that merely resemble slurs**, even when the etymology is unrelated.
- **Ethnic-derived idioms** (verbs and phrases that name a people to mean cheating or similar).
- **Invented words.** Every entry must be attested in a standard dictionary.
- **Spelling variants** unless the distinction is meaningful. Note variants in `usage_notes`.

Clinical or historical terms that survive as insults (for example `halfwit`, `dotard`,
`narcissistic`) are allowed only with the `sensitive` review flag and a note on the issue.

## Choosing a register

Add a register only if the word genuinely belongs to it. Multiple registers are fine.

- **casual**: everyday speech and slang.
- **formal**: polished, restrained prose.
- **archaic**: genuinely old (Early Modern, medieval, Victorian). Set `archaicness >= 1`. Use
  `obsolete` if no one uses it any more.
- **academic**: logic, rhetoric, epistemology, psychology, critical analysis.
- **legal**: only words with a real legal sense (a doctrine, an objection, a cause of action, a
  standard of fault). An ordinary word that lawyers also use is not "legal". Explain the legal sense
  in `usage_notes`.
- **vulgar**: profanity and crude slang. Set `vulgarity >= 1`.

## Scoring

Score relative to the other entries. Anchors: `severity` 1-2 is mild teasing, 5 is a real insult,
8-10 is wounding. `formality` 1-3 is slang, 7-10 is formal prose. Compare with similar entries
before settling on numbers.

## Nuance matters

Synonyms are not interchangeable. Use `meaning_or_nuance` and `usage_notes` to say what makes
the word different (people versus arguments, mild versus strong, regional, dated).

## Review flags

`obscure`, `obsolete`, `regional`, `disputed` (accuracy or usage is contested), `sensitive`
(origin or other senses may offend). Flagged entries are candidates for manual review.

## Checklist before opening a pull request

1. Real word, attested, not a spelling variant of an existing entry.
2. Not excluded by the rules above.
3. Register tags are earned; scores are consistent with neighbouring entries.
4. `insultgen validate-data` and `python -m pytest` pass.
