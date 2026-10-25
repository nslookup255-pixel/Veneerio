import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from vnr.cli.state_dump import StateDumpError, create_state_dump


class StateDumpTest(unittest.TestCase):
    def test_dump_includes_application_component_tree_and_state(self):
        with TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "main.py").write_text(
                "from vnr import App, Component, State\n"
                "from vnr.ui import Column, Text\n"
                "class Child(Component):\n"
                "    value = State({'count': 2})\n"
                "    def render(self):\n"
                "        return Text(str(self.value))\n"
                "class Root(Component):\n"
                "    def render(self):\n"
                "        return Column(Child())\n"
                "app = App(title='Debug', width=640, height=480)\n"
                "app.mount(Root())\n",
                encoding="utf-8",
            )

            dump = create_state_dump(project)

        self.assertEqual(dump["schema_version"], 1)
        self.assertEqual(
            dump["application"],
            {"title": "Debug", "width": 640, "height": 480, "mounted": True},
        )
        root = dump["root"]
        self.assertEqual(root["kind"], "component")
        column = root["rendered"]
        child = column["children"][0]
        self.assertEqual(child["kind"], "component")
        self.assertEqual(child["state"], {"value": {"count": 2}})
        self.assertEqual(child["rendered"]["kind"], "element")
        json.dumps(dump)

    def test_dump_handles_non_json_values_and_cycles(self):
        with TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "main.py").write_text(
                "from vnr import App, Component, State\n"
                "from vnr.ui import Text\n"
                "class Value:\n"
                "    def __repr__(self):\n"
                "        raise ValueError('no representation')\n"
                "class Root(Component):\n"
                "    value = State(None)\n"
                "    def render(self):\n"
                "        cycle = []\n"
                "        cycle.append(cycle)\n"
                "        self.value = {'object': Value(), 'cycle': cycle}\n"
                "        return Text('ready')\n"
                "app = App()\n"
                "app.mount(Root())\n",
                encoding="utf-8",
            )

            dump = create_state_dump(project)

        state = dump["root"]["state"]["value"]
        self.assertEqual(state["object"]["$type"], "main.Value")
        self.assertEqual(state["object"]["repr"], "<repr failed: ValueError>")
        self.assertEqual(state["cycle"][0], {"$type": "builtins.list", "$circular": True})
        json.dumps(dump)

    def test_dump_requires_entry_point_and_application(self):
        with TemporaryDirectory() as directory:
            project = Path(directory)
            with self.assertRaisesRegex(StateDumpError, "entry point is missing"):
                create_state_dump(project)

            (project / "main.py").write_text("value = 1\n", encoding="utf-8")
            with self.assertRaisesRegex(StateDumpError, "no App instance"):
                create_state_dump(project)

    def test_dump_rejects_multiple_applications(self):
        with TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "main.py").write_text(
                "from vnr import App\n"
                "first = App()\n"
                "second = App()\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(StateDumpError, "multiple App instances"):
                create_state_dump(project)

    def test_dump_reports_project_load_errors(self):
        with TemporaryDirectory() as directory:
            project = Path(directory)
            (project / "main.py").write_text(
                "raise ValueError('broken setup')\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                StateDumpError, "could not load application.*broken setup"
            ):
                create_state_dump(project)


if __name__ == "__main__":
    unittest.main()
