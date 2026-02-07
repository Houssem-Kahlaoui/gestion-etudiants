from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import urllib.parse
import database

class GestionHandler(SimpleHTTPRequestHandler):
    """Handler personnalisé pour gérer les requêtes API"""
    
    def do_GET(self):
        """Gérer les requêtes GET"""
        if self.path == '/':
            # Servir index.html
            self.path = '/index.html'
            return SimpleHTTPRequestHandler.do_GET(self)
        
        elif self.path == '/api/etudiants':
            # Retourner tous les étudiants
            eleves = database.db.get_all_eleves()
            self._send_json_response(eleves)
        
        elif self.path == '/api/admis':
            # Retourner les étudiants admis
            admis = database.db.get_eleves_admis()
            self._send_json_response(admis)
        
        elif self.path == '/api/stats':
            # Retourner les statistiques
            stats = {
                "total": database.db.count_eleves(),
                "admis": database.db.count_admis()
            }
            self._send_json_response(stats)
        
        elif self.path == '/style.css':
            # Servir le CSS
            SimpleHTTPRequestHandler.do_GET(self)
        
        else:
            self.send_error(404, "Page non trouvée")
    
    def do_POST(self):
        """Gérer les requêtes POST"""
        if self.path == '/api/ajouter':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Ajouter l'étudiant
            result = database.db.ajouter_eleve(
                data['cin'],
                data['nom'],
                data['prenom'],
                data['age'],
                data['filiere']
            )
            
            self._send_json_response(result)
        
        elif self.path == '/api/ajouter-notes':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Ajouter les notes
            result = database.db.ajouter_notes(
                data['cin'],
                data['math'],
                data['phys'],
                data['info']
            )
            
            self._send_json_response(result)
        
        elif self.path == '/api/reset':
            # Réinitialiser la base de données
            import os
            if os.path.exists("eleves.db"):
                os.remove("eleves.db")
            # Recréer l'instance
            database.db = database.DatabaseManager()
            self._send_json_response({"success": True, "message": "Base réinitialisée"})
        
        elif self.path == '/api/add-examples':
            # Ajouter des exemples
            database.db.ajouter_exemples()
            self._send_json_response({"success": True, "message": "Exemples ajoutés"})
        
        else:
            self.send_error(404, "API non trouvée")
    
    def do_DELETE(self):
        """Gérer les requêtes DELETE pour supprimer un étudiant"""
        if self.path.startswith('/api/supprimer/'):
            try:
                cin = self.path.split('/')[-1]
                result = database.db.supprimer_eleve(cin)
                self._send_json_response(result)
            except Exception as e:
                self._send_json_response({"success": False, "error": str(e)})
        else:
            self.send_error(404, "API non trouvée")
    
    def _send_json_response(self, data):
        """Envoyer une réponse JSON"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response = json.dumps(data, ensure_ascii=False)
        self.wfile.write(response.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Ne pas loguer les messages"""
        pass

def run_server(port=8000):
    """Lancer le serveur HTTP"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, GestionHandler)
    
    print(f"🚀 Serveur démarré sur http://localhost:{port}")
    print(f"📂 Base de données: eleves.db")
    print("📌 Ouvrez votre navigateur et allez à http://localhost:8000")
    print("🛑 Appuyez sur Ctrl+C pour arrêter le serveur\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Serveur arrêté")
        httpd.server_close()

if __name__ == '__main__':
    run_server()