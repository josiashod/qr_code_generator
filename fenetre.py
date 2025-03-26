import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QComboBox, QFileDialog,
                             QMessageBox, QGroupBox)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import cv2

from qr import lire_qr, creer_qr
import os
import sys

class QRApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Codeur/Décodeur QR Binaire")
        self.setGeometry(100, 100, 800, 600)
        
        self.initUI()
    
    def initUI(self):
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Panel de gauche (Encodage)
        encode_panel = QGroupBox("Encodage")
        encode_layout = QVBoxLayout()
        
        self.binary_input = QLineEdit()
        self.binary_input.setPlaceholderText("Entrez votre chaîne binaire (ex: 10100101)")
        
        self.size_combo = QComboBox()
        self.size_combo.addItems(["5x5 (9 bits)", "7x7 (25 bits)"])
        
        encode_btn = QPushButton("Générer QR Code")
        encode_btn.clicked.connect(self.encode_qr)
        
        self.qr_preview = QLabel()
        self.qr_preview.setAlignment(Qt.AlignCenter)
        self.qr_preview.setMinimumSize(300, 300)
        
        save_btn = QPushButton("Enregistrer l'image")
        save_btn.clicked.connect(self.save_qr)
        
        encode_layout.addWidget(QLabel("Chaîne binaire:"))
        encode_layout.addWidget(self.binary_input)
        encode_layout.addWidget(QLabel("Taille:"))
        encode_layout.addWidget(self.size_combo)
        encode_layout.addWidget(encode_btn)
        encode_layout.addWidget(self.qr_preview)
        encode_layout.addWidget(save_btn)
        encode_panel.setLayout(encode_layout)
        
        # Panel de droite (Décodage)
        decode_panel = QGroupBox("Décodage")
        decode_layout = QVBoxLayout()
        
        self.decoded_bits = QLabel("Bits décodés: ")
        self.decoded_bits.setWordWrap(True)
        
        self.image_preview = QLabel()
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setMinimumSize(300, 300)
        
        load_btn = QPushButton("Charger image QR")
        load_btn.clicked.connect(self.load_qr)
        
        decode_btn = QPushButton("Décoder l'image")
        decode_btn.clicked.connect(self.decode_qr)
        
        decode_layout.addWidget(load_btn)
        decode_layout.addWidget(self.image_preview)
        decode_layout.addWidget(decode_btn)
        decode_layout.addWidget(self.decoded_bits)
        decode_panel.setLayout(decode_layout)
        
        # Ajout des panels au layout principal
        main_layout.addWidget(encode_panel)
        main_layout.addWidget(decode_panel)
        
        # Variables d'état
        self.current_qr = None
        self.current_image = None
    
    def encode_qr(self):
        binary_str = self.binary_input.text().strip()
        
        # Validation de l'entrée
        if not binary_str:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une chaîne binaire")
            return
        
        if not all(c in '01' for c in binary_str):
            QMessageBox.warning(self, "Erreur", "La chaîne doit contenir seulement des 0 et 1")
            return
        
        # Déterminer la taille
        size_str = self.size_combo.currentText()
        size = 5 if "5x5" in size_str else 7
        max_bits = (size-2) * (size-2)
        
        # Ajuster la longueur si nécessaire
        if len(binary_str) < max_bits:
            binary_str = binary_str.ljust(max_bits, '0')
        elif len(binary_str) > max_bits:
            binary_str = binary_str[:max_bits]
            QMessageBox.information(self, "Information", f"La chaîne a été tronquée à {max_bits} bits")
        
        # Générer le QR code
        self.current_qr = creer_qr(binary_str, size)
        
        # Convertir en mode 'L' (niveaux de gris) d'abord
        qr_img = self.current_qr.convert('L')
        
        # Convertir en QImage
        qimage = QImage(
            qr_img.tobytes(),
            qr_img.size[0],
            qr_img.size[1],
            qr_img.size[0],  # bytesPerLine
            QImage.Format_Grayscale8
        )
        
        # Afficher sans déformation
        self.qr_preview.setPixmap(QPixmap.fromImage(qimage))

    
    def save_qr(self):
        if not self.current_qr:
            QMessageBox.warning(self, "Erreur", "Aucun QR code à enregistrer")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Enregistrer le QR Code", "", "Images (*.png)")
        
        if file_path:
            if ".png" not in file_path:
                file_path += ".png"
            self.current_qr.save(file_path)
            QMessageBox.information(self, "Succès", "QR code enregistré avec succès")
    
    def load_qr(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Charger une image QR", "", "Images (*.png *.jpg *.bmp *.jpeg)")
        
        if file_path:
            self.current_image = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)
            
            if self.current_image is None:
                QMessageBox.warning(self, "Erreur", "Impossible de charger l'image")
                return
            
            # Afficher l'aperçu
            height, width = self.current_image.shape
            bytes_per_line = width
            q_img = QImage(self.current_image.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
            self.image_preview.setPixmap(QPixmap.fromImage(q_img).scaled(300, 300, Qt.KeepAspectRatio))
    
    def decode_qr(self):
        if self.current_image is None:
            QMessageBox.warning(self, "Erreur", "Veuillez d'abord charger une image")
            return
        
        # Sauvegarder temporairement l'image pour utiliser lire_qr
        temp_path = "temp_qr.png"
        cv2.imwrite(temp_path, self.current_image)
        
        # Décodage avec la fonction importée
        binary_str = lire_qr(temp_path)
        
        if binary_str is not None:
            self.decoded_bits.setText(f"Bits décodés: {binary_str}")
            if os.path.exists(temp_path):
                os.remove(temp_path)
        else:
            self.decoded_bits.setText("Échec du décodage")
            QMessageBox.warning(self, "Erreur", "Impossible de décoder le QR code")
    
    def read_qr_code(self, img):
        """Lit un QR code et retourne la chaîne binaire"""
        try:
            # Binarisation
            _, img_bin = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
            
            # Détection taille
            ligne_haut = img_bin[0, :]
            changements = np.sum(ligne_haut[:-1] != ligne_haut[1:])
            size = 5 if changements == 4 else 7 if changements == 6 else None
            
            if not size:
                QMessageBox.warning(self, "Erreur", "Taille de QR code non reconnue")
                return None
            
            # Redimensionnement
            small = cv2.resize(img_bin, (size, size), cv2.INTER_NEAREST)
            
            # Lecture données
            result = ""
            for y in range(1, size-1):
                for x in range(1, size-1):
                    result += '1' if small[y,x] < 128 else '0'
            
            return result
        except Exception as e:
            QMessageBox.critical(self, "Erreur", f"Erreur lors du décodage: {str(e)}")
            return None

if __name__ == "__main__":
    # Force X11 sous Linux pour éviter les problèmes Wayland
    # if sys.platform.startswith('linux'):
    #     os.environ["QT_QPA_PLATFORM"] = "xcb"

    # Active la gestion des threads X11
    # QCoreApplication.setAttribute(Qt.AA_X11InitThreads)
    app = QApplication(sys.argv)
    window = QRApp()
    window.show()
    sys.exit(app.exec_())