import argparse
import re
import sys
from pathlib import Path

from questionnaire_core import QuestionnaireData, render_questionnaire, split_full_name


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Générateur de questionnaires de satisfaction en PDF."
    )
    parser.add_argument(
        "--output-dir",
        default="generateur_questionnaire/questionnaires_satisfaction",
        help="Répertoire de sortie des PDF générés.",
    )
    parser.add_argument(
        "--logo",
        default=None,
        help="Chemin vers un logo à afficher dans l'en-tête (optionnel).",
    )
    return parser.parse_args()


def prompt(prompt_text: str) -> str:
    return input(prompt_text).strip()


def collect_participants() -> list[str]:
    raw = input("Participants (séparés par des virgules) : ").strip()
    if not raw:
        return []
    tokens = re.split(r"[,\n]", raw)
    return [token.strip() for token in tokens if token.strip()]


def main() -> None:
    args = parse_args()

    print("==============================================")
    print(" Générateur de questionnaires de satisfaction ")
    print("==============================================")
    print("")

    company = prompt("Nom de la société cliente : ")
    training_program = prompt("Parcours de formation : ")
    training_center = prompt("Centre d'entraînement : ")
    start_date = prompt("Date de début : ")
    end_date = prompt("Date de fin : ")
    participants = collect_participants()

    if not participants:
        print("Aucun participant fourni, arrêt.")
        sys.exit(1)

    output_dir = Path(args.output_dir)
    logo_path = args.logo if args.logo else None

    for participant in participants:
        first_name, last_name = split_full_name(participant)
        data = QuestionnaireData(
            participant_last_name=last_name,
            participant_first_name=first_name,
            company=company,
            training_program=training_program,
            training_center=training_center,
            start_date=start_date,
            end_date=end_date,
            logo_path=logo_path,
        )
        pdf_path = render_questionnaire(data, output_dir=output_dir)
        print(f"- Questionnaire généré : {pdf_path}")

    print("")
    print("Opération terminée.")


if __name__ == "__main__":
    main()
