## 2.4 Art Style

### 2.4.1 North Star

Santa's Nordic Workshop should look like a **Scandinavian storybook illustration brought to life**: watercolor/gouache washes on textured paper, restrained ink linework, muted natural palettes, and warm/cool ambient light that feels handcrafted rather than "rendered." The world is grounded (wood, wool, tar, stone, bone, ice) but carries mythic design laws that make each lineage instantly recognizable.

The style must remain:
- **Readable** at gameplay scale (clear silhouettes, strong value separation)
- **Handmade** in finish (paper grain, brush wash, soft edges)
- **Nordic** in materials (no modern plastics, no glossy "toy-store" sheen)

### 2.4.2 Art Pillars

| Pillar | Description |
|--------|-------------|
| **Storybook Craft Realism** | Everything looks built from real materials (birch, ash, oak, wool, iron, tar, bone, ice), depicted with painterly honesty. |
| **Ink + Wash Clarity** | Fine linework defines form; washes establish light, mood, and temperature. Avoid over-rendered micro-detail. |
| **Muted Base, Sacred Accents** | Natural neutrals dominate; color "pops" are reserved for lineage accents, magic, and UI feedback. |
| **Design Laws, Not Decoration** | Each lineage has a geometric rule that shapes architecture, tools, motifs, and silhouettes (see 2.4.6). |
| **Cozy vs. Brutal Contrast** | The workshop can be hearth-warm or kiln-dark—but never modern, never slick, never neon. |

### 2.4.3 Rendering Model

*How it should be painted/produced:*

- **Primary finish:** Watercolor + gouache wash with visible paper texture and thin ink outlines
- **Linework:** Clean, confident, minimal crosshatching; prioritize contour and key folds
- **Shading:** Soft, diffuse; limited hard-edged shadows
- **Texture:** Implied via wash variation, edge darkening, and selective detail (wood grain, wool weave, tar sheen)
- **Lighting:** Ambient first; rim-light used sparingly as "mythic emphasis," not as cinematic bloom

### 2.4.4 Color, Value, and Contrast Rules

**Palette baseline:** Pine greens, birch whites, oak browns, soot blacks, wool greys, stone neutrals, ice blues.

**Saturation discipline:** Keep saturation low-to-medium; reserve high saturation for:
- Magic highlights (subtle)
- Critical interactables
- Faction accents
- Success/fail feedback

**Value readability:** Gameplay objects must separate clearly from floor/background via:
- Darker outline or value banding
- Slightly higher contrast edges
- Controlled background softness

### 2.4.5 Material Language (Canonical Surfaces)

Use materials as identity cues—players should "feel" the world through surfaces.

| Category | Materials |
|----------|-----------|
| **Woods** | Birch (pale + speckled), Ash (smooth + elastic curves), Oak (heavy + warm), Pine (resin + knots) |
| **Metals** | Iron (matte, worn edges), Copper (verdigris accents), Steel (rare; later-era) |
| **Organics** | Wool (soft, fibrous), Leather (matte with creases), Bone/Antler (chalky with polish points) |
| **Chemicals/Craft** | Tar (dark semi-gloss), Resin (honey highlights), Vinegar/Lye (clean sharpness) |
| **Arctic** | Ice (milky translucency), Frost (powdered edge), Sea-spray (mist and speckle) |

### 2.4.6 Lineage Visual Systems (Shape Laws + Motifs)

Each lineage must be identifiable even in silhouette and tool shapes.

#### Ljósálfar (Haven)
- **Shape Law:** Organic "whiplash" curves (Art Nouveau), no right angles, forms follow wood grain
- **Motifs:** Birch bark layering, resin-gold inlays, light/leaf filigree, dragonfly-linen shimmer
- **Lighting Bias:** Cool daylight with warm sun accents; airy and overexposed in wash, not bloom

#### Nisse (Pantry)
- **Shape Law:** "Fast-hald" square forms—stout proportions, straight boards, peg joinery, visible repairs
- **Motifs:** Knit patterns, patched leather, iron hooks, practical storage geometry
- **Lighting Bias:** Hearth-warm, cozy soot, soft bounce light

#### Svartálfar (Dark Hváll)
- **Shape Law:** "Geometric Dark"—hard angles, riveted planes, block silhouettes, carved symbols
- **Motifs:** Soot bands, verdigris hints, tar-black leather, kiln-slit lighting
- **Lighting Bias:** Low-key warm ember sources with heavy shadow massing

#### Marmennill (Sea-Larder)
- **Shape Law:** "Pressure-Hardened"—smooth hydrodynamic forms, minimal protrusions, restrained spiral motifs (narwhal-tusk logic)
- **Motifs:** Translucent skins/isinglass, bone fasteners, wet stone, waterline reflections, bioluminescent pinpoints (subtle)
- **Lighting Bias:** Cold diffuse light + faint underwater glow; always damp and quiet

### 2.4.7 Character Design Guidelines

- **Proportions:** Grounded folk silhouettes (not chibi, not anime). Exaggeration comes from materials and posture, not giant heads.
- **Faces:** Expressive but restrained; "storybook realism" (wrinkles, tired eyes, warmth).
- **Clothing:** Layered, functional, era-appropriate; details read as shape blocks first (cap, apron, cloak), then texture.
- **Hands/Tools:** Tools should look used and maintained—especially Nisse; soot-stained labor reads for Svartálfar.

### 2.4.8 Environment Design Guidelines

- **Background philosophy:** Suggestive, atmospheric, never busy. The workshop must remain navigable and readable.
- **Depth cues:** Soft fog layers, value falloff, simplified distant detail.
- **Set dressing:** Purposeful clusters (storage, hearth, tool wall, drying racks) rather than random clutter.
- **Temperature:** Environments should "feel" warm/cold primarily via palette and wash softness.

### 2.4.9 Props, Stations, and Interactables

- **Station silhouettes:** Instantly readable at a glance (workbench, kiln, press, vat, wrap table, etc.)
- **Faction styling:** Stations inherit lineage laws (curves vs squares vs angles vs hydrodynamics)
- **Interactable readability:** Slightly higher contrast edges, clearer outline, controlled accent color "pin" (not glowing UI)

### 2.4.10 VFX and Particles

VFX must stay **painterly and diegetic**:

| Lineage | Effect Style |
|---------|--------------|
| **Ljósálfar** | Dust motes: soft gold specks, slow drift |
| **Svartálfar** | Soot/ember: sparse ember float, heat shimmer minimal |
| **Nisse** | Steam/milk/boil: soft white plumes, warm |
| **Marmennill** | Mist/spray: fine fog, water droplets, faint glow points |

> Avoid high-energy "spell effects." Magic is implied, not explosive.

### 2.4.11 UI Art Direction

*If illustrated UI is used:*

- **UI surfaces:** Parchment, wood panels, stitched cloth tabs, iron fasteners—kept minimal for readability
- **Icon style:** Inked pictograms with light wash fills; consistent line weight
- **Color semantics:** UI color pops align with gameplay feedback; do not compete with scene palettes

### 2.4.12 Animation Style

- **Target:** 60 FPS for responsive gameplay
- **Motion language:** Hand-animated feel (slight easing imperfections), not mechanical tweening
- **Idle loops:** Subtle breathing/weight shift; cloth and beard movement minimal
- **Interactions:** Clear anticipation + follow-through; keep timing snappy for gameplay

### 2.4.13 Do / Don't Checklist

| Do | Don't |
|----|-------|
| Keep palettes natural and muted | Use glossy, plastic, or modern industrial finishes |
| Use ink lines for clarity, wash for mood | Drift into anime/chibi proportions |
| Make materials legible (wool ≠ leather ≠ tar ≠ ice) | Over-render micro-detail or cinematic lighting |
| Apply lineage shape laws to everything | Use neon colors or high-contrast "arcade magic" VFX |

### 2.4.14 Prompt Template (For Concept Artists or AI Generation)

Use this structure to keep outputs consistent:

```
STYLE: Scandinavian storybook illustration; watercolor + gouache on textured 
       paper; fine ink linework; soft ambient light; muted natural colors; 
       medium detail; simplified atmospheric background.

SUBJECT: [character/station/environment] + [lineage] + [role]

MATERIALS: [3-6 concrete materials: birch bark, wool, tar leather, soapstone, 
           bone, ice, etc.]

SHAPE LAW: [Sunwise curves / Fast-hald squares / Geometric Dark angles / 
            Pressure-Hardened hydrodynamics]

PALETTE: [3 neutrals] + [1 accent]

LIGHTING: [hearth-warm / diffuse arctic daylight / ember-low-key / 
           damp cold fjord]

AVOID: photorealism, 3D render, neon, hyper-detail, extreme contrast
```
