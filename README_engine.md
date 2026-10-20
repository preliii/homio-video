# README engine.py — referință (v30)

Document de consultat doar când ai nevoie de un efect sau parametru anume. Regulile care schimbă comportamentul sunt în promptul principal. Dacă README-ul și codul se contrazic, câștigă codul (docstring-ul din engine.py).

## Teme de campanie (v29)
- `"tema": "minecraft" | "roz" | "reducere"` în config. Fără "tema" clipul arată ca în v28.
- Tema dă: fundalul (desenat în cod: minecraft = cer, nori pixelați, cuburi de iarbă, pământ; roz = inimioare; reducere = dungi + %), culorile textului și ale pastilelor, fontul titlurilor, familia de tranziții, conturul sticker pe produs și stilul ștampilei. Stickerele generice (stele, cercuri) sunt oprite.
- Cu poză de deschidere (poster), tema alege și tranziția poster → hook (minecraft: blocks, roz: iris, reducere: tiles).
- Cadrul final rămâne template-ul homio, neschimbat.
- Temă nouă: un rând în `THEMES` din engine.py (culori, pool de tranziții, font) + o funcție `_bg_<nume>` în `Background` dacă vrei fundal propriu.

## Noutăți v30
- Elementele temei (cuburi, inimioare, %) plutesc animat: în coloanele laterale, în spatele produsului și 2–3 mari, estompate, în prim-plan. Prim-planul nu apare peste poster și dispare la intrarea în cadrul final.
- Cu temă, textul are contur alb (`"edit": {"text_stroke": 0.07}`; 0 = oprit) ca să se citească și când produsul sare peste el.
- Mișcare în trend, la toate clipurile, aleasă per clip (reglabilă din "edit"):
  - `"motion": "echo"` = urmă de mișcare (produsul lasă copii care se sting) | `"blur"` = motion blur clasic.
  - `"shutter": 0.8–1.0` = cât de lung e motion blur-ul (v29: 0.42).
  - `"rgb_split": 0–1` = split RGB pe impact (doar rețetele cu shake).
  - `"text_anim": "blur"` = cuvintele ies din blur.
  - Baby și decor rămân discrete (blur scurt, fără split RGB). Timpul de randare nu crește.

## Noutăți v29 (fără temă)
- Randare în paralel: implicit min(4, nuclee) procese. `--jobs 1` = vechiul mod. Rezultat identic cadru cu cadru.
- Tranziții noi, portate din EffectCraft (MIT/Apache-2.0): `blocks` (Block Dissolve, foarte vizibilă: max 2 utilizări) și `tiles` (Grid Wipe, de bază). Intră în pool-urile toy și set.
- Ștampila „-X%" în hook când pagina are preț vechi; procentul e calculat din cele două prețuri de pe pagină. `"discount_stamp": false` o oprește; nu apare la ghici, gift și clipuri cu mai multe produse.
- Contur sticker: `"edit": {"outline": 22}` (pixeli la rezoluția decupajului; 0 = oprit). Implicit pornit doar cu temă.
- `hook_accent` cu mai multe cuvinte marchează expresia, nu fiecare cuvânt (în „48 lei → 36 lei" cu accent „36 lei", doar al doilea „lei" e marcat).
- QA nou `glife_lipsa` (FAIL): un caracter din text lipsește din font (ex. „→" în Poppins) și s-ar desena ca dreptunghi gol.

## Istoric versiuni
- v30: elemente de temă animate + prim-plan, contur text cu temă, echo / motion blur lung / split RGB / text din blur.
- v29: teme de campanie, randare în paralel, tranzițiile blocks/tiles (din EffectCraft), contur sticker, ștampila -X%, accent ca expresie, QA glife_lipsa.
- v28: QA nou pentru tipografie: `font_min` (FAIL), `cuvinte_pe_ecran_max8` (WARN), `checklist_3x6_fara_titlu` (WARN). Bug corectat: textul nu mai coboară sub `min_size` (hook 77–79 px → 80 px). Singura schimbare de randare față de v27: max 2–3 px la hook/titluri lungi.
- v27: QA nou `cuvinte_interzise` (WARN, nu FAIL: cuvintele sunt permise doar dacă apar pe pagina produsului). Docstring și README corectate. Nicio schimbare de randare.
- v26: cadrul final fără linie sub preț, aceleași fonturi mereu (Playfair pe preț și „Comandă pe homio.ro", Montserrat semibold pe pastile).
- v25: efecte wow automate: bloom/glow la aterizare, înclinare 3D, speed ramp pe impact, reflexie și lumină peste produs, zoom fin pe detalii, text mai animat.
- v24: "bg_image" = fundal foto sub produs, doar la scenele din mijloc, cu trecere lină și atenuare sus pentru text.
- v23: folder out_<produs>_<hook>, căi relative, plafon de zoom 1.5, decupaj automat la o singură poză, QA ghici_pret_ascuns, variație în același batch.
- v22: jurnalul și limitele de variație scoase (nu mai există jurnal.txt).
- v21: fără muzică, doar efecte sonore; "opening_image".
- v20: poză de deschidere.
- v19: efecte noi (tunnel, enter, tour, gift complet, bands).
- v16: cutia gift se scutură din primele 0,1 s.
- v13: cadrul final combinat (preț + signature homio), cover.jpg, carousel/, --preview, --batch, "keyword".
- v12: 19 tipuri de tranziții.

## Trusa de efecte (4–7 per clip, niciodată toate)
- Mișcarea produsului: intrare cu viteză și motion blur, bounce cu overshoot, rotire ±5°, plutire, slam cu camera shake, parallax pe 2 straturi, push-in lent, reveal cu mască (wipe/cerc), split-screen, zoom punch (1.0→1.4 în 0.2 s).
- Grafică și particule: speed lines, praf/fum la impact, burst de linii, confetti, sclipici, stickere, zăpadă/frunze (sezon), cerc/săgeată desenată pe un detaliu, light sweep.
- Text: kinetic, pop cu scale 0→110→100%, marker colorat în spatele cuvântului-cheie, counter până la preț/dimensiune, preț „ștampilat", „? lei" dezvăluit la final (tiparul „Ghici cât costă?").

## Tranziții (21 tipuri)
- De bază: cut, fade, whip (cu blur), slide, zoom, zoomout, stretch, blur, iris, wipe, dip, tiles (v29).
- Foarte vizibile (max 1 tip per clip, max 2 utilizări): spin, shape, circle, lightleak, blocks (v29).
- Accent (max 1 tip per clip, max 2 utilizări): flash, punch, glitch.
- zoomblur: tranziție de bază la wheels, kitchen și set.
- Baby și decor: doar fade, blur, lightleak, wipe, iris, dip, zoomout, slide.
- Familia folosită apare în "tranzitii" din qa.json.

## Efecte avansate (v19+)
- "intro": "tunnel" (nu la baby, decor, gift).
- "enter": "drop" | "mix" | "glide" | "pop" (colecții/combo).
- "tour": true sau {"type":"tour"} în points.
- Gift complet: lid_pop, reveal_from_box.
- Tranziția "bands", light sweep, slam cu shake, scene detail cu zoom_punch.
- "edit": {"transitions": ["whip","bands","punch","stretch"], "grain": 0.012, "vignette": 0.25, "reflect": 0.15, "bg": "dots", "sfx_pitch": 1.05}
- "edit_seed": "text" schimbă tot stilul de edit la același produs și hook.
- AUTO_CROP la o singură poză pe fundal alb (oprit cu "auto_crops": false). Zoom detail plafonat la 1.5 (WARN); "zoom_max" îl schimbă.
- Fundal foto (v24): "bg_image": "assets/fundal_camera_fetita.jpg"; implicit primele 3 scene eligibile (nu hook, poster, checklist, final). Opțional: "bg_scenes": [2,3], "bg_image_veil": 0.12, "bg_image_top": 0.42, "bg_image_zoom": 0.08.

## Efecte v25 (automate; în config doar dacă vreau altfel)
- Reglaj prin "edit" (0 = oprit): {"bloom": 0.9, "tilt3d": 1.0, "speed_ramp": 0.45 (1 = oprit), "reflect": 0.16, "sweep_land": true, "detail_fx": true, "text_anim": "letters|drop|punch|kinetic", "text_glow": 0.5}
- La baby și decor sunt mai discrete automat. Textul din hook rămâne întreg din frame 0 (doar glow-ul pulsează).
- „Mai nebun": cresc bloom și tilt3d, folosesc "punch" sau "drop".

## Parametri config utili
- Durată: automat 9–18 s (motorul scalează scenele la 9,2–17,6 s). "duration": număr forțează o durată.
- Livrare: cadrul final are mereu „Livrare în 1–2 zile"; "product.delivery" din config e ignorat.
- "hook_type": etichetă liberă (intrebare, pov, problema, cifra, cadou, contrast, alegere, setul, ghici, bucla, misterul, reducerea, prag_pret). Doar "ghici" are efect propriu („? lei" care devine preț).
- "loop": false implicit. Cu true, ultimele 0,3 s se amestecă în frame 0 (pentru teste A/B de rewatch; promptul cere implicit fără loop).
- Gift: "gift_box", "gift_ribbon" (hex).
- Preț vechi: "product": {"old_price": ...}.
- Poză de deschidere: "opening_image", "opening_dur".
- Mai multe produse: "products", "multi", "character", "numbers", "lineup_title", "combo_title", "combo_pill", "image": "group". La combo cu 3 produse: eroul mare sus + 2 dedesubt.
- Logo (colț + cadrul final): automat, nu se pune în config.

## Verificări QA automate (PASS/FAIL/WARN în qa.json)
glife_lipsa (v29, FAIL), text_zona_sigura, pret_rotunjit, cta, pret_vechi_taiat, diacritice_virgula, contrast_4.5, hook_max7, frame0_produs_intreg / frame0_hook_liber / frame0_poza, repetitii_max2, livrare_1_2_zile, fara_retur, cuvinte_interzise (v27, WARN), font_min (v28, FAIL: hook ≥ 80 px, titluri ≥ 72 px, restul ≥ 44 px), cuvinte_pe_ecran_max8 (v28, WARN), checklist_3x6_fara_titlu (v28, WARN), signature_final, durata_9_18, logo_o_data_final, contrast_final_4.5, cuvant_cheie_2s, ghici_pret_ascuns, miscare_start, miscare_2.5s, audio_varf_-3dB.

Limite cunoscute:
- `cuvinte_pe_ecran_max8` adună cuvintele pe scenă (nu pe secundă), deci poate avertiza și când textele apar pe rând. Decizia rămâne la contact sheet. Pastilele, prețul, CTA-ul, cuvântul-cheie, checklist-ul și cadrul final nu se numără.
- Textele desenate doar la randare (nu la construirea scenei) nu sunt atribuite unei scene și nu intră în numărătoare.
- `cuvinte_interzise` e doar WARN: motorul nu vede pagina produsului, unde unele cuvinte pot fi permise.
- Rămân la critica de art director: ce se citește pe telefon, bloom/tilt3d, text lipit de plăcuța logo.
