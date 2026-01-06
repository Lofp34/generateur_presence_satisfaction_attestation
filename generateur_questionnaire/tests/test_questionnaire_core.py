from questionnaire_core import QuestionnaireData, render_questionnaire, split_full_name


def test_split_full_name_variants():
    assert split_full_name("Alice Martin") == ("Alice", "Martin")
    assert split_full_name("Jean Claude Van Damme") == ("Jean Claude Van", "Damme")
    assert split_full_name("Madonna") == ("", "Madonna")
    assert split_full_name("   ") == ("", "")


def test_render_questionnaire_creates_pdf(tmp_path):
    data = QuestionnaireData(
        participant_last_name="Martin",
        participant_first_name="Alice",
        company="Entreprise Test",
        training_program="Formation Python",
        training_center="Centre Paris",
        start_date="01/01/2024",
        end_date="05/01/2024",
    )
    pdf_path = render_questionnaire(data, output_dir=tmp_path)
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0
