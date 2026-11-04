# Basketball play studies (public copies)

Live at https://texaser.github.io/basketball-play-review/ (GitHub Pages, repo Texaser/basketball-play-review, published 2026-11-03).

Three short studies on basketball plays, the basketball counterpart of Yulu's soccer page
(https://yulupan00.github.io/video-gen-review/); the tabs at the top of each page switch between them.

1. **Better play** (`index.html`): one moment from a game and two short clips of how the play could continue; pick the better play, or no preference.
2. **Realism** (`realism/`): one clip at a time; could these movements plausibly occur in a competitive game?
3. **Shot value** (`value/`): two shots, each stopped at the release; which is more likely to score?

Built by `build_public.py --study pair|realism|value` from the private served pages (`../strategy_pair/`,
`../realism_clips/`, `../value_pairs/`): `index.html` = `../studies_common.py` with SERVER = false, answers kept in the
browser under the reviewer's name and sent in one submission to the Formspree form given as `--endpoint`
(https://formspree.io/f/xdkeaypg, Hanyi's; the `study` field is bball_pair_v1 / bball_realism_v1 / bball_value_v1).
Videos sit in `videos/` next to each page (495 MB in all); `--video-base URL --videos-out DIR` puts them on an external
host (Cloudflare R2 as Yulu does) so the repo holds only the pages. Answers come back through `import_answers.py --study …`.
