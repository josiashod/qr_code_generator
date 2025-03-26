# Importation des bibliothèques nécessaires
from PIL import Image, ImageDraw
import numpy as np
import cv2
import argparse

## Partie 1 : Création du QR code (encodage)

def creer_qr(binaire, taille=5):
    """
    Crée une image QR code à partir d'une chaîne binaire
    taille peut être 5 ou 7
    """
    
    # Vérifications simples
    if taille not in [5, 7]:
        print("Erreur : La taille doit être 5 ou 7")
        return None
    
    # Calcul de la taille de la zone centrale
    zone_centrale = (taille-2) * (taille-2)
    
    # Vérification de la longueur du code binaire
    if len(binaire) != zone_centrale:
        print(f"Erreur : Le code binaire doit faire {zone_centrale} caractères")
        return None
    
    # Création d'une image vide (tout blanc)
    qr_image = Image.new('1', (taille, taille), 1)  # '1' pour image noir et blanc
    draw = ImageDraw.Draw(qr_image)
    
    # Dessin de la première ligne et colonne alternées
    for i in range(taille):
        # Première ligne
        couleur = 0 if i % 2 == 0 else 1  # Noir si pair, blanc si impair
        draw.point((i, 0), couleur)
        
        # Première colonne (en évitant de redessiner le coin)
        if i != 0:
            draw.point((0, i), couleur)
    
    # Remplissage de la zone centrale
    position = 0  # Pour parcourir la chaîne binaire
    for y in range(1, taille-1):
        for x in range(1, taille-1):
            if position < len(binaire):
                bit = int(binaire[position])
                draw.point((x, y), bit)
                position += 1
    
    # Agrandissement pour mieux voir
    grand_qr = qr_image.resize((taille * 50, taille * 50), Image.NEAREST)
    
    return grand_qr

## Partie 2 : Lecture du QR code (décodage)
def lire_qr(image_path):
    """
    Lit un QR code à partir d'une image et retourne le code binaire
    """
    
    # Charger l'image
    try:
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            print("Erreur : Impossible de charger l'image")
            return None
    except:
        print("Erreur : Problème avec le fichier image")
        return None
    
    # Binarisation de l'image (noir et blanc)
    _, img_bin = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
    
    # Trouver la taille du QR code en comptant les changements de couleur
    ligne_haut = img_bin[0, :]
    changements = 0
    for i in range(1, len(ligne_haut)):
        if ligne_haut[i] != ligne_haut[i-1]:
            changements += 1
    
    # Déduction de la taille
    if changements == 4:   # 5x5
        taille = 5
    elif changements == 6: # 7x7
        taille = 7
    else:
        print("Erreur : Taille de QR code non reconnue")
        return None
    
    # Redimensionnement
    petit_qr = cv2.resize(img_bin, (taille, taille), interpolation=cv2.INTER_NEAREST)
    
    # Extraction des données
    code_binaire = ""
    for y in range(1, taille-1):
        for x in range(1, taille-1):
            if petit_qr[y, x] < 128:  # Noir
                code_binaire += "0"
            else:  # Blanc
                code_binaire += "1"
    
    return code_binaire

## Partie 3 : Fonctions supplémentaires pour rendre plus robuste

def ajouter_controle(binaire):
    """
    Ajoute un bit de parité simple pour détection d'erreur
    """
    nb_uns = binaire.count('1')
    bit_parite = '1' if nb_uns % 2 else '0'
    return binaire + bit_parite

def verifier_controle(binaire):
    """
    Vérifie le bit de parité
    Retourne True si pas d'erreur détectée
    """
    if len(binaire) < 1:
        return False
    
    donnees = binaire[:-1]
    bit_parite = binaire[-1]
    
    nb_uns = donnees.count('1')
    parite_calculee = '1' if nb_uns % 2 else '0'
    
    return bit_parite == parite_calculee

def test():
    print("=== Test encodage 5x5 ===")
    # Pour 5x5, zone centrale = 3x3 = 9 bits
    code_5x5 = "001010001"  # 9 bits exactement
    qr = creer_qr(code_5x5, 5)
    
    if qr:
        qr.save("qr_5x5.png")
        print(f"QR code créé avec le code: {code_5x5}")
        print("Image sauvegardée comme 'qr_5x5.png'")
    
    print("\n=== Test décodage 5x5 ===")
    code_5x5 = lire_qr("qr_5x5.png")
    decode_5x5 = lire_qr("qr_5x5.png")
    print(f"Original: {code_5x5}")
    print(f"Lu:      {code_5x5}")
    print("Correspond!" if code_5x5 == code_5x5 else "Erreur!")

    # Test 7x7 - Version simple
    print("\n=== Test 7x7 ===")
    code_7x7 = "1101001010110100101011010"  # 25 bits pour zone 5x5
    qr = creer_qr(code_7x7, 7)
    qr.save("qr_7x7.png")
    if qr:
        qr.save("qr_7x7.png")
        print(f"QR code créé avec le code: {code_7x7}")
        print("Image sauvegardée comme 'qr_7x7.png'")

    # Décodage
    decode_7x7 = lire_qr("qr_7x7.png")
    print(f"Original: {code_7x7}")
    print(f"Lu:      {decode_7x7}")
    print("Correspond!" if code_7x7 == decode_7x7 else "Erreur!")

def main():
    parser = argparse.ArgumentParser(description="Codeur/Décodeur de QR binaire")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--encoder', help="Chaîne binaire à encoder (ex: '101001')")
    group.add_argument('--decoder', help="Chemin de l'image QR à décoder")
    parser.add_argument('--taille', type=int, choices=[5,7], default=5, 
                       help="Taille du QR (5x5 ou 7x7)")
    parser.add_argument('--output', help="Fichier de sortie pour le QR généré")
    
    args = parser.parse_args()
    
    if args.encoder:
        # Validation entrée binaire
        if not all(c in '01' for c in args.encoder):
            print("Erreur: La chaîne doit contenir seulement des 0 et 1")
            return
            
        qr = creer_qr(args.encoder, args.taille)
        output_file = args.output or f"qr_binaire_{args.taille}x{args.taille}.png"
        qr.save(output_file)
        print(f"QR code généré: {output_file}")
        print(f"Taille: {args.taille}x{args.taille}")
        print(f"Bits encodés: {args.encoder}")
        
    elif args.decoder:
        bits = lire_qr(args.decoder)
        if bits:
            print("\nRésultat du décodage:")
            print(f"Fichier: {args.decoder}")
            print(f"Bits décodés: {bits}")

if __name__ == "__main__":
    main()