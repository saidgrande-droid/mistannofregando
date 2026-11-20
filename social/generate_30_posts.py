import os, subprocess, json

out_dir = "/Users/grafica/Desktop/SITO/SITO PER TRAFFICO/social/piano_30_giorni"
os.makedirs(out_dir, exist_ok=True)
chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

posts_data = [
    # --- SETTIMANA 1 ---
    {
        "day": 1,
        "date": "2026-11-20",
        "file": "giorno_01_meccanico_milano.png",
        "type": "fregometro",
        "caution": "🚨 RUBRICA: IL FREGOMETRO™ • CASO REALE",
        "badge": "📍 MILANO • TAGLIANDO & FRENI",
        "stamp": "RAPINA 🚨",
        "title": "Ti chiedono <mark>480 €</mark> per cambiare le pastiglie freni a Milano.",
        "p1_label": "Preventivo Chiesto", "p1_val": "480 €", "p1_sub": "⚠️ +240 € DI SOVRAPPREZZO",
        "p2_label": "Media Reale Milano", "p2_val": "240 €", "p2_sub": "✅ PREZZO ONESTO MERCATO",
        "verdict_label": "VERDETTO FREGOMETRO:", "diff": "+100%"
    },
    {
        "day": 2,
        "date": "2026-11-21",
        "file": "giorno_02_pizza_margherita.png",
        "type": "carovita",
        "caution": "📈 OSSERVATORIO CAROVITA • DATI INFLAZIONE",
        "badge": "🍕 CIBO FUORI CASA • PIZZA MARGHERITA",
        "stamp": "+42% REALE 📈",
        "title": "Quanto è aumentata la Margherita in Italia: <mark>2019 vs 2026</mark>",
        "p1_label": "Prezzo Medio 2019", "p1_val": "5,50 €", "p1_sub": "✅ PRE-PANDEMIA",
        "p2_label": "Prezzo Medio Oggi", "p2_val": "8,50 €", "p2_sub": "⚠️ +3,00 € A PIZZA",
        "b1": "Milano: 10,50 €", "b2": "Roma: 8,50 €", "b3": "Bologna: 8,00 €", "b4": "Napoli: 5,50 €"
    },
    {
        "day": 3,
        "date": "2026-11-22",
        "file": "giorno_03_diritti_preventivo.png",
        "type": "diritti",
        "caution": "⚖️ I TUOI DIRITTI • CODICE DEL CONSUMO",
        "badge": "🛡️ GUIDA ANTI-FREGATURA",
        "stamp": "COSA DICE LA LEGGE ⚖️",
        "title": "Possono farti pagare il preventivo se <mark>NON lo accetti?</mark>",
        "ans_head": "RISPOSTA BREVE: NO.",
        "ans_body": "Il preventivo in Italia è per legge GRATUITO, a meno che non ti abbiano avvisato per iscritto PRIMA di metterci le mani.",
        "r1_head": "❌ ILLECITO", "r1_txt": "Se ti chiedono 50€ 'per il disturbo' a lavoro finito senza accordo scritto preventivo.",
        "r2_head": "✅ LEGITTIMO", "r2_txt": "Solo se prima ti hanno fatto firmare che lo smontaggio/diagnosi era a pagamento."
    },
    {
        "day": 4,
        "date": "2026-11-23",
        "file": "giorno_04_dentista_roma.png",
        "type": "fregometro",
        "caution": "🚨 RUBRICA: IL FREGOMETRO™ • CASO REALE",
        "badge": "📍 ROMA • DENTISTA PRIVATO",
        "stamp": "SOSPETTO ⚠️",
        "title": "Ti chiedono <mark>280 €</mark> per igiene e una piccola carie a Roma.",
        "p1_label": "Preventivo Chiesto", "p1_val": "280 €", "p1_sub": "⚠️ +150 € SOPRA LA MEDIA",
        "p2_label": "Media Reale Roma", "p2_val": "130 €", "p2_sub": "✅ TARIFFA MEDIA CITTÀ",
        "verdict_label": "VERDETTO FREGOMETRO:", "diff": "+115%"
    },
    {
        "day": 5,
        "date": "2026-11-24",
        "file": "giorno_05_classifica_caffe.png",
        "type": "classifica",
        "caution": "🏆 CLASSIFICA NAZIONALE • 107 PROVINCE",
        "badge": "☕ COSTO DELLA VITA • IL CAFFÈ AL BAR",
        "stamp": "+74% DIVARIO ☕",
        "title": "La classifica del caffè in Italia: <mark>la più cara vs più economica</mark>",
        "t_top": "🔴 LE PIÙ CARE D'ITALIA",
        "t1": "1. Bolzano: 1,65 €", "t2": "2. Trento: 1,55 €", "t3": "3. Bologna: 1,50 €",
        "t_low": "🟢 LE PIÙ ECONOMICHE",
        "l1": "1. Catanzaro: 0,95 €", "l2": "2. Napoli: 1,00 €", "l3": "3. Bari: 1,05 €"
    },
    {
        "day": 6,
        "date": "2026-11-25",
        "file": "giorno_06_carovita_single.png",
        "type": "carovita",
        "caution": "📈 OSSERVATORIO CAROVITA • STILE DI VITA",
        "badge": "🏠 LA TASSA INVISIBILE • VIVERE DA SOLI",
        "stamp": "+48% COSTO 📈",
        "title": "La 'Tassa Single' in Italia: <mark>quanto costa vivere da soli?</mark>",
        "p1_label": "Spesa Mensile Coppia (pro capite)", "p1_val": "780 €", "p1_sub": "✅ COSTI CONDIVISI",
        "p2_label": "Spesa Mensile Single", "p2_val": "1.160 €", "p2_sub": "⚠️ +380 € AL MESE EXTRA",
        "b1": "Affitto: +65%", "b2": "Bollette: +40%", "b3": "Spesa cibo: +35%", "b4": "Rifiuti: +28%"
    },
    {
        "day": 7,
        "date": "2026-11-26",
        "file": "giorno_07_idraulico_torino.png",
        "type": "fregometro",
        "caution": "🚨 RUBRICA: IL FREGOMETRO™ • CASO REALE",
        "badge": "📍 TORINO • IDRAULICO CASA",
        "stamp": "RAPINA 🚨",
        "title": "Ti chiedono <mark>340 €</mark> per cambiare un rubinetto e sifone a Torino.",
        "p1_label": "Preventivo Chiesto", "p1_val": "340 €", "p1_sub": "⚠️ +220 € EXTRA PAGATI",
        "p2_label": "Media Reale Torino", "p2_val": "120 €", "p2_sub": "✅ COSTO MEDIO INTERVENTO",
        "verdict_label": "VERDETTO FREGOMETRO:", "diff": "+183%"
    },

    # --- SETTIMANA 2 ---
    {
        "day": 8,
        "date": "2026-11-27",
        "file": "giorno_08_diritti_coperto.png",
        "type": "diritti",
        "caution": "⚖️ I TUOI DIRITTI • RISTORAZIONE",
        "badge": "🍽️ GUIDA CONSUMATORE AL RISTORANTE",
        "stamp": "QUANDO È ILLEGALE? 🚫",
        "title": "Coperto e servizio a 4,50€ a persona: <mark>quando è ILLEGALE?</mark>",
        "ans_head": "COSA DICE LA LEGGE:",
        "ans_body": "In alcune regioni (es. Lazio dal 2006) il 'coperto' è vietato per legge. Il 'servizio' è lecito SOLO se scritto chiaramente nel menu in percentuale.",
        "r1_head": "❌ ILLECITO", "r1_txt": "Se ti mettono 'servizio 15%' o 'coperto' senza averlo scritto sul menu visibile.",
        "r2_head": "✅ LEGITTIMO", "r2_txt": "Solo se la voce è stampata nero su bianco all'ingresso o sul listino prezzi."
    },
    {
        "day": 9,
        "date": "2026-11-28",
        "file": "giorno_09_elettricista_napoli.png",
        "type": "fregometro",
        "caution": "🚨 RUBRICA: IL FREGOMETRO™ • CASO REALE",
        "badge": "📍 NAPOLI • ELETTRICISTA & QUADRO",
        "stamp": "FUORI SCALA 🚨",
        "title": "Ti chiedono <mark>650 €</mark> per montare un salvavita a Napoli.",
        "p1_label": "Preventivo Chiesto", "p1_val": "650 €", "p1_sub": "⚠️ +370 € DI SOVRAPPREZZO",
        "p2_label": "Media Reale Napoli", "p2_val": "280 €", "p2_sub": "✅ MATERIALE + MANODOPERA",
        "verdict_label": "VERDETTO FREGOMETRO:", "diff": "+132%"
    },
    {
        "day": 10,
        "date": "2026-11-29",
        "file": "giorno_10_carovita_shrinkflation.png",
        "type": "carovita",
        "caution": "📈 OSSERVATORIO CAROVITA • SUPERMERCATO",
        "badge": "🛒 TRUCCHI DEL COMMERCIO • SHRINKFLATION",
        "stamp": "MENO CIBO 📦",
        "title": "I 4 prodotti dove <mark>il peso cala ma il prezzo sale</mark>",
        "p1_label": "Esempio Biscotti", "p1_val": "400g ➔ 350g", "p1_sub": "⚠️ -12,5% DI PRODOTTO",
        "p2_label": "Prezzo al Banco", "p2_val": "+18%", "p2_sub": "🔴 PAGHI DI PIÙ PER AVERE MENO",
        "b1": "Patatine: -20g", "b2": "Cioccolato: -15g", "b3": "Detersivo: -4 lavaggi", "b4": "Pasta: formati ridotti"
    },
    {
        "day": 11,
        "date": "2026-11-30",
        "file": "giorno_11_classifica_bagno.png",
        "type": "classifica",
        "caution": "🏆 CLASSIFICA NAZIONALE • EDILIZIA",
        "badge": "🛁 RISTRUTTURAZIONE • COSTO A METRO QUADRO",
        "stamp": "+85% DIFFERENZA 🛁",
        "title": "Quanto costa rifare il bagno in Italia: <mark>prezzo medio a mq</mark>",
        "t_top": "🔴 LE PIÙ CARE AL MQ",
        "t1": "1. Milano: 1.650 €/mq", "t2": "2. Firenze: 1.480 €/mq", "t3": "3. Roma: 1.420 €/mq",
        "t_low": "🟢 LE PIÙ CONVENIENTI",
        "l1": "1. Cosenza: 890 €/mq", "l2": "2. Taranto: 920 €/mq", "l3": "3. Palermo: 960 €/mq"
    },
    {
        "day": 12,
        "date": "2026-12-01",
        "file": "giorno_12_veterinario_firenze.png",
        "type": "fregometro",
        "caution": "🚨 RUBRICA: IL FREGOMETRO™ • CASO REALE",
        "badge": "📍 FIRENZE • VETERINARIO & ANIMALI",
        "stamp": "SOSPETTO 🐶",
        "title": "Ti chiedono <mark>170 €</mark> per una visita base e vaccino a Firenze.",
        "p1_label": "Preventivo Chiesto", "p1_val": "170 €", "p1_sub": "⚠️ +95 € SOPRA LA MEDIA",
        "p2_label": "Media Reale Firenze", "p2_val": "75 €", "p2_sub": "✅ VISITA + VACCINO STANDARD",
        "verdict_label": "VERDETTO FREGOMETRO:", "diff": "+126%"
    },
    {
        "day": 13,
        "date": "2026-12-02",
        "file": "giorno_13_diritti_meccanico_materiali.png",
        "type": "diritti",
        "caution": "⚖️ I TUOI DIRITTI • MECCANICO & FATTURE",
        "badge": "🔧 TASSE FANTASMA IN FATTURA",
        "stamp": "VOCE DUBBIA 🚫",
        "title": "La voce 'Materiale di consumo' da 40€ dal meccanico: <mark>è obbligatoria?</mark>",
        "ans_head": "COSA DICE LA NORMA:",
        "ans_body": "Stracci, sgrassatore e guanti NON possono costare 40€. La voce forfettaria è lecita solo tra il 2% e il 4% dell'importo totale di manodopera.",
        "r1_head": "❌ FREGATURA", "r1_txt": "Se ti mettono 30-50€ fissi su un lavoretto da 100€ di manodopera.",
        "r2_head": "✅ DIRITTO", "r2_txt": "Puoi chiedere la voce analitica dettagliata prima di saldare la fattura."
    },
    {
        "day": 14,
        "date": "2026-12-03",
        "file": "giorno_14_carovita_colazione.png",
        "type": "carovita",
        "caution": "📈 OSSERVATORIO CAROVITA • ABITUDINI ITALIANE",
        "badge": "🥐 IL RITO DEL MATTINO • CAPPUCCIO & CORNETTO",
        "stamp": "+38% IN 5 ANNI ☕",
        "title": "Quanto costa la colazione al bar in Italia: <mark>2020 vs 2026</mark>",
        "p1_label": "Costo Medio 2020", "p1_val": "2,40 €", "p1_sub": "✅ PREZZO MEDIO NAZIONALE",
        "p2_label": "Costo Medio Oggi", "p2_val": "3,30 €", "p2_sub": "⚠️ +270 €/ANNO PER CHI LA FA TUTTI I GIORNI",
        "b1": "Milano: 3,90 €", "b2": "Venezia: 4,10 €", "b3": "Roma: 3,20 €", "b4": "Bari: 2,60 €"
    },

    # --- SETTIMANA 3 ---
    {
        "day": 15,
        "date": "2026-12-04",
        "file": "giorno_15_ristrutturazione_bologna.png",
        "type": "fregometro",
        "caution": "🚨 RUBRICA: IL FREGOMETRO™ • CASO REALE",
        "badge": "📍 BOLOGNA • RISTRUTTURAZIONE BAGNO",
        "stamp": "FOLLIA 🏗️",
        "title": "Ti chiedono <mark>14.500 €</mark> per rifare un bagno di 5 mq a Bologna.",
        "p1_label": "Preventivo Chiesto", "p1_val": "14.500 €", "p1_sub": "⚠️ +7.700 € DI SOVRAPPREZZO",
        "p2_label": "Media Reale Bologna", "p2_val": "6.800 €", "p2_sub": "✅ COSTO IMPRESA COMPLETO",
        "verdict_label": "VERDETTO FREGOMETRO:", "diff": "+113%"
    },
    {
        "day": 16,
        "date": "2026-12-05",
        "file": "giorno_16_classifica_taxi.png",
        "type": "classifica",
        "caution": "🏆 CLASSIFICA NAZIONALE • TRASPORTI URBANI",
        "badge": "🚖 TARIFFE TAXI • TRATTA CITTADINA 10 KM",
        "stamp": "+65% DIVARIO 🚖",
        "title": "Quanto costa fare 10 km in taxi in Italia: <mark>le città a confronto</mark>",
        "t_top": "🔴 LE CITTÀ PIÙ SALATE",
        "t1": "1. Milano: 24,50 €", "t2": "2. Firenze: 23,80 €", "t3": "3. Roma: 22,00 €",
        "t_low": "🟢 LE CITTÀ PIÙ ECONOMICHE",
        "l1": "1. Napoli: 14,80 €", "l2": "2. Palermo: 15,50 €", "l3": "3. Torino: 17,20 €"
    },
    {
        "day": 17,
        "date": "2026-12-06",
        "file": "giorno_17_fabbro_genova.png",
        "type": "fregometro",
        "caution": "🚨 RUBRICA: IL FREGOMETRO™ • CASO REALE",
        "badge": "📍 GENOVA • PRONTO INTERVENTO FABBRO",
        "stamp": "RAPINA 🔑",
        "title": "Ti chiedono <mark>450 €</mark> per aprire una porta bloccata a Genova.",
        "p1_label": "Preventivo Notturno Chiesto", "p1_val": "450 €", "p1_sub": "⚠️ +270 € OLTRE LA MEDIA",
        "p2_label": "Media Reale Pronto Intervento", "p2_val": "180 €", "p2_sub": "✅ INTERVENTO DI URGENZA",
        "verdict_label": "VERDETTO FREGOMETRO:", "diff": "+150%"
    },
    {
        "day": 18,
        "date": "2026-12-07",
        "file": "giorno_18_diritti_recesso.png",
        "type": "diritti",
        "caution": "⚖️ I TUOI DIRITTI • ACQUISTI & SHOPPING",
        "badge": "📦 DIRITTO DI RECESSO • 14 GIORNI",
        "stamp": "SFATIAMO UN MITO 🛍️",
        "title": "Puoi restituire un prodotto comprato in <mark>negozio fisico?</mark>",
        "ans_head": "LA VERITÀ CHE NESSUNO DICE:",
        "ans_body": "Il diritto di recesso entro 14 giorni vale SOLO per gli acquisti online! Nei negozi fisici il cambio è a discrezione del negoziante, salvo merce difettosa.",
        "r1_head": "💻 ACQUISTO ONLINE", "r1_txt": "Per legge hai 14 giorni di ripensamento senza dover dare alcuna spiegazione.",
        "r2_head": "🏬 NEGOZIO FISICO", "r2_txt": "Il rimborso in contanti non è un obbligo di legge: possono darti un buono spesa."
    },
    {
        "day": 19,
        "date": "2026-12-08",
        "file": "giorno_19_carovita_stanze_studenti.png",
        "type": "carovita",
        "caution": "📈 OSSERVATORIO CAROVITA • EMERGENZA CASA",
        "badge": "🎓 AFFITTI STUDENTI • STANZA SINGOLA",
        "stamp": "+55% IN 4 ANNI 🏠",
        "title": "Quanto costa una stanza singola in Italia: <mark>la mappa del carovita</mark>",
        "p1_label": "Media Nazionale 2021", "p1_val": "390 €", "p1_sub": "✅ COSTO MENSILE MEDIO",
        "p2_label": "Media Nazionale Oggi", "p2_val": "540 €", "p2_sub": "⚠️ +150 €/MESE A STUDENTE",
        "b1": "Milano: 680 €", "b2": "Roma: 520 €", "b3": "Bologna: 510 €", "b4": "Bari: 320 €"
    },
    {
        "day": 20,
        "date": "2026-12-09",
        "file": "giorno_20_tecnologia_palermo.png",
        "type": "fregometro",
        "caution": "🚨 RUBRICA: IL FREGOMETRO™ • CASO REALE",
        "badge": "📍 PALERMO • RIPARAZIONE SMARTPHONE",
        "stamp": "FUORI SCALA 📱",
        "title": "Ti chiedono <mark>320 €</mark> per cambiare lo schermo OLED a Palermo.",
        "p1_label": "Preventivo Chiesto", "p1_val": "320 €", "p1_sub": "⚠️ +180 € OLTRE IL RICAMBIO",
        "p2_label": "Media Reale Palermo", "p2_val": "140 €", "p2_sub": "✅ DISPLAY + MONTAGGIO",
        "verdict_label": "VERDETTO FREGOMETRO:", "diff": "+128%"
    },
    {
        "day": 21,
        "date": "2026-12-10",
        "file": "giorno_21_classifica_manodopera_auto.png",
        "type": "classifica",
        "caution": "🏆 CLASSIFICA NAZIONALE • OFFICINE & MOTORI",
        "badge": "⏱️ TARIFFA ORARIA • MECCANICO AL LAVORO",
        "stamp": "+120% DIFFERENZA ⏱️",
        "title": "Quanto costa 1 ora di manodopera dal meccanico in Italia?",
        "t_top": "🔴 LE PIÙ CARE D'ITALIA",
        "t1": "1. Bolzano: 72 €/ora", "t2": "2. Milano: 68 €/ora", "t3": "3. Bologna: 62 €/ora",
        "t_low": "🟢 LE PIÙ CONVENIENTI",
        "l1": "1. Napoli: 32 €/ora", "l2": "2. Foggia: 35 €/ora", "l3": "3. Catanzaro: 36 €/ora"
    },

    # --- SETTIMANA 4 ---
    {
        "day": 22,
        "date": "2026-12-11",
        "file": "giorno_22_commercialista_verona.png",
        "type": "fregometro",
        "caution": "🚨 RUBRICA: IL FREGOMETRO™ • CASO REALE",
        "badge": "📍 VERONA • COMMERCIALISTA & FISCO",
        "stamp": "SOSPETTO 💼",
        "title": "Ti chiedono <mark>160 €</mark> per un modello 730 singolo a Verona.",
        "p1_label": "Preventivo Chiesto", "p1_val": "160 €", "p1_sub": "⚠️ +100 € SOPRA LA MEDIA",
        "p2_label": "Media Reale Verona", "p2_val": "60 €", "p2_sub": "✅ TARIFFA MEDIA 730 SEMPLICE",
        "verdict_label": "VERDETTO FREGOMETRO:", "diff": "+166%"
    },
    {
        "day": 23,
        "date": "2026-12-12",
        "file": "giorno_23_diritti_garanzia_spedizione.png",
        "type": "diritti",
        "caution": "⚖️ I TUOI DIRITTI • GARANZIA LEGALE",
        "badge": "🛡️ COSA DICE IL CODICE DEL CONSUMO",
        "stamp": "SPESE ILLEGALI 🚫",
        "title": "Prodotto guasto in garanzia: <mark>chi paga le spese di spedizione?</mark>",
        "ans_head": "COSA DICE LA LEGGE:",
        "ans_body": "La garanzia legale di 2 anni stabilisce che la riparazione o sostituzione deve avvenire SENZA ALCUNA SPESA per il consumatore (spese di spedizione incluse).",
        "r1_head": "❌ FREGATURA", "r1_txt": "Se il venditore ti chiede 20€ per inviare il pacco al centro assistenza autorizzato.",
        "r2_head": "✅ DIRITTO", "r2_txt": "Il venditore deve fornirti un'etichetta prepagata o rimborsarti l'intero costo."
    },
    {
        "day": 24,
        "date": "2026-12-13",
        "file": "giorno_24_carovita_bollette_fissi.png",
        "type": "carovita",
        "caution": "📈 OSSERVATORIO CAROVITA • ENERGIA & BOLLETTE",
        "badge": "💡 LA TRAPPOLA IN BOLLETTA • COSTI FISSI",
        "stamp": "PAGHI COMUNQUE ⚡",
        "title": "Quanto paghi in bolletta anche con <mark>CONSUMO ZERO?</mark>",
        "p1_label": "Spesa Luce a Consumo Zero", "p1_val": "18-22 €/mese", "p1_sub": "⚠️ QUOTA FISSA + ONERI",
        "p2_label": "Costo Annuo Solo per Esistere", "p2_val": "~250 €", "p2_sub": "🔴 SENZA ACCENDERE UNA LAMPADINA",
        "b1": "Commercializzazione: ~10€", "b2": "Trasporto contatore: ~8€", "b3": "Oneri sistema: ~3€", "b4": "IVA & accise fisse"
    },
    {
        "day": 25,
        "date": "2026-12-14",
        "file": "giorno_25_imbianchino_bari.png",
        "type": "fregometro",
        "caution": "🚨 RUBRICA: IL FREGOMETRO™ • CASO REALE",
        "badge": "📍 BARI • TINTEGGIATURA APPARTAMENTO",
        "stamp": "FUORI MERCATO 🎨",
        "title": "Ti chiedono <mark>2.800 €</mark> per imbiancare 80 mq a Bari.",
        "p1_label": "Preventivo Chiesto", "p1_val": "2.800 €", "p1_sub": "⚠️ +1.600 € EXTRA",
        "p2_label": "Media Reale Bari", "p2_val": "1.200 €", "p2_sub": "✅ PITTURA BIANCA 2 MANI INCLUSA",
        "verdict_label": "VERDETTO FREGOMETRO:", "diff": "+133%"
    },
    {
        "day": 26,
        "date": "2026-12-15",
        "file": "giorno_26_classifica_cinema.png",
        "type": "classifica",
        "caution": "🏆 CLASSIFICA NAZIONALE • SVAGO & CULTURA",
        "badge": "🎬 BIGLIETTO CINEMA • SABATO SERA",
        "stamp": "+50% DIFFERENZA 🍿",
        "title": "La mappa del cinema in Italia: <mark>dove costa di più il biglietto?</mark>",
        "t_top": "🔴 LE PIÙ CARE D'ITALIA",
        "t1": "1. Milano: 11,50 €", "t2": "2. Roma: 10,50 €", "t3": "3. Firenze: 10,00 €",
        "t_low": "🟢 LE PIÙ ECONOMICHE",
        "l1": "1. Trapani: 7,00 €", "l2": "2. Potenza: 7,50 €", "l3": "3. Campobasso: 7,50 €"
    },
    {
        "day": 27,
        "date": "2026-12-16",
        "file": "giorno_27_caldaia_padova.png",
        "type": "fregometro",
        "caution": "🚨 RUBRICA: IL FREGOMETRO™ • CASO REALE",
        "badge": "📍 PADOVA • MANUTENZIONE CALDAIA",
        "stamp": "SOSPETTO 🔥",
        "title": "Ti chiedono <mark>190 €</mark> per il bollino e fumi caldaia a Padova.",
        "p1_label": "Preventivo Chiesto", "p1_val": "190 €", "p1_sub": "⚠️ +100 € SOPRA LA MEDIA",
        "p2_label": "Media Reale Padova", "p2_val": "90 €", "p2_sub": "✅ PULIZIA + ANALISI FUMI",
        "verdict_label": "VERDETTO FREGOMETRO:", "diff": "+111%"
    },
    {
        "day": 28,
        "date": "2026-12-17",
        "file": "giorno_28_diritti_pos_sovrapprezzo.png",
        "type": "diritti",
        "caution": "⚖️ I TUOI DIRITTI • PAGAMENTI DIGITALI",
        "badge": "💳 COMMISSIONI POS & CARTA DI CREDITO",
        "stamp": "VIETATISSIMO 🚫",
        "title": "Un commerciante può applicare un <mark>sovrapprezzo per pagare con POS?</mark>",
        "ans_head": "COSA DICE LA LEGGE:",
        "ans_body": "È SEVERAMENTE VIETATO dalla legge europea e italiana (direttiva PSD2). Il prezzo deve essere identico sia che paghi in contanti sia con carta.",
        "r1_head": "❌ SANZIONE", "r1_txt": "Il commerciante rischia una multa di 30€ + il 4% dell'importo della transazione.",
        "r2_head": "✅ DIRITTO", "r2_txt": "Non sei obbligato a pagare il 'surplus di 1 euro per il POS': è totalmente illegale."
    },
    {
        "day": 29,
        "date": "2026-12-18",
        "file": "giorno_29_carovita_panettone.png",
        "type": "carovita",
        "caution": "📈 OSSERVATORIO CAROVITA • NATALE",
        "badge": "🎄 FESTE & DOLCI • IL PANETTONE",
        "stamp": "+35% IN 3 ANNI 🎄",
        "title": "Quanto costa il Panettone Artigianale: <mark>l'impennata natalizia</mark>",
        "p1_label": "Prezzo Medio 2021", "p1_val": "28 €/kg", "p1_sub": "✅ PASTICCERIA STANDARD",
        "p2_label": "Prezzo Medio Oggi", "p2_val": "38 €/kg", "p2_sub": "⚠️ +10 €/KG SUL CARRELLO DI NATALE",
        "b1": "Milano: 44 €/kg", "b2": "Torino: 39 €/kg", "b3": "Roma: 36 €/kg", "b4": "Napoli: 35 €/kg"
    },
    {
        "day": 30,
        "date": "2026-12-19",
        "file": "giorno_30_fotografo_venezia.png",
        "type": "fregometro",
        "caution": "🚨 RUBRICA: IL FREGOMETRO™ • CASO REALE",
        "badge": "📍 VENEZIA • FOTOGRAFO NOZZE",
        "stamp": "TASSA SPOSI 💍",
        "title": "Ti chiedono <mark>4.200 €</mark> per foto e video matrimonio a Venezia.",
        "p1_label": "Preventivo Chiesto", "p1_val": "4.200 €", "p1_sub": "⚠️ +2.400 € DI RICARICO",
        "p2_label": "Media Reale Venezia", "p2_val": "1.800 €", "p2_sub": "✅ SERVIZIO COMPLETO MATRIMONIO",
        "verdict_label": "VERDETTO FREGOMETRO:", "diff": "+133%"
    }
]

# TEMPLATES
tmpl_fregometro = """<!doctype html><html><head><meta charset="utf-8" />
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Space+Grotesk:wght@700&family=JetBrains+Mono:wght@800&display=swap" rel="stylesheet">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { width: 1080px; height: 1080px; background-color: #CCFF00; font-family: 'Space Grotesk', system-ui, sans-serif; color: #000000; display: flex; flex-direction: column; justify-content: space-between; padding: 56px; }
.caution-strip { background: #000000; color: #CCFF00; font-family: 'Archivo Black', sans-serif; font-size: 15px; letter-spacing: 0.15em; padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; border-radius: 12px; text-transform: uppercase; }
.huge-card { background: #000000; color: #FFFFFF; border-radius: 36px; padding: 50px; position: relative; box-shadow: 18px 20px 0px rgba(0, 0, 0, 0.3); }
.tag-badge { display: inline-block; background: #CCFF00; color: #000000; font-family: 'Archivo Black', sans-serif; font-size: 16px; padding: 8px 20px; border-radius: 999px; text-transform: uppercase; margin-bottom: 24px; }
.card-title { font-family: 'Archivo Black', sans-serif; font-size: 46px; line-height: 1.1; letter-spacing: -0.02em; margin-bottom: 34px; text-transform: uppercase; }
.card-title mark { background: #FF2E54; color: #FFFFFF; padding: 0 12px; border-radius: 8px; }
.stamp { position: absolute; top: 36px; right: 48px; border: 5px solid #FF2E54; color: #FF2E54; font-family: 'Archivo Black', sans-serif; font-size: 26px; padding: 8px 20px; text-transform: uppercase; letter-spacing: 0.08em; transform: rotate(8deg); border-radius: 12px; background: rgba(255, 46, 84, 0.1); }
.stats-split { display: grid; grid-template-columns: 1.1fr 0.9fr; gap: 20px; margin-bottom: 28px; }
.stat-box { border-radius: 24px; padding: 24px 28px; }
.stat-box.red { background: #1A0D11; border: 2px solid #FF2E54; }
.stat-box.green { background: #0D1A14; border: 2px solid #00FF88; }
.stat-tag { font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; }
.red .stat-tag { color: #FF8599; } .green .stat-tag { color: #85FFC0; }
.stat-number { font-family: 'Archivo Black', sans-serif; font-size: 58px; line-height: 1; }
.red .stat-number { color: #FF2E54; } .green .stat-number { color: #00FF88; }
.stat-note { margin-top: 8px; font-family: 'JetBrains Mono', monospace; font-size: 15px; font-weight: 800; }
.red .stat-note { color: #FF8599; } .green .stat-note { color: #85FFC0; }
.pill-footer { background: #CCFF00; color: #000000; border-radius: 20px; padding: 18px 28px; display: flex; align-items: center; justify-content: space-between; }
.pill-text { font-family: 'Archivo Black', sans-serif; font-size: 22px; text-transform: uppercase; }
.pill-diff { font-family: 'Archivo Black', sans-serif; font-size: 36px; color: #FF2E54; background: #000000; padding: 4px 18px; border-radius: 12px; }
.bottom-banner { background: #000000; color: #FFFFFF; border-radius: 24px; padding: 22px 36px; display: flex; align-items: center; justify-content: space-between; }
.bottom-brand { font-family: 'Archivo Black', sans-serif; font-size: 24px; letter-spacing: -0.02em; }
.bottom-link { font-family: 'JetBrains Mono', monospace; background: #CCFF00; color: #000000; padding: 10px 24px; border-radius: 999px; font-size: 22px; font-weight: 800; }
</style></head>
<body>
  <div class="caution-strip"><span>{caution}</span><span>107 PROVINCE</span><span>DATI REALI</span></div>
  <div class="huge-card">
    <div class="stamp">{stamp}</div>
    <div class="tag-badge">{badge}</div>
    <h1 class="card-title">{title}</h1>
    <div class="stats-split">
      <div class="stat-box red">
        <div class="stat-tag">{p1_label}</div>
        <div class="stat-number">{p1_val}</div>
        <div class="stat-note">{p1_sub}</div>
      </div>
      <div class="stat-box green">
        <div class="stat-tag">{p2_label}</div>
        <div class="stat-number">{p2_val}</div>
        <div class="stat-note">{p2_sub}</div>
      </div>
    </div>
    <div class="pill-footer">
      <div class="pill-text">{verdict_label}</div>
      <div class="pill-diff">{diff}</div>
    </div>
  </div>
  <div class="bottom-banner">
    <div class="bottom-brand">NON FARTI FREGARE. CONTROLLA PRIMA.</div>
    <div class="bottom-link">mistannofregando.it</div>
  </div>
</body></html>"""

tmpl_carovita = """<!doctype html><html><head><meta charset="utf-8" />
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Space+Grotesk:wght@700&family=JetBrains+Mono:wght@800&display=swap" rel="stylesheet">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { width: 1080px; height: 1080px; background-color: #CCFF00; font-family: 'Space Grotesk', system-ui, sans-serif; color: #000000; display: flex; flex-direction: column; justify-content: space-between; padding: 56px; }
.caution-strip { background: #000000; color: #CCFF00; font-family: 'Archivo Black', sans-serif; font-size: 15px; letter-spacing: 0.15em; padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; border-radius: 12px; text-transform: uppercase; }
.huge-card { background: #000000; color: #FFFFFF; border-radius: 36px; padding: 50px; position: relative; box-shadow: 18px 20px 0px rgba(0, 0, 0, 0.3); }
.tag-badge { display: inline-block; background: #FF2E54; color: #FFFFFF; font-family: 'Archivo Black', sans-serif; font-size: 16px; padding: 8px 20px; border-radius: 999px; text-transform: uppercase; margin-bottom: 24px; }
.card-title { font-family: 'Archivo Black', sans-serif; font-size: 44px; line-height: 1.1; letter-spacing: -0.02em; margin-bottom: 34px; text-transform: uppercase; }
.card-title mark { background: #CCFF00; color: #000000; padding: 0 12px; border-radius: 8px; }
.stamp { position: absolute; top: 36px; right: 48px; border: 5px solid #CCFF00; color: #CCFF00; font-family: 'Archivo Black', sans-serif; font-size: 26px; padding: 8px 20px; text-transform: uppercase; letter-spacing: 0.08em; transform: rotate(-6deg); border-radius: 12px; background: rgba(204, 255, 0, 0.1); }
.stats-split { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 26px; }
.stat-box { border-radius: 24px; padding: 22px 28px; }
.stat-box.green { background: #0D1A14; border: 2px solid #00FF88; }
.stat-box.red { background: #1A0D11; border: 2px solid #FF2E54; }
.stat-tag { font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; }
.green .stat-tag { color: #85FFC0; } .red .stat-tag { color: #FF8599; }
.stat-number { font-family: 'Archivo Black', sans-serif; font-size: 50px; line-height: 1; }
.green .stat-number { color: #00FF88; } .red .stat-number { color: #FF2E54; }
.stat-note { margin-top: 8px; font-family: 'JetBrains Mono', monospace; font-size: 15px; font-weight: 800; }
.green .stat-note { color: #85FFC0; } .red .stat-note { color: #FF8599; }
.breakdown-row { background: #111827; border-radius: 20px; padding: 18px 24px; display: flex; justify-content: space-between; align-items: center; font-family: 'JetBrains Mono', monospace; font-size: 17px; font-weight: 800; }
.breakdown-row span { color: #94A3B8; } .breakdown-row strong { color: #CCFF00; }
.bottom-banner { background: #000000; color: #FFFFFF; border-radius: 24px; padding: 22px 36px; display: flex; align-items: center; justify-content: space-between; }
.bottom-brand { font-family: 'Archivo Black', sans-serif; font-size: 24px; letter-spacing: -0.02em; }
.bottom-link { font-family: 'JetBrains Mono', monospace; background: #CCFF00; color: #000000; padding: 10px 24px; border-radius: 999px; font-size: 22px; font-weight: 800; }
</style></head>
<body>
  <div class="caution-strip"><span>{caution}</span><span>DATI INFLAZIONE REALE</span><span>REPORT ITALIA</span></div>
  <div class="huge-card">
    <div class="stamp">{stamp}</div>
    <div class="tag-badge">{badge}</div>
    <h1 class="card-title">{title}</h1>
    <div class="stats-split">
      <div class="stat-box green">
        <div class="stat-tag">{p1_label}</div>
        <div class="stat-number">{p1_val}</div>
        <div class="stat-note">{p1_sub}</div>
      </div>
      <div class="stat-box red">
        <div class="stat-tag">{p2_label}</div>
        <div class="stat-number">{p2_val}</div>
        <div class="stat-note">{p2_sub}</div>
      </div>
    </div>
    <div class="breakdown-row">
      <div><span>{b1}</span></div>
      <div><span>{b2}</span></div>
      <div><span>{b3}</span></div>
      <div><span>{b4}</span></div>
    </div>
  </div>
  <div class="bottom-banner">
    <div class="bottom-brand">MISTANNOFREGANDO.IT • ANALISI INDIPENDENTE</div>
    <div class="bottom-link">mistannofregando.it</div>
  </div>
</body></html>"""

tmpl_diritti = """<!doctype html><html><head><meta charset="utf-8" />
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Space+Grotesk:wght@700&family=JetBrains+Mono:wght@800&display=swap" rel="stylesheet">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { width: 1080px; height: 1080px; background-color: #CCFF00; font-family: 'Space Grotesk', system-ui, sans-serif; color: #000000; display: flex; flex-direction: column; justify-content: space-between; padding: 56px; }
.caution-strip { background: #000000; color: #CCFF00; font-family: 'Archivo Black', sans-serif; font-size: 15px; letter-spacing: 0.15em; padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; border-radius: 12px; text-transform: uppercase; }
.huge-card { background: #000000; color: #FFFFFF; border-radius: 36px; padding: 50px; position: relative; box-shadow: 18px 20px 0px rgba(0, 0, 0, 0.3); }
.tag-badge { display: inline-block; background: #00F0FF; color: #000000; font-family: 'Archivo Black', sans-serif; font-size: 16px; padding: 8px 20px; border-radius: 999px; text-transform: uppercase; margin-bottom: 24px; }
.card-title { font-family: 'Archivo Black', sans-serif; font-size: 42px; line-height: 1.15; letter-spacing: -0.02em; margin-bottom: 30px; text-transform: uppercase; }
.card-title mark { background: #FF2E54; color: #FFFFFF; padding: 0 10px; border-radius: 8px; }
.stamp { position: absolute; top: 36px; right: 48px; border: 5px solid #00F0FF; color: #00F0FF; font-family: 'Archivo Black', sans-serif; font-size: 24px; padding: 8px 20px; text-transform: uppercase; letter-spacing: 0.08em; transform: rotate(5deg); border-radius: 12px; background: rgba(0, 240, 255, 0.1); }
.law-answer { background: #111827; border-left: 6px solid #CCFF00; border-radius: 16px; padding: 24px; margin-bottom: 26px; }
.law-heading { font-family: 'Archivo Black', sans-serif; font-size: 26px; color: #CCFF00; text-transform: uppercase; margin-bottom: 10px; }
.law-body { font-size: 19px; line-height: 1.4; color: #E2E8F0; font-weight: 700; }
.rules-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.rule-box { background: #182234; border-radius: 18px; padding: 18px 22px; }
.rule-icon { font-size: 22px; font-weight: 800; margin-bottom: 6px; }
.rule-txt { font-size: 16px; font-weight: 700; color: #CBD5E1; }
.bottom-banner { background: #000000; color: #FFFFFF; border-radius: 24px; padding: 22px 36px; display: flex; align-items: center; justify-content: space-between; }
.bottom-brand { font-family: 'Archivo Black', sans-serif; font-size: 24px; letter-spacing: -0.02em; }
.bottom-link { font-family: 'JetBrains Mono', monospace; background: #CCFF00; color: #000000; padding: 10px 24px; border-radius: 999px; font-size: 22px; font-weight: 800; }
</style></head>
<body>
  <div class="caution-strip"><span>{caution}</span><span>CODICE DEL CONSUMO</span><span>SALVAVITA</span></div>
  <div class="huge-card">
    <div class="stamp">{stamp}</div>
    <div class="tag-badge">{badge}</div>
    <h1 class="card-title">{title}</h1>
    <div class="law-answer">
      <div class="law-heading">{ans_head}</div>
      <div class="law-body">{ans_body}</div>
    </div>
    <div class="rules-grid">
      <div class="rule-box">
        <div class="rule-icon">{r1_head}</div>
        <div class="rule-txt">{r1_txt}</div>
      </div>
      <div class="rule-box">
        <div class="rule-icon">{r2_head}</div>
        <div class="rule-txt">{r2_txt}</div>
      </div>
    </div>
  </div>
  <div class="bottom-banner">
    <div class="bottom-brand">DIFENDI I TUOI SOLDI. CONDIVIDI IL POST.</div>
    <div class="bottom-link">mistannofregando.it</div>
  </div>
</body></html>"""

tmpl_classifica = """<!doctype html><html><head><meta charset="utf-8" />
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Space+Grotesk:wght@700&family=JetBrains+Mono:wght@800&display=swap" rel="stylesheet">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { width: 1080px; height: 1080px; background-color: #CCFF00; font-family: 'Space Grotesk', system-ui, sans-serif; color: #000000; display: flex; flex-direction: column; justify-content: space-between; padding: 56px; }
.caution-strip { background: #000000; color: #CCFF00; font-family: 'Archivo Black', sans-serif; font-size: 15px; letter-spacing: 0.15em; padding: 12px 24px; display: flex; align-items: center; justify-content: space-between; border-radius: 12px; text-transform: uppercase; }
.huge-card { background: #000000; color: #FFFFFF; border-radius: 36px; padding: 50px; position: relative; box-shadow: 18px 20px 0px rgba(0, 0, 0, 0.3); }
.tag-badge { display: inline-block; background: #F59E0B; color: #000000; font-family: 'Archivo Black', sans-serif; font-size: 16px; padding: 8px 20px; border-radius: 999px; text-transform: uppercase; margin-bottom: 24px; }
.card-title { font-family: 'Archivo Black', sans-serif; font-size: 42px; line-height: 1.15; letter-spacing: -0.02em; margin-bottom: 30px; text-transform: uppercase; }
.card-title mark { background: #FF2E54; color: #FFFFFF; padding: 0 10px; border-radius: 8px; }
.stamp { position: absolute; top: 36px; right: 48px; border: 5px solid #F59E0B; color: #F59E0B; font-family: 'Archivo Black', sans-serif; font-size: 24px; padding: 8px 20px; text-transform: uppercase; letter-spacing: 0.08em; transform: rotate(-5deg); border-radius: 12px; background: rgba(245, 158, 11, 0.1); }
.rankings-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px; }
.rank-card { border-radius: 24px; padding: 22px 26px; }
.rank-card.top { background: #1A0D11; border: 2px solid #FF2E54; }
.rank-card.low { background: #0D1A14; border: 2px solid #00FF88; }
.rank-title { font-family: 'Archivo Black', sans-serif; font-size: 16px; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 12px; }
.top .rank-title { color: #FF2E54; } .low .rank-title { color: #00FF88; }
.rank-item { display: flex; justify-content: space-between; align-items: center; font-family: 'JetBrains Mono', monospace; font-size: 17px; font-weight: 800; padding: 8px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }
.rank-item:last-child { border-bottom: none; }
.rank-item strong { font-size: 20px; }
.top .rank-item strong { color: #FF8599; } .low .rank-item strong { color: #85FFC0; }
.bottom-banner { background: #000000; color: #FFFFFF; border-radius: 24px; padding: 22px 36px; display: flex; align-items: center; justify-content: space-between; }
.bottom-brand { font-family: 'Archivo Black', sans-serif; font-size: 22px; letter-spacing: -0.02em; }
.bottom-link { font-family: 'JetBrains Mono', monospace; background: #CCFF00; color: #000000; padding: 10px 24px; border-radius: 999px; font-size: 22px; font-weight: 800; }
</style></head>
<body>
  <div class="caution-strip"><span>{caution}</span><span>107 PROVINCE ITALIANE</span><span>DATI UFFICIALI</span></div>
  <div class="huge-card">
    <div class="stamp">{stamp}</div>
    <div class="tag-badge">{badge}</div>
    <h1 class="card-title">{title}</h1>
    <div class="rankings-grid">
      <div class="rank-card top">
        <div class="rank-title">{t_top}</div>
        <div class="rank-item">{t1}</div>
        <div class="rank-item">{t2}</div>
        <div class="rank-item">{t3}</div>
      </div>
      <div class="rank-card low">
        <div class="rank-title">{t_low}</div>
        <div class="rank-item">{l1}</div>
        <div class="rank-item">{l2}</div>
        <div class="rank-item">{l3}</div>
      </div>
    </div>
  </div>
  <div class="bottom-banner">
    <div class="bottom-brand">E NELLA TUA CITTÀ QUANTO COSTA? SCRIVILO NEI COMMENTI 👇</div>
    <div class="bottom-link">mistannofregando.it</div>
  </div>
</body></html>"""

print(f"Total posts to generate: {len(posts_data)}")

for p in posts_data:
    ptype = p["type"]
    if ptype == "fregometro":
        
        html = tmpl_fregometro
        for k, v in p.items():
            html = html.replace("{" + k + "}", str(v))

    elif ptype == "carovita":
        
        html = tmpl_carovita
        for k, v in p.items():
            html = html.replace("{" + k + "}", str(v))

    elif ptype == "diritti":
        
        html = tmpl_diritti
        for k, v in p.items():
            html = html.replace("{" + k + "}", str(v))

    elif ptype == "classifica":
        
        html = tmpl_classifica
        for k, v in p.items():
            html = html.replace("{" + k + "}", str(v))

    
    tmp_file = os.path.join(out_dir, "_temp.html")
    dest_png = os.path.join(out_dir, p["file"])
    with open(tmp_file, "w", encoding="utf-8") as f:
        f.write(html)
    
    subprocess.run(
        [
            chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--window-size=1080,1080", "--virtual-time-budget=3000",
            f"--screenshot={dest_png}", f"file://{tmp_file}"
        ],
        check=True
    )
    if os.path.exists(tmp_file): os.remove(tmp_file)
    print(f"Day {p['day']:02d} ({p['date']}): {p['file']} ({os.path.getsize(dest_png)} bytes)")

print("ALL 30 DAYS GENERATED SUCCESSFULLY!")
