# Basketball play studies (public copies)

Three short studies on basketball plays, the basketball counterpart of Yulu's soccer page
(https://yulupan00.github.io/video-gen-review/); the tabs at the top of each page switch between them.

1. **Better play** (`index.html`): one moment from a game and two short clips of how the play could continue; pick the better play, or no preference.
2. **Realism** (`realism/`): one clip at a time; could these movements plausibly occur in a competitive game?
3. **Shot value** (`value/`): two shots, each stopped at the release; which is the more valuable shot?

Built by `build_public.py --study pair|realism|value` from the private served pages (`../strategy_pair/`,
`../realism_clips/`, `../value_pairs/`): `index.html` = `../studies_common.py` with SERVER = false, answers kept in the
browser under the reviewer's name and sent in one submission to the Formspree form given as `--endpoint` (the copies here
still carry the REPLACE_ME endpoint: the Submit button then asks the reviewer to download the JSON and email it).
Videos sit in `videos/` next to each page (495 MB in all); `--video-base URL --videos-out DIR` puts them on an external
host (Cloudflare R2 as Yulu does) so the repo holds only the pages. Answers come back through `import_answers.py --study …`.
