import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_name="eleves.db"):
        """Initialiser le gestionnaire de base de données"""
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        """Établir une connexion à la base de données"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  # Pour avoir des dictionnaires
        return conn
    
    def init_db(self):
        """Initialiser la base de données (VIDE - sans exemples)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Créer la table des étudiants avec CIN comme clé primaire
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS eleves (
            cin TEXT PRIMARY KEY,  -- CIN de 8 chiffres
            nom TEXT NOT NULL,
            prenom TEXT NOT NULL,
            age INTEGER NOT NULL,
            filiere TEXT NOT NULL,
            note_math REAL CHECK(note_math >= 0 AND note_math <= 20),
            note_phys REAL CHECK(note_phys >= 0 AND note_phys <= 20),
            note_info REAL CHECK(note_info >= 0 AND note_info <= 20),
            moyenne REAL,
            date_inscription TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✅ Base de données '{self.db_name}' initialisée (vide)")
    
    def ajouter_exemples(self):
        """Ajouter des exemples d'étudiants (optionnel)"""
        exemples = [
            ('12345678', 'Dupont', 'Jean', 20, 'Informatique', 15.0, 12.0, 18.0),
            ('87654321', 'Martin', 'Marie', 22, 'Mathématiques', 18.0, 14.0, 16.0),
            ('23456789', 'Dubois', 'Pierre', 21, 'Physique', 10.0, 17.0, 12.0),
            ('98765432', 'Leroy', 'Sophie', 19, 'Chimie', 8.0, 9.0, 11.0),
            ('34567890', 'Moreau', 'Thomas', 23, 'Biologie', 16.0, 13.0, 14.0)
        ]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for cin, nom, prenom, age, filiere, math, phys, info in exemples:
            try:
                moyenne = self.calculer_moyenne(math, phys, info)
                cursor.execute('''
                INSERT INTO eleves (cin, nom, prenom, age, filiere, note_math, note_phys, note_info, moyenne)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (cin, nom, prenom, age, filiere, math, phys, info, moyenne))
                print(f"✅ Exemple ajouté: {prenom} {nom} (CIN: {cin})")
            except sqlite3.IntegrityError:
                print(f"⚠️  CIN {cin} existe déjà, ignoré")
                continue
        
        conn.commit()
        conn.close()
        print("✅ Exemples d'étudiants ajoutés")
    
    def calculer_moyenne(self, math, phys, info):
        """Calculer la moyenne avec coefficients: Math(3), Phys(4), Info(2)"""
        if math is None or phys is None or info is None:
            return None
        total_coeff = 3 + 4 + 2
        moyenne = (math * 3 + phys * 4 + info * 2) / total_coeff
        return round(moyenne, 2)
    
    def verifier_cin(self, cin):
        """Vérifier si un CIN existe déjà et s'il est valide (8 chiffres)"""
        if not cin.isdigit() or len(cin) != 8:
            return False, "Le CIN doit contenir exactement 8 chiffres"
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM eleves WHERE cin = ?', (cin,))
        existe = cursor.fetchone()[0] > 0
        
        conn.close()
        
        if existe:
            return False, f"Le CIN {cin} existe déjà"
        
        return True, "CIN valide"
    
    def ajouter_eleve(self, cin, nom, prenom, age, filiere, math=None, phys=None, info=None):
        """Ajouter un nouvel élève avec CIN et notes"""
        # Vérifier le CIN
        cin_valide, message = self.verifier_cin(cin)
        if not cin_valide:
            return {"success": False, "error": message}
        
        # Calculer la moyenne si les notes sont fournies
        moyenne = None
        if math is not None and phys is not None and info is not None:
            moyenne = self.calculer_moyenne(math, phys, info)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
            INSERT INTO eleves (cin, nom, prenom, age, filiere, note_math, note_phys, note_info, moyenne)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (cin, nom, prenom, age, filiere, math, phys, info, moyenne))
            
            conn.commit()
            print(f"✅ Étudiant ajouté: {prenom} {nom} (CIN: {cin})")
            return {"success": True, "cin": cin, "moyenne": moyenne}
        except sqlite3.IntegrityError:
            error_msg = f"Le CIN {cin} existe déjà"
            print(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Erreur: {error_msg}")
            return {"success": False, "error": error_msg}
        finally:
            conn.close()
    
    def ajouter_notes(self, cin, math, phys, info):
        """Ajouter/mettre à jour les notes d'un étudiant"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Vérifier si l'étudiant existe
            cursor.execute('SELECT * FROM eleves WHERE cin = ?', (cin,))
            eleve = cursor.fetchone()
            
            if not eleve:
                return {"success": False, "error": "Étudiant non trouvé"}
            
            # Calculer la nouvelle moyenne
            moyenne = self.calculer_moyenne(math, phys, info)
            
            # Mettre à jour les notes et la moyenne
            cursor.execute('''
            UPDATE eleves 
            SET note_math = ?, note_phys = ?, note_info = ?, moyenne = ?
            WHERE cin = ?
            ''', (math, phys, info, moyenne, cin))
            
            conn.commit()
            print(f"✅ Notes mises à jour pour CIN: {cin}, Moyenne: {moyenne}")
            return {"success": True, "cin": cin, "moyenne": moyenne}
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Erreur: {error_msg}")
            return {"success": False, "error": error_msg}
        finally:
            conn.close()
    
    def get_all_eleves(self):
        """Récupérer tous les élèves"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM eleves ORDER BY nom, prenom')
        eleves = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return eleves
    
    def get_eleves_admis(self):
        """Récupérer les élèves admis (moyenne >= 10)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        SELECT * FROM eleves 
        WHERE moyenne >= 10 
        ORDER BY moyenne DESC, nom, prenom
        ''')
        eleves = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return eleves
    
    def supprimer_eleve(self, cin):
        """Supprimer un élève par son CIN"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Vérifier si l'élève existe
            cursor.execute('SELECT * FROM eleves WHERE cin = ?', (cin,))
            eleve = cursor.fetchone()
            
            if not eleve:
                error_msg = f"Élève avec CIN {cin} non trouvé"
                print(f"❌ {error_msg}")
                return {"success": False, "error": error_msg}
            
            # Supprimer l'élève
            cursor.execute('DELETE FROM eleves WHERE cin = ?', (cin,))
            conn.commit()
            
            print(f"✅ Étudiant supprimé: {eleve['prenom']} {eleve['nom']} (CIN: {cin})")
            return {"success": True, "nom": eleve['nom'], "prenom": eleve['prenom']}
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Erreur: {error_msg}")
            return {"success": False, "error": error_msg}
        finally:
            conn.close()
    
    def count_eleves(self):
        """Compter le nombre d'élèves"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM eleves')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def count_admis(self):
        """Compter le nombre d'élèves admis"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM eleves WHERE moyenne >= 10')
        count = cursor.fetchone()[0]
        
        conn.close()
        return count

# Instance globale de la base de données
db = DatabaseManager()