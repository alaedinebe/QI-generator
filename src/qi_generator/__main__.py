import os
import csv
import time
import json
import pyperclip
import datetime
from pynput.keyboard import Key, Controller

keyboard = Controller()
i = 0  # à incrémenter selon les besoins

# Définir le chemin vers le dossier 'lisa'
lisa_folder = os.path.join(os.getcwd(), 'lisa')

# Récupérer et trier les fichiers JSON dans l'ordre croissant
files = sorted([f for f in os.listdir(lisa_folder) if f.endswith('.json')])

# Initialiser les listes pour savoir quel numéro d'item, nom d'item et slug d'item utiliser
slug_item = []
numero_item = []
nom_item = []
# vérifier l'existence du fichier items.csv
if not os.path.exists("items.csv"):
    print("Le fichier items.csv n'existe pas. Veuillez le créer avant d'exécuter le script.")
    exit(1)
with open("items.csv", "r", encoding="utf-8") as f:
    reader = csv.reader(f, delimiter=';')
    header = next(reader)          # ['item', 'numero', 'nom']
    for row in reader:
        if not row or len(row) < 3:
            continue
        slug_item = row[0]
        numero_item = row[1]
        nom_item = row[2]

        print(f"\nTraitement de l'item fichier : {numero_item} : {nom_item}\n")

        # Étape 0 : Cmd + Tab
        keyboard.press(Key.cmd)
        time.sleep(1)
        keyboard.press(Key.tab)
        time.sleep(0.1)
        keyboard.release(Key.tab)
        time.sleep(1)
        keyboard.release(Key.cmd)

        # Charger les fichiers et extraire la propriété 'content' de chacun
        medical_contexts = []
        file_name = numero_item+".json"
        file_path = os.path.join(lisa_folder, file_name)
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            for j in range(len(data)):
                if data[j]["content"]:  # Vérifier que le champ 'content' existe
                    medical_contexts = data[j]["content"]  # accès au champ 'content' de élément

                    prompt = """
                    ### 🧠 Contexte

                    Tu es un professeur de médecine, expert en physiopathologie, spécialisé dans la conception de *questions à choix multiples (QCM)* pour les étudiants de DFASM préparant l’*Épreuve Dématérialisée Nationale (EDN)*. Tu maîtrises les attendus du programme, la taxonomie de Bloom, et la rédaction pédagogique exigeante.

                    ---

                    ### 🎯 Objectif de la tâche

                    À partir du *contenu médical strictement fourni à la fin du prompt, tu dois générer **5 QCM* de *niveau EDN*, au format JSON spécifique indiqué ci-dessous.

                    Chaque QCM doit être *utile à l’entraînement des étudiants* en médecine dans une logique de consolidation des connaissances et de raisonnement clinique.

                    ---

                    ### 🧾 Contraintes techniques *strictes*

                    Tu dois générer un bloc JSON contenant *exactement 5 objets*, chacun correspondant à une question, avec la structure suivante :

                    json
                    {
                        "statement": "Texte de la question (en français, clair et pertinent pour l'EDN)",
                        "propositions": [
                        {
                            "correct": true | false,
                            "proposition": "Proposition A",
                            "justification": "Justification pédagogique, claire et précise"
                        },
                        {
                            "correct": true | false,
                            "proposition": "Proposition B",
                            "justification": "Justification pédagogique, claire et précise"
                        },
                        {
                            "correct": true | false,
                            "proposition": "Proposition C",
                            "justification": "Justification pédagogique, claire et précise"
                        },
                        {
                            "correct": true | false,
                            "proposition": "Proposition D",
                            "justification": "Justification pédagogique, claire et précise"
                        },
                        {
                            "correct": true | false,
                            "proposition": "Proposition E",
                            "justification": "Justification pédagogique, claire et précise"
                        }
                        ]
                    }


                    ---

                    ### 📚 Contraintes pédagogiques *avancées*

                    * Les *questions* doivent être *formulées en français*, dans un style adapté aux étudiants de 5e/6e année de médecine.
                    * Chaque QCM doit mobiliser un *savoir utile* pour l’EDN :

                    * *définitions* fondamentales (ex : TVP proximale vs distale) ;
                    * *raisonnement clinique* (ex : critères de gravité d’une EP) ;
                    * *catégorisation* (ex : éléments de la MVTE).
                    * Les *propositions* doivent toutes être *pertinentes médicalement* (évite les distracteurs trop évidents).
                    * Il doit y avoir au moins *une proposition correcte* par question.
                    * Il peut y avoir *une ou plusieurs bonnes réponses*.
                    * Les *justifications* doivent être *suffisamment explicites, pédagogiques et **100 % basées sur le contenu fourni. Ne fais **aucune inférence externe*.
                    * Ne mentionne *jamais* « le texte » ou « le contenu » dans les justifications.
                    * Respecte la taxonomie de Bloom : favorise des verbes d’action comme « identifier », « différencier », « reconnaître », « définir », « classer ».

                    ---

                    ### 📄 Contenu médical sur lequel s’appuyer

                    """ + str(medical_contexts) +"""


                    ---

                    ### ❌ Ne fais surtout pas

                    * Ne produis pas de contenu hors de ce champ médical.
                    * Ne produis pas de texte hors JSON (pas de commentaire, pas d’introduction).
                    * Ne mélange pas les champs ou formats.
                    * Ne propose pas plus ou moins de 5 propositions par question.
                    * Ne fais pas de paraphrase du contenu ou de gloses.

                    ---

                    ### ✅ Tu peux maintenant commencer

                    Génère *directement* un tableau JSON de *5 objets QCM complets*, parfaitement conformes au format ci-dessus, et exploitables tels quels dans une base EDN.

                    Aucune phrase explicative n’est attendue avant ou après la sortie. Génère uniquement le JSON proprement.
                    """

                    # Étape 0 : Cmd + L
                    keyboard.press(Key.cmd)
                    time.sleep(1)
                    keyboard.press('l')
                    time.sleep(0.1)
                    keyboard.release('l')
                    time.sleep(1)
                    keyboard.release(Key.cmd)

                    time.sleep(1)

                    keyboard.type("chatgpt.com")
                    time.sleep(1)
                    keyboard.press(Key.enter)
                    keyboard.release(Key.enter) 

                    # Petite pause pour laisser l'app s'ouvrir
                    time.sleep(5)

                    # Étape 2 : Coller le texte
                    pyperclip.copy(prompt)
                    with keyboard.pressed(Key.cmd):
                        keyboard.press('v')
                        keyboard.release('v')

                    keyboard.press(Key.enter)
                    keyboard.release(Key.enter)

                    # Étape 3 : Attendre 1 minute
                    time.sleep(120)

                    # Étape 4 : Cmd + A, Cmd + C
                    for i in range(8):
                        with keyboard.pressed(Key.shift_l):
                            keyboard.press(Key.tab)
                            keyboard.release(Key.tab)
                        time.sleep(0.5)
                    keyboard.press(Key.space)
                    keyboard.release(Key.space)
                    time.sleep(0.5)

                    # Étape 5 : Sauvegarder dans un fichier
                    copied_content = """"
                    {
                        "topic":" """ + nom_item + """",
                        "slug":" """ + slug_item + """",
                    }"""
                    
                    + pyperclip.paste()
                    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                    base_dir = os.path.dirname(os.path.abspath(__file__))
                    save_dir = os.path.join(base_dir, "save", f"prompt_{timestamp}")
                    os.makedirs(save_dir, exist_ok=True)
                    file_path = os.path.join(save_dir, f"content_{file_name[:-3]}_{i}_{timestamp}.json")
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(f'{{"content": {repr(copied_content)}}}')

                    print(f"Contenu sauvegardé dans : {file_path}")

                    i += 1  # Incrémenter l'index pour le prochain fichier
                
                else:
                    print(f"Aucun contenu trouvé dans le fichier {file_name} à l'index {i}.")
                    i=0
                    continue
