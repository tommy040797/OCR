für easy ocr bitte das hier installieren: https://pytorch.org/, je nach grafikkartenverfügbarkeit mit cpu, wenn möglich aber mit mit cuda (abtastfrequenz von 0,2 sekunden machbar, log in sekundenbereich nur falsch, da doppelpunkt im video verschoben wird!!!!)
für tesseract: https://github.com/UB-Mannheim/tesseract/wiki#tesseract-installer-for-windows Daraufhin den Pfad zur installation in der config datei hinterlegen (aktuell nichtmal eine frequenz von 1 machbar, dafür kaum ressourcenbenutzung, overhead ist meine vermutung, da es mit weniger rechtecken deutlich besser lief)
keras: noch nicht implementiert

funktionalität bis jetzt nur mit ndi stream überprüft, aufgrund der bildqualität

pip3 install -r requirements.txt
