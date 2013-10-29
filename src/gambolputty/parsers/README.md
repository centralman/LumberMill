Parser modules
==========

#####RegexParser

Parse a string by named regular expressions.

Configuration example:

    - module: RegexParser
      configuration:
        source-field: field1                    # <default: 'data'; type: string; is: optional>
        mark-on-success: True                   # <default: False; type: boolean; is: optional>
        mark-on-failure: True                   # <default: False; type: boolean; is: optional>
        break_on_match: True                    # <default: True; type: boolean; is: optional>
        field_extraction_patterns:              # <type: [string,list]; is: required>
          httpd_access_log: ['(?P<httpd_access_log>.*)', 're.MULTILINE | re.DOTALL', 'findall']

#####UrlParser

Parse and extract url parameters.

Configuration example:

    - module: UrlParser
      configuration:
        source-field: uri       # <type: string; is: required>

#####XPathParser

Parse an xml string via xpath.

Configuration example:

    - module: XPathParser
      configuration:
        source-field: 'xml_data'                                # <type: string; is: required>
        query:  '//Item[@%(server_name)s]/@NodeDescription'     # <type: string; is: required>

#####CsvParser

Parse a string as csv data.

It will parse the csv and create or replace fields in the internal data dictionary with
the corresponding csv fields.

Configuration example:

    - module: CsvParser
      configuration:
        source-field: 'data'                    # <default: 'data'; type: string; is: optional>
        escapechar: \                           # <default: '\'; type: string; is: optional>
        skipinitialspace: False                 # <default: False; type: boolean; is: optional>
        quotechar: '"'                          # <default: '"'; type: string; is: optional>
        delimiter: ';'                          # <default: '|'; type: char; is: optional>
        fieldnames: ["gumby", "brain", "specialist"]        # <default: False; type: [list]; is: optional>
      receivers:
        - NextHandler

#####JsonParser

It will parse the json data and create or replace fields in the internal data dictionary with
the corresponding json fields.

At the moment only flat json files can be processed correctly.

Configuration example:

    - module: JsonParser
      configuration:
        source-field: 'data'                    # <default: 'data'; type: string; is: optional>
      receivers:
        - NextHandler