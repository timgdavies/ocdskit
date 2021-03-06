import os.path
import sys
from io import StringIO
from tempfile import TemporaryDirectory
from unittest.mock import patch

import pytest

from ocdskit.cli.__main__ import main

schema = '''{
  "properties": {
    "closedStringNull": {
      "type": [
        "string",
        "null"
      ],
      "codelist": "a.csv",
      "openCodelist": false
    },
    "closedArrayNull": {
      "type": [
        "array",
        "null"
      ],
      "codelist": "b.csv",
      "openCodelist": false,
      "items": {
        "type": "string"
      }
    },
    "closedString": {
      "type": "string",
      "codelist": "c.csv",
      "openCodelist": false
    },
    "closedDisorder": {
      "type": "string",
      "codelist": "d.csv",
      "openCodelist": false,
      "enum": [
        "bar",
        "foo"
      ]
    },
    "open": {
      "type": [
        "string",
        "null"
      ],
      "codelist": "a.csv",
      "openCodelist": true
    }
  }
}
'''

schema_with_enum = '''{
  "properties": {
    "closedStringNull": {
      "type": [
        "string",
        "null"
      ],
      "codelist": "a.csv",
      "openCodelist": false,
      "enum": [
        "foo",
        "bar",
        null
      ]
    },
    "closedArrayNull": {
      "type": [
        "array",
        "null"
      ],
      "codelist": "b.csv",
      "openCodelist": false,
      "items": {
        "type": "string",
        "enum": [
          "foo",
          "bar"
        ]
      }
    },
    "closedString": {
      "type": "string",
      "codelist": "c.csv",
      "openCodelist": false,
      "enum": [
        "foo",
        "bar"
      ]
    },
    "closedDisorder": {
      "type": "string",
      "codelist": "d.csv",
      "openCodelist": false,
      "enum": [
        "bar",
        "foo"
      ]
    },
    "open": {
      "type": [
        "string",
        "null"
      ],
      "codelist": "a.csv",
      "openCodelist": true
    }
  }
}
'''

schema_with_modification = '''{
  "properties": {
    "closedStringNull": {
      "type": [
        "string",
        "null"
      ],
      "codelist": "a.csv",
      "openCodelist": false,
      "enum": [
        "foo",
        "bar",
        "baz",
        null
      ]
    },
    "closedArrayNull": {
      "type": [
        "array",
        "null"
      ],
      "codelist": "b.csv",
      "openCodelist": false,
      "items": {
        "type": "string",
        "enum": [
          "foo"
        ]
      }
    },
    "closedString": {
      "type": "string",
      "codelist": "c.csv",
      "openCodelist": false,
      "enum": [
        "foo",
        "bar"
      ]
    },
    "closedDisorder": {
      "type": "string",
      "codelist": "d.csv",
      "openCodelist": false,
      "enum": [
        "bar",
        "foo"
      ]
    },
    "open": {
      "type": [
        "string",
        "null"
      ],
      "codelist": "a.csv",
      "openCodelist": true
    }
  }
}
'''

codelist = 'Code\nfoo\nbar\n'


def test_command(monkeypatch):
    with TemporaryDirectory() as d:
        with open(os.path.join(d, 'release-schema.json'), 'w') as f:
            f.write(schema)

        os.mkdir(os.path.join(d, 'codelists'))
        for basename in ('a', 'b', 'c', 'd'):
            with open(os.path.join(d, 'codelists', '{}.csv'.format(basename)), 'w') as f:
                f.write(codelist)

        with patch('sys.stdout', new_callable=StringIO) as actual:
            monkeypatch.setattr(sys, 'argv', ['ocdskit', 'set-closed-codelist-enums', d])
            main()

        assert actual.getvalue() == ''

        with open(os.path.join(d, 'release-schema.json')) as f:
            assert f.read() == schema_with_enum


def test_unused_codelists(monkeypatch, caplog):
    with TemporaryDirectory() as d:
        with open(os.path.join(d, 'release-schema.json'), 'w') as f:
            f.write(schema)

        os.mkdir(os.path.join(d, 'codelists'))
        for basename in ('a', 'b', 'c', 'd', 'e'):
            with open(os.path.join(d, 'codelists', '{}.csv'.format(basename)), 'w') as f:
                f.write(codelist)

        with patch('sys.stdout', new_callable=StringIO) as actual:
            monkeypatch.setattr(sys, 'argv', ['ocdskit', 'set-closed-codelist-enums', d])
            main()

        assert actual.getvalue() == ''

        with open(os.path.join(d, 'release-schema.json')) as f:
            assert f.read() == schema_with_enum

        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == 'ERROR'
        assert caplog.records[0].message == 'unused codelists: e.csv'


def test_missing_codelists(monkeypatch, caplog):
    with TemporaryDirectory() as d:
        with open(os.path.join(d, 'release-schema.json'), 'w') as f:
            f.write(schema)

        os.mkdir(os.path.join(d, 'codelists'))

        with pytest.raises(KeyError) as excinfo:
            with patch('sys.stdout', new_callable=StringIO) as actual:
                monkeypatch.setattr(sys, 'argv', ['ocdskit', 'set-closed-codelist-enums', d])
                main()

        assert actual.getvalue() == ''

        with open(os.path.join(d, 'release-schema.json')) as f:
            assert f.read() == schema

        assert len(caplog.records) == 0
        assert excinfo.value.args == ('a.csv',)


def test_missing_targets(monkeypatch, caplog):
    with TemporaryDirectory() as d:
        with open(os.path.join(d, 'release-schema.json'), 'w') as f:
            f.write(schema)

        os.mkdir(os.path.join(d, 'codelists'))
        for basename in ('a', 'b', 'c', 'd', '+e'):
            with open(os.path.join(d, 'codelists', '{}.csv'.format(basename)), 'w') as f:
                f.write(codelist)

        with pytest.raises(KeyError) as excinfo:
            with patch('sys.stdout', new_callable=StringIO) as actual:
                monkeypatch.setattr(sys, 'argv', ['ocdskit', 'set-closed-codelist-enums', d])
                main()

        assert actual.getvalue() == ''

        with open(os.path.join(d, 'release-schema.json')) as f:
            assert f.read() == schema

        assert len(caplog.records) == 0
        assert excinfo.value.args == ('e.csv',)


def test_conflicting_codelists(monkeypatch, caplog):
    with TemporaryDirectory() as d:
        with TemporaryDirectory() as e:
            for directory in (d, e):
                os.mkdir(os.path.join(directory, 'codelists'))

                with open(os.path.join(directory, 'release-schema.json'), 'w') as f:
                    f.write(schema)

            for basename in ('a', 'b', 'c', 'd'):
                with open(os.path.join(d, 'codelists', '{}.csv'.format(basename)), 'w') as f:
                    f.write(codelist)

            with open(os.path.join(e, 'codelists', 'a.csv'), 'w') as f:
                f.write('Code\nbaz\n')

            with patch('sys.stdout', new_callable=StringIO) as actual:
                monkeypatch.setattr(sys, 'argv', ['ocdskit', 'set-closed-codelist-enums', d, e])
                main()

            assert actual.getvalue() == ''

            with open(os.path.join(e, 'release-schema.json')) as f:
                assert f.read() == schema_with_enum

            assert len(caplog.records) == 1
            assert caplog.records[0].levelname == 'ERROR'
            assert caplog.records[0].message == 'conflicting codelists: a.csv'


def test_modified_codelists(monkeypatch):
    with TemporaryDirectory() as d:
        with TemporaryDirectory() as e:
            for directory in (d, e):
                os.mkdir(os.path.join(directory, 'codelists'))

                with open(os.path.join(directory, 'release-schema.json'), 'w') as f:
                    f.write(schema)

            for basename in ('a', 'b', 'c', 'd'):
                with open(os.path.join(d, 'codelists', '{}.csv'.format(basename)), 'w') as f:
                    f.write(codelist)

            with open(os.path.join(e, 'codelists', '+a.csv'), 'w') as f:
                f.write('Code\nbaz\n')

            with open(os.path.join(e, 'codelists', '-b.csv'), 'w') as f:
                f.write('Code,Description\nbar,bzz\n')

            with patch('sys.stdout', new_callable=StringIO) as actual:
                monkeypatch.setattr(sys, 'argv', ['ocdskit', 'set-closed-codelist-enums', d, e])
                main()

            assert actual.getvalue() == ''

            with open(os.path.join(e, 'release-schema.json')) as f:
                assert f.read() == schema_with_modification
