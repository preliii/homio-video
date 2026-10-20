# README engine.py — referință (mutat din promptul editorului video)

Document de consultat doar când ai nevoie de un efect sau parametru anume. Regulile care schimbă comportamentul sunt în promptul principal.

## Istoric versiuni
- v26: efecte wow automate: bloom/glow la aterizare, înclinare 3D, speed ramp pe impact, reflexie și lumină peste produs, zoom fin pe detalii, text mai animat.
- v24: "bg_image" = fundal foto sub produs, doar la scenele din mijloc, cu trecere lină și atenuare sus pentru text.
- v23: folder out_<produs>_<hook>, căi relative, plafon de zoom 1.5, decupaj automat la o singură poză, QA ghici_pret_ascuns, variație în același batch.
- v22: jurnalul și limitele de variație scoase.
- v21: fără muzică, doar efecte sonore; "opening_image".
- v20: poză de deschidere.
- v19: efecte noi (tunnel, enter, tour, gift complet, bands).
- v16: cutia gift se scutură din primele 0,1 s.
- v12: 19 tipuri de tranziții.

## Trusa de efecte (4–7 per clip, niciodată toate)
- Mișcarea produsului: intrare cu viteză și motion blur, bounce cu overshoot, rotire ±5°, plutire, slam cu camera shake, parallax pe 2 straturi, push-in lent, reveal cu mască (wipe/cerc), split-screen, zoom punch (1.0→1.4 în 0.2 s).
- Grafică și particule: speed lines, praf/fum la impact, burst de linii, confetti, sclipici, stickere, zăpadă/frunze (sezon), cerc/săgeată desenată pe un detaliu, light sweep.
- Text: kinetic, pop cu scale 0→110→100%, marker colorat în spatele cuvântului-cheie, counter până la preț/dimensiune, preț „ștampilat", „? lei" dezvăluit la final (tiparul „Ghici cât costă?").

## Tranziții (19 tipuri)
- De bază: cut, fade, whip (cu blur), slide, zoom, zoomout, stretch, blur, iris, wipe, dip.
- Foarte vizibile (max 1 tip per clip, max 2 utilizări): spin, shape, circle, lightleak.
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

## Efecte v26 (automate; în config doar dacă vreau altfel)
- Reglaj prin "edit" (0 = oprit): {"bloom": 0.9, "tilt3d": 1.0, "speed_ramp": 0.45 (1 = oprit), "reflect": 0.16, "sweep_land": true, "detail_fx": true, "text_anim": "letters|drop|punch|kinetic", "text_glow": 0.5}
- La baby și decor sunt mai discrete automat. Textul din hook rămâne întreg din frame 0 (doar glow-ul pulsează).
- „Mai nebun": cresc bloom și tilt3d, folosesc "punch" sau "drop".

## Parametri config utili
- Gift: "gift_box", "gift_ribbon" (hex).
- Preț vechi: "product": {"old_price": ...}.
- Poză de deschidere: "opening_image", "opening_dur".
- Mai multe produse: "products", "multi", "character", "numbers", "lineup_title", "combo_title", "combo_pill", "image": "group". La combo cu 3 produse: eroul mare sus + 2 dedesubt.
- Logo (colț + cadrul final): automat, nu se pune în config.
