# design-md · Brand Library Index

Routing table for the `design-md/` corpus — the DESIGN.md files (Google Stitch / getdesign.md format) that describe how real products' UI looks. This is the **single lookup** for "make it look like X" / `match <brand>`.

## How finesse uses this file

1. Brief names a brand (or `/finesse match <brand>`) → find the row here → get the folder + default register.
2. Read `design-md/<folder>/DESIGN.md` as the **locked design source** (palette / type / spacing / radius / components / do's & don'ts).
3. finesse still owns register inference, SOUL/SPECTACLE/DENSITY dials, hero engine (brand), product substrate + data-viz (product), blacklist audit, a11y, pre-flight. Merge contract: `references/design-md.md`.

**Register override rule:** the `register` column is the *default when the brief only says "like X"*. The page's job always wins — a trading dashboard "like Binance" is `product` even though Binance's row defaults to `brand`. Follow §0.A, not this column.

## Index

| Brand | Folder | Register (default) | Voice / soul | Default surface | Notes |
|---|---|---|---|---|---|
| Airbnb | `airbnb` | brand | warm marketplace · coral `#ff385c` | light | — |
| Airtable | `airtable` | product | sober editorial workflow · signature color cards | light | — |
| Apple | `apple` | brand | photography gallery · Action Blue `#0066cc` | light↔dark | chrome recedes; one signature shadow |
| Binance | `binance` | brand | dark financial · Binance Yellow `#FCD535` | dark | → product for trading surfaces |
| BMW | `bmw` | brand | settled corporate automotive | light | — |
| BMW M | `bmw-m` | brand | motorsport bombastic · UPPERCASE display | dark | — |
| Bugatti | `bugatti` | brand | austere luxury auto · near-black | dark | — |
| Cal.com | `cal` | product | calendar-first · Cal Sans · black CTAs | light | — |
| Claude | `claude` | brand | warm editorial · cream + coral serif | light | the canonical warm-editorial AI surface |
| Clay | `clay` | product | claymation-meets-data · navy CTAs | light | — |
| ClickHouse | `clickhouse` | product | database · near-black + electric yellow | dark | yellow used scarcely |
| Cohere | `cohere` | product | controlled enterprise AI · white + green-black | light/dark | mono-feeling display + Unica77 UI |
| Coinbase | `coinbase` | brand | institutional crypto · cool white/blue | light | → product for exchange surfaces |
| Composio | `composio` | product | dev-tools · dark + deep-electric | dark | — |
| Cursor | `cursor` | brand | AI code editor · warm-cream editorial | light | → product |
| Dell 1996 | `dell-1996` | brand | catalog-era retro · black frame + flat color ribbons | light / colorful | homage, not a live brand |
| ElevenLabs | `elevenlabs` | brand | editorial print magazine · off-white | light | — |
| Expo | `expo` | product | React Native infra · quiet white | light | — |
| Ferrari | `ferrari` | brand | cinematic luxury auto · near-black | dark | — |
| Figma | `figma` | brand | mono editorial + oversized pastel blocks | light | → product |
| Framer | `framer` | brand | dark builder artboard · black + white display | dark | page-as-artboard |
| HashiCorp | `hashicorp` | brand | enterprise infra · near-black + per-product accents | dark | Terraform/Vault/Consul color system |
| HP | `hp` | brand | white-paper enterprise · HP Electric Blue `#024ad8` | light | — |
| IBM | `ibm` | brand | Carbon Design · white + IBM Blue `#0f62fe` | light | → product (Carbon is a component system) |
| Intercom | `intercom` | brand | editorial customer-service · cream + Saans | light | — |
| Kraken | `kraken` | brand | crypto exchange · Kraken Purple `#7132f5` | light | ⚠ prose format (no YAML tokens), lighter spec |
| Lamborghini | `lamborghini` | brand | luxury auto · dark + gold | dark | — |
| Linear | `linear.app` | product | near-black `#010102` + lavender `#5e6ad2` | dark | the canonical dark-product language |
| Lovable | `lovable` | product | AI app builder · playful | mixed | — |
| Mastercard | `mastercard` | brand | interlocking circles · yellow/red · commerce | light | — |
| Meta | `meta` | brand | hardware commerce + brand · merch voice | light/dark | Quest / Ray-Ban surfaces |
| MiniMax | `minimax` | brand | premium AI infra · stark white + black-pill CTAs | light | — |
| Mintlify | `mintlify` | product | docs infra · sky-gradient heroes | light/dark | dual-mode |
| Miro | `miro` | brand | playful visual workspace · canary yellow | light | → product |
| Mistral AI | `mistral.ai` | brand | atmospheric sunset gradients over photography | dark | — |
| MongoDB | `mongodb` | product | dual-mode · deep teal + MongoDB green | dark/light | — |
| Nike | `nike` | brand | performance commerce · bold | light/dark | — |
| Nintendo 2001 | `nintendo-2001` | brand | Y2K console chrome · brushed periwinkle | light | homage, not a live brand |
| Notion | `notion` | brand | illustration-rich workspace · deep navy hero | light | → product |
| NVIDIA | `nvidia` | brand | tech · black + emerald green | dark | — |
| Ollama | `ollama` | product | local AI runner · minimal | light | — |
| opencode.ai | `opencode.ai` | product | dev tool · terminal-style | dark | — |
| Pinterest | `pinterest` | brand | image wall · red | light | — |
| PlayStation | `playstation` | brand | gaming · PS blue | dark | — |
| PostHog | `posthog` | product | product analytics · dark | dark | — |
| Raycast | `raycast` | product | command palette · dark + red accent | dark | — |
| Renault | `renault` | brand | automotive | light | — |
| Replicate | `replicate` | product | ML API · dark | dark | — |
| Resend | `resend` | product | email API · dark | dark | — |
| Revolut | `revolut` | brand | fintech · dark navy | dark | → product for app surfaces |
| Runway | `runwayml` | brand | AI video · dark editorial | dark | — |
| Sanity | `sanity` | product | CMS · light/dark | light/dark | — |
| Sentry | `sentry` | product | dev-tools · midnight purple + lime | dark | — |
| Shopify | `shopify` | commerce | cinematic commerce · two parallel tracks | light/dark | marketing track + merchant track |
| Slack | `slack` | brand | workplace messaging · aubergine + cream-lavender | light | → product |
| SpaceX | `spacex` | brand | aerospace austere · black + D-DIN | dark | — |
| Spotify | `spotify` | brand | music · green | dark | — |
| Starbucks | `starbucks` | brand | coffee · green | light | — |
| Stripe | `stripe` | brand | financial infra · deep navy + electric indigo | dark | → product |
| Supabase | `supabase` | product | open-source DB · white/near-black + emerald | light | — |
| Superhuman | `superhuman` | brand | fast-email · editorial indigo | dark | → product |
| Tesla | `tesla` | brand | auto · minimal | light | — |
| The Verge | `theverge` | brand | editorial tech mag · tall serif | light | — |
| Together AI | `together.ai` | brand | AI infra · near-black + orange/magenta/periwinkle | dark/light | — |
| Uber | `uber` | brand | transport super-app · black/white duet + pill radius | light | — |
| Vercel | `vercel` | brand | developer platform · black/ink + mesh gradient | light/dark | → product |
| Vodafone | `vodafone` | brand | telecom · scarlet red · 800-weight display | light | — |
| Voltagent | `voltagent` | product | AI agent platform · near-black + electric green | dark | — |
| Warp | `warp` | product | terminal · warm near-charcoal | dark | — |
| Webflow | `webflow` | brand | visual dev platform · near-black + 5-color accents | dark/light | accent = product categories |
| Wired | `wired` | brand | tech magazine editorial · tall narrow serif | light | — |
| Wise | `wise` | brand | money transfer · heavy 900 display + lime green | light | — |
| xAI | `x.ai` | brand | frontier AI · near-black + white pills | dark | — |
| Zapier | `zapier` | brand | workflow automation · warm cream + orange `#ff4f00` | light | — |

## Adding a brand

1. Create `<folder>/DESIGN.md` following the existing format: YAML frontmatter (`colors`, `typography`, `rounded`, `spacing`, `components` with `{token.ref}` syntax) + prose Overview / Components / Do's & Don'ts / Responsive.
2. Add one row above. If you didn't extract the file yourself, mark uncertain cells with a note (like `kraken`'s prose-format warning).
