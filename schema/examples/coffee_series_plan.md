# Coffee Series: Channel Plan

**Status:** draft for discussion. Episode 1 (`coffee_families`) is built.

## Positioning

Most coffee channels cover brewing gear, recipes and the same "Arabica vs. robusta" facts. This series covers **the plant, the science and the economics behind the cup, told through Mexico.** Each episode answers one question a curious viewer has never thought to ask, and goes one layer deeper than a Wikipedia summary.

| | |
| :--- | :--- |
| Promise | "You'll never look at a cup the same way." Friendly enough for anyone, and specific enough that a barista learns something |
| Lens | Mexico as the recurring case study: its regions, varieties, farmers and history. Few English-language channels cover it, so this is our niche |
| Style | The Vox-style motion design from episode 1: white page, one colour per idea, match cuts, maps and family trees. The look stays consistent so the channel is recognisable |
| Length | 8–12 minutes for main episodes (YouTube rewards watch time), plus a 45–60 s vertical cut of each one for Shorts, Reels and TikTok. Episode 1 (3:00) works as the pilot or channel trailer |
| Rule | Every episode has one hard number, one map or diagram, and one surprise |

## Season 1: From plant to cup

Ordered so that each episode sets up the next. Dates and figures marked † must be checked before scripting.

| # | Working title | The question | Why it's not the usual video | Mexico angle |
|:-:| :--- | :--- | :--- | :--- |
| 1 | **The Coffee Family Tree** *(built)* | Where does arabica come from? | Genetics and species, not "arabica tastes better" | Mexico's own variety tree: Garnica, Oro Azteca |
| 2 | **The Fungus That Turned Ceylon Into a Tea Country** | Why is arabica so fragile? | Leaf rust wiped out Ceylon's (Sri Lanka's) coffee in the 1870s†, which is why it's a tea country today | The 2012 *roya* epidemic, and the trade-off between rust resistance and cup quality in Catimor varieties |
| 3 | **Why Mountain Coffee Tastes Different** | What does altitude actually do? | Slower ripening, denser beans and more sugars. It also explains bean grades such as SHB (Strictly Hard Bean) | Mexico's "Altura" grade, Chiapas and Coatepec |
| 4 | **The Shade Forest in Your Cup** | Why do some farms look like jungle? | Agroforestry, birds, soil and climate resilience | Chiapas and Veracruz shade-grown coffee, and Mexico's place among the top organic producers† |
| 5 | **Washed, Natural, Honey** | What happens between the cherry and the bean? | Fermentation as microbiology, plus the new anaerobic trend | The washed (*lavado*) tradition in Mexico |
| 6 | **How Decaf Is Made, in Veracruz** | How do you take caffeine out of a bean? | The chemistry of solvent, CO₂ and water processes | Mountain Water Process decaf is made in Veracruz† |
| 7 | **Why Does a Plant Make Caffeine?** | What is caffeine *for*? | It works as a pesticide, and it may help bees remember coffee flowers† | Robusta, which has more caffeine, in Chiapas's lowlands |
| 8 | **What Roasting Really Does** | How does a green seed become 800+ aromas†? | The Maillard reaction, caramelisation and first crack, shown as diagrams | Mexican roasting styles and the domestic specialty scene |
| 9 | **Who Gets Paid for Your Coffee** | Where does the price of a cup go? | The futures market (the "C price"), its boom and bust, and each player's share | Mexico's smallholders (most farms are a few hectares†), plus INMECAFE and its collapse in 1989† |
| 10 | **Café de Olla and the Instant Nation** | Why does a coffee-growing country drink instant? | A cultural history | Instant coffee's dominance in Mexico versus *café de olla*† |

### Reserve topics (Season 2 and later)
- **The Germans of Soconusco:** how immigrant *fincas* built Chiapas coffee in the late 1800s†.
- **Geisha:** how a wild Ethiopian variety became the world's most expensive coffee, with a Mexican Geisha example.
- **The future of coffee:** climate maps for 2050, stenophylla, the liberica revival and F1 hybrids (Centroamericano, Starmaya†).
- **Regions of Mexico as terroir:** one episode each for Chiapas, Veracruz, Oaxaca and Puebla.
- **Coffee's waste:** cascara, pulp and water use.
- **The mutant beans:** peaberry and Maragogype. Why some beans are round or giant.

## Production pipeline

1. A brief and a timecoded script (`<name>_script.md`) for each episode, approved before any build.
2. One generator per episode (`<name>.py`). Shared palette, fonts and helpers (cherry, map rig, family-tree nodes, match-cut handoffs) move into a common module once episode 2 starts, so every episode looks the same.
3. Build, preview, and check every match cut. The user then builds the project in After Effects 26.5 and records the VO.
4. Cut the vertical Short from the same precomps.

## Open decisions
- Channel name and language (English only, Spanish only, or both with dubbed VO).
- Release cadence. A sustainable start is one main episode every two weeks, with a Short every week.
- Whether to re-cut episode 1 to 8–10 minutes, or keep it as the trailer.
