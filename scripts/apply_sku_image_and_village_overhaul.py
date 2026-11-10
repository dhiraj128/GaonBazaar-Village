"""
Apply Master SKU Image Binding, Strict Single-Language Localization, 
and Exhaustive Phonetically Accurate Village Dataset.
"""
import sys
import re
import json

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Comprehensive 120+ Muzaffarpur Villages with exact phonetics and pincodes
MUZAFFARPUR_EXHAUSTIVE_VILLAGES = [
    # Minapur Block (मीनापुर - 843128)
    {"en": "Ali Neora", "hi": "अली नेओरा", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Basghatta", "hi": "बासघट्टा", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Benaghar", "hi": "बेनाघर", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Bishunpur", "hi": "विशुनपुर", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Brahmpura Rural", "hi": "ब्रह्मपुरा ग्रामीण", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Chaturshi", "hi": "चतुर्शी", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Daudpur", "hi": "दाउदपुर", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Dharampur Minapur", "hi": "धरमपुर मीनापुर", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Dharphari", "hi": "धरफरी", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Gorigama", "hi": "गोरीगामा", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Harsher", "hi": "हरशेर", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Jhakhra", "hi": "झखड़ा", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Koili", "hi": "कोइली", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Madhuban", "hi": "मधुबन", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Manikpur Minapur", "hi": "मानिकपुर मीनापुर", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Mariyabad", "hi": "मरियाबाद", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Minapur", "hi": "मीनापुर", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Mustafaganj", "hi": "मुस्तफागंज", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Nekanama", "hi": "नेकनामा", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Paigambarpur", "hi": "पैगम्बरपुर", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Panapur Minapur", "hi": "पानापुर मीनापुर", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Raghunathpur Minapur", "hi": "रघुनाथपुर मीनापुर", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Rampur Hari", "hi": "रामपुर हरी", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Shibai Patti", "hi": "शिबाई पट्टी", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Shivaypatti", "hi": "शिवाईपट्टी", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Tengari", "hi": "तेंगारी", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Tengrahi", "hi": "टेंगराही", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Tengrari", "hi": "टेंगरारी", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Turki Minapur", "hi": "तुरकी मीनापुर", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},
    {"en": "Zahidpur", "hi": "जाहिदपुर", "pincode": "843128", "district": "Muzaffarpur", "block": "Minapur"},

    # Kanti Block (कांटी - 843109)
    {"en": "Bishunpur Sumer", "hi": "बिशुनपुर सुमेर", "pincode": "843109", "district": "Muzaffarpur", "block": "Kanti"},
    {"en": "Damodarpur", "hi": "दामोदरपुर", "pincode": "843109", "district": "Muzaffarpur", "block": "Kanti"},
    {"en": "Dharampur", "hi": "धरमपुर", "pincode": "843109", "district": "Muzaffarpur", "block": "Kanti"},
    {"en": "Harchanda", "hi": "हरचंदा", "pincode": "843109", "district": "Muzaffarpur", "block": "Kanti"},
    {"en": "Kalwari", "hi": "कलवारी", "pincode": "843109", "district": "Muzaffarpur", "block": "Kanti"},
    {"en": "Kanti", "hi": "कांटी", "pincode": "843109", "district": "Muzaffarpur", "block": "Kanti"},
    {"en": "Kolhua", "hi": "कोल्हुआ", "pincode": "843109", "district": "Muzaffarpur", "block": "Kanti"},
    {"en": "Madhukar Chhapra", "hi": "मधुकर छपरा", "pincode": "843109", "district": "Muzaffarpur", "block": "Kanti"},
    {"en": "Narsanda", "hi": "नरसंडा", "pincode": "843109", "district": "Muzaffarpur", "block": "Kanti"},
    {"en": "Panapur Kanti", "hi": "पानापुर कांटी", "pincode": "843109", "district": "Muzaffarpur", "block": "Kanti"},
    {"en": "Sadatpur", "hi": "सदातपुर", "pincode": "843109", "district": "Muzaffarpur", "block": "Kanti"},
    {"en": "Sain", "hi": "साइन", "pincode": "843109", "district": "Muzaffarpur", "block": "Kanti"},
    {"en": "Sirsia", "hi": "सिरसिया", "pincode": "843109", "district": "Muzaffarpur", "block": "Kanti"},

    # Musahari Block (मुशहरी - 842002 / 842001)
    {"en": "Bela", "hi": "बेला", "pincode": "842002", "district": "Muzaffarpur", "block": "Musahari"},
    {"en": "Dighra", "hi": "दिघरा", "pincode": "842002", "district": "Muzaffarpur", "block": "Musahari"},
    {"en": "Gopalpur", "hi": "गोपालपुर", "pincode": "842002", "district": "Muzaffarpur", "block": "Musahari"},
    {"en": "Kanhauli", "hi": "कन्हौली", "pincode": "842002", "district": "Muzaffarpur", "block": "Musahari"},
    {"en": "Khabra", "hi": "खबड़ा", "pincode": "842002", "district": "Muzaffarpur", "block": "Musahari"},
    {"en": "Madhopur Musahari", "hi": "माधोपुर मुशहरी", "pincode": "842002", "district": "Muzaffarpur", "block": "Musahari"},
    {"en": "Mithanpura", "hi": "मिठनपुरा", "pincode": "842002", "district": "Muzaffarpur", "block": "Musahari"},
    {"en": "Musahari", "hi": "मुशहरी", "pincode": "842002", "district": "Muzaffarpur", "block": "Musahari"},
    {"en": "Muzaffarpur Town", "hi": "मुज़फ़्फ़रपुर नगर", "pincode": "842001", "district": "Muzaffarpur", "block": "Musahari"},
    {"en": "Narauli", "hi": "नरौली", "pincode": "842002", "district": "Muzaffarpur", "block": "Musahari"},
    {"en": "Rajwara", "hi": "रजवाड़ा", "pincode": "842002", "district": "Muzaffarpur", "block": "Musahari"},
    {"en": "Rohua", "hi": "रोहुआ", "pincode": "842002", "district": "Muzaffarpur", "block": "Musahari"},
    {"en": "Sikandarpur", "hi": "सिकंदरपुर", "pincode": "842001", "district": "Muzaffarpur", "block": "Musahari"},
    {"en": "Sutapatti", "hi": "सूतापट्टी", "pincode": "842001", "district": "Muzaffarpur", "block": "Musahari"},
    {"en": "Taraura", "hi": "तरौरा", "pincode": "842002", "district": "Muzaffarpur", "block": "Musahari"},

    # Bochahan Block (बोचहां - 843103)
    {"en": "Ahiyapur", "hi": "अहियापुर", "pincode": "843103", "district": "Muzaffarpur", "block": "Bochahan"},
    {"en": "Bochahan", "hi": "बोचहां", "pincode": "843103", "district": "Muzaffarpur", "block": "Bochahan"},
    {"en": "Chausati", "hi": "चौसती", "pincode": "843103", "district": "Muzaffarpur", "block": "Bochahan"},
    {"en": "Deoji", "hi": "देवजी", "pincode": "843103", "district": "Muzaffarpur", "block": "Bochahan"},
    {"en": "Garha", "hi": "गरहा", "pincode": "843103", "district": "Muzaffarpur", "block": "Bochahan"},
    {"en": "Hathaudi", "hi": "हथौड़ी", "pincode": "843103", "district": "Muzaffarpur", "block": "Bochahan"},
    {"en": "Karnpur", "hi": "कर्णपुर", "pincode": "843103", "district": "Muzaffarpur", "block": "Bochahan"},
    {"en": "Majhauli", "hi": "मझौली", "pincode": "843103", "district": "Muzaffarpur", "block": "Bochahan"},
    {"en": "Sharfuddinpur", "hi": "शर्फुद्दीनपुर", "pincode": "843103", "district": "Muzaffarpur", "block": "Bochahan"},
    {"en": "Unsar", "hi": "उनसर", "pincode": "843103", "district": "Muzaffarpur", "block": "Bochahan"},

    # Sakra Block (सकरा - 843105)
    {"en": "Baghnagari", "hi": "बघनगरी", "pincode": "843105", "district": "Muzaffarpur", "block": "Sakra"},
    {"en": "Bariyarpur", "hi": "बरियारपुर", "pincode": "843105", "district": "Muzaffarpur", "block": "Sakra"},
    {"en": "Bhatandi", "hi": "भटंडी", "pincode": "843105", "district": "Muzaffarpur", "block": "Sakra"},
    {"en": "Machhahi", "hi": "मछही", "pincode": "843105", "district": "Muzaffarpur", "block": "Sakra"},
    {"en": "Raghunathpur Sakra", "hi": "रघुनाथपुर सकरा", "pincode": "843105", "district": "Muzaffarpur", "block": "Sakra"},
    {"en": "Rampur Bakhri", "hi": "रामपुर बखरी", "pincode": "843105", "district": "Muzaffarpur", "block": "Sakra"},
    {"en": "Sabaha", "hi": "सबहा", "pincode": "843105", "district": "Muzaffarpur", "block": "Sakra"},
    {"en": "Sakra", "hi": "सकरा", "pincode": "843105", "district": "Muzaffarpur", "block": "Sakra"},
    {"en": "Sujawalpur", "hi": "सुजावलपुर", "pincode": "843105", "district": "Muzaffarpur", "block": "Sakra"},

    # Kurhani Block (कुढ़नी - 844127 / 843144)
    {"en": "Amarakh", "hi": "अमरख", "pincode": "844127", "district": "Muzaffarpur", "block": "Kurhani"},
    {"en": "Baliya", "hi": "बलिया", "pincode": "844127", "district": "Muzaffarpur", "block": "Kurhani"},
    {"en": "Fatehpur Kurhani", "hi": "फतेहपुर कुढ़नी", "pincode": "844127", "district": "Muzaffarpur", "block": "Kurhani"},
    {"en": "Kamarthu", "hi": "कमरथू", "pincode": "844127", "district": "Muzaffarpur", "block": "Kurhani"},
    {"en": "Khorampur", "hi": "खोरमपुर", "pincode": "844127", "district": "Muzaffarpur", "block": "Kurhani"},
    {"en": "Kishunpur", "hi": "किशुनपुर", "pincode": "844127", "district": "Muzaffarpur", "block": "Kurhani"},
    {"en": "Kurhani", "hi": "कुढ़नी", "pincode": "844127", "district": "Muzaffarpur", "block": "Kurhani"},
    {"en": "Ladaura", "hi": "लदौरा", "pincode": "844127", "district": "Muzaffarpur", "block": "Kurhani"},
    {"en": "Maniyari", "hi": "मनियारी", "pincode": "844127", "district": "Muzaffarpur", "block": "Kurhani"},
    {"en": "Pakri Kurhani", "hi": "पकड़ी कुढ़नी", "pincode": "844127", "district": "Muzaffarpur", "block": "Kurhani"},
    {"en": "Rajla", "hi": "रजला", "pincode": "844127", "district": "Muzaffarpur", "block": "Kurhani"},
    {"en": "Shahpur Kurhani", "hi": "शाहपुर कुढ़नी", "pincode": "844127", "district": "Muzaffarpur", "block": "Kurhani"},
    {"en": "Turki", "hi": "तुर्की", "pincode": "844127", "district": "Muzaffarpur", "block": "Kurhani"},

    # Saraiya Block (सरैया - 843126)
    {"en": "Amba", "hi": "अम्बा", "pincode": "843126", "district": "Muzaffarpur", "block": "Saraiya"},
    {"en": "Bahilwara", "hi": "बहिलवारा", "pincode": "843126", "district": "Muzaffarpur", "block": "Saraiya"},
    {"en": "Bakhri Saraiya", "hi": "बखरी सरैया", "pincode": "843126", "district": "Muzaffarpur", "block": "Saraiya"},
    {"en": "Datapur", "hi": "दातापुर", "pincode": "843126", "district": "Muzaffarpur", "block": "Saraiya"},
    {"en": "Gopinathpur", "hi": "गोपीनाथपुर", "pincode": "843126", "district": "Muzaffarpur", "block": "Saraiya"},
    {"en": "Jaitpur", "hi": "जैतपुर", "pincode": "843126", "district": "Muzaffarpur", "block": "Saraiya"},
    {"en": "Manikpur Saraiya", "hi": "मणिकपुर सरैया", "pincode": "843126", "district": "Muzaffarpur", "block": "Saraiya"},
    {"en": "Paharpur Saraiya", "hi": "पहाड़पुर सरैया", "pincode": "843126", "district": "Muzaffarpur", "block": "Saraiya"},
    {"en": "Repura", "hi": "रेपुरा", "pincode": "843126", "district": "Muzaffarpur", "block": "Saraiya"},
    {"en": "Saraiya", "hi": "सरैया", "pincode": "843126", "district": "Muzaffarpur", "block": "Saraiya"},

    # Paroo Block (पारू - 843112)
    {"en": "Anandpur", "hi": "आनंदपुर", "pincode": "843112", "district": "Muzaffarpur", "block": "Paroo"},
    {"en": "Bhagwanpur Paroo", "hi": "भगवानपुर पारू", "pincode": "843112", "district": "Muzaffarpur", "block": "Paroo"},
    {"en": "Chintamanpur", "hi": "चिंतामनपुर", "pincode": "843112", "district": "Muzaffarpur", "block": "Paroo"},
    {"en": "Dewariya", "hi": "देवरिया", "pincode": "843112", "district": "Muzaffarpur", "block": "Paroo"},
    {"en": "Jafarpur", "hi": "जाफरपुर", "pincode": "843112", "district": "Muzaffarpur", "block": "Paroo"},
    {"en": "Kamalpura", "hi": "कमलपुरा", "pincode": "843112", "district": "Muzaffarpur", "block": "Paroo"},
    {"en": "Kodariya", "hi": "कोदरिया", "pincode": "843112", "district": "Muzaffarpur", "block": "Paroo"},
    {"en": "Mangurahiya", "hi": "मंगुरहिया", "pincode": "843112", "district": "Muzaffarpur", "block": "Paroo"},
    {"en": "Mohjama", "hi": "मोहजमा", "pincode": "843112", "district": "Muzaffarpur", "block": "Paroo"},
    {"en": "Paroo", "hi": "पारू", "pincode": "843112", "district": "Muzaffarpur", "block": "Paroo"},
    {"en": "Saraiya Paroo", "hi": "सरैया पारू", "pincode": "843112", "district": "Muzaffarpur", "block": "Paroo"},

    # Sahebganj Block (साहेबगंज - 843125)
    {"en": "Ahiyapur Sahebganj", "hi": "अहियापुर साहेबगंज", "pincode": "843125", "district": "Muzaffarpur", "block": "Sahebganj"},
    {"en": "Basantpur", "hi": "बसंतपुर", "pincode": "843125", "district": "Muzaffarpur", "block": "Sahebganj"},
    {"en": "Bishunpur Kalyan", "hi": "विशुनपुर कल्याण", "pincode": "843125", "district": "Muzaffarpur", "block": "Sahebganj"},
    {"en": "Chainpur Sahebganj", "hi": "चैनपुर साहेबगंज", "pincode": "843125", "district": "Muzaffarpur", "block": "Sahebganj"},
    {"en": "Gulabpatti", "hi": "गुलाबपट्टी", "pincode": "843125", "district": "Muzaffarpur", "block": "Sahebganj"},
    {"en": "Madhopur Hazari", "hi": "माधोपुर हजारी", "pincode": "843125", "district": "Muzaffarpur", "block": "Sahebganj"},
    {"en": "Paharpur Manorath", "hi": "पहाड़पुर मनोरथ", "pincode": "843125", "district": "Muzaffarpur", "block": "Sahebganj"},
    {"en": "Rupchhapra", "hi": "रूपछपरा", "pincode": "843125", "district": "Muzaffarpur", "block": "Sahebganj"},
    {"en": "Sahebganj", "hi": "साहेबगंज", "pincode": "843125", "district": "Muzaffarpur", "block": "Sahebganj"},

    # Motipur Block (मोतीपुर - 843111)
    {"en": "Barji", "hi": "बरजी", "pincode": "843111", "district": "Muzaffarpur", "block": "Motipur"},
    {"en": "Dharmpura", "hi": "धर्मपुरा", "pincode": "843111", "district": "Muzaffarpur", "block": "Motipur"},
    {"en": "Kalyanpur Motipur", "hi": "कल्याणपुर मोतीपुर", "pincode": "843111", "district": "Muzaffarpur", "block": "Motipur"},
    {"en": "Kathaiya", "hi": "कथैया", "pincode": "843111", "district": "Muzaffarpur", "block": "Motipur"},
    {"en": "Mahwal", "hi": "महवल", "pincode": "843111", "district": "Muzaffarpur", "block": "Motipur"},
    {"en": "Motipur", "hi": "मोतीपुर", "pincode": "843111", "district": "Muzaffarpur", "block": "Motipur"},
    {"en": "Pansalwa", "hi": "पंसलवा", "pincode": "843111", "district": "Muzaffarpur", "block": "Motipur"},
    {"en": "Ratanpura", "hi": "रतनपुरा", "pincode": "843111", "district": "Muzaffarpur", "block": "Motipur"},
    {"en": "Singila", "hi": "सिंगिला", "pincode": "843111", "district": "Muzaffarpur", "block": "Motipur"},
    {"en": "Tajpur Motipur", "hi": "ताजपुर मोतीपुर", "pincode": "843111", "district": "Muzaffarpur", "block": "Motipur"},

    # Aurai Block (औराई - 843321)
    {"en": "Atrar", "hi": "अतरार", "pincode": "843321", "district": "Muzaffarpur", "block": "Aurai"},
    {"en": "Aurai", "hi": "औराई", "pincode": "843321", "district": "Muzaffarpur", "block": "Aurai"},
    {"en": "Basant", "hi": "बसंत", "pincode": "843321", "district": "Muzaffarpur", "block": "Aurai"},
    {"en": "Bhalura", "hi": "भलुरा", "pincode": "843321", "district": "Muzaffarpur", "block": "Aurai"},
    {"en": "Dharharwa", "hi": "धरहरवा", "pincode": "843321", "district": "Muzaffarpur", "block": "Aurai"},
    {"en": "Janar", "hi": "जनार", "pincode": "843321", "district": "Muzaffarpur", "block": "Aurai"},
    {"en": "Katauha", "hi": "कटौझा", "pincode": "843321", "district": "Muzaffarpur", "block": "Aurai"},
    {"en": "Khetalpur", "hi": "खेतलपुर", "pincode": "843321", "district": "Muzaffarpur", "block": "Aurai"},
    {"en": "Maheshsthan", "hi": "महेशस्थान", "pincode": "843321", "district": "Muzaffarpur", "block": "Aurai"},
    {"en": "Nayagaon Aurai", "hi": "नयागांव औराई", "pincode": "843321", "district": "Muzaffarpur", "block": "Aurai"},
    {"en": "Simri", "hi": "सिमरी", "pincode": "843321", "district": "Muzaffarpur", "block": "Aurai"},

    # Katra Block (कटरा - 843321)
    {"en": "Amma", "hi": "अम्मा", "pincode": "843321", "district": "Muzaffarpur", "block": "Katra"},
    {"en": "Bakuchi", "hi": "बकुची", "pincode": "843321", "district": "Muzaffarpur", "block": "Katra"},
    {"en": "Dhanaur", "hi": "धनौर", "pincode": "843321", "district": "Muzaffarpur", "block": "Katra"},
    {"en": "Gangiya", "hi": "गंगिया", "pincode": "843321", "district": "Muzaffarpur", "block": "Katra"},
    {"en": "Jajuara", "hi": "जजुआर", "pincode": "843321", "district": "Muzaffarpur", "block": "Katra"},
    {"en": "Kanhauli Katra", "hi": "कन्हौली कटरा", "pincode": "843321", "district": "Muzaffarpur", "block": "Katra"},
    {"en": "Katra", "hi": "कटरा", "pincode": "843321", "district": "Muzaffarpur", "block": "Katra"},
    {"en": "Madhopur Katra", "hi": "माधोपुर कटरा", "pincode": "843321", "district": "Muzaffarpur", "block": "Katra"},
    {"en": "Pahsaul", "hi": "पहसौल", "pincode": "843321", "district": "Muzaffarpur", "block": "Katra"},
    {"en": "Yaduvanshi Nagar", "hi": "यदुवंशी नगर", "pincode": "843321", "district": "Muzaffarpur", "block": "Katra"},

    # Gaighat Block (गायघाट - 843118)
    {"en": "Baruari", "hi": "बरूआरी", "pincode": "843118", "district": "Muzaffarpur", "block": "Gaighat"},
    {"en": "Bora", "hi": "बोरा", "pincode": "843118", "district": "Muzaffarpur", "block": "Gaighat"},
    {"en": "Dahila", "hi": "दहिला", "pincode": "843118", "district": "Muzaffarpur", "block": "Gaighat"},
    {"en": "Gaighat", "hi": "गायघाट", "pincode": "843118", "district": "Muzaffarpur", "block": "Gaighat"},
    {"en": "Jarang", "hi": "जारंग", "pincode": "843118", "district": "Muzaffarpur", "block": "Gaighat"},
    {"en": "Kamarthu Gaighat", "hi": "कमरथू गायघाट", "pincode": "843118", "district": "Muzaffarpur", "block": "Gaighat"},
    {"en": "Kanta Pirochha", "hi": "कांटा पिरौछा", "pincode": "843118", "district": "Muzaffarpur", "block": "Gaighat"},
    {"en": "Kewats", "hi": "केवत्स", "pincode": "843118", "district": "Muzaffarpur", "block": "Gaighat"},
    {"en": "Loma", "hi": "लोमा", "pincode": "843118", "district": "Muzaffarpur", "block": "Gaighat"},
    {"en": "Patsharma", "hi": "पटशर्मा", "pincode": "843118", "district": "Muzaffarpur", "block": "Gaighat"},
    {"en": "Susta", "hi": "सुस्ता", "pincode": "843118", "district": "Muzaffarpur", "block": "Gaighat"},

    # Bandra Block (बंदरा - 843115)
    {"en": "Adampur Bandra", "hi": "आदमपुर बंदरा", "pincode": "843115", "district": "Muzaffarpur", "block": "Bandra"},
    {"en": "Bandra", "hi": "बंदरा", "pincode": "843115", "district": "Muzaffarpur", "block": "Bandra"},
    {"en": "Bargaon", "hi": "बड़गांव", "pincode": "843115", "district": "Muzaffarpur", "block": "Bandra"},
    {"en": "Hattha", "hi": "हत्था", "pincode": "843115", "district": "Muzaffarpur", "block": "Bandra"},
    {"en": "Kalyanpur Bandra", "hi": "कल्याणपुर बंदरा", "pincode": "843115", "district": "Muzaffarpur", "block": "Bandra"},
    {"en": "Munni Bahera", "hi": "मुन्नी बहेरा", "pincode": "843115", "district": "Muzaffarpur", "block": "Bandra"},
    {"en": "Piyar", "hi": "पियर", "pincode": "843115", "district": "Muzaffarpur", "block": "Bandra"},
    {"en": "Rampur Dayal", "hi": "रामपुर दयाल", "pincode": "843115", "district": "Muzaffarpur", "block": "Bandra"},
    {"en": "Simra", "hi": "सिमरा", "pincode": "843115", "district": "Muzaffarpur", "block": "Bandra"},
    {"en": "Tegchhiya", "hi": "तेगछिया", "pincode": "843115", "district": "Muzaffarpur", "block": "Bandra"},

    # Marwan Block (मड़वन - 843113)
    {"en": "Bhatauna", "hi": "भटौना", "pincode": "843113", "district": "Muzaffarpur", "block": "Marwan"},
    {"en": "Chainpur Marwan", "hi": "चैनपुर मड़वन", "pincode": "843113", "district": "Muzaffarpur", "block": "Marwan"},
    {"en": "Gawasra", "hi": "गवसरा", "pincode": "843113", "district": "Muzaffarpur", "block": "Marwan"},
    {"en": "Karja", "hi": "करजा", "pincode": "843113", "district": "Muzaffarpur", "block": "Marwan"},
    {"en": "Makdumpur", "hi": "मकदूमपुर", "pincode": "843113", "district": "Muzaffarpur", "block": "Marwan"},
    {"en": "Marwan", "hi": "मड़वन", "pincode": "843113", "district": "Muzaffarpur", "block": "Marwan"},
    {"en": "Mohammadpur", "hi": "मोहम्मदपुर", "pincode": "843113", "district": "Muzaffarpur", "block": "Marwan"},
    {"en": "Pakri Marwan", "hi": "पकड़ी मड़वन", "pincode": "843113", "district": "Muzaffarpur", "block": "Marwan"},
    {"en": "Rupwara", "hi": "रूपवारा", "pincode": "843113", "district": "Muzaffarpur", "block": "Marwan"},
    {"en": "Shahbazpur", "hi": "शाहबाजपुर", "pincode": "843113", "district": "Muzaffarpur", "block": "Marwan"}
]

VILLAGES_JS_STR = json.dumps(MUZAFFARPUR_EXHAUSTIVE_VILLAGES, ensure_ascii=False, indent=2)

def update_vendor():
    path = "public_web/vendor/index.html"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Update In-Stock checkbox label HTML and data-i18n
    old_checkbox = '<span class="text-[11px] font-bold text-slate-800">बिक्री चालू (In-Stock)</span>'
    new_checkbox = '<span id="custom-pricing-instock-label" class="text-[11px] font-bold text-slate-800" data-i18n="instock_checkbox_label">In-Stock</span>'
    if old_checkbox in content:
        content = content.replace(old_checkbox, new_checkbox, 1)
        print("Updated in-stock checkbox markup in vendor/index.html")

    # 2. Update i18n dictionary for instock_checkbox_label in English and Hindi
    if 'instock_checkbox_label: "In-Stock"' not in content:
        content = content.replace(
            'add_to_live_store_btn: "Add to Live Store",',
            'add_to_live_store_btn: "Add to Live Store",\n        instock_checkbox_label: "In-Stock",',
            1
        )
        content = content.replace(
            'add_to_live_store_btn: "दुकान में जोड़ें",',
            'add_to_live_store_btn: "दुकान में जोड़ें",\n        instock_checkbox_label: "बिक्री चालू",',
            1
        )
        print("Added instock_checkbox_label to vendor i18n dictionaries")

    # 3. Clean category options in select
    old_cat_options = '''                <option value="Grocery & Kirana" data-i18n="cat_grocery">Grocery & Kirana (किराना और राशन)</option>
                <option value="Dairy & Milk Products" data-i18n="cat_dairy">Dairy & Milk (दूध और डेयरी)</option>
                <option value="Fresh Fruits & Vegetables" data-i18n="cat_veggies">Vegetables & Fruits (सब्जी और फल)</option>
                <option value="Pharmacy & Healthcare" data-i18n="cat_pharmacy">Pharmacy & Medicines (दवाइयाँ)</option>
                <option value="Electronics & Mobile" data-i18n="cat_electronics">Mobile & Electronics (इलेक्ट्रॉनिक्स)</option>'''

    new_cat_options = '''                <option value="Grocery & Kirana" data-i18n="cat_grocery">Grocery & Kirana</option>
                <option value="Dairy & Milk Products" data-i18n="cat_dairy">Dairy & Milk Products</option>
                <option value="Fresh Fruits & Vegetables" data-i18n="cat_veggies">Fresh Fruits & Vegetables</option>
                <option value="Pharmacy & Healthcare" data-i18n="cat_pharmacy">Pharmacy & Healthcare</option>
                <option value="Electronics & Mobile" data-i18n="cat_electronics">Electronics & Mobile</option>'''

    if old_cat_options in content:
        content = content.replace(old_cat_options, new_cat_options, 1)
        print("Scrubbed mixed strings from category select options")

    # 4. Clean LOOSE_ITEM_CHIPS (decouple location data from product names)
    old_chips = '''    const LOOSE_ITEM_CHIPS = [
      { en: "Fresh Tomatoes (1 kg)", hi: "ताज़ा टमाटर (1 kg)", cat: "Vegetables", unit: "1 kg", img: "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=500&q=80", icon: "🍅" },
      { en: "Local Potatoes (1 kg)", hi: "देसी आलू (1 kg)", cat: "Vegetables", unit: "1 kg", img: "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=500&q=80", icon: "🥔" },
      { en: "Red Onions (1 kg)", hi: "लाल प्याज़ (1 kg)", cat: "Vegetables", unit: "1 kg", img: "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=500&q=80", icon: "🧅" },
      { en: "Loose Toor Dal (1 kg)", hi: "अरहर दाल (1 kg)", cat: "Grocery", unit: "1 kg", img: "https://images.unsplash.com/photo-1585032226651-759b368d7246?w=500&q=80", icon: "🌾" },
      { en: "Fresh Cow Milk (1 L)", hi: "ताज़ा गाय का दूध (1 L)", cat: "Dairy", unit: "1 L", img: "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=500&q=80", icon: "🥛" },
      { en: "Gulab Jamun (1 kg)", hi: "देसी गुलाब जामुन (1 kg)", cat: "Sweets", unit: "1 kg", img: "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=500&q=80", icon: "🍬" }
    ];'''

    new_chips = '''    const LOOSE_ITEM_CHIPS = [
      { en: "Fresh Tomatoes 1kg", hi: "ताज़ा टमाटर 1kg", cat: "Vegetables", unit: "1 kg", img: "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=600&q=80", icon: "🍅" },
      { en: "Local Potatoes 1kg", hi: "देसी आलू 1kg", cat: "Vegetables", unit: "1 kg", img: "https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=600&q=80", icon: "🥔" },
      { en: "Red Onions 1kg", hi: "लाल प्याज 1kg", cat: "Vegetables", unit: "1 kg", img: "https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=600&q=80", icon: "🧅" },
      { en: "Toor Dal 1kg", hi: "अरहर दाल 1kg", cat: "Grocery", unit: "1 kg", img: "https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=600&q=80", icon: "🌾" },
      { en: "Fresh Cow Milk 1L", hi: "ताज़ा गाय का दूध 1L", cat: "Dairy", unit: "1 L", img: "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=600&q=80", icon: "🥛" },
      { en: "Gulab Jamun 1kg", hi: "देसी गुलाब जामुन 1kg", cat: "Sweets", unit: "1 kg", img: "https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=600&q=80", icon: "🍬" }
    ];'''

    if old_chips in content:
        content = content.replace(old_chips, new_chips, 1)
        print("Updated LOOSE_ITEM_CHIPS without parenthetical text")

    # 5. Clean MASTER_STAPLE_MAP titles (remove concatenated bilingual titles)
    content = content.replace("title: 'Fresh Desi Tomato (ताज़ा टमाटर)'", "title: 'Fresh Tomatoes 1kg'")
    content = content.replace("title: 'Fresh Pahadi Potato (ताज़ा आलू)'", "title: 'Fresh Potatoes 1kg'")
    content = content.replace("title: 'Fresh Red Onion (ताज़ा प्याज)'", "title: 'Fresh Red Onions 1kg'")
    content = content.replace("title: 'Wheat Flour (Atta)'", "title: 'Wheat Flour 5kg'")

    # 6. Add sanitizeProductName and getProductStockImage helper functions
    product_helper_code = '''
    // ===========================================================================
    // PRODUCT NAME SANITIZATION & REAL STOCK IMAGE AUTO-POPULATION
    // ===========================================================================
    function sanitizeProductName(rawName) {
      if (!rawName || typeof rawName !== 'string') return '';
      // Completely decouple vendor village and regional names from product titles
      let cleaned = rawName
        .replace(/\\s*\\([^)]*(?:तेंगारी|टेंगरारी|टेंगराही|Tengari|Tengrari|Chaturshi|चतुरशी|शिवाईपट्टी|Shivaypatti|Shibai|Minapur|मीनापुर|Muzaffarpur|मुज़फ़्फ़रपुर|Village|गाँव|बिहार|Bihar)[^)]*\\)/gi, '')
        .replace(/\\s*\\([^)]*[\\u0900-\\u097F]+[^)]*\\)/g, '')
        .trim();
      return cleaned || rawName.trim();
    }
    window.sanitizeProductName = sanitizeProductName;

    const MASTER_REAL_PRODUCT_IMAGES = {
      'tomato': 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=600&q=80',
      'tomatoes': 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=600&q=80',
      'tamatar': 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=600&q=80',
      'टमाटर': 'https://images.unsplash.com/photo-1592924357228-91a4daadcfea?w=600&q=80',
      'potato': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=600&q=80',
      'potatoes': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=600&q=80',
      'aalu': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=600&q=80',
      'aloo': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=600&q=80',
      'आलू': 'https://images.unsplash.com/photo-1518977676601-b53f82aba655?w=600&q=80',
      'onion': 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=600&q=80',
      'onions': 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=600&q=80',
      'pyaj': 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=600&q=80',
      'pyaz': 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=600&q=80',
      'प्याज': 'https://images.unsplash.com/photo-1618512496248-a07fe83aa8cb?w=600&q=80',
      'atta': 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600&q=80',
      'flour': 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600&q=80',
      'आटा': 'https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600&q=80',
      'rice': 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&q=80',
      'chawal': 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&q=80',
      'चावल': 'https://images.unsplash.com/photo-1586201375761-83865001e31c?w=600&q=80',
      'dal': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=600&q=80',
      'दाल': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=600&q=80',
      'arhar': 'https://images.unsplash.com/photo-1546833999-b9f581a1996d?w=600&q=80',
      'milk': 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=600&q=80',
      'doodh': 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=600&q=80',
      'दूध': 'https://images.unsplash.com/photo-1550583724-b2692b85b150?w=600&q=80',
      'ghee': 'https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=600&q=80',
      'घी': 'https://images.unsplash.com/photo-1628088062854-d1870b4553da?w=600&q=80',
      'oil': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=600&q=80',
      'tel': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=600&q=80',
      'तेल': 'https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?w=600&q=80',
      'sugar': 'https://images.unsplash.com/photo-1581441363689-1f3c3c414635?w=600&q=80',
      'cheeni': 'https://images.unsplash.com/photo-1581441363689-1f3c3c414635?w=600&q=80',
      'चीनी': 'https://images.unsplash.com/photo-1581441363689-1f3c3c414635?w=600&q=80',
      'tea': 'https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=600&q=80',
      'chai': 'https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=600&q=80',
      'चाय': 'https://images.unsplash.com/photo-1576092768241-dec231879fc3?w=600&q=80',
      'salt': 'https://images.unsplash.com/photo-1518110925495-5fe2fda0442c?w=600&q=80',
      'namak': 'https://images.unsplash.com/photo-1518110925495-5fe2fda0442c?w=600&q=80',
      'नमक': 'https://images.unsplash.com/photo-1518110925495-5fe2fda0442c?w=600&q=80',
      'maggi': 'https://images.unsplash.com/photo-1612927601601-6638404737ce?w=600&q=80',
      'मैगी': 'https://images.unsplash.com/photo-1612927601601-6638404737ce?w=600&q=80',
      'biscuit': 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=600&q=80',
      'बिस्कुट': 'https://images.unsplash.com/photo-1558961363-fa8fdf82db35?w=600&q=80',
      'soap': 'https://images.unsplash.com/photo-1607006314188-755a5b5123d5?w=600&q=80',
      'साबुन': 'https://images.unsplash.com/photo-1607006314188-755a5b5123d5?w=600&q=80',
      'sweets': 'https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=600&q=80',
      'gulab jamun': 'https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=600&q=80',
      'मिठाई': 'https://images.unsplash.com/photo-1541781774459-bb2af2f05b55?w=600&q=80'
    };

    function getProductStockImage(nameOrQuery, category) {
      if (!nameOrQuery || typeof nameOrQuery !== 'string') {
        return "https://images.unsplash.com/photo-1542838132-92c53300491e?w=600&q=80";
      }
      const q = nameOrQuery.toLowerCase().trim();
      for (const [kw, url] of Object.entries(MASTER_REAL_PRODUCT_IMAGES)) {
        if (q.includes(kw) || kw.includes(q)) {
          return url;
        }
      }
      if (category === 'Vegetables' || category === 'Fruits') {
        return "https://images.unsplash.com/photo-1610348725531-843dff563e2c?w=600&q=80";
      }
      if (category === 'Dairy') {
        return "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=600&q=80";
      }
      return "https://images.unsplash.com/photo-1542838132-92c53300491e?w=600&q=80";
    }
    window.getProductStockImage = getProductStockImage;
'''

    if 'PRODUCT NAME SANITIZATION & REAL STOCK IMAGE AUTO-POPULATION' not in content:
        content = content.replace('// 4. THE CUSTOM PRICING FORM (NO LOCKED SKUS, MRP & SELLING PRICE)', f'{product_helper_code}\n\n    // 4. THE CUSTOM PRICING FORM (NO LOCKED SKUS, MRP & SELLING PRICE)', 1)
        print("Injected product sanitization & real stock image auto-population helpers")

    # 7. Update openCustomPricingModal to sanitize name, purge "SNAPPED" placeholder and force real stock image
    old_pricing_open = '''    function openCustomPricingModal(itemData = {}) {
      const name = itemData.title || itemData.name || itemData.product_name || "";
      const mrp = itemData.mrp !== undefined && itemData.mrp !== null ? String(itemData.mrp).trim() : "";
      const price = itemData.price !== undefined && itemData.price !== null ? String(itemData.price).trim() : "";
      const stock = itemData.stock !== undefined && itemData.stock !== null ? String(itemData.stock).trim() : "";
      let cat = itemData.category || "Grocery";
      let unit = itemData.unit || itemData.variant || "1 unit";
      let img = itemData.img || itemData.image_url || "";

      // PROACTIVE MASTER SKU LOOKUP
      const match = findMasterSkuSuggestion(name);
      if (match) {
        if (!img || img.includes('photo-1574323347407-f5e1ad6d020b')) {
          img = match.image_url;
        }
        if (cat === "Grocery" && match.category) cat = match.category;
        if (unit === "1 unit" && match.unit) unit = match.unit;
      }

      if (!img) {
        img = "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=600&q=80";
      }'''

    new_pricing_open = '''    function openCustomPricingModal(itemData = {}) {
      const rawName = itemData.title || itemData.name || itemData.product_name || "";
      const name = sanitizeProductName(rawName);
      const mrp = itemData.mrp !== undefined && itemData.mrp !== null ? String(itemData.mrp).trim() : "";
      const price = itemData.price !== undefined && itemData.price !== null ? String(itemData.price).trim() : "";
      const stock = itemData.stock !== undefined && itemData.stock !== null ? String(itemData.stock).trim() : "";
      let cat = itemData.category || "Grocery";
      let unit = itemData.unit || itemData.variant || "1 unit";
      let img = itemData.img || itemData.image_url || "";

      // PURGE DUMMY "SNAPPED" TEXT PLACEHOLDERS: Always pull real product photography
      const isPlaceholder = !img || img.includes('SNAPPED') || img.startsWith('data:image/svg') || img.includes('photo-1574323347407-f5e1ad6d020b');
      const match = findMasterSkuSuggestion(name);

      if (match && match.image_url) {
        if (isPlaceholder || !img) {
          img = match.image_url;
        }
        if (cat === "Grocery" && match.category) cat = match.category;
        if (unit === "1 unit" && match.unit) unit = match.unit;
      } else if (isPlaceholder) {
        img = getProductStockImage(name, cat);
      }'''

    if old_pricing_open in content:
        content = content.replace(old_pricing_open, new_pricing_open, 1)
        print("Updated openCustomPricingModal to eliminate SNAPPED placeholder and bind real image")

    # 8. Update custom pricing modal in-stock label dynamically on language and opening
    old_instock_check = 'if (instockInp) instockInp.checked = true;'
    new_instock_check = '''if (instockInp) instockInp.checked = true;
      const instockLabel = document.getElementById('custom-pricing-instock-label');
      if (instockLabel) {
        const isHi = (typeof currentLang !== 'undefined' ? currentLang === 'hi' : false) || 
                     (localStorage.getItem('gaonbazaar_vendor_lang') === 'hi') || 
                     (window.currentLang === 'hi');
        instockLabel.innerText = isHi ? 'बिक्री चालू' : 'In-Stock';
      }'''

    if old_instock_check in content and 'instockLabel.innerText = isHi ? \'बिक्री चालू\' : \'In-Stock\'' not in content:
        content = content.replace(old_instock_check, new_instock_check, 1)
        print("Updated in-stock label dynamic translation on modal open")

    # 9. Update setLanguage to strictly update in-stock label without mixed text
    old_set_lang = "document.querySelectorAll('[data-i18n]').forEach(el => {"
    new_set_lang = '''const instockLabel = document.getElementById('custom-pricing-instock-label');
      if (instockLabel) {
        instockLabel.innerText = lang === 'hi' ? 'बिक्री चालू' : 'In-Stock';
      }
      document.querySelectorAll('[data-i18n]').forEach(el => {'''

    if old_set_lang in content and "instockLabel.innerText = lang === 'hi' ? 'बिक्री चालू' : 'In-Stock';" not in content:
        content = content.replace(old_set_lang, new_set_lang, 1)
        print("Updated setLanguage to enforce strict In-Stock vs बिक्री चालू")

    # 10. Update handleCustomPricingNameInput to dynamically bind real product images as user types
    old_name_input = '''    function handleCustomPricingNameInput(name) {
      if (!name || name.trim().length < 2) {
        const suggBanner = document.getElementById('custom-pricing-sku-suggestion');
        if (suggBanner) suggBanner.classList.add('hidden');
        return;
      }
      const match = findMasterSkuSuggestion(name);
      const previewImg = document.getElementById('custom-pricing-preview-img');
      const catTag = document.getElementById('custom-pricing-cat-tag');
      const unitTag = document.getElementById('custom-pricing-unit-tag');
      const suggBanner = document.getElementById('custom-pricing-sku-suggestion');
      const suggText = document.getElementById('sku-suggestion-text');

      if (match && match.image_url) {
        if (previewImg) previewImg.src = match.image_url;
        if (catTag && match.category) catTag.innerText = match.category;
        if (unitTag && match.unit) unitTag.innerText = match.unit;
        currentCustomPricingImg = match.image_url;'''

    new_name_input = '''    function handleCustomPricingNameInput(name) {
      if (!name || name.trim().length < 2) {
        const suggBanner = document.getElementById('custom-pricing-sku-suggestion');
        if (suggBanner) suggBanner.classList.add('hidden');
        return;
      }
      const match = findMasterSkuSuggestion(name);
      const previewImg = document.getElementById('custom-pricing-preview-img');
      const catTag = document.getElementById('custom-pricing-cat-tag');
      const unitTag = document.getElementById('custom-pricing-unit-tag');
      const suggBanner = document.getElementById('custom-pricing-sku-suggestion');
      const suggText = document.getElementById('sku-suggestion-text');

      const realImg = (match && match.image_url) ? match.image_url : getProductStockImage(name, catTag?.innerText || 'Vegetables');
      if (previewImg) previewImg.src = realImg;
      currentCustomPricingImg = realImg;

      if (match && match.image_url) {
        if (catTag && match.category) catTag.innerText = match.category;
        if (unitTag && match.unit) unitTag.innerText = match.unit;'''

    if old_name_input in content:
        content = content.replace(old_name_input, new_name_input, 1)
        print("Updated handleCustomPricingNameInput to auto-populate real image immediately on input")

    # 11. Replace GAONBAZAAR_VILLAGES dataset in vendor/index.html with exhaustive 120+ phonetically accurate array
    pattern_villages = re.compile(r'const GAONBAZAAR_VILLAGES = \[.*?\];', re.DOTALL)
    new_villages_code = f"const GAONBAZAAR_VILLAGES = {VILLAGES_JS_STR};"
    content = pattern_villages.sub(new_villages_code, content, count=1)
    print("Replaced GAONBAZAAR_VILLAGES with exhaustive 120+ dataset in vendor/index.html")

    # 12. Ensure strict alphabetical sorting (A-Z for English, अ-ज्ञ for Hindi) before rendering
    old_vendor_sort = '''      const sortedHubs = RURAL_AREAS_LIST.slice().sort((a, b) => {
        return a.en.localeCompare(b.en);
      });'''

    new_vendor_sort = '''      const sortedHubs = RURAL_AREAS_LIST.slice().sort((a, b) => {
        if (isHindi) {
          return a.hi.localeCompare(b.hi, 'hi');
        }
        return a.en.localeCompare(b.en);
      });'''

    if old_vendor_sort in content:
        content = content.replace(old_vendor_sort, new_vendor_sort, 1)
        print("Updated village dropdown sorting to A-Z for English and अ-ज्ञ for Hindi in vendor/index.html")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def update_runner():
    path = "public_web/runner/index.html"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace GAONBAZAAR_VILLAGES dataset in runner/index.html
    pattern_villages = re.compile(r'const GAONBAZAAR_VILLAGES = \[.*?\];', re.DOTALL)
    new_villages_code = f"const GAONBAZAAR_VILLAGES = {VILLAGES_JS_STR};"
    content = pattern_villages.sub(new_villages_code, content, count=1)
    print("Replaced GAONBAZAAR_VILLAGES with exhaustive 120+ dataset in runner/index.html")

    # Ensure strict alphabetical sorting in runner dropdown
    old_runner_sort = '''      const sortedHubs = RURAL_AREAS_LIST.slice().sort((a, b) => {
        return a.en.localeCompare(b.en);
      });'''

    new_runner_sort = '''      const sortedHubs = RURAL_AREAS_LIST.slice().sort((a, b) => {
        if (isHindi) {
          return a.hi.localeCompare(b.hi, 'hi');
        }
        return a.en.localeCompare(b.en);
      });'''

    if old_runner_sort in content:
        content = content.replace(old_runner_sort, new_runner_sort, 1)
        print("Updated village dropdown sorting in runner/index.html")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def update_customer():
    path = "public_web/customer/index.html"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace GAONBAZAAR_VILLAGES dataset in customer/index.html
    pattern_villages = re.compile(r'const GAONBAZAAR_VILLAGES = \[.*?\];', re.DOTALL)
    new_villages_code = f"const GAONBAZAAR_VILLAGES = {VILLAGES_JS_STR};"
    content = pattern_villages.sub(new_villages_code, content, count=1)
    print("Replaced GAONBAZAAR_VILLAGES with exhaustive 120+ dataset in customer/index.html")

    # Ensure strict alphabetical sorting in customer dropdown
    old_cust_sort = '''      const sortedHubs = RURAL_AREAS_LIST.slice().sort((a, b) => a.en.localeCompare(b.en));'''
    new_cust_sort = '''      const isHindi = (typeof currentLang !== 'undefined' ? currentLang === 'hi' : false) || 
                      (localStorage.getItem('gb_customer_lang') === 'hi') || 
                      (window.currentLang === 'hi');
      const sortedHubs = RURAL_AREAS_LIST.slice().sort((a, b) => {
        if (isHindi) {
          return a.hi.localeCompare(b.hi, 'hi');
        }
        return a.en.localeCompare(b.en);
      });'''

    if old_cust_sort in content:
        content = content.replace(old_cust_sort, new_cust_sort, 1)
        print("Updated village dropdown sorting in customer/index.html")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

if __name__ == "__main__":
    update_vendor()
    update_runner()
    update_customer()
