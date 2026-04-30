from flask import Flask, render_template, request, redirect
import sqlite3
import pandas as pd
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

# Connexion base
def db():
    return sqlite3.connect("databases.db")

# Page formulaire
@app.route('/')
def home():
    return render_template("form.html")

# Enregistrer données
@app.route('/save', methods=['POST'])
def save():

    age = int(request.form['age'])
    salaire = float(request.form['salaire'])
    ecole = request.form['ecole']
    android = request.form['android']

    conn = db()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO data(age,salaire,ecole,android)
    VALUES(?,?,?,?)
    """,(age,salaire,ecole,android))

    conn.commit()
    conn.close()

    return redirect('/dashboard')

# Dashboard
@app.route('/dashboard')
def dashboard():

    conn = db()
    df = pd.read_sql_query("SELECT * FROM data", conn)
    conn.close()

    # 🔹 Conversion données
    if len(df) > 0:
        df['ecole'] = df['ecole'].map({'publique':0,'privee':1})
        df['android'] = df['android'].map({'non':0,'oui':1})

    # 🔹 Classification KMeans
    if len(df) >= 3:
        X = df[['age','salaire','ecole','android']]
        model = KMeans(n_clusters=3, random_state=0)
        df['classe'] = model.fit_predict(X)
    else:
        df['classe'] = 0

    # 🔹 Analyse descriptive
    stats = df.describe().to_html()
    table = df.to_html()

    # 🔥 🔥 CAMEMBERT (fusion ici)
    if not os.path.exists("static"):
        os.makedirs("static")

    if len(df) == 0:
        labels = ['Faible', 'Moyen', 'Élevé']
        sizes = [33, 33, 34]
    else:
        df['categorie'] = pd.cut(
            df['salaire'],
            bins=[0, 20000, 50000, 100000],
            labels=['Faible', 'Moyen', 'Élevé']
        )

        counts = df['categorie'].value_counts()

        labels = counts.index
        sizes = counts.values

    # Chemin absolu du projet
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Chemin complet vers static
    STATIC_DIR = os.path.join(BASE_DIR, "static")

    # Créer le dossier s'il n'existe pas
    if not os.path.exists(STATIC_DIR):
        os.makedirs(STATIC_DIR)

    # Chemin complet du fichier image
    image_path = os.path.join(STATIC_DIR, "pie.png")

    print("Chemin image :", image_path)  # DEBUG

    # Création graphique
    plt.figure(figsize=(6,6))

    plt.pie(
        sizes,
        labels=labels,
        autopct='%1.1f%%',
        startangle=90
    )

    plt.title("Répartition des revenus")

    # Sauvegarde sécurisée
    plt.savefig(image_path)
    plt.close()

    print("Image créée avec succès")

    plt.title("Répartition des revenus")

    plt.savefig("static/pie.png")
    plt.close()
    return render_template(
        "dashboard.html",
        stats=stats,
        table=table
    )

if __name__ == '__main__':
    app.run(host="0.0.0.0",port=10000)