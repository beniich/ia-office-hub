
import uno
from com.sun.star.frame import Desktop

class OpenOfficeBridge:
    def __init__(self):
        try:
            local_context = uno.getComponentContext()
            resolver = local_context.ServiceManager.createInstanceWithArguments(
                "com.sun.star.bridge.UnoUrlResolver", ("socket,host=localhost,port=2002;urp;",)
            )
            self.context = resolver.resolve()
        except Exception as e:
            print(f"OpenOffice Connection Error: {e}")

    def generate_document(self, doc_type, content, filename):
        # Logique simplifiée pour créer un doc Writer/Calc/Impress
        print(f"Generating {doc_type} with content: {content} as {filename}")
        # Ici on insérerait le code PyUNO pour manipuler le document
        return f"/app/output/{filename}"

    def read_calc_range(self, file_path, range_address="A1:C10"):
        """
        Lit une plage de cellules dans un fichier Calc.
        En mode réel, utilise PyUNO pour extraire les valeurs.
        """
        print(f"Reading data from {file_path} range {range_address}...")
        # Simulation de données extraites d'un fichier .ods
        # Dans la réalité, ici on boucle sur les cellules UNO
        return [
            {"poste": "Marketing", "prevu": 10000, "reel": 12500},
            {"poste": "R&D", "prevu": 50000, "reel": 45000},
            {"poste": "Salaires", "prevu": 100000, "reel": 105000},
        ]
