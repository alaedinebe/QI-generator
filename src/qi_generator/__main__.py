import subprocess
import os
import csv
import time
import json
import pyperclip
import datetime
import re
import traceback  
from pynput.keyboard import Key, Controller
from pynput.mouse import Controller as MouseController
from pynput.mouse import Button

def clean_quotes(s: str) -> str:
    return s.translate({
        ord('’'): ord("'"),
        ord('‘'): ord("'"),
        ord('“'): ord('"'),
        ord('”'): ord('"'),
        0x00A0: 0x20,   # espace insécable -> espace normal
    })

def write_debug(name: str, content: str):
    save_dir = 'resultats'
    try:
        p = os.path.join(save_dir, name)
        with open(p, "w", encoding="utf-8") as df:
            df.write(content)
    except Exception:
        # on ne fait pas planter le script pour un log
        pass

def git_commit_push(file_path: str, slug: str):
    """
    Fonction pour effectuer un git add, commit, et push après la création d'un fichier.
    """
    try:
        # Ajout du fichier à Git (sans sortie dans le terminal)
        subprocess.run(["git", "add", "."], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Commit du fichier avec un message personnalisé (sans sortie dans le terminal)
        commit_message = f"new item {slug}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Pousser les modifications vers le dépôt distant (sans sortie dans le terminal)
        subprocess.run(["git", "push", "origin", "main"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Optionnel : afficher un message sans sortie Git
        print(f"Git commit et push effectués pour le fichier {file_path}.")
    except subprocess.CalledProcessError as e:
        print(f"Erreur Git : {e}")

def main():

    keyboard = Controller()
    mouse = MouseController()

    # --- Afficher la position de la souris au lancement ---
    try:
        x0, y0 = mouse.position
        print(f"Position souris au lancement : ({x0}, {y0})")
    except Exception as e:
        print(f"Impossible de récupérer la position de la souris : {e}")

    # --- Récupérer la vraie taille de l'écran principal (sans libs externes) ---
    try:
        import tkinter as tk
        _root = tk.Tk()
        _root.withdraw()  # pas de fenêtre visible
        screen_width = _root.winfo_screenwidth()
        screen_height = _root.winfo_screenheight()
        _root.destroy()
    except Exception:
        # Fallback si tkinter indisponible
        screen_width = 1920
        screen_height = 1080
    print(f"Taille écran détectée : {screen_width} x {screen_height}")

    # Étape 0 : Alt + Tab (Windows equivalent of Cmd + Tab)
    keyboard.press(Key.alt)
    time.sleep(0.5)
    keyboard.press(Key.tab)
    time.sleep(0.5)
    keyboard.release(Key.tab)
    time.sleep(0.5)
    keyboard.release(Key.alt)
    time.sleep(0.5)

    # Définir le chemin vers le dossier 'lisa'
    lisa_folder = os.path.join(os.getcwd(), 'lisa')

    # Récupérer et trier les fichiers JSON dans l'ordre croissant
    files = sorted([f for f in os.listdir(lisa_folder) if f.endswith('.json')])

    # Initialiser les listes pour savoir quel numéro d'item, nom d'item et slug d'item utiliser
    numero_item = []
    slug = []
    subject = []

    # vérifier l'existence du fichier dbo.csv
    if not os.path.exists("dbo.csv"):
        print("Le fichier dbo.csv n'existe pas. Veuillez le créer avant d'exécuter le script.")
        exit(1)

    print("on est la 1")    
    with open("dbo.csv", "r", encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=',')
        header = next(reader)          # ['item', 'numero', 'nom']
        print("on est la 2")    

        for row in reader:
            print("on est la 3")    

            numero_item = row[0]
            slug = row[1]
            subject = row[2].split('-')[0].strip()

            print(f"\nTraitement de l'item fichier : {numero_item} : {slug}\n")

            # Charger les fichiers et extraire la propriété 'content' de chacun
            medical_contexts = []
            file_name = numero_item+".json"
            file_path = os.path.join(lisa_folder, file_name)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                for j in range(len(data)):
                    if data[j]["content"]:  # Vérifier que le champ 'content' existe

                        base_dir = os.path.dirname(os.path.abspath(__file__))
                        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                        save_dir = os.path.join(base_dir, "save", f"qi_{numero_item}_{slug}_{timestamp}")
                        os.makedirs(save_dir, exist_ok=True)

                        medical_contexts = data[j]["content"]  # accès au champ 'content' de élément

                        prompt = """
                        ### 🧠 Contexte

                        Tu es un professeur de médecine, expert en physiopathologie, spécialisé dans la conception de *questions à choix multiples (QCM)* pour les étudiants de DFASM préparant l'*Épreuve Dématérialisée Nationale (EDN)*. Tu maîtrises les attendus du programme, la taxonomie de Bloom, et la rédaction pédagogique exigeante.

                        ---

                        ### 🎯 Objectif de la tâche

                        À partir du *contenu médical strictement fourni à la fin du prompt, tu dois générer **5 QCM* de *niveau EDN*, au format JSON spécifique indiqué ci-dessous.

                        Chaque QCM doit être *utile à l'entraînement des étudiants* en médecine dans une logique de consolidation des connaissances et de raisonnement clinique.

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
                        * Chaque QCM doit mobiliser un *savoir utile* pour l'EDN :

                        * *définitions* fondamentales (ex : TVP proximale vs distale) ;
                        * *raisonnement clinique* (ex : critères de gravité d'une EP) ;
                        * *catégorisation* (ex : éléments de la MVTE).
                        * Les *propositions* doivent toutes être *pertinentes médicalement* (évite les distracteurs trop évidents).
                        * Il doit y avoir au moins *une proposition correcte* par question.
                        * Il peut y avoir *une ou plusieurs bonnes réponses*.
                        * Les *justifications* doivent être *suffisamment explicites, pédagogiques et **100 % basées sur le contenu fourni. Ne fais **aucune inférence externe*.
                        * Ne mentionne *jamais* « le texte » ou « le contenu » dans les justifications.
                        * Respecte la taxonomie de Bloom : favorise des verbes d'action comme « identifier », « différencier », « reconnaître », « définir », « classer ».

                        ---

                        ### 📄 Contenu médical sur lequel s'appuyer

                        """ + str(medical_contexts) +"""


                        ---

                        ### ❌ Ne fais surtout pas

                        * Ne produis pas de contenu hors de ce champ médical.
                        * Ne produis pas de texte hors JSON (pas de commentaire, pas d'introduction).
                        * Ne mélange pas les champs ou formats.
                        * Ne propose pas plus ou moins de 5 propositions par question.
                        * Ne fais pas de paraphrase du contenu ou de gloses.

                        ---

                        ### ✅ Tu peux maintenant commencer

                        Génère *directement* un tableau JSON de *5 objets QCM complets*, parfaitement conformes au format ci-dessus, et exploitables tels quels dans une base EDN.

                        Aucune phrase explicative n'est attendue avant ou après la sortie. Génère uniquement le JSON proprement.
                        """

                        # Étape 0 : Ctrl + L (Windows equivalent of Cmd + L)
                        keyboard.press(Key.ctrl)
                        time.sleep(0.5)
                        keyboard.press('l')
                        time.sleep(0.1)
                        keyboard.release('l')
                        time.sleep(0.5)
                        keyboard.release(Key.ctrl)

                        time.sleep(1)

                        keyboard.type("chatgpt.com")
                        time.sleep(1)
                        keyboard.press(Key.enter)
                        keyboard.release(Key.enter) 

                        # Petite pause pour laisser l'app s'ouvrir
                        time.sleep(20)

                        # Étape 2 : Coller le texte
                        pyperclip.copy(prompt)
                        with keyboard.pressed(Key.ctrl):
                            keyboard.press('v')
                            keyboard.release('v')

                        keyboard.press(Key.enter)
                        keyboard.release(Key.enter)

                        # Étape 3 : Attendre 2 minutes 
                        time.sleep(120)
                        
                        # Étape 3.5 : Positionner la souris au milieu de l'écran et scroller
                        mouse.position = (screen_width // 2, screen_height // 2)
                        time.sleep(0.5)
                        
                        # Scroller vers le bas 10 fois
                        for scroll_count in range(10):
                            mouse.scroll(0, -300)  # Scroll vers le bas (valeur négative)
                            time.sleep(0.2)

                        # appuyer sur le bouton de copie. sur petit ecran = 568, 522. sur grand écran externe = 886,879
                        mouse.position = (861, 916)
                        # mouse.position = (568, 522)
                        time.sleep(0.5)
                        mouse.click(Button.left)
                        time.sleep(0.5)  

                        raw = pyperclip.paste()
                        txt = clean_quotes(raw).strip()

                        # 1) Retirer un éventuel bloc ```json ... ```
                        m = re.search(r"```(?:json)?\s*(.*?)\s*```", txt, flags=re.S)
                        if m:
                            txt = m.group(1).strip()

                        # 2) Remplacer tous les \[ et \] (LaTeX) par [ et ]
                        txt = re.sub(r'\\\[', '[', txt)
                        txt = re.sub(r'\\\]', ']', txt)

                        # 3) Parser (avec une 2e passe si virgules pendantes)
                        try:
                            content_obj = json.loads(txt)

                            # 4) Construire la charge utile propre (1 question par objet de content_obj)
                            now_ms = int(time.time() * 1000)

                            # S'assurer d'avoir une liste d'objets QCM
                            items = content_obj if isinstance(content_obj, list) else [content_obj]

                            questions = []
                            base_id = f"AIgenerated_{now_ms}"
                            for idx, item in enumerate(items, start=1):
                                questions.append({
                                    "published": False,
                                    "id": f"{base_id}_{idx:02d}",  # ex: AIgenerated_1723298765123_01
                                    "current_version_epoch_ms": now_ms,
                                    "rang": data[j]["rang"],
                                    "topic": {
                                        "subject": subject.strip(),
                                        "item": slug.strip()
                                    },
                                    "data": item  # <-- un seul objet ici
                                })

                            payload = {
                                "topic": {
                                    "item": slug.strip(),
                                    "subject": subject.strip()
                                },
                                "metadata": {
                                    "batch": "IA_aout"
                                },
                                "question": questions  # <-- liste d'objets
                            }

                            # 5) Sauvegarder joliment
                            file_path = os.path.join(f"content_{subject}_{numero_item}_{slug}_{data[j]['identifiant']}_{timestamp}.json")
                            with open(file_path, "w", encoding="utf-8") as f:
                                json.dump(payload, f, ensure_ascii=False, indent=2)

                            print(f"Contenu sauvegardé dans : {file_path}")

                            # Git add, commit, et push après la création du fichier
                            git_commit_push(file_path, slug)

                        except json.JSONDecodeError as e:
                            print(f"[direct] JSONDecodeError: {e.msg} (line {e.lineno}, col {e.colno})")                            

                    else:
                        print(f"Aucun contenu trouvé dans le fichier {file_name}.")
                        continue
