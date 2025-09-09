
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

def create_presence_sheet(societe, academicien, duree, lieu, formation):
    """
    Génère une feuille de présence en PDF pour un académicien.
    """
    output_dir = "feuilles_présence"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    file_name = os.path.join(output_dir, f"Feuille_de_presence_{academicien.replace(' ', '_')}.pdf")
    doc = SimpleDocTemplate(file_name, pagesize=A4, rightMargin=2*cm, leftMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    
    story = []
    styles = getSampleStyleSheet()

    # Titre de l'entreprise
    company_title = Paragraph("Laurent-Serre-Développement", styles['h1'])
    story.append(company_title)
    story.append(Spacer(1, 0.5*cm))

    # Titre du document
    title = Paragraph("FEUILLE DE PRESENCE", styles['h2'])
    story.append(title)
    story.append(Spacer(1, 1*cm))

    # Informations générales
    info_data = [
        ['SOCIETE', societe],
        ['ACADEMICIEN', academicien],
        ['DUREE', duree],
        ['LIEU', lieu],
        ['FORMATION', formation]
    ]
    info_table = Table(info_data, colWidths=[4*cm, 12*cm])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 1*cm))
    
    # Note
    note_text = "*En cas de journée complète de formation, penser à remplir 2 lignes, une pour le matin et une pour l'après-midi"
    story.append(Paragraph(note_text, styles['Italic']))
    story.append(Spacer(1, 0.5*cm))


    # Tableau de présence
    table_header = ['Date', 'Niveau', 'Durée (h)', 'Horaires', 'Signature Stagiaire', 'Signature Formateur']
    
    table_data = [table_header]
    for i in range(16): # 16 lignes pour 8 jours
        horaire = "9h-13h00" if i % 2 == 0 else "14h-18h00"
        table_data.append(['', '', '', horaire, '', ''])

    presence_table = Table(table_data, colWidths=[2.5*cm, 2.5*cm, 2*cm, 2.5*cm, 4*cm, 4*cm], rowHeights=1.5*cm)
    presence_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#CCCCCC')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    story.append(presence_table)

    doc.build(story)
    print(f"Feuille de présence '{file_name}' générée.")

def main():
    """
    Fonction principale pour demander les informations et générer les feuilles.
    """
    print("Générateur de feuilles de présence")
    print("="*30)

    societe = input("Nom de la société cliente : ")
    academiciens_str = input("Nom des académiciens (séparés par une virgule) : ")
    duree = input("Durée de la formation : ")
    lieu = input("Lieu de formation : ")
    formation = input("Nom de la formation : ")
    
    academiciens = [a.strip() for a in academiciens_str.split(',')]
    
    for academicien in academiciens:
        print(f"Génération de la feuille de présence pour {academicien}...")
        create_presence_sheet(societe, academicien, duree, lieu, formation)

    print("="*30)
    print("Toutes les feuilles de présence ont été générées.")

if __name__ == "__main__":
    main()
