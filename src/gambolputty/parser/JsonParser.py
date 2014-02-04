# -*- coding: utf-8 -*-
import pprint
import re
import sys
import types
import BaseModule
from json import JSONDecoder
from Decorators import ModuleDocstringParser

json = False
for module_name in [ 'yajl', 'simplejson', 'json']:
    try:
        json = __import__(module_name)
        #print "Using %s" % module_name
        break
    except ImportError:
        pass
if not json:
    raise ImportError

json_decoder = False
for module_name in ['yajl', 'simplejson', 'json']:
    try:
        json_decoder = __import__(module_name).JSONDecoder
        #print "Using %s" % module_name
        break
    except:
        pass
if not json_decoder:
    raise ImportError

#shameless copy paste from json/decoder.py
FLAGS = re.VERBOSE | re.MULTILINE | re.DOTALL
WHITESPACE = re.compile(r'[ \t\n\r]*', FLAGS)

class ConcatJSONDecoder(JSONDecoder): # json.JSONDecoder
    def decode(self, s, _w=WHITESPACE.match):
        s_len = len(s)
        objs = []
        end = 0
        while end != s_len:
            obj, end = self.raw_decode(s, idx=_w(s, end).end())
            end = _w(s, end).end()
            objs.append(obj)
        return objs

@ModuleDocstringParser
class JsonParser(BaseModule.BaseModule):
    """
    Json codec.

    Decode:
    It will parse the json data in source fields and create or replace fields in the internal data dictionary with
    the corresponding json fields.

    Encode:
    It will build a new list of source fields and create json of this list.

    At the moment only flat json files can be processed correctly.

    mode: Either encode or decode data.
    source_fields:  Input fields for de/encode.
                    If encoding, you can set this field to 'all' to encode the complete event dict.
    target_field:   Target field for de/encode result.
                    If decoding and target is not set, the event dict itself will be updated with decoded fields.
    keep_original:  Switch to keep or drop the original fields used in de/encoding from the event dict.

    Configuration example:

    - module: JsonParser
      mode:                                   # <default: 'decode'; type: string; values: ['decode','encode']; is: optional>
      source_fields:                          # <default: 'data'; type: string||list; is: optional>
      target_field:                           # <default: None; type: None||string; is: optional>
      keep_original:                          # <default: False; type: boolean; is: optional>
      receivers:
        - NextHandler
    """

    module_type = "parser"
    """Set module type"""

    def configure(self, configuration):
        # Call parent configure method
        BaseModule.BaseModule.configure(self, configuration)
        self.source_fields = self.getConfigurationValue('source_fields')
        # Allow single string as well.
        if isinstance(self.source_fields, types.StringTypes):
            self.source_fields = [self.source_fields]
        self.target_field = self.getConfigurationValue('target_field')
        self.drop_original = not self.getConfigurationValue('keep_original')
        if self.getConfigurationValue('mode') == 'decode':
            self.handleEvent = self.decodeEvent
        else:
            self.handleEvent = self.encodeEvent

    def decodeEvent(self, event):
        for source_field in self.source_fields:
            if source_field not in event:
                continue
            json_string = str(event[source_field]).strip("'<>() ").replace('\'', '\"')
            decoded_datasets = ""
            try:
                decoded_datasets = json.loads(json_string)
            except:
                # Maybe we got a stream of json messages. Try to parse them.
                try:
                    decoded_datasets = json.loads(json_string, cls=ConcatJSONDecoder)
                except:
                    etype, evalue, etb = sys.exc_info()
                    self.logger.warning("%sCould not json decode event data: %s. Exception: %s, Error: %s.%s" % (Utils.AnsiColors.WARNING, event, etype, evalue, Utils.AnsiColors.ENDC))
                    continue
            if not isinstance(decoded_datasets, list):
                decoded_datasets = [decoded_datasets]
            copy_event = False
            for decoded_data in decoded_datasets:
                if copy_event:
                    event = event.copy()
                copy_event = True
                if self.drop_original:
                    event.pop(source_field, None)
                if self.target_field:
                    event.update({self.target_field: decoded_data})
                else:
                    event.update(decoded_data)
                yield event

    def encodeEvent(self, event):
        if 'all' in self.source_fields:
            encode_data = event
        else:
            encode_data = {}
            for source_field in self.source_fields:
                if source_field not in event:
                    continue
                encode_data.update({source_field: event[source_field]})
                if self.drop_original:
                    event.pop(source_field, None)
        try:
            encode_data = json.dumps(encode_data)
        except:
            etype, evalue, etb = sys.exc_info()
            self.logger.warning("%sCould not json encode event data: %s. Exception: %s, Error: %s.%s" % (Utils.AnsiColors.WARNING, event, etype, evalue, Utils.AnsiColors.ENDC))
            yield event
            return
        event.update({self.target_field: encode_data})
        yield event
