"""Integration tests exercise the real Streamlit script and session state."""

from datetime import date, timedelta
from pathlib import Path

from streamlit.testing.v1 import AppTest

APP = Path(__file__).resolve().parents[1] / "app.py"


def by_label(elements, label):
    """Find a widget by its public UI label."""
    return next(element for element in elements if element.label == label)


def test_manual_pet_task_edit_completion_and_rerun():
    app = AppTest.from_file(str(APP), default_timeout=15).run()
    assert not app.exception
    by_label(app.text_input, "Pet name").input("Biscuit")
    by_label(app.button, "Add pet").click().run()
    by_label(app.text_input, "Task description").input("Breakfast")
    by_label(app.selectbox, "Frequency").select("daily")
    by_label(app.button, "Add task").click().run()
    assert not app.exception
    owner = app.session_state.owner
    task = owner.get_all_tasks()[0]
    assert owner.pets[0].name == "Biscuit" and task.frequency == "daily"
    by_label(app.text_input, "Edit description").input("Morning breakfast")
    by_label(app.button, "Save changes").click().run()
    assert owner.get_all_tasks()[0].description == "Morning breakfast"
    by_label(app.button, "Mark complete").click().run()
    assert not app.exception
    tasks = owner.get_all_tasks()
    assert len(tasks) == 2 and tasks[0].completed and not tasks[1].completed
    assert tasks[1].due_date == date.today() + timedelta(days=1)
    app.run()
    assert len(app.session_state.owner.get_all_tasks()) == 2


def test_demo_conflicts_filters_and_plan():
    app = AppTest.from_file(str(APP), default_timeout=15).run()
    by_label(app.button, "Load example household").click().run()
    assert not app.exception
    assert len(app.session_state.owner.pets) == 2
    assert any("Conflict" in warning.value for warning in app.warning)
    by_label(app.selectbox, "Filter by pet").select("Luna").run()
    assert len(app.table[0].value) == 2
    assert set(app.table[0].value["Pet"]) == {"Luna"}
    by_label(app.number_input, "Available care time (minutes)").set_value(45)
    by_label(app.button, "Generate schedule").click().run()
    assert not app.exception
    assert len(app.table[1].value) == 3
    assert any("35 of 45" in message.value for message in app.success)


def test_invalid_form_shows_error_without_mutation():
    app = AppTest.from_file(str(APP), default_timeout=15).run()
    by_label(app.button, "Add pet").click().run()
    assert not app.exception
    assert any("Pet name is required" in error.value for error in app.error)
    assert app.session_state.owner.pets == []
